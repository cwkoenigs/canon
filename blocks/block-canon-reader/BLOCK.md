---
id: block-canon-reader
version: 1
title: Read the canon's index and standards
module: canonreader
requires: []
tags: ["python"]
owner: ckoenigs
status: retired
date: 2026-10-17
---

# Read the canon's index and standards

Find the canon, load its `index.json`, and read a standard's text. Written after a rebuild that
could reach the canon only through MCP tools had to guess the index's layout.

## The index

`index.json` has three lists. Every entry has `id`, `version` (int), `title`, `status`
(`accepted` or `proposed`) and `owner`.

- `standards`: also `applies_to` (tag patterns, `*` for all), `path` (the file, relative to the
  canon), `kind` (`standard`, or `gotcha` for a lesson). The file starts with `---` front matter.
- `scaffolds`: also `path` (menu path, e.g. `["python", "cli"]`), `tags`, `defaults`, `dir`,
  `files` and `hash`. Render one with [[block-scaffold-render]].
- `blocks`: also `module`, `requires`, `test_requires`, `tags`, `dir`, `tests` and `hash`.

## API

`canon_root(env=None) -> Path`: `$DS_CANON`, else `~/Developer/canon`.
`Canon.load(root) -> Canon`, which never raises: a missing or broken index gives empty lists and
a line in `.problems`. `.standards`, `.scaffolds`, `.blocks` (lists of dicts, as in the index),
`.counts()` (`{"standards": n, "scaffolds": n, "blocks": n}`), `.accepted(kind)`,
`.find(kind, id)`, `.read_standard(id) -> str` (body without front matter; raises `KeyError` for
an unknown id and `ValueError` for a path outside the canon), `.versions()` (`{id: version}`
across all three), `.applicable(tags)` (standards whose `applies_to` matches), and `.refresh()`
(reloads when `index.json` changed on disk).

## Why it is shaped this way

[[gotcha-validation]] (never raise on bad input in a check), [[gotcha-confined-writes]] (paths
from data stay inside their root).
