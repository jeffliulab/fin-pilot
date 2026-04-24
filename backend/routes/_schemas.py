"""Pydantic response schemas —— routes 层独有（service/repository 用 dataclass）.

按 stacks/python-backend.md：request / response schema 使用 Pydantic。

设计：interfaces.py 的 dataclass 是**内部契约**（service ↔ repository 之间），
本文件的 Pydantic 模型是**外部契约**（route ↔ frontend 之间）。
两者形状一致，转换在 routes/*.py 内做。
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CitationOut(BaseModel):
    label: str
    source_name: str
    url: str


class CompanyCardOut(BaseModel):
    ticker: str
    market: Literal["A", "US"]
    card_type: Literal["financial_kpi", "announcement_timeline", "research_report"]
    title: str
    payload: dict
    citations: list[CitationOut] = Field(default_factory=list)


class CompanyOverviewResponse(BaseModel):
    """``GET /api/v1/stock/{ticker}/overview`` 的响应体。"""

    ticker: str
    market: Literal["A", "US"]
    cards: list[CompanyCardOut]


class HealthResponse(BaseModel):
    """``GET /healthz`` 的响应体。"""

    status: Literal["ok", "degraded"]
    version: str
