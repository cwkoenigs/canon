---
id: block-safe-outdir
version: 1
title: Safe build output directories
module: outdir
requires: []
tags: ["python", "docs"]
owner: ckoenigs
status: accepted
date: 2026-10-16
---

# Safe build output directories

Use before any builder that empties its output directory (Docusaurus does).

## API

`check_out_dir(out, protect) -> Path` refuses the repo, its parents, cwd, home, root and foreign files · `mark_out_dir(out)` after a successful build so it may be rebuilt into.

## Why it is shaped this way

[[gotcha-confined-writes]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-safe-outdir` from a ds-next session copies `outdir.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
