---
id: streamlit-app
version: 1
title: Streamlit app
path: ["streamlit-app"]
tags: ["python", "package", "streamlit", "app"]
owner: ckoenigs
status: accepted
date: 2026-10-19
type: streamlit-app
outputs: ["dashboard"]
test_cmd: uv run pytest -q
lint_cmd: uv run ruff check .
---

# Streamlit app

An interactive dashboard. `app.py` is the Streamlit entry point and holds only layout; everything
that computes lives in `src/` where it is tested without Streamlit. Run locally with
`uv run streamlit run app.py`; deploying it to Snowflake is a later verb, not part of creation.

Declared output: `dashboard`. Use it when people need to explore; for a fixed set of charts a
Snowsight dashboard is lighter.
