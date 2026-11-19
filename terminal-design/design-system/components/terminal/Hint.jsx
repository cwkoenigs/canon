import React from "react";
/** A dim hint at col 3 — the fix after an error, the empty-input nudge. */
export function Hint({ children }) {
  return <div style={{ minHeight: "var(--term-line)", color: "var(--term-dim)" }}>  {children}</div>;
}
