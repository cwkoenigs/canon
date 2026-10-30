---
id: block-markdown-pointers
version: 2
title: Markdown pointer reading
module: pointers
requires: []
tags: ["python"]
owner: ckoenigs
status: proposed
date: 2026-10-17
---

# Markdown pointer reading

Find `[[id]]` and `[[id@N]]` pointers in prose, ignoring every kind of code fence and span.

## Changes

v2: an unknown id is reported as it was written, pin included (`[[ghost@1]] is not in the canon`); v1 dropped the pin. Found by an independent judge, 2026-10-17.

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
