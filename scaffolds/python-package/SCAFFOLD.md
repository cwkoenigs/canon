---
id: python-package
version: 2
title: Python library package
path: ["python", "package"]
tags: ["python", "package"]
owner: ckoenigs
status: accepted
date: 2026-10-16
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# Python library package

An importable library: a src layout managed by uv, one passing test, ruff, and a GitLab CI job
that runs both. No console script. For something people run from a terminal, use `python-cli`.
