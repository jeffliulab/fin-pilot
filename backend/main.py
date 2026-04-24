"""FastAPI application entry —— uvicorn backend.main:app --reload --port 8000.

按 stacks/python-backend.md：
- routes/ 注册到 main 这里；不在 main 写业务
- CORS 显式白名单（不通配 *），来源于 config.api.cors_origins
- 启动 / 关闭挂在 lifespan，不用过时的 on_event 钩子
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import __version__
from backend.config import get_settings
from backend.routes import health, stock

logger = logging.getLogger(__name__)


def _setup_logging(level: str) -> None:
    """Configure root logger; agent-rules 禁止用 print() 当日志."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup + shutdown hooks。"""
    settings = get_settings()
    _setup_logging(settings.log_level)
    logger.info("FinPilot backend v%s 启动 (LLM=%s)", __version__, settings.llm.provider.value)
    yield
    logger.info("FinPilot backend v%s 关闭", __version__)


def create_app() -> FastAPI:
    """Application factory —— 测试可以用不同 settings 创建独立 app。"""
    settings = get_settings()
    app = FastAPI(
        title="FinPilot",
        version=__version__,
        description="金融版 Cursor —— 三栏 AI 工作台（个股 / 行业 / 市场）",
        lifespan=lifespan,
    )

    # CORS：白名单来自 .env 的 CORS_ORIGINS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # 注册 routes
    app.include_router(health.router)
    app.include_router(stock.router)
    # v0.2 加 industry router；v0.3 加 market router；Day 4 加 chat router

    return app


app = create_app()
