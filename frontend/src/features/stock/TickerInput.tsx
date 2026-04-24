/**
 * TickerInput —— 输入 ticker → 触发 workspaceStore.loadCompany.
 *
 * 接受：
 *   - A 股 6 位 code（如 600519、000858），自动剥 .SS / .SZ 后缀
 *   - 美股 alpha（如 AAPL、MSFT）
 */

"use client";

import { FormEvent, useState } from "react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  selectWorkspaceStatus,
  useWorkspaceStore,
} from "@/stores/workspaceStore";

const QUICK_PICKS = ["600519", "000858", "AAPL", "MSFT"];

export function TickerInput() {
  const [value, setValue] = useState("");
  const status = useWorkspaceStore(selectWorkspaceStatus);
  const loadCompany = useWorkspaceStore((s) => s.loadCompany);

  const isLoading = status === "loading";

  const submit = async (ticker: string) => {
    if (!ticker.trim()) return;
    await loadCompany(ticker);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    await submit(value);
  };

  return (
    <div className="flex flex-col gap-2">
      <form className="flex items-center gap-2" onSubmit={handleSubmit}>
        <Input
          name="ticker"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="600519 / AAPL ..."
          className="max-w-xs"
          disabled={isLoading}
          autoFocus
        />
        <Button type="submit" disabled={isLoading || !value.trim()}>
          {isLoading ? "分析中..." : "分析"}
        </Button>
      </form>
      <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
        <span>试试：</span>
        {QUICK_PICKS.map((t) => (
          <button
            key={t}
            type="button"
            disabled={isLoading}
            onClick={() => {
              setValue(t);
              submit(t);
            }}
            className="rounded bg-muted px-1.5 py-0.5 hover:bg-accent hover:text-accent-foreground disabled:opacity-50"
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
