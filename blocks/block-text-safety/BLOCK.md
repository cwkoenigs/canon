---
id: block-text-safety
version: 1
title: Text safety for generated files
module: textsafe
requires: []
tags: ["python"]
owner: ckoenigs
status: accepted
date: 2026-10-16
---

# Text safety for generated files

Insert text a person typed into Python, TOML, YAML or Markdown without breaking or changing the file.

## API

`json_literal(s)` one literal valid in JSON/Python/TOML/YAML · `check_one_line(label, value)` · `check_project_name(name) -> package` · `fill_template(text, values)` one-pass {{key}} filling.

## Why it is shaped this way

[[gotcha-generated-text]]. Taken from ds-next after nine external review rounds; its tests are the
regression tests for those findings.

## Use

`block_add block-text-safety` from a ds-next session copies `textsafe.py` into the repo's package and its
tests into `tests/`, and records the version in `.ds/manifest.toml`. Do not edit the copy in
place: change the block in the canon and bump its version, and every repo using it sees the
update as pending.
