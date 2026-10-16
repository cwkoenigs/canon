---
id: python-cli
version: 1
title: Python command-line tool
path: ["python", "cli"]
tags: ["python", "package", "cli"]
owner: ckoenigs
status: accepted
date: 2026-10-16
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# Python command-line tool

The shape ds-cli itself has: a typer app installed as a console script, a src layout managed by
uv, one passing test, ruff, and a GitLab CI job that runs both. A CLI ships as a package, so it
is tagged `package` as well as `cli` and inherits the package standards.

Use it for anything people run from a terminal. For a library imported by other code, use
`python-package`.
