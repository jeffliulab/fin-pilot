/**
 * CitationLabel —— 显示 [N] 上标，点击触发 drawer (Day 8 接 citationStore).
 *
 * v0.1 Day 6：仅渲染样式 + onclick 占位（console.log）；Day 8 接 citationStore.open(citation).
 */

"use client";

import type { Citation } from "@/types/citation";
import { cn } from "@/lib/utils";

type Props = {
  citation: Citation;
  className?: string;
};

export function CitationLabel({ citation, className }: Props) {
  return (
    <button
      type="button"
      onClick={() => {
        // Day 8: useCitationStore.getState().open(citation)
        // v0.1 Day 6 的占位：直接打开 url 让用户能验证链路
        if (citation.url) {
          window.open(citation.url, "_blank", "noopener,noreferrer");
        } else {
          // eslint-disable-next-line no-console
          console.log("citation has no URL:", citation);
        }
      }}
      title={citation.source_name}
      className={cn(
        "ml-0.5 inline-flex items-center justify-center rounded-md bg-accent px-1.5 py-0.5 text-[10px] font-medium text-accent-foreground hover:bg-accent/70 hover:underline",
        className,
      )}
    >
      {citation.label}
    </button>
  );
}
