import { useState } from "react";
import type { FindingsReport, FixReportEntry, ImprovedCodePayload } from "../api/orchestrator";
import { C, SEVERITY_BADGE, SEVERITY_LABEL } from "./theme";

function CategoryTag({ category }: { category: string }) {
  const map: Record<string, { bg: string; label: string }> = {
    "auto-fixed": { bg: "#28a745", label: "Auto-fixed" },
    "llm-fixed": { bg: "#0366d6", label: "LLM-fixed" },
    unfixable: { bg: "#e65100", label: "Cannot fix" },
  };
  const s = map[category] ?? { bg: "#888", label: category };
  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 10px",
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 700,
        letterSpacing: "0.03em",
        background: s.bg,
        color: "#fff",
        whiteSpace: "nowrap",
      }}
    >
      {s.label}
    </span>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 12,
        fontSize: 11,
        fontWeight: 700,
        background: SEVERITY_BADGE[severity] ?? "#888",
        color: "#fff",
        whiteSpace: "nowrap",
      }}
    >
      {SEVERITY_LABEL[severity] ?? severity.toUpperCase()}
    </span>
  );
}

function StatBadge({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div
      style={{
        padding: "10px 20px",
        background: "#fff",
        borderRadius: 8,
        border: `1px solid ${C.border}`,
        textAlign: "center",
        minWidth: 100,
        boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
      }}
    >
      <div style={{ fontSize: 24, fontWeight: 700, color }}>{value}</div>
      <div style={{ fontSize: 12, color: "#586069", marginTop: 2 }}>{label}</div>
    </div>
  );
}

function FixReportCards({ entries }: { entries: FixReportEntry[] }) {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {entries.map((e, i) => {
        const isUnfixable = e.category === "unfixable";
        const expanded = open === i;
        const detail = e.explanation || (isUnfixable ? e.cannot_fix_reason : "");
        return (
          <div
            key={i}
            style={{
              background: "#fff",
              border: `1px solid ${C.border}`,
              borderRadius: 6,
              overflow: "hidden",
            }}
          >
            <button
              onClick={() => detail && setOpen(expanded ? null : i)}
              style={{
                width: "100%",
                display: "grid",
                gridTemplateColumns: "auto auto 1fr auto auto",
                alignItems: "center",
                gap: "0 14px",
                padding: "11px 16px",
                background: "transparent",
                border: "none",
                cursor: detail ? "pointer" : "default",
                textAlign: "left",
              }}
            >
              <CategoryTag category={e.category} />
              <code style={{ fontWeight: 700, fontSize: 13, color: C.brand, whiteSpace: "nowrap" }}>
                {e.rule_code}
              </code>
              <span style={{ fontSize: 14, color: "#24292e" }}>{e.original_error}</span>
              <span
                style={{
                  fontSize: 13,
                  color: "#586069",
                  whiteSpace: "nowrap",
                  maxWidth: 420,
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {isUnfixable
                  ? e.cannot_fix_reason || "Requires external schema"
                  : e.fix_applied || "—"}
              </span>
              {detail && (
                <span style={{ color: "#888", fontSize: 12, userSelect: "none" }}>
                  {expanded ? "▲" : "▼"}
                </span>
              )}
            </button>
            {expanded && detail && (
              <div
                style={{
                  padding: "10px 16px 14px 20px",
                  borderTop: `1px solid ${C.border}`,
                  fontSize: 13,
                  lineHeight: 1.7,
                  color: "#444",
                  whiteSpace: "pre-wrap",
                }}
              >
                <span style={{ fontWeight: 600, color: C.brand }}>Explanation: </span>
                {detail}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function FindingRow({
  description,
  severity,
  suggested_fix,
}: {
  description: string;
  severity: string;
  suggested_fix: string | null;
}) {
  const [open, setOpen] = useState(false);
  return (
    <div
      style={{
        background: "#fff",
        border: `1px solid ${C.border}`,
        borderRadius: 6,
        marginBottom: 8,
        overflow: "hidden",
      }}
    >
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          padding: "10px 14px",
          background: "transparent",
          border: "none",
          cursor: suggested_fix ? "pointer" : "default",
          textAlign: "left",
          gap: 10,
        }}
      >
        <SeverityBadge severity={severity} />
        <span style={{ fontFamily: "monospace", fontSize: 13, color: "#24292e", flex: 1 }}>
          {description}
        </span>
        {suggested_fix && <span style={{ fontSize: 12, color: "#888" }}>{open ? "▲" : "▼"}</span>}
      </button>
      {open && suggested_fix && (
        <div
          style={{
            padding: "8px 16px 12px",
            borderTop: `1px solid ${C.border}`,
            fontSize: 13,
            color: "#444",
            lineHeight: 1.7,
            whiteSpace: "pre-wrap",
          }}
        >
          {suggested_fix}
        </div>
      )}
    </div>
  );
}

export function AnalysisResults({
  report,
  payload,
  input,
}: {
  report: FindingsReport;
  payload: ImprovedCodePayload | null;
  input: string;
}) {
  if (report.status !== "ok") return null;
  const fixedCode = payload?.final_code ?? null;
  const hasChanges = Boolean(payload && fixedCode !== input);
  return (
    <section style={{ marginTop: 28 }}>
      {report.findings.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16, fontWeight: 700, color: C.brand }}>
            Findings
            <span style={{ marginLeft: 10, fontSize: 13, fontWeight: 400, color: "#586069" }}>
              {report.findings.length} total
            </span>
          </h3>
          {report.findings.map((f, i) => (
            <FindingRow
              key={i}
              severity={f.severity}
              description={f.description}
              suggested_fix={f.suggested_fix}
            />
          ))}
        </div>
      )}

      {payload && (
        <div style={{ display: "flex", gap: 14, marginBottom: 28, flexWrap: "wrap" }}>
          <StatBadge label="Errors found" value={payload.initial_error_count} color="#586069" />
          <StatBadge label="Auto-fixed" value={payload.auto_fixed_count} color="#28a745" />
          <StatBadge
            label="LLM-fixed"
            value={payload.fix_report.filter((e) => e.category === "llm-fixed").length}
            color="#0366d6"
          />
          <StatBadge
            label="Cannot fix"
            value={payload.fix_report.filter((e) => e.category === "unfixable").length}
            color="#e65100"
          />
        </div>
      )}

      {payload && payload.fix_report.length > 0 && (
        <div style={{ marginBottom: 32 }}>
          <h3 style={{ margin: "0 0 14px", fontSize: 16, fontWeight: 700, color: C.brand }}>
            Fix Report
            <span style={{ marginLeft: 10, fontSize: 13, fontWeight: 400, color: "#586069" }}>
              {payload.fix_report.length} {payload.fix_report.length === 1 ? "entry" : "entries"} ·
              click row to expand explanation
            </span>
          </h3>
          <FixReportCards entries={payload.fix_report} />
        </div>
      )}

      {!payload && hasChanges && null}
    </section>
  );
}
