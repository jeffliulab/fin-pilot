"""Tests for AKShareProvider —— 用 monkeypatch 把 ``_akshare()`` 替成假对象，
无需真的调 AKShare 上游接口.

verifies：
- ticker 规范化（剥后缀）
- DataFrame → FinancialStatements 抽取逻辑（关键 KPI 行 + 期间倒序）
- 公告 / 研报 列名容错（中英混杂）
- 上游异常 → DataSourceError
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

import pandas as pd
import pytest

from backend.interfaces import DataSourceError
from backend.repositories.market.akshare_provider import AKShareProvider, _strip_suffix, _to_sina_format


class TestNormalization:
    @pytest.mark.parametrize(
        "input_,expected",
        [("600519.SS", "600519"), ("000858.SZ", "000858"), ("600519", "600519"), ("aapl", "AAPL")],
    )
    def test_strip_suffix(self, input_: str, expected: str) -> None:
        assert _strip_suffix(input_) == expected

    @pytest.mark.parametrize(
        "input_,expected",
        [("600519", "sh600519"), ("600519.SS", "sh600519"), ("000858.SZ", "sz000858")],
    )
    def test_to_sina_format_known_prefixes(self, input_: str, expected: str) -> None:
        assert _to_sina_format(input_) == expected

    def test_to_sina_format_rejects_unknown(self) -> None:
        with pytest.raises(ValueError):
            _to_sina_format("999999")


def _make_financial_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "选项": ["按报告期"] * 3,
            "指标": ["营业总收入", "归母净利润", "毛利率"],
            "2024-09-30": [100.0, 30.0, 50.5],
            "2024-06-30": [90.0, 25.0, 49.8],
            "2024-03-31": [80.0, 22.0, 48.0],
            "2023-12-31": [310.0, 95.0, 51.2],
        }
    )


def _make_notice_df() -> pd.DataFrame:
    """模拟 ak.stock_zh_a_disclosure_report_cninfo 的返回（AKShare 1.18+）."""
    return pd.DataFrame(
        {
            "代码": ["600519", "600519"],
            "简称": ["贵州茅台", "贵州茅台"],
            "公告标题": ["2024 年度业绩快报", "关于召开股东大会的通知"],
            "公告时间": ["2024-12-30", "2024-12-15"],
            "公告链接": ["http://example.com/a.pdf", "http://example.com/b.pdf"],
        }
    )


def _make_research_df() -> pd.DataFrame:
    """模拟 ak.stock_research_report_em 的返回（AKShare 1.18：'日期'/'报告PDF链接'，无空格）."""
    return pd.DataFrame(
        {
            "股票代码": ["600519"],
            "股票简称": ["贵州茅台"],
            "报告名称": ["2024Q4 点评：业绩超预期"],
            "东财评级": ["买入"],
            "机构": ["中信证券"],
            "日期": ["2024-11-05"],
            "分析师": ["张三"],
            "报告PDF链接": ["http://example.com/r.pdf"],
        }
    )


class FakeAk:
    """Stand-in for the akshare module with controllable return values."""

    def __init__(self, financial_df: Any, notice_df: Any, research_df: Any) -> None:
        self._fin = financial_df
        self._notice = notice_df
        self._research = research_df

    def stock_financial_abstract(self, symbol: str) -> Any:
        return self._fin

    def stock_zh_a_disclosure_report_cninfo(self, symbol: str) -> Any:
        return self._notice

    def stock_research_report_em(self, symbol: str) -> Any:
        return self._research


class TestAKShareProvider:
    def _provider_with(
        self,
        financial_df: Any = None,
        notice_df: Any = None,
        research_df: Any = None,
    ) -> AKShareProvider:
        provider = AKShareProvider()
        fake = FakeAk(financial_df, notice_df, research_df)
        provider._akshare = MagicMock(return_value=fake)  # type: ignore[method-assign]
        return provider

    def test_get_financials_extracts_kpi_rows(self) -> None:
        provider = self._provider_with(financial_df=_make_financial_df())
        result = provider.get_financials("600519.SS")

        assert result.ticker == "600519"
        assert result.market == "A"
        assert result.currency == "CNY"
        # 三个我们映射过的 KPI
        assert "revenue" in result.metrics
        assert "net_income" in result.metrics
        assert "gross_margin" in result.metrics
        # 默认取 4 个期间
        assert len(result.metrics["revenue"]) == 4
        # 第一个期间是最新（DataFrame 列顺序）
        first = result.metrics["revenue"][0]
        assert first.period == "2024-09-30"
        assert first.value == 100.0
        assert first.unit == "CNY"
        # 比例类指标单位是 %
        assert result.metrics["gross_margin"][0].unit == "%"
        # 至少一条 citation
        assert len(result.citations) >= 1

    def test_get_financials_raises_on_empty(self) -> None:
        provider = self._provider_with(financial_df=pd.DataFrame())
        with pytest.raises(DataSourceError):
            provider.get_financials("600519")

    def test_get_financials_wraps_upstream_exception(self) -> None:
        provider = AKShareProvider()
        fake = MagicMock()
        fake.stock_financial_abstract.side_effect = RuntimeError("network down")
        provider._akshare = MagicMock(return_value=fake)  # type: ignore[method-assign]
        with pytest.raises(DataSourceError) as exc_info:
            provider.get_financials("600519")
        assert "AKShare" in str(exc_info.value)

    def test_get_announcements_returns_items_with_limit(self) -> None:
        provider = self._provider_with(notice_df=_make_notice_df())
        items = provider.get_announcements("600519", limit=1)

        assert len(items) == 1
        assert items[0].title.startswith("2024 年度业绩快报")
        assert items[0].date == "2024-12-30"
        # cninfo 接口无 "公告类型" 列，type 为空字符串
        assert items[0].type == ""
        assert items[0].url.endswith(".pdf")

    def test_get_announcements_empty_df_returns_empty_list(self) -> None:
        provider = self._provider_with(notice_df=pd.DataFrame())
        assert provider.get_announcements("600519") == []

    def test_get_research_reports_returns_metadata_only(self) -> None:
        provider = self._provider_with(research_df=_make_research_df())
        items = provider.get_research_reports("600519")

        assert len(items) == 1
        report = items[0]
        assert report.title == "2024Q4 点评：业绩超预期"
        assert report.institution == "中信证券"
        assert report.rating == "买入"
        # AKShare 1.18 stock_research_report_em 不再返"最新目标价"列；fallback 为 None
        assert report.target_price is None
        assert report.price_currency == "CNY"
        assert report.analyst == "张三"
        assert report.url and report.url.endswith(".pdf")
