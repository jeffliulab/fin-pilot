import { WorkspaceCanvas } from "@/components/WorkspaceCanvas";

export default function MarketPage() {
  return (
    <WorkspaceCanvas
      emptyHint={
        <div className="space-y-3">
          <div className="text-sm font-medium text-foreground">市场行情（Coming in v0.3）</div>
          <div>
            v0.3 上线：实时行情、资金面（北向 / 融券 / ETF 申赎）、情绪指标、异动监控
            （涨跌停 / 大单净流入）。
          </div>
          <div className="text-[11px] text-muted-foreground/70">
            v0.1 阶段先做个股；市场模块的产品形态已在 docs/PRD.md §3 / VERSIONS.md 锁定。
          </div>
        </div>
      }
    />
  );
}
