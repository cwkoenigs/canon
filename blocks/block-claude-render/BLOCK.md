---
id: block-claude-render
version: 1
title: Claude-Code-style message rendering
module: render
requires: ["snowflake-cortex-agent-sdk==0.0.2", "rich>=13"]
tags: ["cortex", "cli"]
owner: ckoenigs
status: retired
date: 2026-10-16
---

# Claude-Code-style message rendering

Print SDK messages as ⏺ text, ⏺ Tool(arg), ⎿ results; errors red; thinking hidden; a live status line.

## API

`render(console, msg, state, prefix)` updates state['step'|'asked'|'model'] · `status_label(state, started)` · `asks(text)` · `bullet(body)`.

## Why it is shaped this way

[[gotcha-terminal-ui]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-claude-render` from a ds-next session copies `render.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
