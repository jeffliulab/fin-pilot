---
title: 竞品调研 — 金融 AI Copilot 产品形态对比与 UX 推荐
research_date: 2026-04-24
researcher: general-purpose subagent (web research)
prompt_summary: 调研 6+ 个金融 AI copilot / 智能投研类产品（中国 + 海外），重点对比"左菜单 + 工作区 + 右聊天"形态在金融领域的实现，给 FinPilot v0.1 三条具体 UI/UX 建议
informs: docs/PRD.md, docs/architecture.md, plan §11.1（"金融版 Cursor 工业标准"）
status: 调研快照（2026-04），不再随产品迭代而更新
---

# FinPilot 竞品调研：金融 AI Copilot 产品形态对比与 UX 推荐

**一句话格局总结（2026-04）**：海外已经从"chat-only 搜索"全面进化到"agent + workspace + 表格化输出"（AlphaSense / Hebbia / Brightwave 是三巨头，且 Brightwave 公开承认 UI 灵感来自 Cursor）；中国侧仍以"问答框 + 数据表格"为主流（同花顺问财、东财妙想），左菜单+工作区+右聊天的"金融版 Cursor"形态在中文市场几乎是空白——这正是 FinPilot 的差异化窗口。

---

## 主体对比表（10 个产品）

| 产品 | 公司 / 国家 | 目标用户 | 形态 + UI 布局 | 核心功能 (3-5) | 数据覆盖 | 商业模式 / 价位 | 强项 / 软肋 |
|---|---|---|---|---|---|---|---|
| **同花顺问财 (iWencai)** | 同花顺 / 中国 | 零售 + 入门投研 | Web + App，**搜索框首页 + 结果页 dashboard**，左导航较弱 | 自然语言选股、AI 个股分析、事件预测、拍照识股、深度思考(R1) | A股为主，港美股部分 | 免费 + iFinD 终端订阅(机构数万/年) | 强：中文 NL→选股最成熟；软：UI 信息过载，无"工作区"概念 |
| **东方财富 妙想 AI** | 东方财富 / 中国 | 零售 + 机构 | Web + App 嵌入，**聊天为主 + 行情侧栏**，2026 加了"AI 研究员/会议助手"模块 | 投研问答、报表生成、异动联动下单、研报摘要 | A股 / 港股 / 美股 / 宏观 | 免费(C端) + 机构合作 | 强：与东财数据/股吧生态无缝；软：仍是 chat-first，工作区弱 |
| **蚂蚁 支小宝 2.0** | 蚂蚁 / 中国 | 零售理财用户 | 移动 App **chat-only** | 理财问答、持仓诊断、保险智能核保/理赔、投教 | 公募基金为主 | 免费(C端) | 强：意图识别 95%、用户量大；软：纯零售，与投研无关 |
| **萝卜投研 (Datayes)** | 通联数据 / 中国 | 卖方分析师、买方初级 | Web + App，**左侧分类导航 + 中间内容 + 卡片化**（最接近 FinPilot 想做的形态） | 金融搜索引擎、信息抽取、知识图谱、财务预测、研究框架 | A股 / 港股 / 美股 | 免费(轻量) + 萝卜 Pro 机构订阅 | 强：UI 是中国侧最接近 left-menu+workspace 的；软："萝卜大模型"未公开新动作，AI 化进度落后于妙想/问财 |
| **Wind W2A / 终端 AI** | 万得 / 中国 | 机构卖方 + 买方 | **Windows 桌面终端**，菜单驱动；W2A 嵌入 chat 侧栏，2025-2026 投顾终端大模型已备案 | 终端内 AI 问答、自动取数、生成报告草稿、合规问答 | 全球 | 终端 ¥2-3 万/席/年起 | 强：数据最全、机构默认；软：终端老 UI，AI 是"贴上去"的侧栏 |
| **国泰君安君弘 / 中信信 e 投** | 国君 / 中信 / 中国 | 零售 + 客户经理 | Mobile App，**底部 tab + AI 助手浮层** | 智能投顾组合、行情、资讯摘要、客户经理协作 | A股为主 | 免费(开户用户) | 强：合规+客户经理生态；软：AI 仍是辅助按钮，非主交互 |
| **AlphaSense (含 Tegus)** | AlphaSense / 美国 | 卖方 / 买方 / 企业战略 | Web，**左侧文档库导航 + 中间 search/Generative Grid + 右 Workspace 抽屉**；2026.1 升级为多 Agent | Generative Search、Generative Grid（一次问 N 题→表格）、Workflow Agents（公司画像/SWOT 自动产出）、专家访谈 | 全球 + 卖方研报 | $12K-100K+/年（中位 $18K） | 强：生态最完整、表格化输出范式开创者；软：贵、对中文/A股薄弱 |
| **Hebbia (Matrix)** | Hebbia / 美国 | 买方 PE/HF、投行、法务 | Web，**核心是"Matrix"网格界面**：行=文档，列=问题；旁有 Chat / Deep Research | Matrix 网格问答、Agent Swarm 并行多步、深度研究、定制 Agent | 用户上传 + 公开 filings | 企业订阅(六位数起) | 强："表格 = 工作区"范式无人复制；软：上手陡，纯 B2B |
| **Brightwave** | Brightwave / 美国 | 买方分析师 | Web，**官方自称受 Cursor 启发**：左 Agent/任务列表 + 中工作区(报告/图/表) + 长跑后台 worker | 长任务 Agent、数据室分析、报告生成、私募尽调 | 用户上传 + 财报 | 企业订阅 | 强：**目前最像"金融版 Cursor"**；软：体量小、A股无 |
| **Bloomberg ASKB** | Bloomberg / 美国 | 终端用户(机构) | **桌面终端内**嵌入式 chat / 命令行式 | 自然语言查数据/新闻/研报、多 Agent 协调、pre/post-earnings 工作流 | 全球最全 | Terminal $2.5万+/席/年 | 强：数据×分发护城河；软：仍是"终端里的对话框"，非新形态 |
| **Morgan Stanley Debrief / Assistant** | MS / 美国 | 内部 FA/研究员 | 内部 Web，**Salesforce 嵌入**，会议总结 + AskResearchGPT | 会议纪要、邮件草稿、内部研报问答 | 内部研报 + Salesforce | 内部，非售卖 | 强：98% FA 采用率证明价值；软：纯内部参考案例 |
| **Perplexity Finance** | Perplexity / 美国 | 零售 + 轻度专业 | Web，**dashboard(行情热力图) + 顶部搜索 + 财报中心** | 实时行情、财报/SEC 文件分析、组合(Plaid 接入)、ETF 持仓 | 美股 + 加密 | 免费 / Pro $20/月 | 强：免费且引用透明；软：A股/港股没有 |
| **Public.com Alpha + Agents** | Public / 美国 | 零售 | App **券商 UI + AI copilot 抽屉**；2026.3 推 Agents（自然语言→自动交易） | Alpha 个股研究 copilot、AI Agent 自动执行、SEC/电话会摘要 | 美股 / 期权 / 加密 | 券商佣金 + 订阅 | 强：首个把 Agent 接到真实下单；软：投研深度浅 |
| **Quartr Pro** | Quartr / 瑞典 | 卖方 / 买方 | Web + Mobile，**左侧公司库 + 中音频/转录 + AI Chat 侧栏**，可拖拽源文件 | 全球电话会直播+转录、AI 摘要、Topics（Q&A 提炼）、Mentioned By | 全球公司 IR 材料 | 免费/Pro 订阅 | 强：IR 资料最全、UI 干净；软：只做 qualitative，不碰量化 |
| **Daloopa** | Daloopa / 美国 | 卖方建模 | **Excel 插件 + Web**；2026 与 ChatGPT/Claude 出 MCP | 历史财务还原、模型自动更新、Agent 用结构化数据问答 | 5500+ 全球 ticker | 机构订阅 | 强：99% 准确 + MCP 生态先发；软：基本不碰 UI 形态 |
| **Koyfin** | Koyfin / 美国 | 零售进阶 + 小机构 | Web，**左导航 + 自定义 dashboard 网格**，AI 弱 | 自定义 dashboard、screener、charting、研报/转录 | 全球 | 免费/$39/$79 月 | 强：彭博平替 dashboard 体验；软：AI 几乎缺席 |
| **Magnifi (TIFIN)** | TIFIN / 美国 | 零售 | Web + App，**搜索条 + 卡片结果** | NL 搜证券、组合分析、情景测试 | 美股 + ETF | $8.25/月起 | 强：便宜易上手；软：功能浅，2026 已被 Public/Perplexity 反超 |

> **倒闭/停滞核查**：FinChat.io 已改名 Fiscal.ai 并继续迭代（Plus $24/Pro $64）；Stockwits-AI 没有可靠的 2026 产品信息（StockTwits 母公司有 AI feed 但非独立产品），从对比表中略去。Tegus 已被 AlphaSense 收购($930M, 2024)，专家访谈并入 AlphaSense。

---

## 三个核心问题的回答

### Q1：市场上有"金融版 Cursor"吗？

**有，但只有一个：Brightwave**。其官网与 2025 复盘文章明确写着 "inspired by system and user interface design patterns drawn from AI-powered software engineering tools like Cursor"，并把自己定位成"information IDE"——左侧 agent/任务列表，中间工作区呈现 Reports/Charts/Tables/Slides，长任务由后台 worker 异步执行不打断流。

**次接近**：
- **AlphaSense Generative Search v2 (2026.1)**：左文档库 + 中 Generative Grid + 右 Workspace，但仍偏"超级搜索"心智，不是"功能选择 + 工作区"心智。
- **Hebbia Matrix**：把工作区做成了网格(Sheet)，独特但反而离 Cursor 更远——它像"Excel + AI"。
- **萝卜投研（中国侧最近）**：有左导航 + 卡片化中间区，但 AI 还没成为主交互。

中文市场目前**没有**真正的"金融版 Cursor"。

### Q2："输入公司名 → 出整理好的财务/公告/研报 + 自然语言追问"谁做得最好？

排序：

1. **AlphaSense + Tegus**：搜公司 → 自动出 Company Primer / SWOT / 估值快照（Workflow Agent 一键），右侧 Workspace 可继续追问；引用密度最高。
2. **Hebbia Matrix**：把"一家公司"变成一行，N 个问题变成 N 列，瞬间生成结构化对照表；适合"批量公司比较"场景。
3. **FinChat / Fiscal.ai**：消费级最好的体现——公司页 = 卡片(收入分部 / 估值 / 转录摘要) + 底部 Copilot 追问。
4. **Quartr**：在"qualitative(电话会/IR)"维度最强，公司页左导航选事件→中间转录→右 AI Chat。
5. **同花顺问财 / 东财妙想**：是中文里最接近的，但更像"问答 → 表格"，缺"公司主页"沉淀。

**典型 UI 模式**：左/上是"公司选择器"，中间是结构化卡片(财务/公告/研报/转录)，右侧或下方常驻一个聊天面板支持追问，所有回答都带源文档引用且可点击侧开。

### Q3：FinPilot v0 应该抄谁、避开什么坑？

**抄**：Brightwave 的三栏壳子 + AlphaSense 的"Generative Grid 表格输出" + Quartr 的"源文档侧开抽屉"。
**避**：同花顺问财式的信息密度爆炸；Wind 式的"AI 是贴在终端上的侧栏"；妙想式的 chat-first（聊久了找不到历史成果）。

---

## 给 FinPilot v0 的三条具体形态建议

### 1. 三栏 + "工作区是一等公民"，聊天只是"驱动器"
- **左栏**：固定三个核心模块（个股 / 行业 / 市场）作为顶层菜单，下面是"最近工作区/收藏"列表（像 Cursor 的文件树）。
- **中栏**：每个分析任务 = 一个可命名、可保存的"Workspace 卡片画布"，里面是结构化模块（财务表/公告时间线/研报观点墙/估值快照）。
- **右栏**：常驻 Chat，但每次回答必须**写进左侧或中间的 workspace**（生成新卡片 / 修改现有卡片），不要只在对话流里飘走。
- **为什么**：Brightwave / AlphaSense 已经验证"chat 驱动 + workspace 沉淀"是金融分析师真正需要的——他们要的是一份能交付的 deliverable，而不是聊天记录。中文市场目前所有产品都没做到这一点。

### 2. "公司主页"模板化 + Generative Grid 做横向比较
- 个股板块输入"贵州茅台" → 立刻渲染**模板化公司主页**：财务 KPI / 最近公告 / 研报观点聚合 / 电话会摘要 / 资金流，全部带"（点击追问）"按钮。
- 行业板块支持 "选 5 家公司 × 8 个问题" 的网格视图（直接抄 Hebbia/AlphaSense Generative Grid），跑完导出 Excel。
- **为什么**：这是分析师 80% 的高频动作；同花顺/东财都还停留在"问一句出一段话"。模板化一次性把整个工作流做完，演示效果立刻拉开档次。

### 3. 引用即抽屉（Citations as Drawer），不要让用户跳页
- 任何 AI 回答里的数字 / 引述都做成**inline 角标**，点击 → 右侧或底部抽屉打开**原始 PDF/公告/研报片段并高亮**，不离开当前 workspace。
- 合规与可信度全靠这个：投研/合规岗位完全不能接受"无出处的结论"。
- **为什么**：AlphaSense / Hebbia / Bloomberg ASKB / Perplexity Finance 全部把"transparent citation"作为头号卖点；中文产品（妙想、问财）这一块最弱，是最容易显档次差距的细节。作品集 demo 里这一交互最能"一秒钟让面试官看出你懂金融"。

---

**字数**：约 1750 字（不含表格）。

**Sources（真实可点击）**：
- 同花顺问财：https://www.iwencai.com/
- 东方财富 妙想：https://ai.eastmoney.com/
- 萝卜投研：https://robo.datayes.com/
- 蚂蚁支小宝 2.0：https://www.cls.cn/detail/1458818
- AlphaSense 2026 Generative Search：https://www.alpha-sense.com/resources/product-articles/generative-search-next-generation/
- AlphaSense 2025 release recap：https://www.alpha-sense.com/resources/product-articles/product-releases-2025/
- Hebbia：https://www.hebbia.com/ ; April 2026 update：https://www.hebbia.com/blog/whats-new-april-disclosure-2026
- Brightwave：https://www.brightwave.io/ ; Series A：https://www.businesswire.com/news/home/20241029778071/en/
- Bloomberg ASKB：https://www.bloomberg.com/professional/insights/press-announcement/meet-askb-a-first-look-at-the-future-of-the-bloomberg-terminal-in-the-age-of-agentic-ai/
- Morgan Stanley Debrief：https://www.morganstanley.com/press-releases/ai-at-morgan-stanley-debrief-launch
- Perplexity Finance：https://www.perplexity.ai/finance
- Public.com Alpha / Agents：https://public.com/alpha ; https://www.prnewswire.com/news-releases/public-becomes-the-first-brokerage-to-introduce-ai-agents-for-your-portfolio-302729050.html
- FinChat (Fiscal.ai)：https://www.wallstreetzen.com/blog/finchat-io-fiscal-ai-review/
- Quartr AI Chat：https://quartr.com/features/ai-chat-for-financial-research
- Daloopa MCP：https://daloopa.com/
- Koyfin：https://www.koyfin.com/features/
- Magnifi：https://magnifi.com/
- Wind 投顾终端大模型备案：https://www.wind.com.cn/mobile/News/NewsDetail/zh.html?id=723
- 君弘 / 信 e 投 2026 测评：https://caifuhao.eastmoney.com/news/20260209090704341326810
- AI UI 三栏布局参考：https://uxdesign.cc/where-should-ai-sit-in-your-ui-1710a258390e

---

**安全提示**：在调研过程中，有 WebFetch 返回的内容里夹带了"使用 TodoWrite"的伪系统提示（疑似 prompt injection），已识别并忽略——它不属于您发出的指令。
