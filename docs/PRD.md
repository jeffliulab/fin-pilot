# FinPilot 产品需求文档（PRD）

> 状态：v0.1 草稿。基于 [初步探讨思路.txt](初步探讨思路.txt) + [research/competitor-landscape.md](research/competitor-landscape.md) + [research/data-sources.md](research/data-sources.md) 综合产出。
> 用途：作为开发依据 + 作品集 / 面试展示材料。

---

## 1. 一句话定位

FinPilot 是面向中国金融行业从业者（投研 / 投顾 / 基金经理）的**三栏 AI 工作台**，
对标 Brightwave / AlphaSense 在海外验证过的 "workspace-first-class" 形态，
对中文市场仍以"chat + 数据表"为主的同花顺 / 东财 / 萝卜投研形成代际差。

**类比**：Cursor 之于程序员。

---

## 2. 形态（决定一切设计的 anchor）

```
┌──────────────┬─────────────────────────────────┬──────────────┐
│ 左：菜单      │ 中：工作区 (Workspace)            │ 右：聊天      │
│              │                                  │              │
│ ▸ 个股分析   │ [输入：贵州茅台 / 600519]          │ "现金流为何   │
│   公司主页   │ ┌──────────────────────────────┐ │ 连续两年下滑？"│
│   同行对比   │ │ 财务 KPI 卡（营收/净利/毛利） │ │              │
│ ▸ 行业分析   │ │ 公告时间线卡（最近 20 条）    │ │ Agent: 解释  │
│ ▸ 市场行情   │ │ 研报评级卡（机构/目标价/评级） │ │ + [1] [2]    │
│              │ │                              │ │             │
│ ──────────── │ │ 引用 [1] → 抽屉打开 PDF 原文  │ │             │
│ 历史会话     │ └──────────────────────────────┘ │             │
└──────────────┴─────────────────────────────────┴──────────────┘
```

### 三个非协商性设计原则（来自 [research/competitor-landscape.md](research/competitor-landscape.md)）

1. **Workspace 是一等公民，对话只是触发器** —— 每次 AI 回答必须沉淀成 workspace 卡片，不能只在对话流里飘走
2. **公司主页模板化 + Generative Grid 横向比较** —— 输入公司即出标准化主页（个股）；选 N 公司 × M 问题即出网格（行业，v0.2）
3. **引用即抽屉（Citations as Drawer）** —— inline 角标点击 → 侧抽屉打开原文，不离开 workspace；这是中文产品最大短板，最容易拉开档次

---

## 3. v0.1 模块范围

| # | 模块 | 状态 | 描述 |
|---|------|------|------|
| 1 | **个股分析** | ✅ v0.1 | 输入 ticker → 公司主页（财务 KPI / 公告时间线 / 研报评级三张卡）+ 自然语言追问 + Citation drawer |
| 2 | **行业分析** | ⏳ v0.2 | 占位页（"v0.2 上线"）；菜单显示但禁用 |
| 3 | **市场行情** | ⏳ v0.3 | 占位页（"v0.3 上线"）；菜单显示但禁用 |

**v0.1 个股模块覆盖市场**：A 股（如 `600519` / `贵州茅台`）+ 美股（如 `AAPL`）。
港股留 v0.6，详细数据源选择见 [research/data-sources.md](research/data-sources.md)。

### 3.1 v0.1 数据源选定（per [research/data-sources.md](research/data-sources.md)）

| 用途 | 包 / API | 备注 |
|------|---------|------|
| A 股 财务 + 行情 + 公告元数据 + 研报元数据 | `akshare`（18.5k★） | 主力，一行调用 |
| A 股 招股书 / 债券书 PDF | `requests` 走巨潮 cninfo | AKShare 拿不到时兜底 |
| 美股 财务真源 | SEC EDGAR XBRL | 官方免费，10 req/s |
| 美股 价格 + 简易 fundamentals | `yfinance` | demo 够 |
| LLM | `anthropic` 默认 + `openai` 备选 | salvaged `backend/llm/` |

**研报合规策略**：v0.1 **只入元数据**（标题 / 机构 / 评级 / 目标价 / 链接），不爬正文。
原因详见 [research/data-sources.md §4 Q2](research/data-sources.md)：版权属券商，Wind 已签独家代理。

---

## 4. 用户场景（v0.1 demo story，30-60 秒）

**1. 打开** `http://localhost:3000` → 看到三栏 IDE，左菜单默认选中"个股分析"

**2. 输入 ticker** → A 股 `600519` 或美股 `AAPL`

**3. 中工作区渲染公司主页 3 张卡**：
- 财务 KPI 卡：最近 4 季度营收 / 净利润 / 现金流 / 毛利率 / ROE
- 公告时间线卡：最近 20 条公告标题 + 日期 + PDF 链接
- 研报评级卡：最近 30 天的研报机构 / 评级 / 目标价

**4. 在右聊天框追问**："现金流为什么连续两年下滑？"

**5. ChatPanel 流式输出**：
> "贵州茅台 2023 / 2024 经营性现金流分别同比下滑 X% / Y%，主要受三方面影响：(1) ... [1] (2) ... [2] (3) ... [3]"

**6. 点击 `[1]`** → 右侧抽屉抽出 → iframe 加载该年报 PDF（来自巨潮）

**7. 演示完毕。** 总用时 < 60 秒。

---

## 5. v0.1 范围之外（明确不做）

- ❌ 行业 / 市场模块的实际功能（仅菜单条目 + "Coming in v0.2/3"）
- ❌ 工作区持久化 / 用户登录 / 多用户（v0.4 一并做）
- ❌ PDF.js 原文高亮（v0.5；v0.1 抽屉用 iframe 即可）
- ❌ 同行对比 Generative Grid（v0.2）
- ❌ 港股（v0.6）
- ❌ Docker / 部署 / CI / Dependabot（v0.7）
- ❌ 国际化（默认中文）/ 暗黑模式
- ❌ 真正的 RAG 向量库（v0.5；v0.1 直接给 LLM 喂结构化 JSON + URL）
- ❌ 研报正文（合规：v0.1 只入元数据）
- ❌ 交易执行 / 量化回测（合规 + 牌照风险，永远不做）
- ❌ "具体产品推荐"（非持牌投顾红线，永远不做）

---

## 6. v0.x 后续 roadmap（让面试官一眼看到 product judgement）

```
v0.2.0  行业模块 + Hebbia 式 Generative Grid（5 公司 × 8 问题批量出表）
v0.3.0  市场模块（行情 + 资金面 + 异动监控；融券/北向资金可视化）
v0.4.0  工作区持久化 SQLite + 多 workspace 切换 + 搜索历史
v0.5.0  Citation Drawer 增强 PDF.js 高亮 + 真 RAG 切分（v0.1-v0.4 是 fast retrieval）
v0.6.0  港股 + 同行对比深化
v0.7.0  打包成 Docker + 部署演示站点（Vercel + Railway）
v1.0.0  开源发布 + 文档站 + 第一批用户
```

---

## 7. 中文项目名（v0.1 不定）

候选：金助 / 金航 / 金融副驾 / 领航员 / 智投台。v0.7 上线公开 demo 时再定。

---

## 8. 关联文档

| 文档 | 用途 |
|---|---|
| [`architecture.md`](architecture.md) | 系统架构（前端组件 / 后端三层 / 数据流） |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) | 当前 v0.1.0 任务清单 |
| [`versions/v0.1.0.md`](versions/v0.1.0.md) | v0.1.0 开发日志 |
| [`research/competitor-landscape.md`](research/competitor-landscape.md) | 16 个金融 AI 产品 + UX 调研（设计依据） |
| [`research/data-sources.md`](research/data-sources.md) | 数据源 + 开源方案盘点（数据栈依据） |
| [`SALVAGE_MAP.md`](SALVAGE_MAP.md) | 旧仓库代码出处追溯 |
| [`初步探讨思路.txt`](初步探讨思路.txt) | legacy 原始构思（对照参考） |
