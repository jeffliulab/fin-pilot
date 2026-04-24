"""Tests for backend/services/stock/company_overview.py.

用 fake MarketDataProvider 注入 —— 不调真 AKShare / EDGAR。
"""

from __future__ import annotations

from typing import Any

import pytest

from backend.interfaces import (
    Announcement,
    Citation,
    FinancialMetric,
    FinancialStatements,
    Market,
    ResearchReport,
)
from backend.services.stock.company_overview import get_company_overview


class FakeProvider:
    """Stand-in MarketDataProvider with controllable return values."""

    def __init__(
        self,
        market: Market,
        financials: FinancialStatements,
        announcements: list[Announcement],
        reports: list[ResearchReport],
    ) -> None:
        self.market: Market = market
        self._financials = financials
        self._announcements = announcements
        self._reports = reports

    def get_financials(self, ticker: str) -> FinancialStatements:
        return self._financials

    def get_announcements(self, ticker: str, limit: int = 20) -> list[Announcement]:
        return self._announcements[:limit]

    def get_research_reports(self, ticker: str, limit: int = 30) -> list[ResearchReport]:
        return self._reports[:limit]


def _make_a_share_financials() -> FinancialStatements:
    """貴州茅台 4 季 sample data。"""
    return FinancialStatements(
        ticker="600519",
        market="A",
        currency="CNY",
        metrics={
            "revenue": [
                FinancialMetric(name="revenue", period="2024-09-30", value=100.0, unit="CNY"),
                FinancialMetric(name="revenue", period="2024-06-30", value=90.0, unit="CNY"),
                FinancialMetric(name="revenue", period="2024-03-31", value=80.0, unit="CNY"),
                FinancialMetric(name="revenue", period="2023-12-31", value=310.0, unit="CNY"),
            ],
            "gross_margin": [
                FinancialMetric(name="gross_margin", period="2024-09-30", value=50.5, unit="%"),
                FinancialMetric(name="gross_margin", period="2024-06-30", value=49.8, unit="%"),
            ],
        },
        citations=[
            Citation(label="[1]", source_name="AKShare · 600519", url="http://example.com/600519")
        ],
    )


def _make_announcements() -> list[Announcement]:
    return [
        Announcement(title="2024 年度业绩快报", date="2024-12-30", type="业绩报告", url="http://x/a"),
        Announcement(title="股东大会通知", date="2024-12-15", type="股东大会", url="http://x/b"),
        Announcement(title="董事辞职", date="2024-12-01", type="人事变动", url="http://x/c"),
    ]


def _make_reports() -> list[ResearchReport]:
    return [
        ResearchReport(
            title="超预期", institution="中信", analyst="张三", rating="买入",
            target_price=2200.0, price_currency="CNY", date="2024-11-05", url="http://x/r1",
        ),
        ResearchReport(
            title="维持评级", institution="华泰", analyst="李四", rating="买入",
            target_price=2100.0, price_currency="CNY", date="2024-11-04", url="http://x/r2",
        ),
        ResearchReport(
            title="谨慎乐观", institution="中金", analyst="王五", rating="增持",
            target_price=1900.0, price_currency="CNY", date="2024-11-03", url=None,
        ),
        ResearchReport(
            title="无目标价", institution="国泰君安", analyst=None, rating=None,
            target_price=None, price_currency="CNY", date="2024-11-02", url=None,
        ),
    ]


class TestGetCompanyOverview:
    def test_returns_three_cards(self) -> None:
        provider = FakeProvider(
            market="A",
            financials=_make_a_share_financials(),
            announcements=_make_announcements(),
            reports=_make_reports(),
        )
        cards = get_company_overview("600519", provider=provider)
        assert len(cards) == 3
        assert [c.card_type for c in cards] == [
            "financial_kpi",
            "announcement_timeline",
            "research_report",
        ]
        # 全部 card 复用同一个 ticker / market
        assert all(c.ticker == "600519" for c in cards)
        assert all(c.market == "A" for c in cards)

    def test_financial_card_payload_shape(self) -> None:
        provider = FakeProvider(
            market="A",
            financials=_make_a_share_financials(),
            announcements=[],
            reports=[],
        )
        cards = get_company_overview("600519", provider=provider)
        kpi = cards[0]
        assert kpi.card_type == "financial_kpi"
        payload = kpi.payload
        assert payload["currency"] == "CNY"
        # revenue + gross_margin 两个指标
        names = [s["name"] for s in payload["summary"]]
        assert "revenue" in names
        assert "gross_margin" in names
        # revenue 的 trend：4 期，按时间正序
        revenue_summary = next(s for s in payload["summary"] if s["name"] == "revenue")
        assert revenue_summary["display_name"] == "营业总收入"
        assert revenue_summary["latest_value"] == 100.0
        assert revenue_summary["latest_period"] == "2024-09-30"
        assert revenue_summary["trend"] == [310.0, 80.0, 90.0, 100.0]  # 旧→新
        # citations 透传
        assert kpi.citations and kpi.citations[0].label == "[1]"

    def test_announcement_card_serializes_dataclass(self) -> None:
        provider = FakeProvider(
            market="A",
            financials=_make_a_share_financials(),
            announcements=_make_announcements(),
            reports=[],
        )
        cards = get_company_overview("600519", provider=provider, announcement_limit=2)
        ann_card = cards[1]
        assert ann_card.card_type == "announcement_timeline"
        items = ann_card.payload["items"]
        assert len(items) == 2  # respects limit
        assert items[0]["title"] == "2024 年度业绩快报"
        assert items[0]["date"] == "2024-12-30"
        assert items[0]["type"] == "业绩报告"

    def test_research_card_computes_consensus_and_distribution(self) -> None:
        provider = FakeProvider(
            market="A",
            financials=_make_a_share_financials(),
            announcements=[],
            reports=_make_reports(),
        )
        cards = get_company_overview("600519", provider=provider)
        research = cards[2]
        assert research.card_type == "research_report"
        meta = research.payload
        # consensus = 平均(2200, 2100, 1900) = 2066.67
        assert meta["consensus_target"] == pytest.approx(2066.67, rel=1e-3)
        assert meta["consensus_target_basis"] == 3
        # 评级分布：买入 2, 增持 1（None 不计）
        assert meta["rating_distribution"]["买入"] == 2
        assert meta["rating_distribution"]["增持"] == 1
        assert "None" not in meta["rating_distribution"]
        assert meta["report_count"] == 4

    def test_us_market_research_card_has_explanatory_citation(self) -> None:
        us_financials = FinancialStatements(
            ticker="AAPL", market="US", currency="USD", metrics={}, citations=[]
        )
        provider = FakeProvider(
            market="US", financials=us_financials, announcements=[], reports=[]
        )
        cards = get_company_overview("AAPL", provider=provider)
        research = cards[2]
        assert research.market == "US"
        assert any("EDGAR 不收录卖方研报" in c.source_name for c in research.citations)
