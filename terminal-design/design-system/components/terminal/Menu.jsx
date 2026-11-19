import React from "react";
/** The slash-command menu under the prompt: name · description · kind. The focused row is the only filled row. */
export function Menu({ items = [], active = 0, total, hint = "↑↓ move · tab complete · enter run" }) {
  return (
    <div>
      {items.map((it, i) => {
        const on = i === active;
        return (
          <div key={it.name} style={{ display: "flex", minHeight: "var(--term-line)", background: on ? "var(--term-hl)" : "transparent" }}>
            <span style={{ width: "22ch", flex: "none", fontWeight: on ? 700 : 400 }}>  /{it.name}</span>
            <span style={{ flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", color: on ? "var(--term-text)" : "var(--term-muted)" }}>{it.desc}</span>
            <span style={{ flex: "none", color: on ? "var(--term-text)" : "var(--term-dim)", width: "10ch", textAlign: "right" }}>{it.kind}  </span>
          </div>
        );
      })}
      <div style={{ minHeight: "var(--term-line)", color: "var(--term-dim)" }}>  ▼  {active + 1}/{total || items.length} · {hint}</div>
    </div>
  );
}
