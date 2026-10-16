---
id: block-scaffold-render
version: 1
title: Render an accepted canon scaffold
module: scaffoldrender
requires: []
tags: ["python"]
owner: ckoenigs
status: accepted
date: 2026-10-16
---

# Render an accepted canon scaffold

Turn a scaffold entry from the canon's index.json into `{repo path: text}`, ready for
`write_tree` from [[block-confined-write]]. Written after a rebuild reimplemented this and
rewrote `dot-` anywhere in a path and skipped the stale-template check.

## API

`render_scaffold(canon_root, entry, name, purpose, test_cmd=None, lint_cmd=None) -> dict[str, str]`
refuses a scaffold that is not accepted, whose templates no longer match the index hash, or
whose template paths are not plain relative paths. `__package__` in a path segment becomes the
package; a segment starting with `dot-` starts with `.` instead. Placeholders are filled in one
pass: `{{name}}`, `{{package}}`, and `{{purpose_json}}`, `{{test_cmd_json}}`, `{{lint_cmd_json}}`
as JSON string literals (raw `{{purpose}}`, `{{test_cmd}}`, `{{lint_cmd}}` for prose).
`scaffold_digest(canon_root, entry)` is the hash build_index.py writes.

## Why it is shaped this way

[[gotcha-generated-text]], [[gotcha-confined-writes]], [[gotcha-agent-trust]].
