"""Tests for backend/repositories/market/factory.py —— 纯逻辑，无 network."""

from __future__ import annotations

import pytest

from backend.repositories.market.akshare_provider import AKShareProvider
from backend.repositories.market.edgar_provider import EdgarProvider
from backend.repositories.market.factory import (
    UnsupportedMarketError,
    detect_v01_market,
    get_provider,
)


class TestDetectV01Market:
    @pytest.mark.parametrize(
        "ticker,expected",
        [
            ("600519", "A"),
            ("600519.SS", "A"),
            ("000858", "A"),
            ("000858.SZ", "A"),
            ("AAPL", "US"),
            ("aapl", "US"),
            ("MSFT", "US"),
        ],
    )
    def test_supported_markets(self, ticker: str, expected: str) -> None:
        assert detect_v01_market(ticker) == expected

    @pytest.mark.parametrize("ticker", ["0700.HK", "BTC-USD", "SAP.DE", "EURUSD=X"])
    def test_unsupported_markets_raise(self, ticker: str) -> None:
        with pytest.raises(UnsupportedMarketError):
            detect_v01_market(ticker)


class TestGetProvider:
    def test_a_share_returns_akshare_provider(self) -> None:
        provider = get_provider("600519")
        assert isinstance(provider, AKShareProvider)
        assert provider.market == "A"

    def test_us_returns_edgar_provider(self) -> None:
        provider = get_provider("AAPL")
        assert isinstance(provider, EdgarProvider)
        assert provider.market == "US"

    def test_unsupported_market_raises(self) -> None:
        with pytest.raises(UnsupportedMarketError):
            get_provider("0700.HK")
