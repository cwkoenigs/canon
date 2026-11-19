import React from "react";
/** One terminal row, exactly one line tall. Use for anything the other primitives don't cover. */
export function Line({ children, color, style }) {
  return <div style={{ minHeight: "var(--term-line)", color: color ? "var(--term-" + color + ")" : undefined, ...style }}>{children || " "}</div>;
}
