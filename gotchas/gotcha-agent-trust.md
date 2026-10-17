---
id: gotcha-agent-trust
version: 3
title: What to let the model decide
applies_to: ["cortex"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# What to let the model decide

## Rules

1. **Deterministic code writes files; the model reviews and calls tools.** Every project file
   came from a scaffold rendered by code, so a good model and a cheap one produce the same repo.
2. **Do not trust the model to pass complete arguments.** It sent `tags: ["python", "cli"]` and
   dropped `package`, losing a standard. Derive what the inputs imply in code and union it.
3. **Make the model fetch before it acts.** `scaffold_project` accepts only a scaffold this
   session fetched with `scaffold_get` (id, version and template hash), not just a version
   number it could guess.
4. **Keep what the user typed.** A tag the user typed survives even when another field that
   would also imply it is blank.
5. **Agents drop requirements silently.** Given a spec, a build agent skipped "Cortex reviews the
   draft" in /new and reported everything done. End every build by walking the spec item by item
   and saying which are done and how; never accept "all done" without that list.
6. **A review gates the action.** If the model's review raises a concern, or the review cannot run
   (an error, a cap, a timeout), do not go ahead: show why and let the person decide. A rebuild's
   /new created the repo anyway after its review failed.

## Check

- Accepted code: [[block-cortex-session]].
- Acceptance checks cover every spec item, including side effects such as a model turn.
