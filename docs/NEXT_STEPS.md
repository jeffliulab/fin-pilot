# 当前任务清单

> 按 [agent-rules / workflows/rapid-versioning.md](https://github.com/jeffliulab/agent-rules) 轻量模式。
> 完成的勾上 `[x]`，新发现的任务即时追加。
> 版本总览 → [`../VERSIONS.md`](../VERSIONS.md)；版本日志 → [`versions/`](versions/)。

## 当前状态

- ✅ **v0.1.0 已封版**（2026-04-24，git tag `v0.1.0`）—— 详见 [`versions/v0.1.0-封版.md`](versions/v0.1.0-封版.md)
- ⏳ **v0.2.0 开发中** —— 行业模块 + Generative Grid；详细计划见 [`versions/v0.2.0-开发中.md`](versions/v0.2.0-开发中.md)
  - 待用户 ack [v0.2.0-开发中.md §11](versions/v0.2.0-开发中.md) 决策 A + B 后启动 Day 1

## v0.2.0 任务清单

### 启动前阻塞

- [ ] 用户 ack 决策 **A**（LLM provider 默认；推荐 OpenAI gpt-4o-mini）
- [ ] 用户 ack 决策 **B**（8 问题模板内容是否调整）

### Day 1 — 行业数据源调研（0.5d）

- [ ] AKShare `stock_board_industry_*` smoke test：列出所有行业 + 任选一个行业列出成员公司
- [ ] 评估稳定性 / 限流；如果不稳，准备静态 fallback 字典（覆盖 20 个常用行业）
- [ ] 决定行业 ID 命名（用东财板块代码还是行业中文名）

### Day 2 — Backend：repositories（1d）

- [ ] `backend/repositories/industry/__init__.py`
- [ ] `backend/repositories/industry/akshare_industry_provider.py`：
  - `list_industries() -> list[Industry]`
  - `list_companies(industry_id) -> list[Company]`
- [ ] 单测：mock akshare，验证两个方法的返回结构

### Day 3 — Backend：单 cell query（1d）

- [ ] `backend/services/industry/__init__.py`
- [ ] `backend/services/industry/industry_query.py`：
  - `query_cell(ticker, question, llm, provider) -> AsyncIterator[CellChunk]`
  - 内部按 question_id 选 prompt + 拉数据 + 走 LLM streaming
- [ ] 8 个 prompt 模板：`backend/data/prompts/industry/Q1.j2` ... `Q8.j2`
- [ ] 单测：mock provider + LLM，验证一个 cell 的 stream 流

### Day 4-5 — Backend：grid orchestrator + route（1.5d）

- [ ] `backend/services/industry/grid_orchestrator.py`：
  - `run_grid(industry_id, tickers[5], questions[8]) -> AsyncIterator[GridEvent]`
  - asyncio.create_task 并发 5×8 = 40 cells
  - asyncio.Semaphore(8) 限流
  - asyncio.as_completed 流式 yield 完成的 cell
- [ ] `backend/routes/industry.py`：
  - `GET /api/v1/industries` → list industries
  - `GET /api/v1/industries/{id}/companies` → list companies
  - `POST /api/v1/industries/grid/stream` → SSE Vercel AI SDK Data Stream，发 cell_start / cell_delta / cell_done / cell_error data parts
- [ ] 协议扩展文档（_schemas.py 或 routes/_dsp.py 加注释）
- [ ] 单测：mock orchestrator，验证协议格式

### Day 6 — Frontend：选择器（1d）

- [ ] `frontend/src/types/industry.ts`
- [ ] `frontend/src/services/industryApi.ts`
- [ ] `frontend/src/features/industry/IndustryPicker.tsx`：下拉行业列表
- [ ] `frontend/src/features/industry/CompanyMultiSelect.tsx`：多选公司（最多 5）
- [ ] `frontend/src/features/industry/QuestionTemplatePicker.tsx`：8 个预设 + 自定义输入

### Day 7 — Frontend：Grid 组件（1.5d）

- [ ] `frontend/src/features/industry/GenerativeGrid.tsx`：CSS Grid 5 行 × 8 列
- [ ] `frontend/src/components/GridCellResult.tsx`：单 cell（spinner / streaming text / done with [N]）
- [ ] `frontend/src/stores/gridStore.ts`：cell_id → cell state（content / status / citations）

### Day 8 — Frontend：Stream hook（1d）

- [ ] `frontend/src/hooks/useGridStream.ts`：解析 cell_* data parts → 分发到 gridStore
- [ ] 接通：用户提交 → POST grid/stream → 流式更新 cell

### Day 9 — Polish（0.5d）

- [ ] Cell 详情抽屉（点 cell 卡片展开）
- [ ] Cell 失败状态（显示错误 + retry 按钮）
- [ ] Citation drawer 复用（点 [N] 已通）
- [ ] 错误处理（部分 cell 失败 graceful，整 grid 不挂）

### Day 10 — Excel 导出 + 归档（0.5d）

- [ ] `pip install openpyxl`
- [ ] `backend/routes/industry.py` 加 `/api/v1/industries/grid/export.xlsx` endpoint
- [ ] 前端"导出 Excel"按钮
- [ ] 端到端 demo 录视频
- [ ] 更新 `frontend/src/components/LeftMenu.tsx`：industry 模块从 disabled 移到 active
- [ ] **归档 v0.2.0**：rename `versions/v0.2.0-开发中.md` → `versions/v0.2.0-封版.md`，更新 VERSIONS.md，打 `git tag v0.2.0`

## 已完成

（v0.2.0 启动后每完成一项从"启动前阻塞 / DayN"勾选移到这里）

## 阻塞

- 等用户 ack v0.2.0-开发中.md §11 决策 A + B
