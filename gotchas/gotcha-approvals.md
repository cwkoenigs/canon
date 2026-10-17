---
id: gotcha-approvals
version: 2
title: Approving what a model wants to do
applies_to: ["cortex", "cli"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: ds-next build, 2026-10-16
---

# Approving what a model wants to do

## Rules

1. **Only an explicit answer approves.** `y`, `a` (always this session) or `n`; Enter alone asks
   again. A default of yes approved writes nobody chose.
2. **Show the whole request.** Truncating at 1,500 characters let a long command hide its
   destructive tail.
3. **One question at a time.** Cortex can request parallel tool calls; two prompts on one
   terminal send an answer to the wrong one. Serialize with a lock.
4. **A form submission approves exactly what was submitted.** When the model's call differs in
   any field, show the change and ask. Without this the model once replaced a vague purpose with
   its own invented example and it was written into the repo.
5. **The model never invents an answer.** Offer a suggestion only when it follows from what the
   user gave; a purpose or schema it made up is not a suggestion.
6. **Clearing a session clears its approvals** ("always" grants, pending drafts).
7. **A verdict is a report, not an action.** Tools that only report back to your code, such as
   `review_verdict`, run without asking and are never compared with the form. A rebuild wired
   its verdict tool through the draft approval, so it asked "Allow?" for its own review and
   showed every field as changed.

## Check

- Tests: concurrent requests never overlap; a 4,000-character command reaches the prompt whole;
  `"", "", "n"` denies after three asks.
- Accepted code: [[block-approver]].
