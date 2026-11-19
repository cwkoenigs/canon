import React from "react";
/** ✗ what failed, red only on that line, then the fix in dim. */
export function ErrorLine({ children, fix }) {
  return (
    <div>
      <div style={{ minHeight: "var(--term-line)" }}><span style={{ color: "var(--term-err)" }}>✗</span> {children}</div>
      {fix ? <div style={{ minHeight: "var(--term-line)", color: "var(--term-dim)" }}>  {fix}</div> : null}
    </div>
  );
}
