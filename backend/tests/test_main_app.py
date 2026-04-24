"""Tests for backend/main.py + routes (FastAPI TestClient smoke test).

Mocks ``backend.routes.stock.get_company_overview`` —— 不真调 provider。
"""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient

import backend.routes.stock as stock_route
from backend import __version__
from backend.config import get_settings
from backend.interfaces import CompanyCard, DataSourceError
from backend.main import create_app
from backend.repositories.market.factory import UnsupportedMarketError


@pytest.fixture
def client() -> TestClient:
    get_settings.cache_clear()  # 防止前测污染 lru_cache
    return TestClient(create_app())


# === /healthz ===
class TestHealthz:
    def test_returns_ok_with_version(self, client: TestClient) -> None:
        resp = client.get("/healthz")
        assert resp.status_code == 200
        body = resp.json()
        assert body == {"status": "ok", "version": __version__}


# === /api/v1/stock/{ticker}/overview ===
def _fake_cards() -> list[CompanyCard]:
    return [
        CompanyCard(
            ticker="600519",
            market="A",
            card_type="financial_kpi",
            title="财务 KPI",
            payload={"summary": [], "currency": "CNY"},
            citations=[],
        ),
        CompanyCard(
            ticker="600519",
            market="A",
            card_type="announcement_timeline",
            title="公告",
            payload={"items": []},
            citations=[],
        ),
        CompanyCard(
            ticker="600519",
            market="A",
            card_type="research_report",
            title="研报",
            payload={"items": [], "consensus_target": None, "rating_distribution": {}, "report_count": 0, "consensus_target_basis": 0},
            citations=[],
        ),
    ]


class TestStockOverviewEndpoint:
    def test_happy_path_returns_cards(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(stock_route, "get_company_overview", lambda ticker: _fake_cards())

        resp = client.get("/api/v1/stock/600519/overview")
        assert resp.status_code == 200
        body = resp.json()
        assert body["ticker"] == "600519"
        assert body["market"] == "A"
        assert len(body["cards"]) == 3
        assert [c["card_type"] for c in body["cards"]] == [
            "financial_kpi",
            "announcement_timeline",
            "research_report",
        ]

    def test_unsupported_market_returns_422(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def boom(ticker: str) -> Any:
            raise UnsupportedMarketError("HK is v0.6")

        monkeypatch.setattr(stock_route, "get_company_overview", boom)
        resp = client.get("/api/v1/stock/0700.HK/overview")
        assert resp.status_code == 422
        assert "HK" in resp.json()["detail"]

    def test_data_source_failure_returns_502(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def boom(ticker: str) -> Any:
            raise DataSourceError("AKShare", "上游限流")

        monkeypatch.setattr(stock_route, "get_company_overview", boom)
        resp = client.get("/api/v1/stock/600519/overview")
        assert resp.status_code == 502
        assert "上游" in resp.json()["detail"]

    def test_empty_cards_returns_404(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(stock_route, "get_company_overview", lambda ticker: [])
        resp = client.get("/api/v1/stock/600519/overview")
        assert resp.status_code == 404


# === OpenAPI doc shape ===
class TestOpenAPI:
    def test_openapi_includes_stock_route(self, client: TestClient) -> None:
        resp = client.get("/openapi.json")
        assert resp.status_code == 200
        paths = resp.json()["paths"]
        assert "/api/v1/stock/{ticker}/overview" in paths
        assert "/healthz" in paths
