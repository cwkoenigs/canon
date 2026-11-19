import React from "react";
/** The one live line at the rail tip: ◐ step · 4s · ctrl-c interrupts. Reused in place, never stacked. */
export function Status({ step, secs = 0, frame = 0 }) {
  const frames = "◐◓◑◒";
  return (
    <div style={{ minHeight: "var(--term-line)" }}>
      <span style={{ color: "var(--voice-agent)" }}>{frames[frame % 4]}</span> <span style={{ color: "var(--voice-machine)" }}>{step}</span><span style={{ color: "var(--term-dim)" }}> · {secs}s · ctrl-c interrupts</span>
    </div>
  );
}
