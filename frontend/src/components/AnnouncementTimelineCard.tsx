/**
 * AnnouncementTimelineCard —— 渲染近 N 条公告的时间线.
 */

"use client";

import { ExternalLink } from "lucide-react";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ScrollArea } from "@/components/ui/scroll-area";
import { CitationLabel } from "@/components/CitationLabel";
import type { Citation } from "@/types/citation";
import type { AnnouncementTimelinePayload } from "@/types/stock";

type Props = {
  title: string;
  payload: AnnouncementTimelinePayload;
  citations: Citation[];
};

export function AnnouncementTimelineCard({ title, payload, citations }: Props) {
  const items = payload.items;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>{title}</span>
          {citations.map((c) => (
            <CitationLabel key={c.label + c.url} citation={c} />
          ))}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {items.length === 0 ? (
          <div className="py-6 text-center text-sm text-muted-foreground">
            暂无公告
          </div>
        ) : (
          <ScrollArea className="h-72">
            <ol className="space-y-2">
              {items.map((ann, idx) => (
                <li
                  key={`${ann.date}-${idx}`}
                  className="flex items-start gap-3 border-b border-border/50 pb-2 last:border-0"
                >
                  <div className="w-20 shrink-0 text-[11px] tabular-nums text-muted-foreground">
                    {ann.date}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                        {ann.type || "公告"}
                      </span>
                      {ann.url && (
                        <a
                          href={ann.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          title="打开原文"
                          className="text-muted-foreground hover:text-foreground"
                        >
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      )}
                    </div>
                    <div className="mt-1 text-sm">{ann.title}</div>
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
