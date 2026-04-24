# FinPilot · 金融从业者的 AI Copilot

> 像 GitHub Copilot 之于程序员，FinPilot 之于金融从业者 ——
> 让每一位分析师、客户经理、合规专员都有一个懂金融、守合规、能整理的 AI 搭档。

**定位**：面向**金融行业（投研 / 投顾 / 合规 / 资管）**的 Agent Copilot。
**不做**：财务记账、报税、CFO 工作流 —— 这些在姐妹项目 [`../agent-as-a-cfo/`](../agent-as-a-cfo/) 里。

## 计划模块（节选自 [docs/初步探讨思路.txt](docs/初步探讨思路.txt)）

| # | 模块 | 目标用户 | 优先级 |
|---|------|---------|--------|
| 1 | 个股 / 行业深度分析（RAG + Function Calling + 多轮追问） | 投研分析师 | **必做** |
| 2 | 销售话术 / 营销物料合规审查（多 Agent 共识） | 客户经理、合规专员 | **必做** |
| 3 | 投研晨报生成（多源汇总 + 个性化订阅） | 投研助理 | 选做 |
| 4 | 客户画像与配置建议（结构化抽取 + 规则引擎） | 银行理财经理 | 选做 |

详见 [docs/PRD-draft.md](docs/PRD-draft.md)。

## 仓库结构

```
fin-pilot/
├── docs/                       规划文档（PRD、思路、salvage map）
└── src/fin_pilot/              主代码包
    ├── llm/                    多 provider LLM 抽象（OpenAI/Claude/Ollama）
    ├── analysis/               技术指标、情绪、异动、宏观
    ├── agents/                 stock/news/analyst agents + Jinja2 prompts
    └── data/                   行情、新闻、宏观数据接入
```

旧仓库的原始拷贝不在树内 —— 如需追溯原文件，去对应的 archived GitHub repo（详见 [docs/SALVAGE_MAP.md](docs/SALVAGE_MAP.md)）。

## 来源

本项目从以下 5 个**已封存（archived）**仓库中筛选搬运而来，详见 [docs/SALVAGE_MAP.md](docs/SALVAGE_MAP.md)：

- `jeffliulab/AI_Financial_Advisor` ← 主要源（LLM/indicators/agents）
- `jeffliulab/Financial_Agent_Try` ← OpenManus 工具库（参考）
- `jeffliulab/wencfo` ← 财务相关 → 已转移至 `../agent-as-a-cfo/`
- `jeffliulab/financial_advisor` ← 财务相关 → 已转移至 `../agent-as-a-cfo/`
- `jeffliulab/cfoknows-system` ← 财务 .NET 架构 → 已转移至 `../agent-as-a-cfo/`

## 状态

🚧 早期脚手架阶段。代码继承自旧仓库，**尚未做适配验证**。下一步：
1. 选定模块 1 和模块 2 的最小可演示路径；
2. 把 `src/fin_pilot/llm/` 里的 provider 抽象打通到模块 1；
3. 写 PRD 终稿（见 `docs/PRD-draft.md`）。
