---
id: block-confined-write
version: 1
title: Confined file writes
module: confined
requires: []
tags: ["python"]
owner: ckoenigs
status: proposed
date: 2026-10-16
---

# Confined file writes

Write files under a destination and nowhere else: no `..`, no absolute paths, no symbolic links on the way.

## API

`inside(dest, rel) -> Path` · `write_tree(dest, {rel: text})` checks every path before writing any · `create_new(folder, stem, text)` never overwrites (stem-2.md, stem-3.md ...).

## Why it is shaped this way

[[gotcha-confined-writes]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-confined-write` from a ds-next session copies `confined.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
