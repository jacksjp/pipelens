import axios from "axios";

const baseURL = import.meta.env.VITE_ORCHESTRATOR_URL ?? "/api";

export const orchestrator = axios.create({ baseURL });

export interface Finding {
  severity: "info" | "low" | "medium" | "high" | "critical";
  description: string;
  original_snippet: string | null;
  suggested_fix: string | null;
}

export interface FindingsReport {
  status: string;
  agent: string;
  findings: Finding[];
  improved_code: string | null;
}

export async function critique(input: string): Promise<FindingsReport> {
  const res = await orchestrator.post<FindingsReport>("/critique", { input });
  return res.data;
}

export async function health(): Promise<{ status: string }> {
  const res = await orchestrator.get<{ status: string }>("/health");
  return res.data;
}
