---
id: gotcha-approvals
version: 4
title: Approving what a model wants to do
applies_to: ["cortex", "cli"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-28
source: ds-next build, 2026-10-16; rule-cli and ds-next reviews, 2026-10-26
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
5. **The model never invents an answer; code still suggests what it knows.** Pre-fill what
   follows from context: owner from `git config user.name`, a name given on the command line
   (`/new python cli my-tool`), a scaffold's defaults. Leave a field blank, and required, only
   when nothing gives it, like a purpose. A rebuild read this rule as "suggest nothing" and left
   the name blank too.
6. **Clearing a session clears its approvals** ("always" grants, pending drafts).
7. **A verdict is a report, not an action.** Tools that only report back to your code, such as
   `review_verdict`, run without asking and are never compared with the form. A rebuild wired
   its verdict tool through the draft approval, so it asked "Allow?" for its own review and
   showed every field as changed.
8. **Reads inside the project do not ask; reads outside it do.** Cortex asks permission for its
   own `Read`, `Glob` and `Grep`. Inside the working directory, allow them without a prompt; a
   read outside it (`~/.ssh`, `/etc`, a `..` pattern) still asks, so a person sees the model
   reach out. Commands, writes and edits always ask. Accepted code: [[block-cortex-session]].

9. **No settings file approves or runs anything on its own.** A cloned repo's hooks ran in a
   session: Claude Code ran `.claude/settings.json` hooks, and Cortex Code ran the hooks in both
   `.cortex/settings.json` and `.claude/settings.json` on the first prompt, with nothing asked. An
   allow rule in the person's own Claude settings ran a command without the approval callback being
   called. For Claude, pass `settings='{"disableAllHooks": true}'` and a `PreToolUse` callback that
   answers "ask" for every tool but Claude Code's own reads. Cortex has no switch that works
   ([[gotcha-cortex-sdk]] rule 12): before a session in a repo whose settings define hooks, show every
   hook's command whole and ask. (ds-next local-001; rule-cli, now ds-code, local-015 to local-017.)
10. **Draw control characters; never pass them through.** A dialog that prints a command as the
   model wrote it lets escape codes in it style the terminal: SGR "conceal" hid part of a command
   in the approval. Turn C0 control characters other than tab and newline into Unicode control
   pictures (`␛`) before drawing anything a model or a repo wrote. (rule-cli local-013.)

## Check

- Tests: concurrent requests never overlap; a 4,000-character command reaches the prompt whole;
  `"", "", "n"` denies after three asks.
- Tests, offline with the real Claude Code and a stand-in API: a repo's hook does not run, and a
  command the person's settings allow still asks. A command holding `\x1b[8m` shows `␛[8m`.
- Accepted code: [[block-approver]].
