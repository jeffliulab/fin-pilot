---
title: 个股分析模块 v0 数据源 + 开源方案调研
research_date: 2026-04-24
researcher: general-purpose subagent (web research)
prompt_summary: 为"个股分析"模块调研 A 股 + 港股 + 美股的财务/公告/研报/IPO 数据源（免费/开源优先），盘点至少 5 个开源"个股分析 Agent"项目，给 v0.1 数据栈推荐 + A 股 vs 美股工程量对比
informs: docs/PRD.md §3.1（数据源选定）, plan §4.3, backend/repositories/market/
status: 调研快照（2026-04），不再随产品迭代而更新
---

# FinPilot 个股分析模块 v0 数据源 + 开源方案调研

> 截至 2026-04，研究阶段产出，未执行任何变更。下方所有结论可直接进入 v0 PRD。

---

## 1. 数据源对比表

### 1.1 财务数据（季报/年报标准化指标）

| 数据源 | 市场 | 免费？ | 速率 / 限制 | 覆盖深度 | 成熟度 | v0 评价 |
|---|---|---|---|---|---|---|
| **AKShare** (`akfamily/akshare`, ~18.5k★) | A / 港 / 美 / 期 / 基 / 加密 | 完全免费、无需注册 | 上游限频（东财/新浪），无显式额度 | A股三表+常见因子全；港美靠新浪/雪球，深度一般 | 高，文档活跃 | **首选** A股财务 + 港股辅助 |
| **Tushare Pro** (`waditu/tushare`) | A / 港 / 美 | Freemium，按"积分"分级 | 财务数据需 ≥2000 积分；港股财务需 15000 积分或单独购权；接口限频 200/min、10w/天 | A股结构化质量最高，复权/财务标准化好 | 高，机构级 | A股财务交叉验证；港美**v0 别上** |
| **Baostock** | A 股 | 完全免费、无需注册 | 限制少 | 日线 + 季频财务，深度浅于 Tushare | 维护频率低 | 备胎 / 离线回填 |
| **efinance** | A / 港 / 美 / 基 | 免费，封装东财 | 东财近年限频明显加严 | 行情 + 公告 + 资金流；研报字段薄 | 中 | 资金流 + 实时分时补充 |
| **yfinance** | 美 / 部分港 | 免费，非官方 | 不稳定，2024 起 Yahoo 多次封 | 美股三表 + 估值，足够 demo | 中（社区维护） | **美股 v0 首选** |
| **SEC EDGAR XBRL** (`data.sec.gov`) | 美 | 完全免费，官方 | 10 req/s/IP，需 User-Agent；无每日额度 | 权威、结构化、可溯 30+ 年 | 高 | **美股财务真源**（搭配 yfinance 取价） |
| **Alpha Vantage** | 美 / FX | Freemium | 免费仅 25 calls/天（2025 收紧） | 全 | 高 | 不推荐：免费档不可用 |
| **Finnhub** | 美 / 港 | Freemium | 60 calls/min 免费 | 实时报价 + 基本面 + 新闻情绪 | 高 | 美股**情绪/新闻**补强 |
| **Polygon.io** | 美 | Freemium | 免费仅 1 年历史 | 强在分钟级行情 | 高 | v0 用不到 |
| **FMP / EODHD** | 美 / 全球 | Freemium 250/天 | — | 三表 + 估值齐 | 高 | 备选 |

### 1.2 公告

| 数据源 | 市场 | API？ | 结构化 | 历史 | v0 评价 |
|---|---|---|---|---|---|
| **巨潮资讯网 cninfo** | A 股 | 半官方 POST `/new/hisAnnouncement/query`（社区已逆向，2024 起部分 AES 加密） | 元数据 JSON，正文 PDF | 1990s 至今 | **A股公告唯一权威源**；通过 AKShare `stock_notice_report()` 间接取更稳 |
| **上交所/深交所披露易** | A 股 | 官方页面，无 REST | 弱 | 长 | 巨潮覆盖即可 |
| **HKEXnews** | 港 | 无官方 REST，Title Search 可逆向 | PDF 为主 | 长 | v0 港股做"公告列表"够用 |
| **SEC EDGAR Submissions API** | 美 | `data.sec.gov/submissions/CIK{}.json` 官方 | 全结构化 + XBRL | 全 | **美股公告真源**，10-K/10-Q/8-K 全 |

### 1.3 研报

| 来源 | 合规性 | 可行性 | v0 评价 |
|---|---|---|---|
| **东方财富研报中心** `data.eastmoney.com/report/` | 灰色：公开页可看，爬有 ToS 风险，版权属券商 | AKShare `stock_research_report_em()` 能拿标题/评级/目标价 | **只取元数据**（标题、机构、评级、目标价、PDF 链接），不入库正文 |
| **慧博投研** `hibor.com.cn` | 灰色，"免费分享"性质 | 站内可下，自动化爬有风险 | 不建议自动爬 |
| 同花顺 / 券商官网 | 版权严格，多家已与 Wind 签代理 | — | 别碰 |
| AlphaSense / Refinitiv | 合规但贵 | 个人项目无门 | — |
| Seeking Alpha | 部分免费 | 美股 demo 可手抓个例 | 美股辅助 |

**v0 研报合规结论见第 4 节。**

### 1.4 IPO / 债券文件

| 来源 | v0 评价 |
|---|---|
| 巨潮 IPO 招股书 | 走 cninfo 同接口，按 `category=category_ndbg_szsh` 等过滤 |
| SEC EDGAR S-1 | 官方 XBRL，开箱即用 |
| 中国债券信息网 `chinabond.com.cn` | 页面爬，AKShare 也封了部分债券接口 | 

---

## 2. 开源 / 现有"个股分析 Agent"项目盘点

| 项目 | Star | 最近更新 | Scope | 端到端个股分析？ | v0 可复用度 |
|---|---|---|---|---|---|
| [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) | ~49.8k | 活跃（2026-03） | 18 个"名人投资人"agent（Buffett/Munger/Wood…）多 agent 投票出买卖建议，FastAPI + React 前端 | 是，美股 | **抄架构**：agent 角色分工 + LangGraph 编排可直接借鉴；数据层只接美股，A股要替 |
| [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) | 高（论文 arXiv 2412.20138 v5） | 活跃 | 多 agent：分析师→研究员→交易员→风控→基金经理 五层 | 是，美股 | **抄"辩论式"工作流**；纯 LLM 推理，无需 GPU |
| [AI4Finance-Foundation/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 数千★ | 活跃 | "智能体平台"，含 Market Forecaster / Document Analyzer / Annual Report Generator | 部分（生成年报分析报告 demo 强） | **直接抄 Annual Report Agent** 的 prompt + 流程 |
| [AI4Finance-Foundation/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) | 大几万★ | 活跃 | 财经 LLM 微调 + Forecaster | 否（偏模型层） | v0 用不到，留作后续"财经 LLM finetune" |
| [OpenBB-finance/OpenBB](https://github.com/OpenBB-finance/OpenBB) | ~40k★ | 活跃 | "金融数据平台 + AI Workspace"，已有 [AKShare/Tushare 扩展博客](https://openbb.co/blog/extending-openbb-for-a-share-and-hong-kong-stock-analysis-with-akshare-and-tushare/) 和 [AI Stock Analysis Agent 博客](https://openbb.co/blog/ai-powered-stock-analysis-agent) | 是 | **最值得作为数据底座**：MCP server + 100+ data provider 统一抽象，A股已有社区适配 |
| [UditGupta10/GPT-InvestAR](https://github.com/UditGupta10/GPT-InvestAR) | 中 | 2024 后冷 | 用 embedding 把年报当 RAG 源做投资特征 | 部分 | **抄 RAG 切分策略**给招股书/10-K 用 |
| [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading) | 中 | 论文项目 | 带分层记忆的 LLM trading agent | 否 | 仅参考记忆设计 |
| [ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) | 小 | 活跃 | LLM 驱动的 A/H/美股日报，AKShare + LLM + 推送 | **是，覆盖 A 股** | **v0 中文示例首选**：直接看它怎么把 AKShare 喂给 LLM |

---

## 3. v0 数据栈推荐（具体到包名 + 用途 + 限制）

> 原则：A 股优先；纯 Python；零成本；2 周内能跑出 demo。

```
# === 数据层 ===
akshare              # A股财务/行情/公告/研报元数据 主力；港美兜底
tushare              # A股财务交叉验证（注册拿 2000 积分免费档）
sec-edgar-api        # 美股 10-K/10-Q/8-K + XBRL company facts
yfinance             # 美股价格 + 简易 fundamentals（demo 够用）
requests + httpx     # cninfo 巨潮 PDF 抓取（AKShare 拿不到的细项）
pdfplumber / PyMuPDF # 公告/招股书 PDF → 文本
duckdb               # 本地存历史季度财务，零运维

# === Agent 层 ===
langgraph            # 抄 ai-hedge-fund / TradingAgents 的多 agent 编排
anthropic            # Claude 做 reasoning + 同行对比
openai (可选)        # 做 embedding（A股财报 RAG）

# === 可选：直接套壳 ===
openbb               # 如果想省自己写 provider 抽象层的活；A股已有社区扩展
```

**角色分工：**

- **AKShare** = A股一切结构化数据的"瑞士军刀"，是 v0 的脊柱
- **Tushare Pro** = A股财务的"质检员"，遇到 AKShare 字段缺失/异常时回查
- **巨潮 cninfo** = A股公告 PDF 真源，AKShare 拿不到的招股书/债券书走它
- **SEC EDGAR + yfinance** = 美股完整闭环（EDGAR 拿真财务，yf 拿价格 + 简表）
- **东财研报元数据**（via AKShare `stock_research_report_em`）= **只入元数据**，正文不存
- **LangGraph + Claude** = 复刻 ai-hedge-fund / TradingAgents 的"分析师 → 研究员 → 总结" 工作流

**已知限制：**

- AKShare 上游是新浪/东财，遇大促或他们改版会断接口，需要每周冒烟测试
- Tushare 港股财务字段要 15000 积分，v0 港股**不要**靠 Tushare
- yfinance 2024 后被 Yahoo 多次封，生产前需备 EDGAR 兜底
- 巨潮接口已部分 AES 加密，复杂度上升；优先走 AKShare 封装，不行再自己撕

---

## 4. 四个重点问题的回答

### Q1：v0 个股分析模块该用哪些数据源？

**推荐组合：AKShare（主） + Tushare Pro 免费档（A股财务校验） + 巨潮 cninfo（A股公告/招股书 PDF） + SEC EDGAR + yfinance（美股闭环） + 东财研报元数据（仅标题/评级/目标价）。**

- A 股：90% 数据走 AKShare；财务做 Tushare 二次校验；公告 PDF 走 cninfo
- 美股加分项：EDGAR 拿三表 / yfinance 拿价格 / Finnhub 免费档拿新闻情绪
- 港股加分项：AKShare（来自新浪/雪球），不上 Tushare 港股
- 全部零成本，单机跑得动

### Q2：研报这块怎么处理？

**v0 不入正文，只入元数据。** 理由：

1. 研报版权严格属于券商研究所；2024 起多家券商已与 Wind 签独家代理协议，自动化抓取正文有明确法律风险
2. 慧博/同花顺的"免费下载"是用户行为豁免，平台自动爬属灰色
3. **可合规取**：东财研报中心的"标题 + 机构 + 评级 + 目标价 + 发布日期 + 原文链接"——这些是事实性数据，AKShare `stock_research_report_em()` 已封装。v0 用这层做"市场一致预期"足够撑 demo
4. 没有公开的开源研报数据集（FinGPT 训练用的多是新闻 + 公告，不是研报正文）
5. 想做"研报深度解读"的演示 demo？**用美股 Seeking Alpha 公开文章 + SEC 10-K MD&A 章节**替代——合规且效果同样炸

### Q3：开源项目里有没有现成的可以拿来即用？

**没有"装上即用"的 A 股版，但有三层可抄：**

- **架构层**：抄 [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)（49.8k★） 或 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 的多 agent 编排（LangGraph + 角色分工 + 辩论式）
- **数据底座**：用 [OpenBB Platform](https://github.com/OpenBB-finance/OpenBB) 当 provider 抽象层，他们已有[官方博客示范用 AKShare/Tushare 扩展 A股/港股](https://openbb.co/blog/extending-openbb-for-a-share-and-hong-kong-stock-analysis-with-akshare-and-tushare/)，省一周适配工作
- **中文示例**：[ZhuLinsen/daily_stock_analysis](https://github.com/ZhuLinsen/daily_stock_analysis) 直接演示 AKShare → LLM → 报告 的最小闭环，可作为 v0 的 hello world
- **报告生成**：抄 [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) 的 Annual Report Agent prompt 模板

**结论：架构抄 ai-hedge-fund，数据底座选 OpenBB（或自写 + AKShare），中文样板看 daily_stock_analysis，报告生成 prompt 抄 FinRobot。** 没有任何项目能 git clone 完事——必须自己写"A股版的 ai-hedge-fund"。

### Q4：A 股 vs 美股的工程量差异

**v0 应该 A 股先。** 量化对比：

| 维度 | A 股 | 美股 |
|---|---|---|
| 财务数据获取 | AKShare 一行调用 | EDGAR XBRL 要解析 us-gaap taxonomy |
| 公告获取 | cninfo 接口已被加密包了一层 | EDGAR 完全开放 + 结构化 |
| 公告语种 | 中文，LLM 处理零摩擦 | 英文 |
| 研报 | 灰色，只能拿元数据 | Seeking Alpha 公开文章可用 |
| Demo 受众 | 中文用户更买账 A 股 demo | 国际化加分但非必须 |
| 开源参考 | 弱，A股版要自己拼 | 强，ai-hedge-fund 现成 |
| 工程总量 | 数据接入轻、内容理解轻 | 数据接入中、解析重 |

**建议节奏：**

1. **Week 1-2**：A 股全闭环（AKShare + cninfo + 1 个分析 agent + Claude 生成报告）
2. **Week 3**：把 A 股的"分析 agent 工作流"复用到美股，数据 provider 换成 EDGAR + yfinance
3. **Week 4+**：港股、同行对比、自然语言追问

A 股先跑通，是因为**单一数据源 (AKShare) 能覆盖财务+行情+公告+研报元数据 90% 场景**，工程摩擦最小。美股虽然开源参考多，但要自己拼 EDGAR + yfinance + Finnhub 三家，反而慢。

---

## Sources

- [akfamily/akshare GitHub](https://github.com/akfamily/akshare)
- [Tushare Pro 积分文档](https://tushare.pro/document/1?doc_id=290)
- [Tushare 港股财务指标](https://tushare.pro/document/2?doc_id=388)
- [SEC EDGAR APIs 官方](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC EDGAR API Guide 2026 (TLDR Filing)](https://tldrfiling.com/blog/sec-edgar-api-guide/)
- [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- [TradingAgents 论文 arXiv 2412.20138v5](https://arxiv.org/html/2412.20138v5)
- [AI4Finance/FinRobot](https://github.com/AI4Finance-Foundation/FinRobot)
- [AI4Finance/FinGPT](https://github.com/AI4Finance-Foundation/FinGPT)
- [OpenBB Platform GitHub](https://github.com/OpenBB-finance/OpenBB)
- [OpenBB 博客：用 AKShare/Tushare 扩展 A股/港股](https://openbb.co/blog/extending-openbb-for-a-share-and-hong-kong-stock-analysis-with-akshare-and-tushare/)
- [OpenBB 博客：构建 AI Stock Analysis Agent](https://openbb.co/blog/ai-powered-stock-analysis-agent)
- [UditGupta10/GPT-InvestAR](https://github.com/UditGupta10/GPT-InvestAR)
- [pipiku915/FinMem-LLM-StockTrading](https://github.com/pipiku915/FinMem-LLM-StockTrading)
- [ZhuLinsen/daily_stock_analysis（中文 A/H/US LLM 分析）](https://github.com/ZhuLinsen/daily_stock_analysis)
- [巨潮资讯网爬虫示例 gaodechen/cninfo_process](https://github.com/gaodechen/cninfo_process)
- [HKEXnews](https://www.hkexnews.hk/index.htm)
- [东方财富研报中心](https://data.eastmoney.com/report/stock.jshtml)
- [Best Free Stock Market APIs 2026 (DEV)](https://dev.to/nexgendata/best-free-stock-market-apis-and-data-tools-in-2026-a-developers-honest-comparison-1926)
- [Best Financial Data APIs in 2026](https://www.nb-data.com/p/best-financial-data-apis-in-2026)
- [金融数据服务业数据合规指引（中伦律所）](https://www.zhonglun.com/research/articles/8744.html)
- [awesome-quant](https://github.com/wilsonfreitas/awesome-quant)
- [awesome-ai-in-finance (georgezouq)](https://github.com/georgezouq/awesome-ai-in-finance)
