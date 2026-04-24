"""Tests for backend/services/chat/orchestrator.py.

Splits coverage：
- _prepare_node：纯 prompt 渲染，无 mock
- ChatOrchestrator.stream：mock Anthropic AsyncAnthropic（streaming context manager + text_stream）
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.config import LLMProviderType
from backend.interfaces import Citation
from backend.services.chat.orchestrator import (
    ChatChunk,
    ChatOrchestrator,
    ChatRequest,
    _prepare_node,
)


class TestPrepareNode:
    def test_renders_system_and_user_prompts(self) -> None:
        state = {
            "user_message": "现金流为何下滑",
            "cards": [
                {
                    "title": "财务 KPI",
                    "card_type": "financial_kpi",
                    "payload": {
                        "currency": "CNY",
                        "summary": [
                            {
                                "name": "revenue",
                                "display_name": "营业总收入",
                                "latest_value": 100.0,
                                "latest_period": "2024-09-30",
                                "unit": "CNY",
                                "trend": [310.0, 80.0, 90.0, 100.0],
                                "trend_periods": ["2023-12", "2024-03", "2024-06", "2024-09"],
                            }
                        ],
                    },
                },
            ],
            "citations": [
                {"label": "[1]", "source_name": "AKShare 600519", "url": "http://ex/1"}
            ],
        }
        result = _prepare_node(state)
        assert "rendered_system" in result
        assert "rendered_prompt" in result
        # system prompt 关键词
        assert "FinPilot" in result["rendered_system"]
        assert "[N]" in result["rendered_system"]
        # follow_up 包含工作区 + 引用 + 用户问题
        prompt = result["rendered_prompt"]
        assert "现金流为何下滑" in prompt
        assert "营业总收入" in prompt
        assert "[1]" in prompt
        assert "AKShare 600519" in prompt

    def test_handles_empty_cards_and_citations(self) -> None:
        state = {"user_message": "你好", "cards": [], "citations": []}
        result = _prepare_node(state)
        assert "你好" in result["rendered_prompt"]


# === ChatOrchestrator streaming ===
class _FakeAnthropicStream:
    """Mocks ``async with client.messages.stream(...) as stream`` 的最小行为."""

    def __init__(self, chunks: list[str], finish_reason: str = "stop") -> None:
        self._chunks = chunks
        self._finish_reason = finish_reason

    async def __aenter__(self) -> "_FakeAnthropicStream":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    @property
    def text_stream(self) -> AsyncIterator[str]:
        async def gen() -> AsyncIterator[str]:
            for c in self._chunks:
                yield c

        return gen()

    async def get_final_message(self) -> Any:
        msg = MagicMock()
        msg.stop_reason = self._finish_reason
        return msg


class _FakeAsyncAnthropic:
    """Drop-in for anthropic.AsyncAnthropic with a controllable stream."""

    def __init__(self, chunks: list[str], finish_reason: str = "stop") -> None:
        self._chunks = chunks
        self._finish_reason = finish_reason
        self.messages = MagicMock()
        # `messages.stream(...)` 必须返回 _FakeAnthropicStream（NOT awaited，是 sync 工厂）
        self.messages.stream = MagicMock(
            return_value=_FakeAnthropicStream(self._chunks, self._finish_reason)
        )


@pytest.fixture
def orchestrator_with_chunks() -> Any:
    def _factory(chunks: list[str], finish_reason: str = "stop") -> ChatOrchestrator:
        # 跳过 Settings 校验：直接造对象再注入
        orch = ChatOrchestrator.__new__(ChatOrchestrator)
        orch._settings = MagicMock()
        orch._settings.temperature = 0.5
        orch._provider = LLMProviderType.ANTHROPIC
        orch._client = _FakeAsyncAnthropic(chunks, finish_reason)
        orch._model = "claude-test"
        return orch

    return _factory


class TestStream:
    @pytest.mark.asyncio
    async def test_emits_delta_chunks_then_finish(
        self, orchestrator_with_chunks
    ) -> None:
        orch = orchestrator_with_chunks(["Hello, ", "world", "!"])
        request = ChatRequest(
            message="hi",
            cards=[],
            citations=[Citation(label="[1]", source_name="src", url="http://x")],
        )
        chunks: list[ChatChunk] = []
        async for chunk in orch.stream(request):
            chunks.append(chunk)

        # 3 个 delta + 1 个 finish
        assert len(chunks) == 4
        assert [c.type for c in chunks] == ["delta", "delta", "delta", "finish"]
        assert "".join(c.content for c in chunks if c.type == "delta") == "Hello, world!"
        # finish chunk 携带 citations
        finish = chunks[-1]
        assert finish.finish_reason == "stop"
        assert finish.citations is not None
        assert finish.citations[0].label == "[1]"

    @pytest.mark.asyncio
    async def test_no_chunks_still_yields_finish(self, orchestrator_with_chunks) -> None:
        orch = orchestrator_with_chunks([], finish_reason="end_turn")
        request = ChatRequest(message="hi", cards=[], citations=[])
        chunks = [c async for c in orch.stream(request)]
        assert len(chunks) == 1
        assert chunks[0].type == "finish"
        assert chunks[0].finish_reason == "end_turn"
