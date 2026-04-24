/**
 * workspaceStore —— v0.1 in-memory zustand store for the company main page.
 *
 * v0.4 升级到持久化（SQLite + 多 workspace 切换）；当前刷新即丢.
 *
 * 用法：
 *   const { status, cards, loadCompany } = useWorkspaceStore();
 *   await loadCompany("600519");
 */

import { create } from "zustand";

import { getCompanyOverview } from "@/services/stockApi";
import { ApiError } from "@/services/apiClient";
import type { CompanyCard, Market } from "@/types/stock";
import type { Workspace, WorkspaceStatus } from "@/types/workspace";

type WorkspaceActions = {
  loadCompany: (ticker: string) => Promise<void>;
  reset: () => void;
};

const INITIAL_STATE: Workspace = {
  status: "idle",
  ticker: null,
  market: null,
  cards: [],
  errorMessage: null,
};

export const useWorkspaceStore = create<Workspace & WorkspaceActions>(
  (set) => ({
    ...INITIAL_STATE,

    loadCompany: async (ticker: string) => {
      const trimmed = ticker.trim();
      if (!trimmed) return;

      set({
        status: "loading" as WorkspaceStatus,
        ticker: trimmed,
        cards: [],
        errorMessage: null,
      });

      try {
        const resp = await getCompanyOverview(trimmed);
        set({
          status: "ready",
          ticker: resp.ticker,
          market: resp.market,
          cards: resp.cards,
          errorMessage: null,
        });
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.detail
            : `未知错误：${(err as Error).message}`;
        set({
          status: "error",
          errorMessage: message,
          cards: [],
        });
      }
    },

    reset: () => set(INITIAL_STATE),
  }),
);

/** Selector helpers —— 在组件里用，避免不必要的 re-render. */
export const selectWorkspaceCards = (s: Workspace): CompanyCard[] => s.cards;
export const selectWorkspaceStatus = (s: Workspace): WorkspaceStatus => s.status;
export const selectWorkspaceTicker = (s: Workspace): string | null => s.ticker;
export const selectWorkspaceMarket = (s: Workspace): Market | null => s.market;
export const selectWorkspaceError = (s: Workspace): string | null =>
  s.errorMessage;
