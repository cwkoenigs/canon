---
id: gotcha-terminal-ui
version: 3
title: Claude-Code-style terminals with prompt_toolkit and rich
applies_to: ["cli"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: ds-next build, 2026-10-16
---

# Claude-Code-style terminals with prompt_toolkit and rich

## Rules

1. **Never let a model interview one question at a time.** Each question is a model turn of
   seconds to a minute; eight questions took minutes and users stalled. Use a local form with
   every field on one screen and suggestions filled in, then one model turn to review.
2. **Empty Enter must do something visible.** Users press Enter to accept `[defaults]`. If a
   question is pending, Enter means "keep my answers as they are", never "accept your
   suggestion"; otherwise print a hint. Detect a question anywhere in the last lines, since
   models put an example after the question mark.
3. **Show the step and elapsed seconds while waiting** ("Running scaffold_get… 7s"). A spinner
   that only says "Working…" looks hung at 80 seconds.
4. **Hide the model's thinking.** Printing it reads as the tool talking about the user.
5. **Escape before `HTML(...)`.** prompt_toolkit parses it as XML: a folder named `R&D` crashes
   the toolbar. Use `html.escape` on every interpolated value.
6. **Turn off rich markup for data.** `Console(markup=False)` for anything printing user or
   canon text, or `[[testing]]` renders as `[]`.
7. **A prompt can remove your SIGINT handler.** Re-install the turn's Ctrl-C handler after any
   prompt opened during a turn.
8. **Testing in a pty:** set `PROMPT_TOOLKIT_NO_CPR=1`, and send whole characters, not bytes,
   or multi-byte characters arrive as stray control bytes.
9. **Never report an action that did not happen.** A rebuild printed "(empty reply sent)" on Enter
   while sending nothing. Say what was done, or do it.
10. **Fill every suggestion you can derive, and require in the form what the canon requires.**
   Owner comes from `git config user.name`; the form refuses a blank owner before any model turn.
   A rebuild left owner blank, so its review rightly refused a good draft: the person learned
   about a missing field one model turn late, from the model.

## Check

- Accepted code: [[block-tui-widgets]], [[block-claude-render]].
- The form opens with owner already filled in, and refuses to submit without one.
