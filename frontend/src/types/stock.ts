/**
 * Stock-related types —— 镜像 backend/interfaces.py + backend/routes/_schemas.py.
 *
 * 任何 schema 改了 backend，这里同步改；约定 backend 是 source of truth.
 */

import type { Citation } from "./citation";

export type Market = "A" | "US";

export type CardType =
  | "financial_kpi"
  | "announcement_timeline"
  | "research_report";

/** financial_kpi card payload —— 一行就是一个 KPI（如 revenue / ROE）。 */
export type KPISummaryItem = {
  name: string; // e.g. "revenue"
  display_name: string; // e.g. "营业总收入"
  latest_value: number | null;
  latest_period: string; // e.g. "2024-09-30"
  unit: string; // "CNY" / "%" / "USD"
  trend: (number | null)[]; // 旧 → 新
  trend_periods: string[]; // 旧 → 新
};

export type FinancialKPIPayload = {
  summary: KPISummaryItem[];
  currency: string;
};

/** announcement_timeline card payload */
export type AnnouncementItem = {
  title: string;
  date: string;
  type: string;
  url: string;
};

export type AnnouncementTimelinePayload = {
  items: AnnouncementItem[];
};

/** research_report card payload */
export type ResearchReportItem = {
  title: string;
  institution: string;
  analyst: string | null;
  rating: string | null;
  target_price: number | null;
  price_currency: string;
  date: string;
  url: string | null;
};

export type ResearchReportPayload = {
  items: ResearchReportItem[];
  consensus_target: number | null;
  consensus_target_basis: number;
  rating_distribution: Record<string, number>;
  report_count: number;
};

/** Discriminated union over card_type —— 让 TypeScript 在卡片渲染分支处能窄化 payload. */
export type CompanyCard =
  | {
      ticker: string;
      market: Market;
      card_type: "financial_kpi";
      title: string;
      payload: FinancialKPIPayload;
      citations: Citation[];
    }
  | {
      ticker: string;
      market: Market;
      card_type: "announcement_timeline";
      title: string;
      payload: AnnouncementTimelinePayload;
      citations: Citation[];
    }
  | {
      ticker: string;
      market: Market;
      card_type: "research_report";
      title: string;
      payload: ResearchReportPayload;
      citations: Citation[];
    };

/** GET /api/v1/stock/{ticker}/overview response. */
export type CompanyOverviewResponse = {
  ticker: string;
  market: Market;
  cards: CompanyCard[];
};
