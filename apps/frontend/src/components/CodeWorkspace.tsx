import { useState, type FormEvent } from "react";
import { C } from "./theme";

function computeChangedLines(original: string, fixed: string): Set<number> {
  const originalLines = original.split("\n");
  const fixedLines = fixed.split("\n");
  const changed = new Set<number>();
  const maxLines = Math.max(originalLines.length, fixedLines.length);

  for (let index = 0; index < maxLines; index++) {
    if (originalLines[index] !== fixedLines[index]) {
      changed.add(index);
    }
  }

  return changed;
}

export function CodeWorkspace({
  input,
  setInput,
  fixedCode,
  originalCode,
  loading,
  onSubmit,
}: {
  input: string;
  setInput: (value: string) => void;
  fixedCode: string | null;
  originalCode: string;
  loading: boolean;
  onSubmit: (event: FormEvent) => void;
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    if (!fixedCode) return;
    try {
      await navigator.clipboard.writeText(fixedCode);
      setCopied(true);
      setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  const panelHead: React.CSSProperties = {
    padding: "8px 14px",
    background: C.surface,
    borderBottom: `1px solid ${C.border}`,
    fontWeight: 600,
    fontSize: 12,
    color: "#586069",
    letterSpacing: "0.03em",
    textTransform: "uppercase",
  };
  const panelBox: React.CSSProperties = {
    flex: 1,
    border: `1px solid ${C.border}`,
    borderRadius: 8,
    overflow: "hidden",
    display: "flex",
    flexDirection: "column",
    background: "#fff",
    boxShadow: "0 1px 4px rgba(0,0,0,0.07)",
  };
  const changedLines = fixedCode ? computeChangedLines(originalCode, fixedCode) : new Set<number>();

  return (
    <form onSubmit={onSubmit} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div
        style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 1fr)", gap: 16 }}
      >
        <div style={panelBox}>
          <div style={panelHead}>Your Code</div>
          <textarea
            id="code-input"
            rows={13}
            wrap="off"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste SQL or Python code here…"
            style={{
              flex: 1,
              fontFamily: "'Fira Code', 'Cascadia Code', monospace",
              fontSize: 13,
              padding: 14,
              border: "none",
              outline: "none",
              resize: "vertical",
              lineHeight: 1.6,
              color: "#24292e",
              background: "transparent",
              whiteSpace: "pre",
              overflowX: "auto",
            }}
          />
        </div>

        <div style={{ ...panelBox, background: "#fff" }}>
          <div
            style={{
              ...panelHead,
              background: C.surface,
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              gap: 10,
            }}
          >
            <span>{fixedCode ? "Fixed Code" : "Fixed Code (pending analysis)"}</span>
            <button
              type="button"
              onClick={handleCopy}
              disabled={!fixedCode}
              style={{
                border: `1px solid ${C.border}`,
                background: fixedCode ? "#fff" : "#f5f7fa",
                color: fixedCode ? C.brand : "#9aa4b2",
                borderRadius: 6,
                fontSize: 12,
                fontWeight: 700,
                padding: "4px 10px",
                cursor: fixedCode ? "pointer" : "not-allowed",
                letterSpacing: "0.02em",
                textTransform: "none",
              }}
              aria-label="Copy fixed code"
              title={fixedCode ? "Copy fixed code" : "No fixed code to copy"}
            >
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
          {fixedCode ? (
            <pre
              style={{
                flex: 1,
                margin: 0,
                padding: 14,
                fontFamily: "'Fira Code', 'Cascadia Code', monospace",
                fontSize: 13,
                lineHeight: 1.7,
                color: "#24292e",
                overflowX: "auto",
                whiteSpace: "pre",
              }}
            >
              {fixedCode.split("\n").map((line, index) => {
                const highlighted = changedLines.has(index);
                return (
                  <div
                    key={index}
                    style={{
                      display: "block",
                      whiteSpace: "pre",
                      background: highlighted ? "#e6ffed" : "transparent",
                      color: highlighted ? "#176f2c" : "#24292e",
                      borderLeft: highlighted ? "3px solid #28a745" : "3px solid transparent",
                      paddingLeft: 10,
                      marginLeft: -10,
                    }}
                  >
                    {line || " "}
                  </div>
                );
              })}
            </pre>
          ) : (
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "#bbb",
                fontSize: 13,
                fontStyle: "italic",
                padding: 20,
                minHeight: 280,
              }}
            >
              {loading ? "Analyzing…" : "Fixed code will appear here after analysis"}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            padding: "9px 28px",
            background: loading ? "#ccc" : C.brand,
            color: "#fff",
            border: "none",
            borderRadius: 6,
            cursor: loading ? "default" : "pointer",
            fontWeight: 700,
            fontSize: 14,
            letterSpacing: "0.02em",
            boxShadow: loading ? "none" : "0 2px 6px rgba(13,71,161,0.25)",
          }}
        >
          {loading ? "Analyzing…" : "Analyze"}
        </button>
        {loading && (
          <span style={{ fontSize: 13, color: "#586069" }}>Running pipeline linting…</span>
        )}
      </div>
    </form>
  );
}
