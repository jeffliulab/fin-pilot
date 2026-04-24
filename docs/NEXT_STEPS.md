# v0.1.0 任务清单

> 按 [agent-rules / workflows/rapid-versioning.md](https://github.com/jeffliulab/agent-rules) 的轻量模式。
> 完成的勾上 `[x]`，新发现的任务即时追加。版本总览见 [`../VERSIONS.md`](../VERSIONS.md)。

## 进行中

### Day 1 — 工程地基（0.5d）

- [x] 设置版本追踪三件套（`VERSIONS.md` + `docs/NEXT_STEPS.md` + `docs/versions/v0.1.0.md`）
- [x] 写 `AGENTS.md` + `CLAUDE.md` shim（指向 agent-rules）
- [x] 搬调研报告 `.claude/plans/*` → `docs/research/`
- [x] 重写 `README.md` 为英文 + 新增 `README_zh.md`
- [x] 重写 `docs/PRD-draft.md` → `docs/PRD.md`（金融版 Cursor 方向）
- [x] 新增 `docs/architecture.md`（三栏 + 数据流）
- [x] `src/fin_pilot/` → `backend/` 搬迁（按 plan §5 目录布局；独立 commit）
- [x] 写 `pyproject.toml` + `.env.example`
- [ ] 创建虚拟环境 `conda create -n fin-pilot python=3.11`（用户本地执行）
- [ ] 跑 `from backend.llm import get_llm` 通

### Day 2 — 后端：数据 provider（1d，2026-04-24 完成）

- [x] `backend/interfaces.py`：`MarketDataProvider` Protocol + 跨层 dataclass（Citation / CompanyCard / FinancialStatements / Announcement / ResearchReport / DataSourceError）—— Protocol 放 interfaces.py 比单独 base.py 更符合 agent-rules"跨层契约集中"原则
- [x] `backend/constants.py`：limits / endpoints / 魔法数字
- [x] `backend/repositories/market/akshare_provider.py`：A 股财务/公告/研报元数据
- [x] `backend/repositories/market/edgar_provider.py`：美股 SEC XBRL（companyfacts + submissions），含 ticker→CIK 缓存 + 150ms rate-limiting
- [x] `backend/repositories/market/factory.py`：`get_provider(ticker)` + `UnsupportedMarketError`（非 A/US 市场拒绝）
- [x] `backend/tests/test_market_factory.py` + `test_akshare_provider.py` + `test_edgar_provider.py`：35 tests，全部 PASS（mock akshare 模块 + mock httpx，无需真网络）
- [-] `yfinance_provider.py`：**Day 2 不做**。salvaged `stock_data.py` 已经能拿价格；v0.1 的 3 张卡（财务 KPI / 公告 / 研报）都不需要 OHLCV 时间序列，所以不必把 yfinance 包进 `MarketDataProvider`。需要价格图表时（v0.2 或 v0.4）再加

### Day 3 — 后端：services + routes（1d）

- [ ] `backend/services/stock/company_overview.py`：拼装 5 张 CompanyCard
- [ ] `backend/routes/stock.py`：`GET /api/v1/stock/{ticker}/overview`
- [ ] `backend/routes/health.py`：`GET /healthz`
- [ ] `backend/main.py`：FastAPI app + CORS（白名单 `localhost:3000`）

### Day 4 — 后端：chat + LLM（1d）

- [ ] `backend/services/chat/orchestrator.py`：LangGraph 单 agent 起步
- [ ] `backend/routes/chat.py`：`POST /api/v1/chat/stream`（SSE）
- [ ] `backend/data/prompts/stock/{system_prompt,company_overview,follow_up}.j2`
- [ ] 端到端 curl smoke test

### Day 5 — 前端：项目初始化 + 三栏壳（1d）

- [ ] `cd frontend && npx create-next-app@14 . --typescript --tailwind --app`
- [ ] 装 `zustand @tanstack/react-query lucide-react ai @ai-sdk/react @ai-sdk/anthropic recharts`
- [ ] `npx shadcn@latest init` + 装 `button card drawer input scroll-area`
- [ ] `src/app/layout.tsx`：三栏 grid
- [ ] `src/components/{ThreePaneLayout,LeftMenu,WorkspaceCanvas,ChatPanel}.tsx`（壳）
- [ ] `npm run dev` 看到三栏空壳

### Day 6 — 前端：个股 module 数据流（1d）

- [ ] `src/services/{apiClient,stockApi}.ts`
- [ ] `src/stores/workspaceStore.ts`（zustand）
- [ ] `src/features/stock/{TickerInput,CompanyView}.tsx`
- [ ] `src/components/{FinancialKPICard,AnnouncementTimelineCard,ResearchReportListCard}.tsx`
- [ ] 跑 `贵州茅台` / `AAPL` 渲染主页

### Day 7 — 前端：ChatPanel + Vercel AI SDK（1d）

- [ ] `src/hooks/useChat.ts`（基于 `@ai-sdk/react` 的 `useChat`）
- [ ] `src/features/stock/ChatStream.tsx`：流式渲染 + `[N]` 角标内嵌
- [ ] 端到端：问"现金流为啥两年下滑？" 看到流 + 角标

### Day 8 — Citation drawer（0.5d）

- [ ] `src/components/CitationDrawer.tsx`
- [ ] `src/stores/citationStore.ts`
- [ ] 角标 onClick → drawer 抽出 + iframe 加载 URL
- [ ] A 股点角标打开巨潮；美股点打开 EDGAR

### Day 9 — 行业 / 市场占位 + 文档（0.5d）

- [ ] `src/app/{industry,market}/page.tsx`：占位卡 "Coming in v0.2 / v0.3"
- [ ] `LeftMenu` 标灰禁用 + tooltip
- [ ] 完善 `docs/architecture.md` 反映实际实现

### Day 10 — 测试 / demo / 归档（0.5d）

- [ ] `pytest backend/tests/ -v` 全绿
- [ ] 录 60 秒 demo 视频 → README
- [ ] 写 `docs/versions/v0.1.0.md` 总结
- [ ] 更新 `VERSIONS.md`：v0.1.0 → 已完成
- [ ] 打 `v0.1.0` git tag + commit `chore: archive v0.1.0 and open v0.2.0`

## 已完成

（v0.1.0 启动时为空，每完成一项从"进行中"勾选移到这里）

## 阻塞

- 无
