"""Stock endpoints —— /api/v1/stock/*.

按 stacks/python-backend.md 的 routes 层职责：
- 参数校验（FastAPI Path / Query 自动）
- 调 service
- 把 dataclass → Pydantic response，格式化 JSON

业务逻辑禁止堆这里。
"""

from __future__ import annotations

import logging
from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Path

from backend.interfaces import CompanyCard, DataSourceError
from backend.repositories.market.factory import UnsupportedMarketError
from backend.services.stock.company_overview import get_company_overview

from ._schemas import CitationOut, CompanyCardOut, CompanyOverviewResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/stock", tags=["stock"])


def _to_card_out(card: CompanyCard) -> CompanyCardOut:
    """Dataclass CompanyCard → Pydantic CompanyCardOut。"""
    return CompanyCardOut(
        ticker=card.ticker,
        market=card.market,
        card_type=card.card_type,
        title=card.title,
        payload=card.payload,
        citations=[CitationOut(**asdict(c)) for c in card.citations],
    )


@router.get(
    "/{ticker}/overview",
    response_model=CompanyOverviewResponse,
    summary="Company main page (financial KPI + announcements + research reports)",
)
def get_overview(
    ticker: str = Path(
        ...,
        description="股票代码：A 股 6 位（如 600519、000858）或美股 alpha（如 AAPL）",
        min_length=1,
        max_length=20,
    ),
) -> CompanyOverviewResponse:
    """返回公司主页 3 张工作区卡片。

    错误处理：
    - 422 ticker 不属于 v0.1 支持市场（A 股 / 美股）
    - 502 上游数据源失败（AKShare / EDGAR 限流 / 改版）
    - 500 其他未预期错误（不暴露内部堆栈）
    """
    try:
        cards = get_company_overview(ticker)
    except UnsupportedMarketError as exc:
        logger.warning("Unsupported market for ticker=%s: %s", ticker, exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DataSourceError as exc:
        logger.error("DataSource error for ticker=%s: %s", ticker, exc)
        raise HTTPException(status_code=502, detail=f"上游数据源失败：{exc}") from exc

    if not cards:
        raise HTTPException(status_code=404, detail=f"ticker {ticker!r} 未返回任何卡片")

    return CompanyOverviewResponse(
        ticker=cards[0].ticker,
        market=cards[0].market,
        cards=[_to_card_out(c) for c in cards],
    )
