/**
 * LeftMenu —— 左栏：3 个核心模块 + 历史 workspace 占位.
 *
 * 个股 module v0.1 完整实现；行业 / 市场是禁用占位（v0.2/0.3 上线，详见
 * docs/PRD.md §3 + VERSIONS.md）。
 *
 * 用 Next.js Link 做客户端导航，<usePathname> 高亮当前选中项。
 */

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LineChart, Building2, Activity, Sparkles } from "lucide-react";

import { cn } from "@/lib/utils";

type ModuleEntry = {
  href: string;
  label: string;
  icon: typeof LineChart;
  enabled: boolean;
  comingIn?: string;
};

const MODULES: ModuleEntry[] = [
  { href: "/stock", label: "个股分析", icon: LineChart, enabled: true },
  { href: "/industry", label: "行业分析", icon: Building2, enabled: false, comingIn: "v0.2" },
  { href: "/market", label: "市场行情", icon: Activity, enabled: false, comingIn: "v0.3" },
];

export function LeftMenu() {
  const pathname = usePathname();

  return (
    <div className="flex h-full flex-col gap-1 px-3 py-4">
      {/* Logo / 项目名 */}
      <div className="mb-4 flex items-center gap-2 px-2">
        <Sparkles className="h-5 w-5 text-primary" />
        <div>
          <div className="text-sm font-semibold leading-tight">FinPilot</div>
          <div className="text-[10px] uppercase tracking-wider text-muted-foreground">
            v0.1 · dev
          </div>
        </div>
      </div>

      {/* 模块菜单 */}
      <div className="mb-4">
        <div className="px-2 py-1 text-[10px] uppercase tracking-wider text-muted-foreground">
          模块
        </div>
        <nav className="flex flex-col gap-0.5">
          {MODULES.map((m) => {
            const isActive = pathname?.startsWith(m.href);
            return m.enabled ? (
              <Link
                key={m.href}
                href={m.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                  isActive
                    ? "bg-accent text-accent-foreground"
                    : "text-muted-foreground hover:bg-accent/50 hover:text-foreground",
                )}
              >
                <m.icon className="h-4 w-4" />
                <span>{m.label}</span>
              </Link>
            ) : (
              <div
                key={m.href}
                title={`${m.comingIn} 上线`}
                className="flex cursor-not-allowed items-center justify-between gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground/50"
              >
                <span className="flex items-center gap-2">
                  <m.icon className="h-4 w-4" />
                  <span>{m.label}</span>
                </span>
                <span className="rounded bg-muted px-1.5 py-0.5 text-[10px] font-medium text-muted-foreground">
                  {m.comingIn}
                </span>
              </div>
            );
          })}
        </nav>
      </div>

      {/* 历史会话占位（v0.4 工作区持久化才真用得上） */}
      <div className="mt-2">
        <div className="px-2 py-1 text-[10px] uppercase tracking-wider text-muted-foreground">
          历史会话
        </div>
        <div className="px-2 py-2 text-xs text-muted-foreground/70">
          v0.4 持久化 SQLite 上线后开放
        </div>
      </div>
    </div>
  );
}
