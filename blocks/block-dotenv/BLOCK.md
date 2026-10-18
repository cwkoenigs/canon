---
id: block-dotenv
version: 1
title: Dotenv file parsing
module: dotenv
requires: []
tags: ["python"]
owner: ckoenigs
status: proposed
date: 2026-10-17
---

# Dotenv file parsing

Dotenv file parsing

## Why it is shaped this way

Promoted on the blind judge's tests (96/96); served as proposed until the owner reviews it (adr-001).

Promoted from a real repo (envcheck seed build 3 (Haiku; blind judge 96/96)) on 2026-10-17: its judge-validated tests are the block's
tests. [[gotcha-generated-text]]

## Use

`code_search`/`code_add` from a ds-next session, or `from canon_lib.dotenv import ...` with canon-lib.
Do not edit the copy in place: change the block in the canon and bump its version.
