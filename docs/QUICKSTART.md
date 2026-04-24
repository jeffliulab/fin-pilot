# FinPilot v0.1.0 本地启动指南

> 第一次跑请按这个顺序来。需要：Python 3.11+ 和 Node 22+，以及一个
> Anthropic Claude 的 API key（默认 LLM provider）。

---

## 1. 后端：FastAPI

### 1.1 建虚拟环境（推荐 conda）

```bash
cd /path/to/fin-pilot
conda create -n fin-pilot python=3.11 -y
conda activate fin-pilot
```

### 1.2 装依赖

```bash
pip install -e ".[dev]"
```

> 这一步会装 fastapi / uvicorn / akshare / yfinance / langchain / langgraph /
> anthropic / openai 等约 100 MB 的依赖；首次跑大概 1-2 分钟。

### 1.3 配 .env

```bash
cp .env.example .env
# 编辑 .env，至少填 ANTHROPIC_API_KEY
```

最少需要的字段（任选一个 LLM provider 填 key）：

```
# 三选一：
LLM_PROVIDER=anthropic                          # 默认；用 Claude 3.5 Sonnet
ANTHROPIC_API_KEY=sk-ant-xxx

# 或：用 ChatGPT
LLM_PROVIDER=openai                             # 用 gpt-4o-mini（便宜）；改 orchestrator 默认 model 切 gpt-4o
OPENAI_API_KEY=sk-proj-xxx

# 或：用 DeepSeek（中文好 + 最便宜）
LLM_PROVIDER=deepseek                           # 用 deepseek-chat
DEEPSEEK_API_KEY=sk-xxx

# 这两个不论选哪 provider 都要填：
SEC_EDGAR_USER_AGENT="FinPilot dev your@email"  # SEC 要求带联系方式
CORS_ORIGINS=http://localhost:3000              # 前端地址
```

### 1.4 跑测试（可选，先确认环境健康）

```bash
pytest backend/tests/ -v
# 期望：58 passed
```

### 1.5 启动 backend

```bash
uvicorn backend.main:app --reload --port 8000
```

打开 http://localhost:8000/docs 看 OpenAPI 文档；试试：

```bash
curl http://localhost:8000/healthz
# {"status":"ok","version":"0.1.0.dev"}
```

---

## 2. 前端：Next.js

新开一个终端（不要关 backend）：

### 2.1 装依赖

```bash
cd frontend
npm install
```

> 第一次跑 ~30 秒。

### 2.2 配 env（默认值就够了）

```bash
cp .env.example .env.local
# 默认 NEXT_PUBLIC_API_URL=http://localhost:8000，与 backend 默认端口对得上
```

### 2.3 启动 frontend

```bash
npm run dev
# Local: http://localhost:3000
```

---

## 3. 试试

1. 浏览器打开 http://localhost:3000 —— 自动重定向到 `/stock`
2. 左菜单选「个股分析」（默认就是）
3. 中工作区上方点快速试用按钮 `600519`（贵州茅台）—— agent 会拉财务 / 公告 / 研报评级三张卡到中区
4. 切到 `AAPL` 看美股版本（数据走 SEC EDGAR）
5. 在右侧聊天框问：**"现金流为什么连续两年下滑？"** —— 看 Claude 流式回答 + `[N]` 角标
6. 点回答里的 `[1]` 角标 —— 右侧抽屉抽出，iframe 加载原文 URL（如果是巨潮 / SEC 站点可能因 X-Frame-Options 空白，点抽屉右上角 ↗ 在新标签打开）

---

## 4. 常见问题

**backend 报 `ANTHROPIC_API_KEY 未设置`**
→ `.env` 文件没填 / 没在虚拟环境里跑。检查 `echo $ANTHROPIC_API_KEY` 是否有值；
   或确认 `cd /path/to/fin-pilot` 之后再 `uvicorn` 启动（FastAPI 从 cwd 加载 .env）。

**前端报 `网络请求失败`**
→ backend 没起来，或端口冲突。`curl http://localhost:8000/healthz` 看 backend 是否
   响应。如果 backend 跑在别的端口，改 `frontend/.env.local` 的 `NEXT_PUBLIC_API_URL`。

**输入 `0700.HK` 报 `422`**
→ v0.1 只支持 A 股 + 美股；港股留 v0.6。

**AKShare 接口报错 / 返空**
→ 上游（东财 / 新浪）偶发限流 / 改版。看 backend log 中具体哪个函数失败；
   通常等几分钟再试。

**SEC EDGAR 报 `403`**
→ User-Agent 不规范。SEC 强制要求 User-Agent 含联系方式，把 `.env` 里的
   `SEC_EDGAR_USER_AGENT` 改为 `"YourName your@email.com"` 形式。

---

## 5. 想跑跑代码 / 改改东西？

- 后端三层：[`backend/routes/`](../backend/routes/) → [`backend/services/`](../backend/services/) → [`backend/repositories/`](../backend/repositories/)
- 前端组件：[`frontend/src/components/`](../frontend/src/components/)
- 前端业务：[`frontend/src/features/`](../frontend/src/features/)
- 类型对齐：[`frontend/src/types/stock.ts`](../frontend/src/types/stock.ts) 镜像 [`backend/interfaces.py`](../backend/interfaces.py)
- 数据流走向：见 [`architecture.md §4`](architecture.md)

后续 v0.2+ 路线图见 [`../VERSIONS.md`](../VERSIONS.md)。
