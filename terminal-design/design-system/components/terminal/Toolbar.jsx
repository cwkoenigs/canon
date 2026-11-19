import React from "react";
/** The one quiet band under the prompt: facts left, context right. Changes at most once per prompt. */
export function Toolbar({ left, right }) {
  return (
    <div style={{ display: "flex", minHeight: "var(--term-line)", background: "var(--term-surface)", color: "var(--term-dim)" }}>
      <span>  {left}</span><span style={{ flex: 1 }}></span><span>{right}  </span>
    </div>
  );
}
