---
id: block-tui-widgets
version: 4
title: Inline picker and one-screen form
module: widgets
requires: ["prompt-toolkit>=3.0.40"]
tags: ["cli"]
owner: ckoenigs
status: accepted
date: 2026-10-19
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

v4: plain terminal colours (cyan for what is active) instead of a fixed hex accent, and a ◆ before titles, to match the team's updater.
