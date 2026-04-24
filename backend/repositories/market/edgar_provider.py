"""美股 SEC EDGAR 数据 provider —— 通过 data.sec.gov 官方公开 API.

实现 ``MarketDataProvider`` 协议（financials / announcements）。
**研报维度返回空列表** —— EDGAR 不提供研报；想做美股研报演示走 Seeking Alpha
公开文章或 SEC 10-K MD&A 章节，详见 docs/research/data-sources.md §4 Q2。

EDGAR 使用约定：
- 必须在 HTTP 头里带 ``User-Agent``（含联系方式），否则 SEC 返回 403
- 速率限制 10 req/s/IP；本实现统一 sleep 150ms（~7 req/s 安全裕度）
- ticker → CIK 映射通过 ``company_tickers.json`` 一次性加载并缓存

主要 XBRL 概念（us-gaap taxonomy）：
- Revenues / RevenueFromContractWithCustomerExcludingAssessedTax
- NetIncomeLoss
- NetCashProvidedByUsedInOperatingActivities
- StockholdersEquity (用于 ROE 计算)
"""

from __future__ import annotations

import logging
import os
import threading
import time

import httpx

from backend.constants import (
    DEFAULT_ANNOUNCEMENT_LIMIT,
    DEFAULT_FINANCIAL_PERIODS,
    DEFAULT_HTTP_TIMEOUT_SEC,
    DEFAULT_RESEARCH_REPORT_LIMIT,  # noqa: F401  保留 import 以便统一接口签名
    EDGAR_BASE_URL,
    EDGAR_FORMS_FOR_ANNOUNCEMENTS,
    EDGAR_RATE_LIMIT_SLEEP_SEC,
    EDGAR_TICKER_CIK_URL,
)
from backend.interfaces import (
    Announcement,
    Citation,
    DataSourceError,
    FinancialMetric,
    FinancialStatements,
    Market,
    ResearchReport,
)

logger = logging.getLogger(__name__)


# === Ticker → CIK 缓存（进程级单例） ===
_ticker_cik_cache: dict[str, str] | None = None
_cache_lock = threading.Lock()


def _get_user_agent() -> str:
    """SEC 要求 User-Agent 含联系方式 —— 从环境变量读，没设就给一个降级值并 warn."""
    ua = os.getenv("SEC_EDGAR_USER_AGENT")
    if not ua:
        logger.warning(
            "SEC_EDGAR_USER_AGENT 未配置，使用降级值；生产环境必须按 SEC 要求"
            "设置 'YourName your@email.com' 形式"
        )
        return "FinPilot dev unknown@example.com"
    return ua


def _load_ticker_cik_map(client: httpx.Client) -> dict[str, str]:
    """Lazy-load + cache the ticker→CIK 10-digit zero-padded map."""
    global _ticker_cik_cache
    if _ticker_cik_cache is not None:
        return _ticker_cik_cache
    with _cache_lock:
        if _ticker_cik_cache is not None:  # double-check
            return _ticker_cik_cache
        try:
            resp = client.get(EDGAR_TICKER_CIK_URL)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise DataSourceError("EDGAR", f"加载 ticker→CIK 映射失败: {exc}", cause=exc) from exc

        data = resp.json()
        # JSON 形如 {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
        mapping: dict[str, str] = {}
        for entry in data.values():
            ticker = str(entry.get("ticker", "")).upper()
            cik = entry.get("cik_str")
            if ticker and cik is not None:
                mapping[ticker] = str(cik).zfill(10)
        _ticker_cik_cache = mapping
        logger.info("EDGAR ticker→CIK map loaded: %d tickers", len(mapping))
        return mapping


# === Provider ===
class EdgarProvider:
    """美股 SEC EDGAR provider，实现 ``MarketDataProvider`` Protocol。"""

    market: Market = "US"

    def __init__(self) -> None:
        self._client = httpx.Client(
            headers={"User-Agent": _get_user_agent(), "Accept": "application/json"},
            timeout=DEFAULT_HTTP_TIMEOUT_SEC,
        )

    def __del__(self) -> None:  # pragma: no cover
        try:
            self._client.close()
        except Exception:
            pass

    # === 内部工具 ===
    def _ticker_to_cik(self, ticker: str) -> str:
        ticker = ticker.upper().strip()
        mapping = _load_ticker_cik_map(self._client)
        cik = mapping.get(ticker)
        if not cik:
            raise DataSourceError("EDGAR", f"ticker '{ticker}' 不在 SEC 公司列表中")
        return cik

    def _get_companyfacts(self, cik: str) -> dict:
        url = f"{EDGAR_BASE_URL}/api/xbrl/companyfacts/CIK{cik}.json"
        time.sleep(EDGAR_RATE_LIMIT_SLEEP_SEC)
        try:
            resp = self._client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise DataSourceError("EDGAR", f"companyfacts CIK{cik} 失败: {exc}", cause=exc) from exc
        return resp.json()

    def _get_submissions(self, cik: str) -> dict:
        url = f"{EDGAR_BASE_URL}/submissions/CIK{cik}.json"
        time.sleep(EDGAR_RATE_LIMIT_SLEEP_SEC)
        try:
            resp = self._client.get(url)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            raise DataSourceError("EDGAR", f"submissions CIK{cik} 失败: {exc}", cause=exc) from exc
        return resp.json()

    @staticmethod
    def _extract_metric_periods(
        facts: dict,
        concept_candidates: list[str],
        unit: str = "USD",
        max_periods: int = DEFAULT_FINANCIAL_PERIODS,
    ) -> list[FinancialMetric]:
        """Extract last ``max_periods`` quarterly values for any concept that exists.

        XBRL companyfacts 的结构：
            facts['us-gaap'][CONCEPT]['units'][UNIT] = [{end, val, form, fy, fp, ...}, ...]
        我们优先取 form='10-Q' 的季度数据，按 end date 倒序去重后取前 N。
        """
        gaap = facts.get("facts", {}).get("us-gaap", {})
        for concept in concept_candidates:
            entry = gaap.get(concept)
            if not entry:
                continue
            unit_data = entry.get("units", {}).get(unit, [])
            if not unit_data:
                continue
            # 优先 10-Q 季度数据；同 end date 去重保留 form 优先级 10-K > 10-Q
            buckets: dict[str, dict] = {}
            for item in unit_data:
                end = item.get("end")
                if not end:
                    continue
                # 去重：10-K 优先于 10-Q（年报包含季报数据）
                if end in buckets and buckets[end].get("form") == "10-K":
                    continue
                buckets[end] = item

            sorted_items = sorted(buckets.values(), key=lambda x: x.get("end", ""), reverse=True)[
                :max_periods
            ]
            return [
                FinancialMetric(
                    name=concept,
                    period=item["end"],
                    value=float(item["val"]) if item.get("val") is not None else None,
                    unit=unit,
                )
                for item in sorted_items
            ]
        return []

    # === API ===
    def get_financials(self, ticker: str) -> FinancialStatements:
        cik = self._ticker_to_cik(ticker)
        facts = self._get_companyfacts(cik)

        # 不同公司用不同 concept 名（Revenues vs RevenueFromContractWithCustomer...）
        revenue = self._extract_metric_periods(
            facts,
            ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"],
        )
        net_income = self._extract_metric_periods(facts, ["NetIncomeLoss"])
        ocf = self._extract_metric_periods(
            facts, ["NetCashProvidedByUsedInOperatingActivities"]
        )
        equity = self._extract_metric_periods(facts, ["StockholdersEquity"])

        # Rename concept → standardized metric name for the cross-layer contract
        metrics: dict[str, list[FinancialMetric]] = {
            "revenue": [_renamed(m, "revenue") for m in revenue],
            "net_income": [_renamed(m, "net_income") for m in net_income],
            "operating_cash_flow": [_renamed(m, "operating_cash_flow") for m in ocf],
        }
        # Compute ROE from net_income / stockholders_equity if both available
        if net_income and equity:
            roe_metrics: list[FinancialMetric] = []
            equity_by_period = {m.period: m.value for m in equity}
            for m in net_income:
                eq_val = equity_by_period.get(m.period)
                roe_val = (
                    (m.value / eq_val * 100.0)
                    if (m.value is not None and eq_val and eq_val != 0)
                    else None
                )
                roe_metrics.append(
                    FinancialMetric(name="roe", period=m.period, value=roe_val, unit="%")
                )
            metrics["roe"] = roe_metrics

        return FinancialStatements(
            ticker=ticker.upper(),
            market="US",
            currency="USD",
            metrics=metrics,
            citations=[
                Citation(
                    label="[1]",
                    source_name=f"SEC EDGAR · {ticker.upper()} Company Facts (XBRL)",
                    url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}",
                )
            ],
        )

    def get_announcements(
        self, ticker: str, limit: int = DEFAULT_ANNOUNCEMENT_LIMIT
    ) -> list[Announcement]:
        cik = self._ticker_to_cik(ticker)
        sub = self._get_submissions(cik)
        recent = sub.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accession_numbers = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])

        items: list[Announcement] = []
        for i, form in enumerate(forms):
            if form not in EDGAR_FORMS_FOR_ANNOUNCEMENTS:
                continue
            acc_no = accession_numbers[i] if i < len(accession_numbers) else ""
            primary = primary_docs[i] if i < len(primary_docs) else ""
            acc_no_nodash = acc_no.replace("-", "")
            url = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_no_nodash}/{primary}"
                if acc_no and primary
                else ""
            )
            items.append(
                Announcement(
                    title=f"{form} filing",
                    date=dates[i] if i < len(dates) else "",
                    type=form,
                    url=url,
                )
            )
            if len(items) >= limit:
                break
        return items

    def get_research_reports(
        self, ticker: str, limit: int = DEFAULT_RESEARCH_REPORT_LIMIT
    ) -> list[ResearchReport]:
        """SEC EDGAR 不提供研报；返回空列表 —— 见 docs/research/data-sources.md §4 Q2."""
        return []


def _renamed(metric: FinancialMetric, new_name: str) -> FinancialMetric:
    """Return a copy of the metric with a different ``name`` (XBRL concept → standardized)."""
    return FinancialMetric(name=new_name, period=metric.period, value=metric.value, unit=metric.unit)
