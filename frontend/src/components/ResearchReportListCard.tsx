/**
 * ResearchReportListCard —— 研报评级 + 共识目标价 + 评级分布 + 列表.
 *
 * v0.1：只入元数据（标题 / 机构 / 评级 / 目标价 / 链接），不入正文.
 */

"use client";

import { ExternalLink } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CitationLabel } from "@/components/CitationLabel";
import { cn } from "@/lib/utils";
import type { Citation } from "@/types/citation";
import type { ResearchReportPayload } from "@/types/stock";

type Props = {
  title: string;
  payload: ResearchReportPayload;
  citations: Citation[];
};

const RATING_COLOR: Record<string, string> = {
  买入: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  增持: "bg-blue-500/15 text-blue-700 dark:text-blue-300",
  推荐: "bg-blue-500/15 text-blue-700 dark:text-blue-300",
  Buy: "bg-emerald-500/15 text-emerald-700 dark:text-emerald-300",
  Outperform: "bg-blue-500/15 text-blue-700 dark:text-blue-300",
  中性: "bg-muted text-muted-foreground",
  持有: "bg-muted text-muted-foreground",
  Hold: "bg-muted text-muted-foreground",
  Neutral: "bg-muted text-muted-foreground",
  减持: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  卖出: "bg-rose-500/15 text-rose-700 dark:text-rose-300",
  Underperform: "bg-amber-500/15 text-amber-700 dark:text-amber-300",
  Sell: "bg-rose-500/15 text-rose-700 dark:text-rose-300",
};

function ratingClass(rating: string | null): string {
  if (!rating) return "bg-muted text-muted-foreground";
  return RATING_COLOR[rating] ?? "bg-muted text-muted-foreground";
}

export function ResearchReportListCard({ title, payload, citations }: Props) {
  const items = payload.items;
  const hasConsensus = payload.consensus_target !== null;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>{title}</span>
          {citations.map((c) => (
            <CitationLabel key={c.label + c.source_name} citation={c} />
          ))}
        </CardTitle>
        <CardDescription className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1">
          {hasConsensus ? (
            <span>
              共识目标价：
              <span className="font-medium text-foreground">
                {payload.consensus_target}
              </span>
              <span className="ml-1 text-[10px] text-muted-foreground">
                （基于 {payload.consensus_target_basis} 份）
              </span>
            </span>
          ) : (
            <span className="text-muted-foreground">暂无共识目标价</span>
          )}
          {Object.entries(payload.rating_distribution).length > 0 && (
            <span className="flex flex-wrap items-center gap-1">
              {Object.entries(payload.rating_distribution).map(([rating, count]) => (
                <span
                  key={rating}
                  className={cn(
                    "rounded px-1.5 py-0.5 text-[10px] font-medium",
                    ratingClass(rating),
                  )}
                >
                  {rating} × {count}
                </span>
              ))}
            </span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="py-6 text-center text-sm text-muted-foreground">
            暂无研报
          </div>
        ) : (
          <ScrollArea className="h-72">
            <ol className="space-y-2">
              {items.map((report, idx) => (
                <li
                  key={`${report.date}-${idx}`}
                  className="border-b border-border/50 pb-2 last:border-0"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                        <span className="tabular-nums">{report.date}</span>
                        <span>·</span>
                        <span>{report.institution}</span>
                        {report.analyst && (
                          <>
                            <span>·</span>
                            <span>{report.analyst}</span>
                          </>
                        )}
                      </div>
                      <div className="mt-0.5 text-sm">{report.title}</div>
                    </div>
                    <div className="flex shrink-0 flex-col items-end gap-1">
                      {report.rating && (
                        <span
                          className={cn(
                            "rounded px-1.5 py-0.5 text-[10px] font-medium",
                            ratingClass(report.rating),
                          )}
                        >
                          {report.rating}
                        </span>
                      )}
                      {report.target_price !== null && (
                        <span className="text-[11px] tabular-nums text-muted-foreground">
                          → {report.target_price} {report.price_currency}
                        </span>
                      )}
                      {report.url && (
                        <a
                          href={report.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:text-foreground"
                          title="打开研报原文"
                        >
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ol>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}
