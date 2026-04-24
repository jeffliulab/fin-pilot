# Salvage Map — 旧仓库 → fin-pilot

记录 2026-04-24 从 5 个已封存的旧 GitHub 仓库中搬运了哪些资产。
原始仓库虽然 archived 仍可只读访问；本地完整克隆位于 `/tmp/fin-pilot-source-repos/`（重启可能消失）。

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

## 参考资产（`salvaged/`，**不在主代码路径上**）

| 子目录 | 来自 | 用途 |
|--------|------|------|
| `ai_financial_advisor/` | AI_Financial_Advisor | 原 README / pyproject / 35 个 pytest 测试 / docs，做为搭模块时的参考与测试种子 |
| `openmanus_tools/` | Financial_Agent_Try（OpenManus fork） | 16 个工具模块（browser、pdf、bash、web_search、deep_research、MCP 等），日后做"研报抓取 + 公告解析"等可借鉴 |
| `openmanus_prompts/` | Financial_Agent_Try | 8 套 prompt 模板（SWE / browser / planning / CoT / MCP / toolcall），做提示词工程时参考 |

## 已转移到 agent-as-a-cfo 的部分

下列内容与"金融"无关，已搬至姐妹项目 `../agent-as-a-cfo/`：

- `wencfo/{brain,backend,tax_service}` —— LangGraph + 报税自动化 + FastAPI auth
- `financial_advisor/{brain,server}` —— 旧记账原型 + budget_planner
- `cfoknows-system/` —— .NET 10 + Azure AD B2C 架构参考
