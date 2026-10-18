---
id: python-package
version: 3
title: Python library package
path: ["python", "package"]
tags: ["python", "package"]
owner: ckoenigs
status: accepted
date: 2026-10-18
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# Python library package

An importable library: a src layout managed by uv, one passing test, ruff, and a GitLab CI job
that runs both. No console script. For something people run from a terminal, use `python-cli`.

v3: a new repo starts on `canon-lib`, the team's accepted code, as a dependency, with the canon and its index version recorded in `.ds/manifest.toml` and a note for agents in `AGENTS.md`.
