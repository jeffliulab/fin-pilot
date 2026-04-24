/**
 * Workspace state types —— v0.1 in-memory（zustand），v0.4 持久化 SQLite.
 */

import type { CompanyCard } from "./stock";

export type WorkspaceStatus = "idle" | "loading" | "ready" | "error";

export type Workspace = {
  status: WorkspaceStatus;
  ticker: string | null;
  market: "A" | "US" | null;
  cards: CompanyCard[];
  errorMessage: string | null;
};
