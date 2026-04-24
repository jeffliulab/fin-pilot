"""Market provider factory —— ticker 字符串 → 对应市场的 ``MarketDataProvider`` 实现.

按 agent-rules/principles/architecture.md 的"注册表 / 工厂模式"：新增市场 = 加一行
注册，不改分发逻辑。

v0.1 只支持 A 股 + 美股；其他市场（HK/EU/JP/CRYPTO/FOREX/COMMODITY）抛
``UnsupportedMarketError``，等 v0.6+ 的港股扩展。
"""

from __future__ import annotations

import logging

from backend.interfaces import Market, MarketDataProvider

from .akshare_provider import AKShareProvider
from .edgar_provider import EdgarProvider
from .market_types import MarketType, detect_market_type

logger = logging.getLogger(__name__)


# 注册表：salvaged MarketType enum → v0.1 contract Market literal + provider 工厂
_PROVIDER_REGISTRY: dict[MarketType, tuple[Market, type[MarketDataProvider]]] = {
    MarketType.CN: ("A", AKShareProvider),
    MarketType.US: ("US", EdgarProvider),
}


class UnsupportedMarketError(ValueError):
    """Raised when a ticker maps to a market 不在 v0.1 支持范围内."""


def detect_v01_market(ticker: str) -> Market:
    """Wrapper：用 salvaged ``detect_market_type`` 判定，再转成 v0.1 ``Market`` 字面量.

    A 股 ticker 接受两种格式：
      - 带后缀："600519.SS" / "000858.SZ"
      - 裸 6 位："600519" / "000858"（按前缀判 SS / SZ）
    """
    market_enum = detect_market_type(ticker)

    # 容错：用户输入裸 6 位 A 股 code（market_types.py 默认按 alpha 判，会归 UNKNOWN）
    code = ticker.strip().upper()
    if market_enum == MarketType.UNKNOWN and code.isdigit() and len(code) == 6:
        market_enum = MarketType.CN

    mapping = _PROVIDER_REGISTRY.get(market_enum)
    if mapping is None:
        raise UnsupportedMarketError(
            f"Ticker '{ticker}' detected as market={market_enum.value}; "
            f"v0.1 supports only A-shares and US. 见 plan §11 / PRD §3。"
        )
    return mapping[0]


def get_provider(ticker: str) -> MarketDataProvider:
    """Return a ``MarketDataProvider`` instance for the ticker's market.

    Raises:
        UnsupportedMarketError: ticker 不属于 A 股或美股
    """
    market_enum = detect_market_type(ticker)

    code = ticker.strip().upper()
    if market_enum == MarketType.UNKNOWN and code.isdigit() and len(code) == 6:
        market_enum = MarketType.CN

    mapping = _PROVIDER_REGISTRY.get(market_enum)
    if mapping is None:
        raise UnsupportedMarketError(
            f"Ticker '{ticker}' detected as market={market_enum.value}; "
            f"v0.1 supports only A-shares and US."
        )

    _market_literal, provider_cls = mapping
    logger.debug("Selected provider %s for ticker=%s", provider_cls.__name__, ticker)
    return provider_cls()
