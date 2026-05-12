import type { FormEvent } from "react";
import { HeaderBar } from "./HeaderBar";
import { SideNavigator } from "./SideNavigator";
import { CodeWorkspace } from "./CodeWorkspace";
import { AnalysisResults } from "./AnalysisResults";
import { AdminPage } from "./AdminPage";
import type { FindingsReport, ImprovedCodePayload } from "../api/orchestrator";
import type { Page } from "./types";

export function AnalysisShell({
  page,
  setPage,
  input,
  setInput,
  fixedCode,
  loading,
  onSubmit,
  apiError,
  report,
  payload,
}: {
  page: Page;
  setPage: (page: Page) => void;
  input: string;
  setInput: (value: string) => void;
  fixedCode: string | null;
  loading: boolean;
  onSubmit: (event: FormEvent) => void;
  apiError: string | null;
  report: FindingsReport | null;
  payload: ImprovedCodePayload | null;
}) {
  return (
    <div
      style={{
        fontFamily: "system-ui,-apple-system,sans-serif",
        minHeight: "100vh",
        background: "#f4f6fb",
      }}
    >
      <HeaderBar />
      <div style={{ display: "flex", minHeight: "calc(100vh - 64px)" }}>
        <SideNavigator page={page} setPage={setPage} />
        <main style={{ flex: 1, minWidth: 0, padding: "28px 24px 60px", maxWidth: 1280 }}>
          {page === "admin" && <AdminPage />}
          {page === "analyze" && (
            <>
              <div style={{ marginBottom: 22 }}>
                <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: "#0d47a1" }}>
                  Code Analysis
                </h2>
                <p style={{ margin: "5px 0 0", color: "#586069", fontSize: 14 }}>
                  Paste SQL or Python code to lint, auto-fix, and explain every issue found.
                </p>
              </div>

              <CodeWorkspace
                input={input}
                setInput={setInput}
                fixedCode={fixedCode}
                originalCode={input}
                loading={loading}
                onSubmit={onSubmit}
              />

              {apiError && (
                <div
                  role="alert"
                  style={{
                    marginTop: 16,
                    padding: "12px 16px",
                    background: "#ffeef0",
                    border: "1px solid #f97583",
                    borderRadius: 6,
                    color: "#86181d",
                    fontSize: 14,
                  }}
                >
                  {apiError}
                </div>
              )}

              {report?.status === "error" && (
                <div
                  style={{
                    marginTop: 16,
                    padding: "12px 16px",
                    background: "#ffeef0",
                    border: "1px solid #f97583",
                    borderRadius: 6,
                  }}
                >
                  <strong style={{ color: "#86181d" }}>Agent error</strong>
                  <ul style={{ margin: "6px 0 0", paddingLeft: 20 }}>
                    {report.findings.map((f, i) => (
                      <li key={i} style={{ color: "#86181d", fontSize: 13 }}>
                        {f.description}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {report?.status === "ok" && (
                <AnalysisResults report={report} payload={payload} input={input} />
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}
