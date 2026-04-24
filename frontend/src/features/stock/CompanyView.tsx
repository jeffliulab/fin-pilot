/**
 * CompanyView —— /stock 页面的主体：订阅 workspaceStore，按 status 分支渲染.
 *
 * - idle    → emptyHint
 * - loading → spinner + "加载中..."
 * - error   → 红字 + 错误详情
 * - ready   → 3 张 Card 串行渲染
 */

"use client";

import { Loader2 } from "lucide-react";

import { AnnouncementTimelineCard } from "@/components/AnnouncementTimelineCard";
import { FinancialKPICard } from "@/components/FinancialKPICard";
import { ResearchReportListCard } from "@/components/ResearchReportListCard";
import {
  selectWorkspaceCards,
  selectWorkspaceError,
  selectWorkspaceStatus,
  selectWorkspaceTicker,
  useWorkspaceStore,
} from "@/stores/workspaceStore";
import type { CompanyCard } from "@/types/stock";

function CardSwitch({ card }: { card: CompanyCard }) {
  switch (card.card_type) {
    case "financial_kpi":
      return (
        <FinancialKPICard
          title={card.title}
          payload={card.payload}
          citations={card.citations}
        />
      );
    case "announcement_timeline":
      return (
        <AnnouncementTimelineCard
          title={card.title}
          payload={card.payload}
          citations={card.citations}
        />
      );
    case "research_report":
      return (
        <ResearchReportListCard
          title={card.title}
          payload={card.payload}
          citations={card.citations}
        />
      );
    default:
      // exhaustive switch —— 后续加新 card_type 时编译器会催
      return null;
  }
}

export function CompanyView() {
  const status = useWorkspaceStore(selectWorkspaceStatus);
  const cards = useWorkspaceStore(selectWorkspaceCards);
  const ticker = useWorkspaceStore(selectWorkspaceTicker);
  const errorMessage = useWorkspaceStore(selectWorkspaceError);

  if (status === "idle") {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="max-w-md text-center text-sm text-muted-foreground">
          <div className="mb-2 font-medium text-foreground">个股分析</div>
          <div>
            输入 A 股 6 位代码（如 <code className="rounded bg-muted px-1.5 py-0.5">600519</code>）
            或美股 ticker（<code className="rounded bg-muted px-1.5 py-0.5">AAPL</code>），
            agent 会拉财务 / 公告 / 研报评级三张卡到这里。
          </div>
          <div className="mt-3 text-[11px] text-muted-foreground/70">
            数据源：A 股 → AKShare + 巨潮；美股 → SEC EDGAR
          </div>
        </div>
      </div>
    );
  }

  if (status === "loading") {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>正在加载 {ticker} 的数据...</span>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="max-w-md rounded-md border border-destructive/30 bg-destructive/5 p-4 text-sm text-destructive">
          <div className="mb-1 font-medium">加载失败</div>
          <div className="break-all text-[12px]">{errorMessage}</div>
          <div className="mt-2 text-[11px] text-destructive/70">
            常见原因：backend 没启动 / ticker 不在 A 股或美股 / 上游接口被封.
          </div>
        </div>
      </div>
    );
  }

  // status === "ready"
  return (
    <div className="flex flex-col gap-4">
      <div className="text-xs text-muted-foreground">
        {ticker} · 已加载 {cards.length} 张卡片
      </div>
      {cards.map((card, idx) => (
        <CardSwitch key={`${card.card_type}-${idx}`} card={card} />
      ))}
    </div>
  );
}
