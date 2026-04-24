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

## 状态

🚧 **v0.1.0 开发中**（2026-04-24 启动）。版本路线图见 [`VERSIONS.md`](VERSIONS.md)，当前任务见 [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)。

本项目由 `jeffliulab/` 下的 5 个已封存仓库筛选搬运而来（详见 [`docs/SALVAGE_MAP.md`](docs/SALVAGE_MAP.md)）。
财务（记账 / 报税 / CFO）相关内容在姐妹项目 [`agent-as-a-cfo`](https://github.com/jeffliulab/agent-as-a-cfo)。

## License

待定（开源时按 [agent-rules workflows/github.md](https://github.com/jeffliulab/agent-rules) 处理）。
