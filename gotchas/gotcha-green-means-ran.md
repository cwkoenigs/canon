---
id: gotcha-green-means-ran
version: 1
title: A green check proves the job finished, not that it did the work
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: ringneck-pork Oinkr Health release, 2026-10-17
---

# A green check proves the job finished, not that it did the work

## The pattern

CI and deploy statuses report that a process exited cleanly. A process can exit cleanly having
skipped itself, run against a stale configuration, or deployed without the inputs it needed.
Reading "success" as "it worked" hid three different failures in one afternoon.

## Evidence

- **The review that never reviewed.** `anthropics/claude-code-action` refuses to run when a PR's
  workflow file differs from the default branch's copy — and reports *success* when it refuses.
  Three "successful" runs on PR #11 reviewed nothing; so did the only green run in the repo's
  history (Oct 15), which was the PR that added the workflow. The real runs had failed since the
  start on `401 OAuth access token is invalid`, hidden behind `is_error: true` and a default that
  suppresses the response text.
- **The rerun that ran old code.** `gh run rerun` re-executes the workflow *at the original
  commit*. A rerun after fixing the token still used the pre-fix workflow (wrong model, output
  hidden), so its result said nothing about the fix.
- **The preview that deployed without its data.** A Vercel PR preview built green and served
  pages, but preview deployments do not inherit branch-scoped env vars: every API call answered
  "No Snowflake credentials found" and the gate was off. The check said READY.

## What to do about it

1. **Trust evidence of work, not the exit code.** For an agent step: a result with
   `num_turns > 1` and non-zero cost, and the artifact it was supposed to produce (the comment,
   the file). For a deploy: a probe of the thing that depends on configuration (`/api/version`
   plus one call that touches the database), not the build status.
2. **Know the two-second failure.** A run that fails ~2 s after init with `total_cost_usd: 0`
   never reached the model: it is a credential or account problem, not the code. Stop reading the
   diff and check the secret.
3. **Capture secrets by hand and test before storing.** A regex over `setup-token` output stored
   a truncated token. The fix was: copy the whole token, prove it with
   `CLAUDE_CODE_OAUTH_TOKEN=… claude -p 'Reply OK'`, then `gh secret set`.
4. **Trigger a fresh run after a config change; do not rerun.** Push a commit (an empty one is
   fine) so the workflow, secrets and model are the current ones.
5. **Change a workflow on the default branch first**, or the PR that changes it will be skipped
   with a green mark. Turn `show_full_output` on there when a failure is opaque, and off again
   once it is understood.
