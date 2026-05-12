/// <reference types="vite/client" />
import axios from "axios";

const baseURL = import.meta.env.VITE_ORCHESTRATOR_URL ?? "/api";

export const orchestrator = axios.create({ baseURL });

export interface Finding {
  severity: "info" | "low" | "medium" | "high" | "critical";
  description: string;
  original_snippet: string | null;
  suggested_fix: string | null;
}

export interface FixReportEntry {
  rule_code: string;
  original_error: string;
  fix_applied: string;
  explanation: string;
  fixable: boolean;
  cannot_fix_reason: string;
  category: "auto-fixed" | "llm-fixed" | "unfixable";
}

export interface ImprovedCodePayload {
  final_code: string;
  fix_report: FixReportEntry[];
  initial_error_count: number;
  auto_fixed_count: number;
  remaining_count: number;
}

export interface FindingsReport {
  status: string;
  agent: string;
  findings: Finding[];
  improved_code: string | null;
}

export function parseImprovedCode(raw: string | null): ImprovedCodePayload | null {
  if (!raw) return null;
  try {
    return JSON.parse(raw) as ImprovedCodePayload;
  } catch {
    return null;
  }
}

export async function critique(input: string): Promise<FindingsReport> {
  const res = await orchestrator.post<FindingsReport>("/critique", { input });
  return res.data;
}

export async function health(): Promise<{ status: string }> {
  const res = await orchestrator.get<{ status: string }>("/health");
  return res.data;
}
