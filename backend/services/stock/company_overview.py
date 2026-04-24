"""Service: 拼装公司主页的 3 张 CompanyCard.

调 ``MarketDataProvider`` 拿三类原始数据 → 标准化为前端 workspace 卡片的
``CompanyCard.payload`` schema。

v0.1 三张卡（与 docs/PRD.md §3 / docs/architecture.md §1 对齐）：
1. financial_kpi —— 关键 KPI（营收 / 净利 / 现金流 / 毛利 / ROE / 资产负债率）+ 4 期趋势
2. announcement_timeline —— 最近 20 条公告
3. research_report —— 最近 30 条研报元数据 + 共识目标价 + 评级分布

按 stacks/python-backend.md：service 层不感知 HTTP / Request / Response。
"""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import asdict

from backend.constants import (
    DEFAULT_ANNOUNCEMENT_LIMIT,
    DEFAULT_RESEARCH_REPORT_LIMIT,
)
from backend.interfaces import (
    Announcement,
    Citation,
    CompanyCard,
    FinancialMetric,
    FinancialStatements,
    Market,
    MarketDataProvider,
    ResearchReport,
)
from backend.repositories.market.factory import get_provider

logger = logging.getLogger(__name__)


# === KPI display 映射 ===
_KPI_DISPLAY_NAMES = {
    "revenue": "营业总收入",
    "net_income": "归母净利润",
    "operating_cash_flow": "经营现金流",
    "gross_margin": "毛利率",
    "roe": "净资产收益率",
    "debt_ratio": "资产负债率",
}


def _build_kpi_summary(metrics: dict[str, list[FinancialMetric]]) -> list[dict]:
    """把 metrics dict → 前端可直接渲染的 summary 列表。"""
    summary: list[dict] = []
    for metric_name, periods in metrics.items():
        if not periods:
            continue
        latest = periods[0]  # provider 保证最新在前
        # trend: 按时间正序（旧 → 新），方便前端 Recharts 直接喂
        trend_chronological = [
            (p.value if p.value is not None else None) for p in reversed(periods)
        ]
        summary.append(
            {
                "name": metric_name,
                "display_name": _KPI_DISPLAY_NAMES.get(metric_name, metric_name),
                "latest_value": latest.value,
                "latest_period": latest.period,
                "unit": latest.unit,
                "trend": trend_chronological,
                "trend_periods": [p.period for p in reversed(periods)],
            }
        )
    return summary


def _build_research_meta(reports: list[ResearchReport]) -> dict:
    """共识目标价 + 评级分布。"""
    target_prices = [r.target_price for r in reports if r.target_price is not None]
    consensus_target = (
        round(sum(target_prices) / len(target_prices), 2) if target_prices else None
    )
    rating_distribution = dict(
        Counter(r.rating for r in reports if r.rating).most_common()
    )
    return {
        "consensus_target": consensus_target,
        "consensus_target_basis": len(target_prices),
        "rating_distribution": rating_distribution,
        "report_count": len(reports),
    }


def _financial_card(stmt: FinancialStatements) -> CompanyCard:
    payload = {
        "summary": _build_kpi_summary(stmt.metrics),
        "currency": stmt.currency,
    }
    return CompanyCard(
        ticker=stmt.ticker,
        market=stmt.market,
        card_type="financial_kpi",
        title="财务 KPI（最近 4 期）",
        payload=payload,
        citations=stmt.citations,
    )


def _announcement_card(
    items: list[Announcement], ticker: str, market: Market
) -> CompanyCard:
    return CompanyCard(
        ticker=ticker,
        market=market,
        card_type="announcement_timeline",
        title=f"公告时间线（最近 {len(items)} 条）",
        payload={"items": [asdict(it) for it in items]},
        citations=[],
    )


def _research_card(
    items: list[ResearchReport], ticker: str, market: Market
) -> CompanyCard:
    payload = {
        "items": [asdict(r) for r in items],
        **_build_research_meta(items),
    }
    title = f"研报评级（最近 {len(items)} 条）" if items else "研报评级（暂无）"
    citations: list[Citation] = []
    if market == "US":
        # US 端 EDGAR 不出研报，用一条解释性 citation 标注
        citations.append(
            Citation(
                label="[*]",
                source_name="说明：SEC EDGAR 不收录卖方研报，US 端研报字段在 v0.6 港股 + Seeking Alpha 集成后开放",
                url="https://github.com/jeffliulab/fin-pilot/blob/main/docs/research/data-sources.md#13-研报",
            )
        )
    return CompanyCard(
        ticker=ticker,
        market=market,
        card_type="research_report",
        title=title,
        payload=payload,
        citations=citations,
    )


# === 公开 API ===
def get_company_overview(
    ticker: str,
    *,
    announcement_limit: int = DEFAULT_ANNOUNCEMENT_LIMIT,
    research_limit: int = DEFAULT_RESEARCH_REPORT_LIMIT,
    provider: MarketDataProvider | None = None,
) -> list[CompanyCard]:
    """Build the 3-card workspace for one company's main page.

    Args:
        ticker: 股票代码（A 股 6 位 / 美股 alpha）；factory 会自动选 provider
        announcement_limit: 公告最多返回多少条
        research_limit: 研报最多返回多少条
        provider: 注入用 —— 测试时 mock；production 留空让 factory 选

    Returns:
        list[CompanyCard]：3 张固定顺序的卡（财务 / 公告 / 研报）

    Raises:
        UnsupportedMarketError: ticker 不属于 A/US（v0.1 范围外）
        DataSourceError: 上游接口失败
    """
    if provider is None:
        provider = get_provider(ticker)

    logger.info("Building company overview for ticker=%s via %s", ticker, type(provider).__name__)

    # v0.1 串行调用：3 个接口约 3-5s 总耗时；v0.2 再考虑 ThreadPool 并行
    financials = provider.get_financials(ticker)
    announcements = provider.get_announcements(ticker, limit=announcement_limit)
    research = provider.get_research_reports(ticker, limit=research_limit)

    cards = [
        _financial_card(financials),
        _announcement_card(announcements, ticker=financials.ticker, market=financials.market),
        _research_card(research, ticker=financials.ticker, market=financials.market),
    ]
    logger.info(
        "Built %d cards for %s (announcements=%d, research=%d)",
        len(cards),
        ticker,
        len(announcements),
        len(research),
    )
    return cards
