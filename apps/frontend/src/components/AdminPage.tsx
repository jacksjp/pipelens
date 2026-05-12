import { C } from "./theme";

export function AdminPage() {
  const card: React.CSSProperties = {
    background: "#fff",
    border: `1px solid ${C.border}`,
    borderRadius: 10,
    padding: 24,
    boxShadow: "0 1px 4px rgba(0,0,0,0.06)",
  };
  const sections = [
    {
      title: "Agent Configuration",
      desc: "Manage lint agent settings, model selection, retries and timeouts.",
    },
    {
      title: "MCP Server",
      desc: "View MCP server status, registered tools and connection health.",
    },
    { title: "Audit Logs", desc: "Browse historical analysis runs, errors and fix reports." },
    { title: "Users & Roles", desc: "Manage team access, permissions and API key rotation." },
  ];
  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: C.brand }}>Admin</h2>
        <p style={{ margin: "6px 0 0", color: "#586069", fontSize: 14 }}>
          System configuration and management — coming soon.
        </p>
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
          gap: 16,
        }}
      >
        {sections.map((s) => (
          <div key={s.title} style={card}>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.brand, marginBottom: 8 }}>
              {s.title}
            </div>
            <div style={{ fontSize: 13, color: "#586069", lineHeight: 1.6 }}>{s.desc}</div>
            <div
              style={{
                marginTop: 14,
                display: "inline-block",
                padding: "4px 12px",
                background: C.surface,
                border: `1px solid ${C.border}`,
                borderRadius: 20,
                fontSize: 11,
                color: "#888",
                fontWeight: 600,
              }}
            >
              Placeholder
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
