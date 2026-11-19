import React from "react";
const fill = "─".repeat(200);
/** A square frame. A frame means "needs you": kind = input (dim edge) | approval (warn edge).
 *  onRail prefixes every line with │ so it sits inside a turn. keys renders in the bottom rule. */
export function Frame({ title, kind = "input", keys, onRail = false, children }) {
  const edge = kind === "approval" ? "var(--edge-approval)" : "var(--edge-input)";
  const rail = onRail ? <span style={{ color: "var(--term-rule)" }}>│ </span> : null;
  const Rule = ({ left, content, right }) => (
    <div style={{ display: "flex", minHeight: "var(--term-line)" }}>
      {rail}<span style={{ color: edge, flex: "none" }}>{left}</span>{content ? <span style={{ flex: "none" }}>{content}</span> : null}
      <span style={{ color: edge, flex: 1, overflow: "hidden", whiteSpace: "nowrap" }}>{content ? " " : ""}{fill}</span><span style={{ color: edge, flex: "none" }}>{right}</span>
    </div>
  );
  return (
    <div>
      <Rule left={title ? "┌─ " : "┌"} content={title} right="┐" />
      {React.Children.map(children, (c, i) => (
        <div key={i} style={{ display: "flex", minHeight: "var(--term-line)" }}>
          {rail}<span style={{ color: edge, flex: "none" }}>│ </span><span style={{ flex: 1, minWidth: 0, overflow: "hidden" }}>{c}</span><span style={{ color: edge, flex: "none" }}> │</span>
        </div>
      ))}
      <Rule left={keys ? "└─ " : "└"} content={keys} right="┘" />
    </div>
  );
}
