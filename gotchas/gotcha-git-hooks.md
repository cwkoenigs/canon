---
id: gotcha-git-hooks
version: 1
title: Installing git hooks and running git
applies_to: ["python"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# Installing git hooks and running git

## Rules

1. **Ask git where hooks live:** `git rev-parse --git-path hooks`. `core.hooksPath` can move
   them, possibly outside the repo; do not write there, report it.
2. **Keep someone else's hook.** If a pre-push hook already exists and is not yours (a git
   template, a team's), move it to `pre-push.local` and run it first from yours, passing its exit
   code through. Never drop it.
3. **Shell-quote anything you embed** in a hook script with `shlex.quote`. JSON quoting does not
   stop `$(...)` or backticks in a path from running.
4. **A hook that cannot run its check must say so** on stderr, not exit 0 in silence; and it
   should fall back to the absolute path of the tool that installed it.
5. **Git failures are failures.** Check every git command's exit code. After `git init`, confirm
   `git rev-parse --show-toplevel` is the new repo before `git add`, or a failed init stages
   files into a parent repository.

## Check

- Tests: an existing foreign hook still runs and can still stop the push; `core.hooksPath`
  outside the repo is reported; a path containing `$(touch x)` never runs.
- Accepted code: [[block-git-hooks]].
