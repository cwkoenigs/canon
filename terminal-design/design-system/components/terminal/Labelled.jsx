import React from "react";
/** label + value on the shared 12-column label grid. Used by forms, /status and the approval diff. */
export function Labelled({ label, required = false, focused = false, indent = 2, children }) {
  return (
    <div style={{ minHeight: "var(--term-line)", display: "flex" }}>
      <span style={{ whiteSpace: "pre" }}>{" ".repeat(indent)}</span>
      <span style={{ color: focused ? "var(--voice-you)" : "var(--term-dim)", fontWeight: focused ? 700 : 400, width: "calc(var(--term-label-w) + 2ch)", flex: "none" }}>
        {focused ? "❯ " : "  "}{label}
      </span>
      <span style={{ color: required ? "var(--term-dim)" : "transparent", flex: "none", width: "2ch" }}>{required ? "* " : "  "}</span>
      <span style={{ flex: 1, minWidth: 0 }}>{children}</span>
    </div>
  );
}
