import React from "react";
import { Mascot } from "./Mascot.jsx";
const fill = "─".repeat(200);
/** The two-pane banner shown once at startup: mascot + word-mark left, facts right, the path on a footer row. */
export function Banner({ version = "0.1.0", tagline = "start, check and grow", facts = [], hints = [], path = "" }) {
  const e = "var(--edge-input)";
  const H = ({ children }) => <span style={{ color: e, flex: "none" }}>{children}</span>;
  const Fill = ({ cap }) => <span style={{ color: e, flex: 1, overflow: "hidden", whiteSpace: "nowrap" }}>{fill}</span>;
  return (
    <div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}>
        <H>┌─ </H><span style={{ color: "var(--term-brand)", fontWeight: 700 }}>ds-next</span><span style={{ color: "var(--term-dim)" }}> {version} </span>
        <span style={{ color: e, width: "calc(var(--term-banner-left) - 10ch - " + (version.length) + "ch)", overflow: "hidden", whiteSpace: "nowrap", flex: "none" }}>{fill}</span><H>┬</H><Fill /><H>┐</H>
      </div>
      <div style={{ display: "flex" }}>
        <div style={{ display: "flex", flexDirection: "column", flex: "none" }}>
          <span style={{ color: e }}>{Array.from({ length: 13 }).map((_, i) => <div key={i} style={{ minHeight: "var(--term-line)" }}>│</div>)}</span>
        </div>
        <div style={{ width: "var(--term-banner-left)", flex: "none" }}>
          <Mascot />
          <div style={{ minHeight: "var(--term-line)" }}> </div>
          <div style={{ minHeight: "var(--term-line)" }}>  <b>ds-next</b><span style={{ color: "var(--term-muted)" }}> · {tagline.split(" ").slice(0, 3).join(" ")}</span></div>
          <div style={{ minHeight: "var(--term-line)", color: "var(--term-muted)" }}>  {tagline.split(" ").slice(3).join(" ")}</div>
        </div>
        <div style={{ flex: "none" }}>{Array.from({ length: 13 }).map((_, i) => <div key={i} style={{ minHeight: "var(--term-line)", color: e }}>│ </div>)}</div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ minHeight: "var(--term-line)" }}> </div>
          {facts.map(([k, v]) => <div key={k} style={{ minHeight: "var(--term-line)", display: "flex" }}><span style={{ color: "var(--term-dim)", width: "calc(var(--term-label-w) + 3ch)", flex: "none" }}>  {k}</span><span>{v}</span></div>)}
          <div style={{ minHeight: "var(--term-line)" }}> </div>
          {hints.map((h, i) => <div key={i} style={{ minHeight: "var(--term-line)", color: "var(--term-dim)" }}>  {h}</div>)}
        </div>
        <div style={{ flex: "none" }}>{Array.from({ length: 13 }).map((_, i) => <div key={i} style={{ minHeight: "var(--term-line)", color: e }}>│</div>)}</div>
      </div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}>
        <H>├</H><span style={{ color: e, width: "var(--term-banner-left)", overflow: "hidden", whiteSpace: "nowrap", flex: "none" }}>{fill}</span><H>┴</H><Fill /><H>┤</H>
      </div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}><H>│</H><span style={{ flex: 1, textAlign: "center", color: "var(--term-muted)" }}>{path}</span><H>│</H></div>
      <div style={{ display: "flex", minHeight: "var(--term-line)" }}><H>└</H><Fill /><H>┘</H></div>
    </div>
  );
}
