import React from "react";
const fill = "─".repeat(200);
/** The framed prompt: a top rule carrying the session tag, then │ › and the input with a block cursor. */
export function Prompt({ tag = "New session", value = "", closed = true }) {
  const e = "var(--edge-input)";
  return (
    <div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}>
        <span style={{ color: e, flex: "none" }}>┌</span><span style={{ color: e, flex: 1, overflow: "hidden", whiteSpace: "nowrap" }}>{fill}</span>
        <span style={{ background: "var(--band-bg)", color: "var(--band-fg)", fontWeight: 700, flex: "none" }}> {tag} </span><span style={{ color: e, flex: "none" }}>─┐</span>
      </div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}>
        <span style={{ color: e, flex: "none" }}>│ </span><span style={{ color: "var(--voice-you)", fontWeight: 700 }}>›</span> <span>{value}</span><span style={{ background: "var(--term-cursor)", color: "var(--term-cursor-fg)" }}> </span>
        <span style={{ flex: 1 }}></span>{closed ? <span style={{ color: e, flex: "none" }}>│</span> : null}
      </div>
      {closed ? <div style={{ display: "flex", minHeight: "var(--term-line)" }}><span style={{ color: e, flex: "none" }}>└</span><span style={{ color: e, flex: 1, overflow: "hidden", whiteSpace: "nowrap" }}>{fill}</span><span style={{ color: e, flex: "none" }}>┘</span></div> : null}
    </div>
  );
}
