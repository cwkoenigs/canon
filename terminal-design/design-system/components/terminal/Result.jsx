import React from "react";
/** First line of a tool result at col 5, folded: ⎿ text  ┄ N more lines · ctrl-o. error turns it red. */
export function Result({ children, more = 0, error = false, foldKey = "ctrl-o" }) {
  return (
    <div style={{ minHeight: "var(--term-line)" }}>
      <span style={{ color: "var(--term-rule)" }}>│</span>   <span style={{ color: error ? "var(--term-err)" : "var(--term-dim)" }}>⎿ {children}</span>
      {more > 0 ? <span style={{ color: "var(--term-dim)" }}>  ┄ {more} more lines · {foldKey}</span> : null}
    </div>
  );
}
