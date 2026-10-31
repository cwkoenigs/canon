---
id: operating-principles
version: 1
title: Operating Principles
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 1
---

# Operating Principles

### 1.1 Retired: Restricted-Data Gate

Removed in v1.1 (2026-09-25). The per-change data-classification question and the internal-only
review track were a carry-over from a project that handled regulated data; no current project
does. External review is always available. The only content rule that remains is in §9.2: secrets
never enter a diff, a log, or a review handoff, and `so-codex-review` refuses to transmit one it
finds. The section number is kept so older references resolve.

### 1.2 Correctness Before Cleverness

- Correct behavior includes data accuracy, privacy, security, accessibility, operational safety,
  cost control, and user trust.
- Prefer simple, observable, platform-native patterns over custom machinery.
- Before hand-rolling a workflow, check whether the platform, a shared internal package, or an
  existing skill already covers the need.

### 1.3 Make Work Visible and Auditable

- Material changes SHOULD create a decision log capturing the problem, assumptions, baseline
  gaps, plan, gates, and rollout evidence.
- Every production workflow SHOULD expose status, owner, inputs, outputs, failures, retry behavior,
  version, and where to look during an incident.
- Hidden manual steps are operational risk. Eliminate them, automate them, or document them in the
  runbook and rollout checklist.

### 1.4 Stable Checkpoints Beat Big Bang Changes

- Work SHOULD be split into phases that end in a stable state.
- A phase may temporarily go red while proving a regression test, but it MUST NOT end red.
- Every phase needs concrete exit criteria: commands, deployed observations, validation queries,
  screenshots, or data reconciliation.

### 1.5 Human Accountability Remains Mandatory

- Agents and LLMs MAY draft code, plans, documentation, tests, queries, summaries, and reviews.
- Agents MUST NOT be the final accountable owner of a production change.
- Human reviewers remain responsible for validating privacy, security, data semantics, business
  behavior, and rollout readiness.

