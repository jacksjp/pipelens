import { useState } from "react";
import type { Page } from "./types";
import { C } from "./theme";

export function SideNavigator({ page, setPage }: { page: Page; setPage: (page: Page) => void }) {
  const [collapsed, setCollapsed] = useState(false);

  const itemStyle = (active: boolean): React.CSSProperties => ({
    display: "flex",
    alignItems: "center",
    justifyContent: collapsed ? "center" : "flex-start",
    gap: collapsed ? 0 : 12,
    width: "100%",
    padding: collapsed ? "12px 10px" : "12px 14px",
    border: "none",
    borderRadius: 10,
    background: active ? "rgba(13,71,161,0.12)" : "transparent",
    color: active ? C.brand : "#394b59",
    cursor: "pointer",
    textAlign: "left",
    fontWeight: active ? 700 : 600,
    fontSize: 14,
    whiteSpace: "nowrap",
  });

  return (
    <aside
      style={{
        width: collapsed ? 84 : 250,
        transition: "width 0.18s ease",
        borderRight: `1px solid ${C.border}`,
        background: "#fff",
        display: "flex",
        flexDirection: "column",
        padding: 14,
        gap: 14,
        position: "sticky",
        top: 64,
        height: "calc(100vh - 64px)",
        overflow: "hidden",
      }}
    >
      <button
        type="button"
        onClick={() => setCollapsed((v) => !v)}
        style={{
          alignSelf: collapsed ? "center" : "flex-end",
          border: `1px solid ${C.border}`,
          background: C.surface,
          borderRadius: 10,
          width: collapsed ? 44 : 34,
          height: collapsed ? 44 : 34,
          cursor: "pointer",
          fontWeight: 700,
          color: C.brand,
          display: "grid",
          placeItems: "center",
          boxShadow: "0 1px 4px rgba(0, 0, 0, 0.08)",
        }}
        aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
      >
        <span
          aria-hidden="true"
          style={{
            display: "inline-flex",
            flexDirection: "column",
            gap: 3,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <span
            style={{
              width: collapsed ? 17 : 14,
              height: 2,
              background: C.brand,
              borderRadius: 999,
              transition: "width 0.18s ease",
            }}
          />
          <span
            style={{
              width: collapsed ? 17 : 14,
              height: 2,
              background: C.brand,
              borderRadius: 999,
              transition: "width 0.18s ease",
            }}
          />
          <span
            style={{
              width: collapsed ? 17 : 14,
              height: 2,
              background: C.brand,
              borderRadius: 999,
              transition: "width 0.18s ease",
            }}
          />
        </span>
      </button>

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <div
          style={{
            fontSize: 11,
            fontWeight: 700,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            color: "#6b7785",
          }}
        >
          {collapsed ? "" : "Workspace"}
        </div>
        <button
          type="button"
          onClick={() => setPage("analyze")}
          style={itemStyle(page === "analyze")}
        >
          <span
            style={{ width: 26, textAlign: "center", fontSize: collapsed ? 24 : 19, lineHeight: 1 }}
          >
            ⌕
          </span>
          {!collapsed && <span>Analyze</span>}
        </button>
        <button type="button" onClick={() => setPage("admin")} style={itemStyle(page === "admin")}>
          <span
            style={{ width: 26, textAlign: "center", fontSize: collapsed ? 24 : 19, lineHeight: 1 }}
          >
            ⚙
          </span>
          {!collapsed && <span>Admin</span>}
        </button>
      </div>

      {!collapsed && (
        <div
          style={{
            marginTop: "auto",
            padding: 14,
            borderRadius: 12,
            background: C.surface,
            border: `1px solid ${C.border}`,
          }}
        >
          <div style={{ fontSize: 12, fontWeight: 700, color: C.brand, marginBottom: 6 }}>
            PipeLens
          </div>
          <div style={{ fontSize: 12, color: "#586069", lineHeight: 1.6 }}>
            Inspect code, trace lint findings, and keep the pipeline honest.
          </div>
        </div>
      )}
    </aside>
  );
}
