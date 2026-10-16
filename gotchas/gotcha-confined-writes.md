---
id: gotcha-confined-writes
version: 1
title: Writes that stay where they were asked to go
applies_to: ["python"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# Writes that stay where they were asked to go

A tool that writes a repo, a capture or a site must never write, or delete, anywhere else.

## Rules

1. **Refuse absolute paths and `..`** in any relative path that came from data (a template
   list, an index, a model's tool call).
2. **Refuse symbolic links on the way**, not just at the end: `dest/.git -> other/.git` or
   `.ds -> elsewhere` redirects every write beneath it. Check each component, then confirm the
   resolved target is still under the destination.
3. **Check every path before writing any**, so a refusal leaves nothing half-written.
4. **Never empty a directory you did not create.** Docusaurus empties `--out-dir` before it
   builds: `ds-next docs --out .` inside a repo deleted the repo, `.git` included. Build only into
   a new or empty directory, or one carrying a marker your own previous build wrote, and refuse
   any directory that is, or contains, the repo, the working directory, home, or the root.
5. **Never overwrite a file you did not write** (a capture with the same title, an existing hook):
   create with `open(path, "x")` and pick a new name, or move the old one aside.

## Check

- Tests for `../x`, `/abs`, a symlinked destination, a symlinked `.git`, and `--out .`.
- Accepted code: [[block-confined-write]], [[block-safe-outdir]].
