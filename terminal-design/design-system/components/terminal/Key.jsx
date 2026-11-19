import React from "react";
/** The one filled key in a key line: " Enter submit ". variant = key (accent) | band (brand). */
export function Key({ children, variant = "key" }) {
  const bg = variant === "band" ? "var(--band-bg)" : "var(--key-bg)";
  const fg = variant === "band" ? "var(--band-fg)" : "var(--key-fg)";
  return <span style={{ background: bg, color: fg, fontWeight: 700 }}> {children} </span>;
}
