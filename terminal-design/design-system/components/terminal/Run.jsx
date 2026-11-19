import React from "react";
/** A tool call on the rail: → then the tool name bold, the argument muted. */
export function Run({ tool, arg }) {
  return (
    <div style={{ minHeight: "var(--term-line)" }}>
      <span style={{ color: "var(--term-rule)" }}>│</span> <span style={{ color: "var(--voice-machine)" }}>→</span> <b>{tool}</b>{arg ? <span style={{ color: "var(--voice-machine)" }}> {arg}</span> : null}
    </div>
  );
}
