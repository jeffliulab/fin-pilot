# Salvage Map — 旧仓库 → fin-pilot

记录 2026-04-24 从 5 个已封存的旧 GitHub 仓库中搬运了哪些资产。
原始仓库均已 archived 但仍可公开只读访问，需要追溯原文件直接去 GitHub 看：

- https://github.com/jeffliulab/AI_Financial_Advisor *(archived)*
- https://github.com/jeffliulab/Financial_Agent_Try *(archived)*
- https://github.com/jeffliulab/wencfo *(archived，财务相关已转 agent-as-a-cfo)*
- https://github.com/jeffliulab/financial_advisor *(archived，财务相关已转 agent-as-a-cfo)*
- https://github.com/jeffliulab/cfoknows-system *(archived，财务相关已转 agent-as-a-cfo)*

## 主代码（`src/fin_pilot/`）

| 模块 | 来自 | 原路径 |
|------|------|--------|
| `llm/` | AI_Financial_Advisor | `src/ai_financial_advisor/llm/`（base / factory / openai / claude / ollama 五个 provider） |
| `analysis/` | AI_Financial_Advisor | `src/ai_financial_advisor/analysis/`（indicators MACD/OBV/MFI、sentiment、anomaly、trend_score、macro） |
| `agents/` | AI_Financial_Advisor | `src/ai_financial_advisor/agents/`（stock_agent / news_agent / analyst_agent + Jinja2 prompts/） |
| `data/` | AI_Financial_Advisor | `src/ai_financial_advisor/data/`（news_fetcher / news_scraper / stock_data / macro_data / market_types + storage/sqlite_store） |
| `config.py`, `__init__.py` | AI_Financial_Advisor | 同上根目录 |

**适配改动**：
- 包名 `ai_financial_advisor` → `fin_pilot`（`__init__.py` 重写；`agents/` 中两处 `PackageLoader` 已改）
- 版本号重置为 `0.0.1`

**显式不搬**（因不符合 4 模块规划）：
- `web/`（Gradio UI，将重新设计）
- `strategies/backtester.py`（量化回测，超出 Copilot 范畴）
- `notifications/`（telegram/alert，与目标用户不匹配）
- `cli.py`（旧 Typer 入口，将基于新模块重写）

## 曾经一度保留、现已删除的参考资产

初始提交（commit `cc36b03`）时一并保留了一份 `salvaged/` 目录做缓冲，2026-04-24 当天清理掉了 ——
理念已抽到主代码 + 本文档，原始拷贝去 archived GitHub repo 即可。删除内容包括：

- 来自 AI_Financial_Advisor 的旧 README / pyproject / 35 个 pytest 测试 / docs
- 来自 Financial_Agent_Try（OpenManus fork）的 16 个工具模块（browser / pdf / web_search / MCP 等）
- 来自 Financial_Agent_Try 的 8 套 prompt 模板（SWE / browser / planning / CoT / MCP / toolcall）

如未来真要做"研报抓取 + 公告解析"，去 `Financial_Agent_Try` 的 `open_manus/app/{tool,prompt}/` 直接看 GitHub 上的源文件。

## 已转移到 agent-as-a-cfo 的部分

下列内容与"金融"无关，已搬至姐妹项目 `../agent-as-a-cfo/`：

- `wencfo/{brain,backend,tax_service}` —— LangGraph + 报税自动化 + FastAPI auth
- `financial_advisor/{brain,server}` —— 旧记账原型 + budget_planner
- `cfoknows-system/` —— .NET 10 + Azure AD B2C 架构参考
