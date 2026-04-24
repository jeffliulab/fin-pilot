# FinPilot — Cursor for Financial Analysts

> Like Cursor for software engineers — FinPilot is a three-pane AI workspace for stock research,
> industry tracking, and market intelligence, built around the workspace-first-class principle
> that Brightwave / AlphaSense / Hebbia pioneered.

> 🇨🇳 中文版 README → [`README_zh.md`](README_zh.md)

## What it is

A fullstack copilot (FastAPI + Next.js) for finance professionals — research analysts, fund managers,
client advisors. Three modules in v0.x roadmap:

| # | Module | v0.1 status |
|---|---|---|
| 1 | **Stock analysis** — paste ticker → company main page (financials / announcements / research ratings) + natural-language follow-up + citation drawer | ✅ A-shares + US (`600519`, `AAPL`) |
| 2 | **Industry analysis** — macro / industry / policy / events with Hebbia-style 5×8 generative grid | ⏳ v0.2 |
| 3 | **Market intelligence** — quotes / capital flows / sentiment / anomaly monitoring | ⏳ v0.3 |

## Why three-pane

Per [`docs/research/competitor-landscape.md`](docs/research/competitor-landscape.md), the
**workspace + chat** pattern (Brightwave / AlphaSense / Cursor) consistently beats
**chat-only** (most Chinese incumbents) for analyst workflows: deliverables sediment in the
workspace, chat drives but doesn't bury results, citations open inline as drawers without
leaving the page.

## Tech stack

- **Backend**: FastAPI + Python 3.11 + LangGraph + AKShare (A-shares) + SEC EDGAR (US) + yfinance
- **Frontend**: Next.js 14 + TypeScript strict + Tailwind + shadcn/ui + Zustand + TanStack Query + Vercel AI SDK
- **LLM**: Anthropic Claude 3.5 Sonnet default; OpenAI / DeepSeek / Ollama via salvaged provider abstraction
- **Storage**: in-memory in v0.1 (zustand); SQLite in v0.4

This stack is the union of [Brightwave / Perplexity / Cursor / ai-hedge-fund](docs/research/competitor-landscape.md) — see plan §11.1 for industry-standard rationale.

## Repo layout

```
fin-pilot/
├── AGENTS.md / CLAUDE.md         agent rules entry (→ ~/Local_Root/agent-rules/)
├── VERSIONS.md                   version overview (rapid-versioning, pre-1.0)
├── README.md / README_zh.md      English / Chinese
├── pyproject.toml                backend deps
├── .env.example                  required env keys
├── docs/
│   ├── PRD.md                    product requirements
│   ├── architecture.md           system architecture (3-pane + data flow)
│   ├── NEXT_STEPS.md             current v0.1.0 task list
│   ├── SALVAGE_MAP.md            provenance of code from archived repos
│   ├── research/                 frozen research snapshots
│   │   ├── competitor-landscape.md
│   │   └── data-sources.md
│   └── versions/v0.1.0.md        per-version dev log
├── backend/                      FastAPI three-layer (routes / services / repositories)
└── frontend/                     Next.js (created in Day 5)
```

## Status

🚧 **v0.1.0 in development** (started 2026-04-24). See [`VERSIONS.md`](VERSIONS.md) for roadmap and [`docs/NEXT_STEPS.md`](docs/NEXT_STEPS.md) for current tasks.

This project was bootstrapped from 5 archived predecessor repos under `jeffliulab/` (see [`docs/SALVAGE_MAP.md`](docs/SALVAGE_MAP.md)). Finance-related (accounting / tax / CFO) content lives in the sibling project [`agent-as-a-cfo`](https://github.com/jeffliulab/agent-as-a-cfo).

## License

TBD (will follow [agent-rules workflows/github.md](https://github.com/jeffliulab/agent-rules) when public).
