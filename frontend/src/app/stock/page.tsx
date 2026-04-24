/**
 * /stock —— 个股分析模块入口页.
 *
 * Day 5：占位（输入框 + 空 workspace 提示）；Day 6 接 backend
 *   /api/v1/stock/{ticker}/overview，写入 workspaceStore，渲染 3 张卡片.
 */

import { WorkspaceCanvas } from "@/components/WorkspaceCanvas";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function StockPage() {
  return (
    <WorkspaceCanvas
      emptyHint={
        <div className="space-y-3">
          <div className="text-sm font-medium text-foreground">个股分析</div>
          <div>
            输入 A 股 6 位代码（如 <code className="rounded bg-muted px-1.5 py-0.5">600519</code>）
            或美股 ticker（<code className="rounded bg-muted px-1.5 py-0.5">AAPL</code>），
            agent 会拉财务 / 公告 / 研报评级三张卡到这里。
          </div>
          <div className="text-[11px] text-muted-foreground/70">
            v0.1 Day 5 壳 · TickerInput / 数据流接通在 Day 6
          </div>
        </div>
      }
    >
      {/* Day 5 占位：放一个待对接的输入条（disabled） */}
      <div className="mb-4 flex items-center gap-2">
        <Input
          placeholder="600519 / AAPL ..."
          className="max-w-xs"
          disabled
        />
        <Button disabled>分析</Button>
        <span className="text-[11px] text-muted-foreground">
          Day 6 接通后启用
        </span>
      </div>
    </WorkspaceCanvas>
  );
}
