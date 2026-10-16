---
id: block-git-hooks
version: 1
title: Git commands and hook installation
module: githooks
requires: []
tags: ["python"]
owner: ckoenigs
status: accepted
date: 2026-10-16
---

# Git commands and hook installation

Run git with failures surfaced, init a repo safely, and install a hook without losing an existing one.

## API

`git(repo, *args)` raises GitError · `init_own_repo(repo)` · `hook_script(marker, command, fallback)` shell-quoted, chains <name>.local, says when its tool is missing · `install_hook(repo, name, script, marker) -> problem | None`.

## Why it is shaped this way

[[gotcha-git-hooks]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-git-hooks` from a ds-next session copies `githooks.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
