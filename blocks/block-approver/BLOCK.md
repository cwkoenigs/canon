---
id: block-approver
version: 1
title: Approvals for model tool calls
module: approver
requires: ["snowflake-cortex-agent-sdk==0.0.2"]
tags: ["cortex", "cli"]
owner: ckoenigs
status: retired
date: 2026-10-16
---

# Approvals for model tool calls

The can_use_tool callback for an interactive terminal: serialized, whole, explicit, draft-aware.

## API

`Approver(ask, prefix, draft_tool, ignore)` where `ask(title, detail) -> str` shows and reads; `.draft` pre-approves one exact call; `.reset()` · `describe_permission(tool_name, inp, prefix)` · `changed_keys`.

## Why it is shaped this way

[[gotcha-approvals]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-approver` from a ds-next session copies `approver.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
