import { PipeLensLogo } from "./PipeLensLogo";

export function HeaderBar() {
  return (
    <header
      style={{
        background: "linear-gradient(135deg, #0d47a1 0%, #1565c0 60%, #1976d2 100%)",
        boxShadow: "0 2px 8px rgba(0,0,0,0.18)",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}
    >
      <div
        style={{
          maxWidth: 1600,
          margin: "0 auto",
          padding: "0 24px",
          height: 64,
          display: "flex",
          alignItems: "center",
          gap: 14,
        }}
      >
        <PipeLensLogo size={38} />
        <div style={{ lineHeight: 1.05 }}>
          <div style={{ fontSize: 18, fontWeight: 800, color: "#fff", letterSpacing: "-0.02em" }}>
            PipeLens
          </div>
          <div
            style={{
              fontSize: 10,
              color: "rgba(255,255,255,0.65)",
              letterSpacing: "0.12em",
              textTransform: "uppercase",
            }}
          >
            Pipeline Lint Auditor
          </div>
        </div>
        <div
          style={{
            marginLeft: "auto",
            color: "rgba(255,255,255,0.65)",
            fontSize: 12,
            fontWeight: 600,
          }}
        >
          Ready for analysis
        </div>
      </div>
    </header>
  );
}
