---
id: gotcha-agent-trust
version: 5
title: What to let the model decide
applies_to: ["cortex"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
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
6. **A review gates the action, with no override.** If the model's review raises a concern, or
   the review cannot run (an error, a cap, a timeout), do not go ahead: show why, and let the
   person fix the draft and submit again. There is no "create anyway". A rebuild's /new created
   the repo after its review failed; two later rebuilds read "let the person decide" as a y/n
   override, which brings the same hole back.
7. **Get the verdict as data, not prose.** Give the review a tool to answer with, such as
   `review_verdict(ok: bool, concerns: list[str])`, and gate on that call. Without a verdict call,
   treat the review as not approved. A rebuild decided "concern raised" by whether the reply
   ended in a question, so "the purpose is vague." with no question mark still created the repo.

## Check

- Accepted code: [[block-cortex-session]].
- Acceptance checks cover every spec item, including side effects such as a model turn.
- A draft the review must object to is refused, whatever words the review used.
