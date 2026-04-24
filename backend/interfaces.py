"""跨层契约 —— 所有 routes / services / repositories 共用的 dataclass 与 Protocol.

按 agent-rules/principles/architecture.md：跨模块通信优先通过接口契约而不是直接耦合实现。
任何会被多层引用的数据形状都集中在这里，避免循环 import。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol

# === Market type aliases ===
# v0.1 只支持 A 股 + 美股；类型标注为字面量便于编辑器与 mypy 报错
Market = Literal["A", "US"]


# === Citation：所有 AI 输出的引用统一格式 ===
@dataclass
class Citation:
    """A pointer to the original source backing an AI claim or a card field.

    Rendered as ``[N]`` superscript inline in chat / cards; clicking opens a
    side drawer with the URL.
    """

    label: str  # e.g. "[1]"
    source_name: str  # e.g. "巨潮·贵州茅台 2024 年度报告" / "SEC 10-K Apple 2024"
    url: str  # 真实可点击 URL


# === 财务数据 ===
@dataclass
class FinancialMetric:
    """One metric value at one period (季度 or 年度)."""

    name: str  # e.g. "revenue" / "net_income" / "operating_cash_flow"
    period: str  # e.g. "2024Q4" / "2024-FY"
    value: float | None  # None = 缺失
    unit: str  # e.g. "CNY" / "USD" / "%"


@dataclass
class FinancialStatements:
    """A company's standardized financial statements over recent periods.

    Layout：metrics 是 ``{metric_name: [FinancialMetric, ...]}``，
    每个 metric 内部按 period 倒序（最新季度在前）。
    """

    ticker: str
    market: Market
    currency: str  # 主报告币种
    metrics: dict[str, list[FinancialMetric]] = field(default_factory=dict)
    citations: list[Citation] = field(default_factory=list)


# === 公告 ===
@dataclass
class Announcement:
    """One filing / disclosure / announcement."""

    title: str
    date: str  # ISO date string "YYYY-MM-DD"
    type: str  # e.g. "年报" / "业绩预告" / "10-K" / "8-K"
    url: str  # PDF / HTML URL


# === 研报 ===
@dataclass
class ResearchReport:
    """Sell-side research report metadata.

    v0.1 只入元数据（标题 / 机构 / 评级 / 目标价 / 链接），不入正文。
    版权归券商；详见 docs/research/data-sources.md §4 Q2。
    """

    title: str
    institution: str  # 券商 / 研究机构名称
    analyst: str | None  # 分析师姓名（可缺）
    rating: str | None  # 评级 e.g. "买入" / "增持" / "Buy" / "Outperform"
    target_price: float | None  # 目标价（数值，单位与 price_currency 一致）
    price_currency: str  # e.g. "CNY" / "USD"
    date: str  # 发布日期 ISO string
    url: str | None  # 原文 URL（可缺）


# === 工作区卡片：service → routes → 前端 ===
CardType = Literal["financial_kpi", "announcement_timeline", "research_report"]


@dataclass
class CompanyCard:
    """A workspace card rendered as one section of the company main page.

    payload 的 schema 由 card_type 决定：
      - financial_kpi: {"summary": [{name, latest_value, yoy_change, ...}]}
      - announcement_timeline: {"items": [Announcement.__dict__, ...]}
      - research_report: {"items": [ResearchReport.__dict__, ...], "consensus_target": float}
    """

    ticker: str
    market: Market
    card_type: CardType
    title: str  # 卡片标题，e.g. "财务 KPI（最近 4 季度）"
    payload: dict
    citations: list[Citation] = field(default_factory=list)


# === Repository contract：services 与 repositories 之间的边界 ===
class MarketDataProvider(Protocol):
    """A market data provider for one country / exchange.

    实现：
      - AKShareProvider (A 股，repositories/market/akshare_provider.py)
      - EdgarProvider (美股 SEC，repositories/market/edgar_provider.py)

    factory.py 根据 ticker 自动选择对应实现。
    """

    market: Market

    def get_financials(self, ticker: str) -> FinancialStatements:
        """Fetch standardized financials for the given ticker.

        Raises:
            ValueError: ticker 不属于本 provider 的 market
            DataSourceError: 上游接口失败 / 限流 / 数据缺失
        """
        ...

    def get_announcements(self, ticker: str, limit: int = 20) -> list[Announcement]:
        """Fetch most recent ``limit`` announcements / filings, newest first."""
        ...

    def get_research_reports(self, ticker: str, limit: int = 30) -> list[ResearchReport]:
        """Fetch most recent ``limit`` research reports metadata, newest first.

        美股端可能返回空列表（SEC EDGAR 不提供研报）。
        """
        ...


# === Errors ===
class DataSourceError(RuntimeError):
    """Raised when an external data source (AKShare / EDGAR / yfinance) fails.

    携带原始 exception + 数据源名称，让上层决定降级 / 重试 / 报错给用户。
    """

    def __init__(self, source: str, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(f"[{source}] {message}")
        self.source = source
        self.cause = cause
