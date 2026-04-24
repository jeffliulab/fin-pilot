"""Tests for EdgarProvider —— 用 monkeypatch 替换内部 HTTP helpers，无需真网络.

verifies：
- ticker → CIK 映射
- companyfacts → FinancialStatements 抽取（XBRL concept 容错 + 期间去重）
- submissions → Announcements 列表过滤（10-K / 10-Q / 8-K）
- get_research_reports 始终返回空列表（EDGAR 无研报）
"""

from __future__ import annotations

import pytest

import backend.repositories.market.edgar_provider as ep_mod
from backend.interfaces import DataSourceError
from backend.repositories.market.edgar_provider import EdgarProvider


@pytest.fixture(autouse=True)
def _reset_cik_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """每个测试都从干净的 cache 开始。"""
    monkeypatch.setattr(ep_mod, "_ticker_cik_cache", None)


def _patch_ticker_cik_map(monkeypatch: pytest.MonkeyPatch, mapping: dict[str, str]) -> None:
    """注入预期的 ticker→CIK map，不发真请求。"""
    monkeypatch.setattr(ep_mod, "_ticker_cik_cache", mapping)


class TestTickerToCik:
    def test_known_ticker_returns_cik(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        assert provider._ticker_to_cik("AAPL") == "0000320193"
        assert provider._ticker_to_cik("aapl") == "0000320193"

    def test_unknown_ticker_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        with pytest.raises(DataSourceError):
            provider._ticker_to_cik("NOPE")


def _facts_with_revenue_and_income() -> dict:
    return {
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [
                            {"end": "2024-09-30", "val": 100, "form": "10-Q"},
                            {"end": "2024-06-30", "val": 90, "form": "10-Q"},
                            {"end": "2024-03-31", "val": 80, "form": "10-Q"},
                            {"end": "2023-12-31", "val": 310, "form": "10-K"},
                        ]
                    }
                },
                "NetIncomeLoss": {
                    "units": {
                        "USD": [
                            {"end": "2024-09-30", "val": 30, "form": "10-Q"},
                            {"end": "2024-06-30", "val": 25, "form": "10-Q"},
                            {"end": "2024-03-31", "val": 22, "form": "10-Q"},
                            {"end": "2023-12-31", "val": 95, "form": "10-K"},
                        ]
                    }
                },
                "StockholdersEquity": {
                    "units": {
                        "USD": [
                            {"end": "2024-09-30", "val": 600, "form": "10-Q"},
                            {"end": "2024-06-30", "val": 575, "form": "10-Q"},
                            {"end": "2024-03-31", "val": 550, "form": "10-Q"},
                            {"end": "2023-12-31", "val": 540, "form": "10-K"},
                        ]
                    }
                },
            }
        }
    }


class TestGetFinancials:
    def test_extracts_revenue_income_and_computes_roe(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        monkeypatch.setattr(provider, "_get_companyfacts", lambda cik: _facts_with_revenue_and_income())

        result = provider.get_financials("AAPL")

        assert result.ticker == "AAPL"
        assert result.market == "US"
        assert result.currency == "USD"
        # revenue / net_income / roe 都填齐
        assert "revenue" in result.metrics
        assert "net_income" in result.metrics
        assert "roe" in result.metrics
        assert len(result.metrics["revenue"]) == 4
        # 最新期在前
        assert result.metrics["revenue"][0].period == "2024-09-30"
        assert result.metrics["revenue"][0].value == 100.0
        # ROE = net_income / equity * 100
        roe_latest = result.metrics["roe"][0]
        assert roe_latest.period == "2024-09-30"
        assert roe_latest.value == pytest.approx(30 / 600 * 100, rel=1e-3)
        assert roe_latest.unit == "%"
        # citation 存在
        assert len(result.citations) >= 1

    def test_handles_missing_concept_gracefully(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        # 只给 NetIncomeLoss，不给 Revenues
        facts = {
            "facts": {
                "us-gaap": {
                    "NetIncomeLoss": {
                        "units": {"USD": [{"end": "2024-09-30", "val": 30, "form": "10-Q"}]}
                    }
                }
            }
        }
        monkeypatch.setattr(provider, "_get_companyfacts", lambda cik: facts)

        result = provider.get_financials("AAPL")
        # revenue 缺失也不抛
        assert result.metrics["revenue"] == []
        assert result.metrics["net_income"][0].value == 30.0


class TestGetAnnouncements:
    def test_filters_to_known_forms_and_builds_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        submissions = {
            "filings": {
                "recent": {
                    "form": ["10-K", "DEF 14A", "S-3", "10-Q", "8-K"],
                    "filingDate": ["2024-11-01", "2024-09-15", "2024-08-01", "2024-08-05", "2024-07-30"],
                    "accessionNumber": ["0000320193-24-000001", "0000320193-24-000002", "0000320193-24-000003", "0000320193-24-000004", "0000320193-24-000005"],
                    "primaryDocument": ["aapl-20241101.htm", "def14a.htm", "s3.htm", "aapl-q3.htm", "8k.htm"],
                }
            }
        }
        monkeypatch.setattr(provider, "_get_submissions", lambda cik: submissions)

        items = provider.get_announcements("AAPL", limit=10)

        # S-3 不在 EDGAR_FORMS_FOR_ANNOUNCEMENTS 中，应被过滤掉
        types = [a.type for a in items]
        assert "S-3" not in types
        assert "10-K" in types
        assert "DEF 14A" in types
        assert "10-Q" in types
        assert "8-K" in types
        # URL 拼接正确
        for item in items:
            if item.type == "10-K":
                assert "0000320193" in item.url
                assert "000032019324000001" in item.url
                assert item.url.endswith("aapl-20241101.htm")

    def test_respects_limit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        submissions = {
            "filings": {
                "recent": {
                    "form": ["10-Q"] * 30,
                    "filingDate": [f"2024-{m:02d}-01" for m in range(1, 31)],
                    "accessionNumber": [f"0000320193-24-{i:06d}" for i in range(30)],
                    "primaryDocument": [f"q{i}.htm" for i in range(30)],
                }
            }
        }
        monkeypatch.setattr(provider, "_get_submissions", lambda cik: submissions)

        items = provider.get_announcements("AAPL", limit=5)
        assert len(items) == 5


class TestResearchReports:
    def test_always_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        _patch_ticker_cik_map(monkeypatch, {"AAPL": "0000320193"})
        provider = EdgarProvider()
        assert provider.get_research_reports("AAPL") == []
