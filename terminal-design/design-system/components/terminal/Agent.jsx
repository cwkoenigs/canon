import React from "react";
/** The agent's words. ● on the first line, │ on the rest; pass lines as an array to control wrapping. */
export function Agent({ lines = [], children }) {
  const rows = lines.length ? lines : [children];
  return (
    <div>
      {rows.map((l, i) => (
        <div key={i} style={{ minHeight: "var(--term-line)" }}>
          <span style={{ color: i === 0 ? "var(--voice-agent)" : "var(--term-rule)" }}>{i === 0 ? "●" : "│"}</span> {l}
        </div>
      ))}
    </div>
  );
}
