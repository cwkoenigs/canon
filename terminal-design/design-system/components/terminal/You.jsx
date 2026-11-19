import React from "react";
/** What you typed, echoed in the transcript: › in accent-strong, then the line. */
export function You({ children }) {
  return <div style={{ minHeight: "var(--term-line)" }}><span style={{ color: "var(--voice-you)", fontWeight: 700 }}>›</span> {children}</div>;
}
