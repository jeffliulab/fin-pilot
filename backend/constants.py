"""Magic numbers, endpoints, defaults —— 集中放这里，避免散落到业务代码.

按 agent-rules/principles/engineering.md：魔法数字提取到 constants.py。
"""

from __future__ import annotations

# === 数据源默认参数 ===
DEFAULT_ANNOUNCEMENT_LIMIT = 20
DEFAULT_RESEARCH_REPORT_LIMIT = 30
DEFAULT_FINANCIAL_PERIODS = 4  # 最近 4 个季度

# === HTTP 通用 ===
DEFAULT_HTTP_TIMEOUT_SEC = 30
DEFAULT_HTTP_RETRIES = 1

# === SEC EDGAR ===
EDGAR_BASE_URL = "https://data.sec.gov"
EDGAR_TICKER_CIK_URL = "https://www.sec.gov/files/company_tickers.json"
EDGAR_RATE_LIMIT_SLEEP_SEC = 0.15  # 7 req/s 安全低于官方 10 req/s 上限
EDGAR_FORMS_FOR_ANNOUNCEMENTS = ("10-K", "10-Q", "8-K", "20-F", "S-1", "DEF 14A")

# === AKShare ===
AKSHARE_TIMEOUT_SEC = 30
# A 股 ticker 标准化：用户输入可能带 .SS / .SZ 后缀，AKShare 接口要 6 位裸 code
A_SHARE_SH_PREFIX = ("600", "601", "603", "605", "688", "689")
A_SHARE_SZ_PREFIX = ("000", "001", "002", "003", "300", "301")
A_SHARE_BJ_PREFIX = ("430", "830", "831", "832", "833", "834", "835", "836", "837", "838", "839", "870", "871", "872", "873")  # 北交所

# === 卡片渲染 ===
KPI_DEFAULT_METRICS = (
    "revenue",
    "net_income",
    "operating_cash_flow",
    "gross_margin",
    "roe",
    "debt_ratio",
)
