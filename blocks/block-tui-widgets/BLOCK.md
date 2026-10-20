---
id: block-tui-widgets
version: 7
title: Inline picker and one-screen form
module: widgets
requires: ["prompt-toolkit>=3.0.40"]
tags: ["cli"]
owner: ckoenigs
status: accepted
date: 2026-10-20
---

# Inline picker and one-screen form

Claude-style choices and forms drawn under the prompt: ↑↓/digits to pick, every form field on one screen.

## API

`await pick(title, [(value, label, desc)]) -> value | None` · `await form(title, [Field(key, label, value, hint, required)], footer(values) -> str, validate(values) -> (key, msg) | None) -> dict | None`.

## Why it is shaped this way

[[gotcha-terminal-ui]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-tui-widgets` from a ds-next session copies `widgets.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.

v2: a `Field` may carry `choices`; the form shows it as `‹ label ›` and ←/→ or space cycles it, so a pick and a form fit on one screen.

v3: a `Field` may carry `example` (shown while empty), `normalize` (rewrites as typed) and `check` (a live red line; Enter refuses while it fires).

v4: draws with the terminal design system's roles and glyphs (`from . import ui_style`, so add `block-ui-style` first): the form sits in a square frame, labels on the 12-column grid, the submit key as the one filled band.

v5: the picker sits in a frame too; `form(width=...)`; the key line shares one helper; a live rule break is marked ✗.

v6: `prompt_line`, a closed frame around the line being typed (session tag on the top rule, completion menu below, history on ↑↓), and `prompt_frame` to reprint it with the accepted text.

v7: `prompt_line` is Cortex Code's box: the terminal's width, rounded corners, the `/` menu a row under it, the status band after; `resize_safe` on every Application, which answers a terminal resize by clearing the screen and scrollback, calling the host's `repaint` and drawing fresh (VS Code's terminal re-wraps rows on a column change and moved every redraw under a ghost of the last); framed widgets held to the grid inside a filler VSplit, since the root container is always written full width.
