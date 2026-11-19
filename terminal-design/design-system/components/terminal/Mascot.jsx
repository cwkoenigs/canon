import React from "react";
const GRID = ["............................","................C......C....","....DDDDDD......CC....CC....","..DDDDDDDDDD....CCCCCCCCC...",".DDDDDDDDDDDD..CCCCCCCCCCC..",".DDDDDDDDDDDD..CCCCCCCCCCC..",".DDDkkDDDkkDD..CCkkCCCCkkC..",".DDDkkDDDkkDD..CCkkCCCCkkC..",".DDDDDDDDDDDD..CCCCCCCCCCC..",".DDDDDkkDDDDD..CCCCCkkCCCC..",".DD.DDDDDD.DD...CCCCCCCCC...","....DDDDDD........CCCCC.....","..CCCDDDDDDDDDCCCCCCCCCDDD..","..CDDDDDDDDDDDCCCCCCCCCCCD..","..DDDDDDDDDDD..CCCCCCCCCC...","..DDDDDDDDDDD..CCCCCCCCCC.C.","..DDDDDDDDDDD..CCCCCCCCCCCC.","..DDDDDDDDDDD..CCCCCCCCCC...","..DDD..DDD.....CCC..CCC.....","..DDD..DDD.....CCC..CCC....."];
const INK = { D: "var(--term-brand)", C: "var(--term-accent-strong)", k: "var(--term-bg)", ".": "transparent" };
/** The dog and the cat, arms around each other. 28×20 pixels; each row is two pixel rows (▀▄█ in a real terminal). */
export function Mascot() {
  const rows = [];
  for (let r = 0; r < GRID.length; r += 2) {
    const cells = [];
    for (let c = 0; c < GRID[r].length; c++) {
      const t = GRID[r][c], b = GRID[r + 1][c];
      cells.push(t === "." && b === "." ? <span key={c}> </span>
        : <span key={c} style={{ display: "inline-block", width: "1ch", height: "var(--term-line)", verticalAlign: "top", background: "linear-gradient(" + INK[t] + " 50%," + INK[b] + " 50%)" }}> </span>);
    }
    rows.push(<div key={r} style={{ minHeight: "var(--term-line)" }}>{cells}</div>);
  }
  return <div>{rows}</div>;
}
