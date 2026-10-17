---
id: block-cortex-session
version: 3
title: Cortex Code session with in-process tools
module: cortex_session
requires: ["snowflake-cortex-agent-sdk==0.0.2"]
tags: ["cortex"]
owner: ckoenigs
status: accepted
date: 2026-10-17
---

# Cortex Code session with in-process tools

Drive Cortex Code from Python with your own MCP tools, read-only ones auto-approved, the rest asked.

## API

`CortexSession(cwd, tools, server, read_only, ask, system_prompt, model, connection, effort)` with `turn(prompt, idle_timeout=None)` (async iterator of SDK messages; raises `TurnStalled` after a silent stream), `interrupt()`, `set_effort()`, `close()`, `reset()` · `text_result(s)`, `error_result(s)` (ERROR: prefix).

Approvals: `read_only` MCP tools and Cortex's own reads (`Read`, `Glob`, `Grep`) inside `cwd` run
without asking; a read outside `cwd`, and every command, write and edit, goes to `ask`.

## Why it is shaped this way

[[gotcha-cortex-sdk]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-cortex-session` from a ds-next session copies `cortex_session.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
