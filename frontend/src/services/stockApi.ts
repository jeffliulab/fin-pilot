/**
 * Stock API client —— 镜像 backend/routes/stock.py.
 */

import type { CompanyOverviewResponse } from "@/types/stock";

import { apiFetch } from "./apiClient";

/** GET /api/v1/stock/{ticker}/overview —— 返回公司主页 3 张卡. */
export async function getCompanyOverview(
  ticker: string,
  signal?: AbortSignal,
): Promise<CompanyOverviewResponse> {
  const safeTicker = encodeURIComponent(ticker.trim());
  return apiFetch<CompanyOverviewResponse>(
    `/api/v1/stock/${safeTicker}/overview`,
    { signal },
  );
}
