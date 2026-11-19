import React from "react";
/** Closes a turn: ╰ then facts joined by · — "#1 · 3 tool calls · 15.2s · $0.0041". */
export function Footer({ facts = [] }) {
  return <div style={{ minHeight: "var(--term-line)" }}><span style={{ color: "var(--term-rule)" }}>╰</span> <span style={{ color: "var(--term-dim)" }}>{facts.join(" · ")}</span></div>;
}
