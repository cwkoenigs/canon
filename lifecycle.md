---
id: lifecycle
version: 1
title: Project Lifecycle Standards
applies_to: ["*"]
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 4
---

# Project Lifecycle Standards

### 4.1 Definition of Ready

A task is ready when these are known or explicitly deferred:

- Goal and non-goals.
- Expected user or system behavior.
- Inputs, outputs, and contracts.
- Acceptance criteria.
- Test expectations.
- Failure behavior.
- Logging and operational visibility.
- Deployment target and owner.
- Rollback or remediation path.
- Constraints for agents and automated tools.

Exploratory tasks may proceed with fewer details, but MUST be labeled exploratory and SHOULD NOT
ship directly to production.

### 4.2 Definition of Done

A change is done only when:

- Acceptance criteria are met.
- Tests and required checks pass or a waiver is documented.
- Security, privacy, and data impacts are reviewed.
- User-visible behavior changes are approved.
- Data contracts and semantic definitions are updated if affected.
- Operational behavior is observable.
- Rollback/remediation is documented.
- No secrets, debug output, temporary code, or untracked manual steps remain.
- Deployment was verified by real behavior, not only by a successful command.

### 4.3 Repositories

Production repositories SHOULD include:

- `README.md` with purpose, setup, architecture overview, and common commands.
- `AGENTS.md` when agents are expected to work in the repo.
- `RUNBOOK.md` for operational workflows.
- Test, lint, typecheck, and build commands.
- Deploy instructions and environment mapping.
- Security/privacy notes.
- Data dictionary, semantic model, or catalog link for data projects.
- Decision logs, ADRs, or a link to the central decision-log directory.

