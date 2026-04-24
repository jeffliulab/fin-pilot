# FinPilot · 金融版 Cursor

> 像 Cursor 之于程序员，FinPilot 是面向金融分析师 / 投顾 / 基金经理的三栏 AI 工作台 ——
> 个股研究、行业跟踪、市场情报；workspace 一等公民，引用即抽屉，对齐 Brightwave / AlphaSense / Hebbia
> 在海外验证过的"分析师真正想要的形态"。

> 🇬🇧 English README → [`README.md`](README.md)

## 是什么

全栈 AI copilot（FastAPI + Next.js），三栏 IDE 形态（左菜单 + 中工作区 + 右聊天）。
v0.x roadmap 三个核心模块：

| # | 模块 | v0.1 状态 |
|---|---|---|
| 1 | **个股分析** —— 输入 ticker → 公司主页（财务 / 公告 / 研报评级）+ 自然语言追问 + Citation drawer | ✅ A 股 + 美股（`600519`、`AAPL`） |
| 2 | **行业分析** —— 宏观 / 行业 / 政策 / 重大事件 + Hebbia 式 5×8 网格批量出表 | ⏳ v0.2 |
| 3 | **市场行情** —— 行情 / 资金面 / 情绪 / 异动监控 | ⏳ v0.3 |

## 为什么是三栏

按 [`docs/research/competitor-landscape.md`](docs/research/competitor-landscape.md) 的调研结论：
**workspace + chat**（Brightwave / AlphaSense / Cursor）这套形态在分析师工作流上压倒
**chat-only**（中国主流）—— 交付物沉淀进 workspace，对话驱动但不埋结果，引用作为侧抽屉打开不离开当前页。

## 技术栈

- **后端**：FastAPI + Python 3.11 + LangGraph + AKShare（A 股）+ SEC EDGAR（美股）+ yfinance
- **前端**：Next.js 14 + TypeScript 严格 + Tailwind + shadcn/ui + Zustand + TanStack Query + Vercel AI SDK
- **LLM**：默认 Anthropic Claude 3.5 Sonnet；通过 salvaged provider 抽象支持 OpenAI / DeepSeek / Ollama 切换
- **存储**：v0.1 in-memory（zustand）；v0.4 引入 SQLite

这套栈是 [Brightwave / Perplexity / Cursor / ai-hedge-fund](docs/research/competitor-landscape.md) 的并集 ——
详见 plan §11.1 关于"金融版 Cursor 工业标准"的说明。

## 仓库结构

```
fin-pilot/
├── AGENTS.md / CLAUDE.md         agent 规则入口（→ ~/Local_Root/agent-rules/）
├── VERSIONS.md                   版本总览（rapid-versioning，pre-1.0 模式）
├── README.md / README_zh.md      英文 / 中文
├── pyproject.toml                后端依赖
├── .env.example                  所需环境变量
├── docs/
│   ├── PRD.md                    产品需求
│   ├── architecture.md           系统架构（三栏 + 数据流）
│   ├── NEXT_STEPS.md             当前 v0.1.0 任务清单
│   ├── SALVAGE_MAP.md            旧仓库代码出处追溯
│   ├── research/                 调研报告快照
│   │   ├── competitor-landscape.md  16 个金融 AI 产品 + UX 对比
│   │   └── data-sources.md          A 股 / 美股数据源 + 开源方案
│   └── versions/v0.1.0.md        当前版本开发日志
├── backend/                      FastAPI 三层架构（routes / services / repositories）
└── frontend/                     Next.js（Day 5 创建）
```

## 快速开始

详细步骤见 [`docs/QUICKSTART.md`](docs/QUICKSTART.md)。TL;DR：

```bash
# 后端
conda create -n fin-pilot python=3.11 -y && conda activate fin-pilot
pip install -e ".[dev]"
cp .env.example .env  # 填 ANTHROPIC_API_KEY
uvicorn backend.main:app --reload --port 8000

# 前端（另一个终端）
cd frontend && npm install
cp .env.example .env.local
npm run dev  # http://localhost:3000
```

然后浏览器开 http://localhost:3000 → 点 `600519` 快捷按钮 → 在右侧问 "为什么现金流连续两年下滑？" → 点回答里的 `[1]` 在抽屉看原文。

## 状态

✅ **v0.1.0 就绪**（2026-04-24 归档）。后端 58 个单测通过，前端 build 干净。版本路线图见 [`VERSIONS.md`](VERSIONS.md)，10 天开发日志见 [`docs/versions/v0.1.0.md`](docs/versions/v0.1.0.md)。

v0.1 已实现：
- 三栏壳子（左菜单 / 中工作区 / 右聊天）
- 个股模块 —— A 股（AKShare）+ 美股（SEC EDGAR + yfinance），3 张卡（财务 / 公告 / 研报评级）+ sparkline + 评级分布
- Claude 流式聊天 + `[N]` 内联引用 + 点击抽屉

延期项（详见 [`docs/PRD.md`](docs/PRD.md) §5）：
- 行业模块（v0.2）/ 市场模块（v0.3）
- 工作区持久化 + 多 workspace（v0.4）
- PDF.js 原文高亮（v0.5）
- 港股（v0.6）
- 公开部署（v0.7）

本项目由 `jeffliulab/` 下的 5 个已封存仓库筛选搬运而来（详见 [`docs/SALVAGE_MAP.md`](docs/SALVAGE_MAP.md)）。
财务（记账 / 报税 / CFO）相关内容在姐妹项目 [`agent-as-a-cfo`](https://github.com/jeffliulab/agent-as-a-cfo)。

## License

待定（开源时按 [agent-rules workflows/github.md](https://github.com/jeffliulab/agent-rules) 处理）。
