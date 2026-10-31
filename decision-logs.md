---
id: decision-logs
version: 1
title: Decision Logs and Lineage
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 3
---

# Decision Logs and Lineage

Material work SHOULD create a durable decision log. Store it in the project repo, or in a central
decision-log directory when that is the stronger local convention. Whichever is chosen, record the
location once and use it consistently:

```text
docs/decisions/<YYYY-MM-DD>-<app-slug>-<slug>.md
docs/decisions/<YYYY-MM-DD>-<app-slug>-bug-<slug>.md
```

### 3.1 Decision Log Template

```markdown
# <Feature | Bug | Change>: <summary>
- Date: <YYYY-MM-DD>
- App/repo:
- Author:
- Owner:
- User-visible behavior changes: <none | list with sign-off>

## Phase & Gate Tracker
| # | Phase / Gate | State | Evidence / outcome |
|---|---|---|---|
| 1 | Discovery | [ ] | |
| G1 | Plan review | [ ] | |
| 2 | Implement with tests | [ ] | |
| G2 | Interim review | [ ] | |
| 3 | Dev observe | [ ] | |
| G3 | Pre-closeout review | [ ] | |
| 4 | Prod rollout + observe | [ ] | |
| 5 | Cleanup | [ ] | |

## Environments & Toolchain
- Local/dev:
- QA/stage:
- Production:
- Tests:
- Deploy:
- Validation surface:
- Execution identity / object owner:

## Baseline Scan
- [ ] <gap> - <suggested addition>

## Rollback / Remediation
- <step> -> <reverse action or forward fix>

## Phased Plan
<phase details>

## Decisions & Rationale
- <decision> - <why>
```

### 3.2 Bug-Specific Additions

Bug logs SHOULD also include:

- Symptom.
- Expected vs actual behavior.
- Regression window.
- Root cause location.
- Blast-radius scan and sibling occurrences.
- Regression test added.
- Whether bad data was written or users were misled.
- Backfill, correction, or notification decision.

