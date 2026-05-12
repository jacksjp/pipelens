export const C = {
  removed: { bg: "#ffeef0", border: "#f97583", text: "#86181d" },
  added: { bg: "#e6ffed", border: "#85e89d", text: "#176f2c" },
  unfixable: { bg: "#fff8e1", border: "#ffc107", text: "#6d4c00" },
  equal: { bg: "#ffffff", text: "#24292e" },
  empty: { bg: "#fafafa", text: "transparent" },
  info: { bg: "#e6ffed", text: "#176f2c", badge: "#28a745" },
  medium: { bg: "#fff8e1", text: "#6d4c00", badge: "#f9a825" },
  high: { bg: "#ffeef0", text: "#86181d", badge: "#d73a49" },
  critical: { bg: "#ffeef0", text: "#86181d", badge: "#d73a49" },
  low: { bg: "#f1f8ff", text: "#032f62", badge: "#0366d6" },
  brand: "#0d47a1",
  surface: "#f6f8fa",
  border: "#e1e4e8",
};

export const SEVERITY_LABEL: Record<string, string> = {
  info: "Fixed",
  low: "Low",
  medium: "Warning",
  high: "High",
  critical: "Critical",
};

export const SEVERITY_BADGE: Record<string, string> = {
  info: C.info.badge,
  low: C.low.badge,
  medium: C.medium.badge,
  high: C.high.badge,
  critical: C.critical.badge,
};
