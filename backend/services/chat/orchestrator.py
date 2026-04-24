"""Chat orchestrator —— LangGraph state 编排 + Anthropic SDK 直接做 streaming.

按 plan §5.2 / docs/architecture.md §3.4 的设计：

- v0.1：单 agent（"个股分析助手"），LangGraph 在这里只起 state 管理 + prompt 渲染
  的脚手架作用；streaming 走 Anthropic SDK 直连，不过 graph
- v0.2+：在同一 graph 里加 "行业对比 agent" / "市场情绪 agent" 节点，自动多 agent
  共识；那时把 streaming 也搬进 LangGraph（用 langchain-anthropic 的 astream_events）

为什么 v0.1 不一上来就把 streaming 放进 graph：
- LangGraph 的原生 streaming 需要绑 langchain-anthropic 的 ChatAnthropic 类，
  跟我们 salvaged 的 LLMProvider 抽象错位
- 一个 LLM 调用没必要走完整 graph 状态机；先把"准备 prompt → 流"这条流水线
  跑稳，v0.2 再扩
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

import anthropic
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.graph import END, StateGraph

from backend.config import LLMSettings, get_settings
from backend.interfaces import Citation

logger = logging.getLogger(__name__)


# === Request / Chunk 类型 ===
@dataclass
class ChatRequest:
    """用户的一条 chat 请求 + 当前工作区快照."""

    message: str
    cards: list[dict]
    citations: list[Citation]


@dataclass
class ChatChunk:
    """流式输出的一个 chunk —— routes 层转成 SSE 协议."""

    type: str  # "delta" | "finish" | "error"
    content: str = ""  # delta 时是文本片段
    citations: list[Citation] | None = None  # finish 时附带
    finish_reason: str | None = None  # finish 时 e.g. "stop" / "max_tokens"


# === LangGraph 状态 ===
class ChatState(TypedDict, total=False):
    user_message: str
    cards: list[dict]
    citations: list[dict]  # serialized for prompt
    rendered_system: str
    rendered_prompt: str


# === Prompt 渲染（LangGraph 节点） ===
_PROMPT_DIR = Path(__file__).parents[2] / "data" / "prompts" / "stock"
_prompt_env = Environment(
    loader=FileSystemLoader(_PROMPT_DIR),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True,
)


def _prepare_node(state: ChatState) -> dict:
    """LangGraph node: render Jinja2 prompts from state.

    把 cards + citations + user_message 喂进模板，返回 system + user prompt。
    """
    system = _prompt_env.get_template("system_prompt.j2").render()
    follow_up = _prompt_env.get_template("follow_up.j2").render(
        cards=state["cards"],
        citations=state["citations"],
        user_message=state["user_message"],
    )
    return {"rendered_system": system, "rendered_prompt": follow_up}


def _build_chat_graph():
    """单节点 graph —— v0.2 加 industry / market agents 时在这里 add_node。"""
    graph = StateGraph(ChatState)
    graph.add_node("prepare", _prepare_node)
    graph.set_entry_point("prepare")
    graph.add_edge("prepare", END)
    return graph.compile()


# 模块级 singleton，避免每次请求都重建
_chat_graph = _build_chat_graph()


# === Orchestrator ===
class ChatOrchestrator:
    """协调 prompt prep + LLM streaming + finish event 三段。

    ``stream(request)`` 返回 async iterator，routes 层逐个 chunk emit 给前端。
    """

    def __init__(self, settings: LLMSettings | None = None) -> None:
        if settings is None:
            settings = get_settings().llm
        self._settings = settings
        # v0.1 默认 Claude；其他 provider 走 v0.2 切换（routes 现只暴露 anthropic
        # 路径，避免 streaming 各 provider 接口差异污染 v0.1）
        if not settings.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY 未设置；v0.1 streaming 默认 Claude")
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = "claude-3-5-sonnet-latest"

    async def stream(self, request: ChatRequest) -> AsyncIterator[ChatChunk]:
        """Yield ChatChunk per Claude SSE event + final finish chunk.

        Stages：
            1. LangGraph prepare 节点渲染 prompts（同步，~ms）
            2. Anthropic AsyncAnthropic 流式 chat completion（每个 token 一个 delta）
            3. finish chunk 携带 citations 列表（前端用来渲染右侧抽屉）
        """
        # 1. Prepare via graph
        prepared = await _chat_graph.ainvoke(
            {
                "user_message": request.message,
                "cards": request.cards,
                "citations": [
                    {"label": c.label, "source_name": c.source_name, "url": c.url}
                    for c in request.citations
                ],
            }
        )

        logger.debug(
            "chat orchestrator: model=%s, prompt_chars=%d, citations=%d",
            self._model,
            len(prepared["rendered_prompt"]),
            len(request.citations),
        )

        # 2. Stream from Claude
        finish_reason: str | None = None
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=2048,
                temperature=self._settings.temperature,
                system=prepared["rendered_system"],
                messages=[{"role": "user", "content": prepared["rendered_prompt"]}],
            ) as stream:
                async for text in stream.text_stream:
                    yield ChatChunk(type="delta", content=text)
                # 取 finish reason
                final = await stream.get_final_message()
                finish_reason = final.stop_reason or "stop"
        except anthropic.APIError as exc:
            logger.error("Anthropic API error: %s", exc)
            yield ChatChunk(type="error", content=f"Anthropic API error: {exc}")
            return

        # 3. Finish
        yield ChatChunk(
            type="finish",
            citations=request.citations,
            finish_reason=finish_reason or "stop",
        )
