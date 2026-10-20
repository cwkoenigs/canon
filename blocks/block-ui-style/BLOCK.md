---
id: block-ui-style
version: 4
title: Terminal design system tokens
module: ui_style
requires: ["rich>=13"]
tags: ["cli", "terminal"]
owner: ckoenigs
status: accepted
date: 2026-10-20
---

# Terminal design system tokens

The one module a terminal prints through, so every team CLI reads the same way ([[terminal-design]]):

- **Colour roles**, twelve of them (`text`, `muted`, `dim`, `rule`, `accent`, `strong`, `brand`,
  `ok`, `warn`, `err`, `band`, `key`, `surface`, `hl`), each with a dark and a light truecolor value
  from the Industry steel ramp and a fixed ANSI-16 fallback. `theme()` gives a rich Theme,
  `pt_style()` the same roles for prompt_toolkit, `console()` a Console with the theme.
  `DS_THEME=light` picks the light ramp; no `COLORTERM` falls back to ANSI; `color=False` drops
  colour and keeps the glyphs, for logs and CI.
- **Glyphs** on `G`: `›` you, `●` the agent, `→` a tool call, `⎿` its result, `│` the rail,
  `╰` the turn's footer, `✓ ⚠ ✗` outcomes, `❯` the focused row, `┄` a fold. One meaning each.
- **Grid**: `INDENT` 2, `RESULT_INDENT` 4, `LABEL_W` 12, designed at 80 columns (`width()`).
- **Line builders**: `agent_lines`, `run`, `result`, `outcome`, `footer`, `status_label`,
  `labelled`, `hint`, `error`; **frames**: `frame` (a frame means "needs you"), `banner`, `toolbar`.

Taken from ds-next's `ui_style.py`; `block-tui-widgets` v4 imports it as `from . import ui_style`.

v2: `session_rule()` for a static rule above a one-line prompt (a multi-line prompt message redraws badly); banner chrome in the bright accent with a visible edge.

v3: a mark for the banner's left pane.

v4: the mark is the team mascot, `MASCOT` and `mascot_lines()`, a dog (brand) and a cat (strong) with their arms around each other, drawn in half-blocks; `banner()` shows it unless `art` is given. Roles `eye`, `on_brand`, `on_strong`, `on_eye` for it.
