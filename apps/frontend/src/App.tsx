import { useState } from "react";
import { critique, type FindingsReport } from "./api/orchestrator";

export default function App() {
  const [input, setInput] = useState("");
  const [report, setReport] = useState<FindingsReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await critique(input);
      setReport(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", maxWidth: 800 }}>
      <h1>Code Critic</h1>
      <form onSubmit={onSubmit}>
        <label htmlFor="sql-input" style={{ display: "block", marginBottom: 8 }}>
          SQL query or stored procedure name:
        </label>
        <textarea
          id="sql-input"
          rows={6}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          style={{ width: "100%", fontFamily: "monospace" }}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ marginTop: 8 }}>
          {loading ? "Analyzing…" : "Critique"}
        </button>
      </form>

      {error && <p role="alert" style={{ color: "crimson" }}>{error}</p>}

      {report && (
        <section aria-label="Findings report" style={{ marginTop: "2rem" }}>
          <h2>Report from {report.agent}</h2>
          <p>Status: {report.status}</p>
          <p>{report.findings.length} finding(s)</p>
        </section>
      )}
    </main>
  );
}
