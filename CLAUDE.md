# Claude Code 入口（兼容 shim）

canonical 入口在 [`AGENTS.md`](AGENTS.md)。

本文件保留给习惯从 `CLAUDE.md` 启动的 agent runtime（如 Claude Code），不重复维护正文。

## 服务器 / 部署上下文

本项目当前在 Hetzner 服务器（`dev.jeffliulab.com`，IP `89.167.35.145`）上直接开发。服务器 IP、域名、HTTPS、nginx 子路径策略、当前已占用的端口、已部署的"测试网页"（hbi-demo）等公共信息见 [`/home/CLAUDE.md`](../CLAUDE.md)。

> 本仓库 `AGENTS.md` 写的"前端 3000 起步"是 **macOS 本地** 的约定。在服务器上 `3000` 已被 hbi-demo 长期占用，启动 dev server 前必须 `lsof` 实测，按探测段顺移并通过 process env 同步 `CORS_ORIGINS` / `NEXT_PUBLIC_API_URL`，不要改仓库 `.env`。

> **Git 工作流约定**：本仓库 `commit` 后 **立即 `git push origin <branch>`**（包括 `main`）。随时备份比 PR review 更重要——单人项目，本机即开发即生产。打了 release tag 也要 `git push origin <tag>` 一起推上去。
