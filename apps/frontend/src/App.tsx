import { useState, type FormEvent } from "react";
import { critique, parseImprovedCode, type FindingsReport } from "./api/orchestrator";
import { AnalysisShell } from "./components/AnalysisShell.tsx";
import type { Page } from "./components/types";

export default function App() {
  const [page, setPage] = useState<Page>("analyze");
  const [input, setInput] = useState("");
  const [report, setReport] = useState<FindingsReport | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setApiError(null);
    setReport(null);
    try {
      const response = await critique(input);
      setReport(response);
    } catch (error) {
      setApiError(error instanceof Error ? error.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  const payload = report ? parseImprovedCode(report.improved_code) : null;
  const fixedCode = payload?.final_code ?? null;

  return (
    <AnalysisShell
      page={page}
      setPage={setPage}
      input={input}
      setInput={setInput}
      fixedCode={fixedCode}
      loading={loading}
      onSubmit={onSubmit}
      apiError={apiError}
      report={report}
      payload={payload}
    />
  );
}
