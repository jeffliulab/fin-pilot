# FinPilot 系统架构

> 对应 [PRD.md](PRD.md) 的 v0.1 范围。架构遵循
> [agent-rules / stacks/python-backend.md](https://github.com/jeffliulab/agent-rules) 的三层 + [stacks/frontend.md](https://github.com/jeffliulab/agent-rules) 的 Next.js 默认。

---

## 1. 整体形态

```
┌────────────────────────────────────────────────────────────────────┐
│                          浏览器（localhost:3000）                    │
│  ┌──────────┬──────────────────────────────┬──────────────┐        │
│  │ LeftMenu │      WorkspaceCanvas          │  ChatPanel   │        │
│  │          │   ┌──────────────────────┐   │              │        │
│  │ 个股 ✓   │   │ FinancialKPICard     │   │ TickerInput  │        │
│  │ 行业 (灰)│   │ AnnouncementTimeline │   │ ChatStream   │        │
│  │ 市场 (灰)│   │ ResearchReportList   │   │              │        │
│  └──────────┴──────────────────────────────┴──────────────┘        │
│                          │                  │                      │
│                CitationDrawer (右侧抽出)                            │
└─────────────────────┬─────────────────────────┬────────────────────┘
                      │                         │
            REST + SSE (Vercel AI SDK)         │
                      │                         │
┌─────────────────────▼─────────────────────────▼────────────────────┐
│                    后端（FastAPI on localhost:8000）                 │
│  ┌──────────┐ ┌────────────────┐ ┌─────────────────────────┐       │
│  │ routes/  │→│ services/      │→│ repositories/market/    │       │
│  │  stock   │ │  stock         │ │  akshare_provider       │       │
│  │  chat    │ │  chat (LangGraph)│ │  edgar_provider        │       │
│  │  health  │ │  workspace     │ │  yfinance_provider      │       │
│  └──────────┘ └────────────────┘ └─────────────────────────┘       │
│                       │                       │                    │
│                       ▼                       ▼                    │
│                  ┌─────────┐            ┌──────────┐               │
│                  │  llm/   │            │ 外部数据源 │               │
│                  │ Claude  │            │ AKShare  │               │
│                  │ OpenAI  │            │ EDGAR    │               │
│                  └─────────┘            └──────────┘               │
└────────────────────────────────────────────────────────────────────┘
```

---

## 2. 前端架构（per [stacks/frontend.md](https://github.com/jeffliulab/agent-rules)）

### 2.1 目录布局

```
frontend/
├── src/
│   ├── app/                     # 路由 + 布局（Next.js App Router）
│   │   ├── layout.tsx           # ThreePaneLayout 根布局
│   │   ├── page.tsx             # 重定向 → /stock
│   │   ├── stock/page.tsx
│   │   ├── industry/page.tsx    # placeholder
│   │   └── market/page.tsx      # placeholder
│   ├── components/              # 纯展示
│   │   ├── ui/                  # shadcn/ui 组件
│   │   ├── ThreePaneLayout.tsx
│   │   ├── LeftMenu.tsx
│   │   ├── WorkspaceCanvas.tsx
│   │   ├── ChatPanel.tsx
│   │   ├── FinancialKPICard.tsx
│   │   ├── AnnouncementTimelineCard.tsx
│   │   ├── ResearchReportListCard.tsx
│   │   └── CitationDrawer.tsx
│   ├── features/                # 业务组合
│   │   ├── stock/
│   │   │   ├── TickerInput.tsx
│   │   │   ├── CompanyView.tsx
│   │   │   └── ChatStream.tsx
│   │   └── workspace/
│   │       └── WorkspaceList.tsx
│   ├── hooks/                   # use-prefix
│   │   ├── useChat.ts
│   │   ├── useWorkspace.ts
│   │   └── useCitation.ts
│   ├── services/                # API 客户端（组件不直接 fetch）
│   │   ├── apiClient.ts
│   │   ├── stockApi.ts
│   │   ├── chatApi.ts
│   │   └── workspaceApi.ts
│   ├── stores/                  # zustand
│   │   ├── workspaceStore.ts
│   │   ├── chatStore.ts
│   │   └── citationStore.ts
│   ├── types/                   # 与 backend 对齐
│   │   ├── stock.ts
│   │   ├── workspace.ts
│   │   ├── chat.ts
│   │   └── citation.ts
│   └── lib/
│       └── styles/theme.css     # CSS Variables，不硬编码颜色
└── public/
```

### 2.2 关键交互流

1. 用户在 `LeftMenu` 选"个股" → `app/stock/page.tsx` 渲染 `<CompanyView/>`
2. `<TickerInput/>` 提交 → `stockApi.getCompanyOverview(ticker)` → 返回 cards → 写入 `workspaceStore`
3. `<WorkspaceCanvas/>` 订阅 `workspaceStore`，按 `card_type` 渲染对应组件
4. 用户在 `<ChatPanel/>` 输入问题 → **Vercel AI SDK `useChat` hook** 驱动 SSE 流到 `<ChatStream/>`，`[N]` 角标内嵌为可点击 button
5. 点 `[1]` → `useCitation()` 触发 `citationStore.open(citation)` → `<CitationDrawer/>` 抽出 + iframe 加载 URL

---

## 3. 后端架构（per [stacks/python-backend.md](https://github.com/jeffliulab/agent-rules)）

### 3.1 目录布局

```
backend/
├── main.py                      # FastAPI app + lifespan + CORS（白名单 localhost:3000）
├── config.py                    # pydantic-settings，env-driven
├── constants.py                 # 数据源 endpoint、超时、卡片类型枚举
├── interfaces.py                # Protocol + dataclass 跨层契约
├── routes/                      # 表现层：参数校验 / 调用 service / 格式化响应
│   ├── stock.py
│   ├── industry.py              # skeleton (v0.2)
│   ├── market.py                # skeleton (v0.3)
│   ├── chat.py
│   ├── workspace.py
│   └── health.py
├── services/                    # 业务层：核心逻辑，不感知 HTTP
│   ├── stock/
│   │   ├── company_overview.py
│   │   ├── financials.py
│   │   └── follow_up.py
│   ├── chat/
│   │   └── orchestrator.py      # LangGraph 编排
│   └── workspace/
│       └── card_store.py        # in-memory（v0.1）
├── repositories/                # 数据层：CRUD + 外部数据访问
│   ├── market/
│   │   ├── base.py              # MarketDataProvider Protocol
│   │   ├── akshare_provider.py
│   │   ├── edgar_provider.py
│   │   ├── yfinance_provider.py
│   │   └── factory.py
│   └── citations/
│       └── source_resolver.py
├── llm/                         # ← salvaged 五个 provider（drop-in）
├── data/prompts/
│   └── stock/
│       ├── company_overview.j2
│       ├── follow_up.j2
│       └── system_prompt.j2
└── tests/
```

### 3.2 三层职责（agent-rules）

| 层 | 职责 | 禁止 |
|---|---|---|
| `routes/` | Pydantic 参数校验、调用 service、格式化 JSON / SSE 响应 | 写业务逻辑 |
| `services/` | 核心业务逻辑（拼装 cards、orchestrate LLM） | 感知 HTTP / Request / Response |
| `repositories/` | 数据 CRUD、外部 API（AKShare / EDGAR） | 业务判断 |

### 3.3 关键接口契约（`interfaces.py`）

```python
@dataclass
class CompanyCard:
    ticker: str
    market: Literal["A", "US"]
    card_type: Literal["financial_kpi", "announcement_timeline", "research_report"]
    title: str
    payload: dict
    citations: list[Citation]

@dataclass
class Citation:
    label: str          # "[1]"
    source_name: str    # "巨潮·2024 年报"
    url: str            # 用户点角标后跳的真实 URL

class MarketDataProvider(Protocol):
    def get_financials(self, ticker: str) -> FinancialStatements: ...
    def get_announcements(self, ticker: str, limit: int) -> list[Announcement]: ...
    def get_research_reports(self, ticker: str, limit: int) -> list[ResearchReport]: ...
```

### 3.4 LangGraph 编排（v0.1 单 agent，留 v0.2+ 多 agent 路径）

`services/chat/orchestrator.py` 的 graph 结构：

```
[user_message]
      │
      ▼
[load_workspace_context] ──→ 把当前 workspace 的 cards 序列化成 JSON 喂给 LLM
      │
      ▼
[llm_node] ──→ Claude 3.5 Sonnet，prompt 强约束输出含 [N] 角标
      │
      ▼
[parse_citations] ──→ 提取 [N] → 映射到 cards 的 Citation → 注入响应
      │
      ▼
[stream_response]
```

v0.2 加"行业对比 agent"、v0.3 加"市场情绪 agent" 时，只需要在同一 graph 里加节点，不重写 service / route。

---

## 4. 数据流（个股模块端到端）

```
1. 用户输入 600519
       ↓
2. POST /api/v1/stock/600519/overview
       ↓
3. routes/stock.py 调 services/stock/company_overview.get_overview("600519")
       ↓
4. services/stock/company_overview.py 调 repositories/market/factory.get_provider("600519")
       → 返回 AKShareProvider 实例
       ↓
5. provider.get_financials() / get_announcements() / get_research_reports()
       → 三次 AKShare 调用（可并发）
       ↓
6. company_overview 拼装 3 张 CompanyCard（含 Citation 列表）
       ↓
7. routes/stock.py 序列化 JSON 返回前端
       ↓
8. 前端 stockApi.getCompanyOverview() 收到 → 写入 workspaceStore
       ↓
9. WorkspaceCanvas 订阅变化 → 渲染三张卡

──── 用户在 ChatPanel 追问 ────

10. POST /api/v1/chat/stream
        body: { message: "现金流为啥下滑", workspace_snapshot: <cards JSON> }
        ↓
11. routes/chat.py 调 services/chat/orchestrator.run(...)
        ↓
12. LangGraph: load_context → llm_node (Claude SSE) → parse_citations → stream
        ↓
13. SSE chunks 流回前端
        ↓
14. Vercel AI SDK useChat 渲染流，识别 [1] 角标 → button
        ↓
15. 用户点 [1] → citationStore.open(citation) → CitationDrawer iframe 加载 URL
```

---

## 5. 配置与运行（v0.1）

### 5.1 必须的 env（见 `.env.example`）

```
LLM_PROVIDER=anthropic            # anthropic | openai | deepseek | ollama
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...                # 备用
DEEPSEEK_API_KEY=...              # 备用
LOG_LEVEL=INFO
```

### 5.2 启动

```bash
# 后端（一个终端）
conda activate fin-pilot
uvicorn backend.main:app --reload --port 8000

# 前端（另一个终端）
cd frontend && npm run dev        # localhost:3000
```

### 5.3 端到端 smoke

```bash
curl http://localhost:8000/healthz
# → {"status": "ok"}

curl http://localhost:8000/api/v1/stock/600519/overview
# → {"cards": [...]}
```

---

## 6. 不在本架构内的（v0.1 punt）

- 用户认证 / RBAC / 多租户 → v0.4 引入 SQLite 时一起
- 真 RAG 向量库 → v0.5
- 行业 / 市场模块的具体数据 / agent 编排 → v0.2 / v0.3
- 部署架构（Docker / Nginx / PM2） → v0.7

详细推迟原因见 [PRD.md §5](PRD.md)。
