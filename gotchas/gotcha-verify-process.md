---
id: gotcha-verify-process
version: 2
title: How to build so the result can be trusted
applies_to: ["*"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# How to build so the result can be trusted

## Rules

1. **Check the newest releases before pinning a dependency,** and look past the obvious package
   name: the supported Cortex SDK was a different package published three days earlier.
2. **Probe the real tool before designing around it.** The allowlist, the permission payload and
   the dropped error flag were each discovered only by a live call.
3. **Drive the real interaction,** not just unit tests: the interview's UX problems and the
   invented-purpose bug appeared only when the flow was used as a person would.
4. **Prove each new test by breaking it:** restore the old code, watch the test fail, restore
   the fix. (See [[testing]].)
5. **Get an outside review and loop until the findings stop being real.** Nine rounds found 37
   defects, the worst (a repo-deleting docs build) in round seven.
6. **Never `cd dir && rm -rf *`:** create a fresh directory for each run instead.
7. **"It exited" is not "it exited cleanly".** A crash also ends the process: a check that /exit
   leaves passed while /exit printed a traceback. Check exit status and scan output for tracebacks.
8. **Write down a lesson before it costs twice.** The task-group crash was found in the rebuild
   and repeated in ds-next the same hour, because it was remembered and not yet written.
