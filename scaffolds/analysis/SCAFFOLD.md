---
id: analysis
version: 1
title: Analysis
path: ["analysis"]
tags: ["python", "analysis"]
owner: ckoenigs
status: accepted
date: 2026-10-19
type: analysis
outputs: ["report"]
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# Analysis

One-off or exploratory work whose output is a report: a memo, charts, a feasibility study. Nothing
is deployed. The code that makes the report lives in `src/`, is tested, and writes under `reports/`,
which is committed so the result travels with the repo.

Declared output: `report`. The lightest type; use it unless something has to run on a schedule or
be served.
