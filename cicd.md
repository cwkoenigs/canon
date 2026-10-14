---
id: cicd
version: 1
title: CI/CD and Release Management
applies_to: ["*"]
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 11
---

# CI/CD and Release Management

### 11.1 CI Minimum Gates

CI SHOULD run:

- Formatting check.
- Lint/static analysis.
- Type checks where applicable.
- Unit tests.
- Integration tests for changed boundaries.
- Security/dependency scans.
- Query or schema validation where applicable.
- LLM prompt/eval tests when prompt behavior changes.
- Documentation checks for required files.
- **Generated-artifact freshness** — if the repo generates committed files, CI MUST prove the
  committed copies match a fresh run of the generator.

**Enforce in CI what you would otherwise write down as "remember to."** A documented manual step is
a known drift hazard; a CI check is a guarantee. Prefer deriving lists from the filesystem over
maintaining parallel hand-written registries.

Run the repo's own checks locally before pushing.

### 11.2 Deployment Standards

- Deployments MUST be repeatable.
- Infrastructure and database changes SHOULD be scripted.
- Manual steps MUST be documented and minimized.
- Production deploys MUST have rollback or remediation notes.
- Feature flags SHOULD be used for risky changes when feasible.
- Post-deploy verification MUST prove the deployed system changed as intended.

### 11.3 Database Migration Standards

Migrations SHOULD be:

- Versioned.
- Ordered.
- Repeat-safe.
- Tested in lower environments.
- Backward-compatible where possible.
- Paired with rollback or forward-fix strategy.
- Audited after execution.

Avoid destructive migrations without backup/clone strategy, consumer impact analysis, approval,
communication plan, and recovery plan.

