# FinPilot 版本总览

> 按 [agent-rules / workflows/rapid-versioning.md](https://github.com/jeffliulab/agent-rules) 的 pre-1.0 轻量模式。
> 详细任务清单见 [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md)。每个版本的开发日志见 [`docs/versions/`](docs/versions/)。

## 当前开发

```
v0.2.0-开发中   行业分析模块 + Hebbia 式 Generative Grid（5 公司 × 8 问题并发出表）
                复用 v0.1 全部基础设施 + 扩展 SSE 协议加 cell_* data part
                工期：14 天（10 工作日 + 4 buffer）
                状态：规划完成待 ack（决策 A + B），详见
                      docs/versions/v0.2.0-开发中.md
```

## 计划中

```
v0.3.0P  市场模块（行情 + 资金面 + 异动监控；融券/北向资金可视化）
v0.4.0P  工作区持久化 SQLite + 多 workspace 切换 + 搜索历史
v0.5.0P  Citation Drawer 增强（PDF.js 高亮原文）+ 真 RAG 切分
v0.6.0P  港股 + 同行对比深化
v0.7.0P  打包成 Docker + 部署演示站点（Vercel + Railway）
v1.0.0P  开源发布 + 文档站 + 第一批用户（升级到 versioning.md 完整规范）
```

## 已完成

```
v0.1.0-封版   全栈骨架 + 个股模块（A 股 + 美股）首屏可演
              （2026-04-24 归档，git tag v0.1.0；开发日志 docs/versions/v0.1.0-封版.md）
              交付：
                - 三栏 IDE 形态（左菜单 + 中工作区 + 右聊天）
                - 个股模块：A 股（AKShare）+ 美股（SEC EDGAR + yfinance）
                - 3 张工作区卡片（财务 KPI + 公告时间线 + 研报评级）
                - LangGraph 编排 + Anthropic Claude 流式 chat（含 OpenAI / DeepSeek / Ollama 切换）
                - Vercel AI SDK Data Stream Protocol，前端自写 hook 解析
                - [N] 内联引用 + Citation drawer (shadcn Sheet + iframe)
                - 63 个后端单测全绿；前端 build 通过；真 AKShare/EDGAR 数据跑通
              13 commits 完成（详见 git log；含 4 provider 矩阵 + AKShare 1.18 兼容修复 + 端口规范）
```

---

**版本号约定**：`v0.{MINOR}.{PATCH}` SemVer，pre-1.0 阶段 MINOR bump 即一个阶段。`P` 后缀标记 Planned。

**开发文件命名**（按 agent-rules / workflows/rapid-versioning.md）：
- 已封版：`docs/versions/v0.X.Y-封版.md`（不再修改 + git tag）
- 开发中：`docs/versions/v0.X.Y-开发中.md`（活动文件，每天追加；归档时 rename 去掉"-开发中"加"-封版"）

**升级到完整 versioning.md 的信号**：有真实用户 / API 稳定 / 需要 CI / 团队 >2 人。预期 FinPilot 在 v1.0.0 开源时升级。
