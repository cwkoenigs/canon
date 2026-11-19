import React from "react";
/** The terminal pane: mono type, 80-column width, dark or light ramp. Everything else renders inside it. */
export function Term({ theme = "dark", cols = 80, children, style }) {
  return (
    <div data-theme={theme} style={{
      fontFamily: "var(--font-mono)", fontSize: "var(--term-font-size)", lineHeight: "var(--term-line)",
      whiteSpace: "pre", background: "var(--term-bg)", color: "var(--term-text)", padding: "var(--term-pane-pad)",
      width: "calc(" + cols + "ch + 36px)", boxSizing: "border-box", ...style }}>
      {children}
    </div>
  );
}
