---
id: ml-pipeline
version: 1
title: ML pipeline
path: ["ml-pipeline"]
tags: ["python", "package", "ml", "pipeline", "snowflake"]
owner: ckoenigs
status: accepted
date: 2026-10-19
type: ml-pipeline
outputs: ["model", "features"]
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# ML pipeline

Features in, a trained model out. `features.py` turns source rows into feature rows and
`train.py` fits a model on them; both are plain functions with tests, so the pipeline is proven
before anything runs in Snowflake. Where the features and model are published (a project schema in
dev, FEATURE_STORE and MODELS in prod) is decided by the deploy and promote verbs, not here.

Declared outputs: `model`, `features`.
