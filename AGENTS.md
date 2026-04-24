# FinPilot — Agent 规则入口

本项目遵守 [`~/Local_Root/agent-rules/agent-rules/`](../agent-rules/agent-rules/) 的统一规范。

## 项目类型

**fullstack-app** —— 后端 FastAPI + 前端 Next.js。

按 [`paths/fullstack-app.md`](../agent-rules/agent-rules/paths/fullstack-app.md) 阅读顺序：

1. [`GLOBAL.md`](../agent-rules/agent-rules/GLOBAL.md)
2. [`principles/architecture.md`](../agent-rules/agent-rules/principles/architecture.md)
3. [`principles/engineering.md`](../agent-rules/agent-rules/principles/engineering.md)
4. [`stacks/python-backend.md`](../agent-rules/agent-rules/stacks/python-backend.md) — 后端 FastAPI 三层
5. [`stacks/frontend.md`](../agent-rules/agent-rules/stacks/frontend.md) — 前端 Next.js
6. [`workflows/git.md`](../agent-rules/agent-rules/workflows/git.md)
7. [`workflows/quality.md`](../agent-rules/agent-rules/workflows/quality.md)
8. [`workflows/rapid-versioning.md`](../agent-rules/agent-rules/workflows/rapid-versioning.md) — pre-1.0 轻量版本管理
9. [`workflows/github.md`](../agent-rules/agent-rules/workflows/github.md)（公开仓库）

## 项目专属约定

### 范围边界
- 本项目（fin-pilot）只做**金融**（投资 / 投研 / 行情 / 合规）相关
- 财务记账 / 报税 / CFO 工作流 → 姐妹项目 [`agent-as-a-cfo`](https://github.com/jeffliulab/agent-as-a-cfo)
- v0.1 个股模块只覆盖 **A 股 + 美股**，港股留 v0.6+

### 技术栈（已锁定，详见 plan §11）
- 后端：FastAPI + Python 3.11+ + LangGraph + AKShare + SEC EDGAR
- 前端：Next.js 14+ + TypeScript 严格 + Tailwind + shadcn/ui + Zustand + TanStack Query + Vercel AI SDK
- LLM：默认 Claude 3.5 Sonnet，可切 OpenAI / DeepSeek / Ollama
- 数据库：v0.1 不引入（in-memory zustand）

### 版本管理
- 当前版本：见 [`VERSIONS.md`](VERSIONS.md)
- 当前任务：[`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)
- 当前开发日志：[`docs/versions/v0.1.0.md`](docs/versions/v0.1.0.md)
- pre-1.0 轻量模式，每天追加日志，每完成一项打勾

### Git 流程
- Push 前必须问 "PR 还是直推 main？"（v0.1 单人开发倾向直推）
- Conventional Commits：`type(scope): description`
- `src/` → `backend/` 重组等大变动作为独立 commit

### 文档语言
- 文件 / 目录英文优先（`初步探讨思路.txt` 等 legacy 名豁免）
- 文档正文中文（简体）
- 代码 / commit / 标识符英文

## 关键文档索引

| 文档 | 用途 |
|---|---|
| [`docs/PRD.md`](docs/PRD.md) | 产品需求 |
| [`docs/architecture.md`](docs/architecture.md) | 系统架构 |
| [`docs/SALVAGE_MAP.md`](docs/SALVAGE_MAP.md) | 旧仓库代码出处追溯 |
| [`docs/research/competitor-landscape.md`](docs/research/competitor-landscape.md) | 16 个金融 AI 产品 + UX 调研 |
| [`docs/research/data-sources.md`](docs/research/data-sources.md) | A 股 / 美股数据源 + 开源方案 |
| [`docs/初步探讨思路.txt`](docs/初步探讨思路.txt) | legacy 原始构思（参考） |
