/**
 * FinancialKPICard —— 渲染一组财务 KPI 行，每行：display_name + latest_value + sparkline.
 *
 * Sparkline 用 recharts 的 LineChart（无 axis、无 grid，纯趋势线）.
 */

"use client";

import { Line, LineChart, ResponsiveContainer, Tooltip } from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { CitationLabel } from "@/components/CitationLabel";
import type { Citation } from "@/types/citation";
import type { FinancialKPIPayload, KPISummaryItem } from "@/types/stock";

type Props = {
  title: string;
  payload: FinancialKPIPayload;
  citations: Citation[];
};

function formatValue(item: KPISummaryItem): string {
  if (item.latest_value === null) return "—";
  if (item.unit === "%") return `${item.latest_value.toFixed(2)} ${item.unit}`;
  // 大数转亿/百万显示
  const v = item.latest_value;
  if (Math.abs(v) >= 1e8) return `${(v / 1e8).toFixed(2)} 亿 ${item.unit}`;
  if (Math.abs(v) >= 1e6) return `${(v / 1e6).toFixed(2)} 百万 ${item.unit}`;
  return `${v.toLocaleString()} ${item.unit}`;
}

function Sparkline({ trend, periods }: { trend: (number | null)[]; periods: string[] }) {
  const data = trend.map((v, i) => ({ period: periods[i] ?? `t${i}`, value: v ?? 0 }));
  const allMissing = trend.every((v) => v === null);
  if (allMissing) {
    return <div className="h-8 w-24 text-[10px] text-muted-foreground">无数据</div>;
  }
  return (
    <div className="h-8 w-24">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <Line
            type="monotone"
            dataKey="value"
            stroke="hsl(var(--primary))"
            strokeWidth={1.5}
            dot={false}
            isAnimationActive={false}
          />
          <Tooltip
            contentStyle={{
              fontSize: "11px",
              padding: "4px 8px",
              borderRadius: "4px",
            }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export function FinancialKPICard({ title, payload, citations }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <span>{title}</span>
          {citations.map((c) => (
            <CitationLabel key={c.label + c.url} citation={c} />
          ))}
        </CardTitle>
        <CardDescription>币种：{payload.currency}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="divide-y divide-border">
          {payload.summary.map((item) => (
            <div
              key={item.name}
              className="flex items-center justify-between gap-4 py-2"
            >
              <div className="flex flex-col">
                <span className="text-sm font-medium">{item.display_name}</span>
                <span className="text-[11px] text-muted-foreground">
                  截至 {item.latest_period}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <Sparkline trend={item.trend} periods={item.trend_periods} />
                <div className="w-32 text-right text-sm tabular-nums">
                  {formatValue(item)}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
