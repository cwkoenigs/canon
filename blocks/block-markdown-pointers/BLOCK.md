---
id: block-markdown-pointers
version: 1
title: Markdown [[pointer]] reading
module: pointers
requires: []
tags: ["python"]
owner: ckoenigs
status: accepted
date: 2026-10-16
---

# Markdown [[pointer]] reading

Find [[id]] and [[id@N]] pointers in prose, ignoring every kind of code fence and span.

## API

`mask_code(text)` · `pointers(text) -> [(id, pin)]` · `pointer_problems(text, {id: version}) -> [str]`.

## Why it is shaped this way

[[gotcha-validation]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-markdown-pointers` from a ds-next session copies `pointers.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
