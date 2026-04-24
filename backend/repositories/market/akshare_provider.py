"""A 股数据 provider —— 通过 akshare 访问东方财富 / 新浪 / 巨潮等公开数据源.

实现 ``MarketDataProvider`` 协议（financials / announcements / research_reports）。
研报字段**只入元数据**（标题/机构/评级/目标价/链接），不入正文 —— 见
docs/research/data-sources.md §4 Q2 的合规理由。

AKShare 接口约定：
- 输入 ticker 用 6 位裸 code（如 "600519"），无 .SS/.SZ 后缀
- 部分函数需要带交易所前缀（如 "sh600519"），由 ``_to_sina_format`` 转换
- 上游接口偶发限流 / 改版，所有调用包在 ``DataSourceError`` 中

NOTE：AKShare API 在不同小版本间偶有变动；本文件中的函数名 / 列名假设
akshare>=1.15。venv 配置后跑 ``pytest backend/tests/test_akshare_provider.py``
做冒烟测试。
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from backend.constants import (
    A_SHARE_BJ_PREFIX,
    A_SHARE_SH_PREFIX,
    A_SHARE_SZ_PREFIX,
    DEFAULT_ANNOUNCEMENT_LIMIT,
    DEFAULT_FINANCIAL_PERIODS,
    DEFAULT_RESEARCH_REPORT_LIMIT,
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

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# === Ticker 规范化 ===
def _strip_suffix(ticker: str) -> str:
    """Drop ``.SS`` / ``.SZ`` / ``.BJ`` suffix to get pure 6-digit code."""
    t = ticker.upper().strip()
    for suffix in (".SS", ".SZ", ".BJ"):
        if t.endswith(suffix):
            return t[: -len(suffix)]
    return t


def _to_sina_format(ticker: str) -> str:
    """Convert "600519" → "sh600519" / "000858" → "sz000858" for sina-style APIs."""
    code = _strip_suffix(ticker)
    if code.startswith(A_SHARE_SH_PREFIX):
        return f"sh{code}"
    if code.startswith(A_SHARE_SZ_PREFIX):
        return f"sz{code}"
    if code.startswith(A_SHARE_BJ_PREFIX):
        return f"bj{code}"
    raise ValueError(f"Unrecognized A-share ticker: {ticker}")


def _normalize_period(raw: str) -> str:
    """AKShare 期间列名是 'YYYYMMDD'（如 '20260331'）；标准化为 'YYYY-MM-DD'."""
    s = str(raw).strip()
    if len(s) == 8 and s.isdigit():
        return f"{s[:4]}-{s[4:6]}-{s[6:8]}"
    return s


# === Provider ===
class AKShareProvider:
    """A 股市场数据 provider，实现 ``MarketDataProvider`` Protocol。"""

    market: Market = "A"

    # AKShare 在 import 时会做 pandas 检查，import 较慢；用 lazy import
    def _akshare(self):  # pragma: no cover - thin wrapper
        import akshare as ak

        return ak

    # === Financials ===
    def get_financials(self, ticker: str) -> FinancialStatements:
        """Fetch standardized A-share financial summary via ``stock_financial_abstract``.

        AKShare 返回的 DataFrame 形如：
            选项 | 指标       | 2024-09-30 | 2024-06-30 | ...
            按报告期 | 营业总收入  | xxx        | xxx
            按报告期 | 净利润     | xxx        | xxx

        我们抽取关键 KPI 行 + 最近 ``DEFAULT_FINANCIAL_PERIODS`` 列。
        """
        code = _strip_suffix(ticker)
        ak = self._akshare()
        try:
            df = ak.stock_financial_abstract(symbol=code)
        except Exception as exc:
            raise DataSourceError("AKShare", f"stock_financial_abstract({code}) 失败", cause=exc) from exc

        if df is None or df.empty:
            raise DataSourceError("AKShare", f"{code} 财务数据为空")

        # 抽前 N 个期间（最新在最前，AKShare 默认倒序）
        period_cols = [c for c in df.columns if c not in ("选项", "指标")][:DEFAULT_FINANCIAL_PERIODS]

        # 需要采集的中文指标 → 英文 metric_name 映射
        metric_map = {
            "营业总收入": "revenue",
            "归母净利润": "net_income",
            "经营活动产生的现金流量净额": "operating_cash_flow",
            "毛利率": "gross_margin",
            "净资产收益率(ROE)": "roe",
            "资产负债率": "debt_ratio",
        }

        metrics: dict[str, list[FinancialMetric]] = {}
        for cn_name, en_name in metric_map.items():
            row = df[df["指标"] == cn_name]
            if row.empty:
                continue
            row = row.iloc[0]
            metric_list: list[FinancialMetric] = []
            for period in period_cols:
                raw_val = row.get(period)
                value: float | None = None
                if raw_val is not None and str(raw_val).strip() not in ("", "--", "nan"):
                    try:
                        value = float(raw_val)
                    except (TypeError, ValueError):
                        value = None
                # 比例类指标（毛利率 / ROE / 资产负债率）单位是 %
                unit = "%" if en_name in {"gross_margin", "roe", "debt_ratio"} else "CNY"
                metric_list.append(
                    FinancialMetric(
                        name=en_name,
                        period=_normalize_period(period),
                        value=value,
                        unit=unit,
                    )
                )
            metrics[en_name] = metric_list

        return FinancialStatements(
            ticker=code,
            market="A",
            currency="CNY",
            metrics=metrics,
            citations=[
                Citation(
                    label="[1]",
                    source_name=f"AKShare · {code} 关键财务指标",
                    url=f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code={code}",
                )
            ],
        )

    # === Announcements ===
    def get_announcements(
        self, ticker: str, limit: int = DEFAULT_ANNOUNCEMENT_LIMIT
    ) -> list[Announcement]:
        """Per-stock announcements via ``stock_zh_a_disclosure_report_cninfo``.

        AKShare 1.18 列约定：
            代码 | 简称 | 公告标题 | 公告时间 | 公告链接

        注：旧 ``stock_notice_report`` 的 ``symbol`` 参数其实是市场分类（"全部"
        / "沪深京A股"），不是 ticker；切换到 cninfo 接口拿 per-stock 公告。
        """
        code = _strip_suffix(ticker)
        ak = self._akshare()
        try:
            df = ak.stock_zh_a_disclosure_report_cninfo(symbol=code)
        except Exception as exc:
            raise DataSourceError(
                "AKShare",
                f"stock_zh_a_disclosure_report_cninfo({code}) 失败",
                cause=exc,
            ) from exc

        if df is None or df.empty:
            return []

        # 列名容错（cninfo 接口标准列名）
        col_title = next((c for c in df.columns if c in ("公告标题", "title")), None)
        col_date = next(
            (c for c in df.columns if c in ("公告时间", "公告日期", "date", "日期")),
            None,
        )
        col_url = next(
            (c for c in df.columns if c in ("公告链接", "网址", "url", "链接")), None
        )
        col_type = next(
            (c for c in df.columns if c in ("公告类型", "type", "类型")), None
        )

        if not (col_title and col_date):
            logger.warning(
                "stock_zh_a_disclosure_report_cninfo columns 未识别: %s",
                list(df.columns),
            )
            return []

        items: list[Announcement] = []
        for _, row in df.head(limit).iterrows():
            url_val = row.get(col_url) if col_url else None
            items.append(
                Announcement(
                    title=str(row[col_title]),
                    date=str(row[col_date])[:10],
                    type=str(row[col_type]) if col_type else "",
                    url=str(url_val) if url_val else "",
                )
            )
        return items

    # === Research reports ===
    def get_research_reports(
        self, ticker: str, limit: int = DEFAULT_RESEARCH_REPORT_LIMIT
    ) -> list[ResearchReport]:
        """Fetch recent sell-side research reports metadata via ``stock_research_report_em``.

        合规要点：**只入元数据**，不入正文 —— 版权属券商。
        AKShare 1.15+ 列约定：
            股票代码 | 股票简称 | 报告名称 | 东财评级 | 机构 | 近一月个股研报数 |
            最新目标价 | 报告日期 | 分析师 | 报告 PDF 链接
        """
        code = _strip_suffix(ticker)
        ak = self._akshare()
        try:
            df = ak.stock_research_report_em(symbol=code)
        except Exception as exc:
            raise DataSourceError(
                "AKShare", f"stock_research_report_em({code}) 失败", cause=exc
            ) from exc

        if df is None or df.empty:
            return []

        col_title = next(
            (c for c in df.columns if c in ("报告名称", "title", "研报名称")), None
        )
        col_inst = next(
            (c for c in df.columns if c in ("机构", "institution", "研究机构")), None
        )
        col_rating = next(
            (c for c in df.columns if c in ("东财评级", "rating", "评级")), None
        )
        # AKShare 1.18 没"最新目标价"列；保留容错
        col_target = next(
            (c for c in df.columns if c in ("最新目标价", "target_price", "目标价")), None
        )
        # AKShare 1.18 列名是 "日期"，旧版本是 "报告日期"
        col_date = next(
            (c for c in df.columns if c in ("日期", "报告日期", "date")), None
        )
        col_analyst = next(
            (c for c in df.columns if c in ("分析师", "analyst")), None
        )
        # AKShare 1.18 列名是 "报告PDF链接"（无空格），旧版本带空格
        col_url = next(
            (
                c
                for c in df.columns
                if c in ("报告PDF链接", "报告 PDF 链接", "url", "链接", "PDF链接")
            ),
            None,
        )

        if not (col_title and col_inst and col_date):
            logger.warning(
                "stock_research_report_em columns 未识别: %s", list(df.columns)
            )
            return []

        items: list[ResearchReport] = []
        for _, row in df.head(limit).iterrows():
            target_val: float | None = None
            if col_target and row.get(col_target) is not None:
                try:
                    target_val = float(row[col_target])
                except (TypeError, ValueError):
                    target_val = None
            items.append(
                ResearchReport(
                    title=str(row[col_title]),
                    institution=str(row[col_inst]),
                    analyst=str(row[col_analyst]) if col_analyst else None,
                    rating=str(row[col_rating]) if col_rating else None,
                    target_price=target_val,
                    price_currency="CNY",
                    date=str(row[col_date])[:10],
                    url=str(row[col_url]) if col_url and row[col_url] else None,
                )
            )
        return items
