import { WorkspaceCanvas } from "@/components/WorkspaceCanvas";

export default function IndustryPage() {
  return (
    <WorkspaceCanvas
      emptyHint={
        <div className="space-y-3">
          <div className="text-sm font-medium text-foreground">行业分析（Coming in v0.2）</div>
          <div>
            v0.2 上线：宏观 / 行业 / 政策 / 重大事件 + Hebbia 式 5×8 Generative Grid（5
            公司 × 8 问题批量出表）。
          </div>
          <div className="text-[11px] text-muted-foreground/70">
            v0.1 阶段先做个股；行业模块的产品形态已在 docs/PRD.md §3 / VERSIONS.md 锁定。
          </div>
        </div>
      }
    />
  );
}
