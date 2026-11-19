import React from "react";
/** A flat outcome line with no rail — local commands: ✓ subject  detail. kind = ok | warn | err. */
export function Outcome({ kind = "ok", subject, detail }) {
  const g = { ok: "✓", warn: "⚠", err: "✗" }[kind];
  return (
    <div style={{ minHeight: "var(--term-line)" }}>
      <span style={{ color: "var(--term-" + kind + ")" }}>{g}</span> <b>{subject}</b>{detail ? <span style={{ color: "var(--term-muted)" }}>  {detail}</span> : null}
    </div>
  );
}
