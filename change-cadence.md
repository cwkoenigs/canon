---
id: change-cadence
version: 1
title: Standard Change Cadence
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 2
---

# Standard Change Cadence

Use this cadence for material feature work, bug fixes, deployments, schema changes, production data
workflows, and agent-assisted work. Small documentation or exploratory changes may use a lighter
version.

### 2.1 Intake

Capture:

- App, repo, workflow, or data objects involved.
- One-line summary of the feature, bug, or operational need.
- Expected user/system behavior and non-goals.
- Data sources, downstream consumers, and named datasets if known.
- Environments: local, dev, QA/stage, production.
- Test runner, deploy command, validation surface, and owner.
- Acceptance criteria and definition of done.

### 2.2 Retired: Review-Track Classification

Removed in v1.1 with §1.1. There is one review track: internal review plus external review at the
§2.5 gates, with the developer confirming before each external call.

### 2.3 Discovery and Baseline Scan

Before implementation:

- Read the relevant code, configuration, tests, deploy files, runbooks, and known incidents.
- Identify the repo's real test and deploy commands instead of assuming a toolchain.
- Check for existing platform or internal capabilities before proposing custom logic.
- Record baseline gaps as recommendations, not blockers:
  - Automated tests.
  - Post-deploy smoke or validation check.
  - Dev/prod separation.
  - QA or contract documentation.
  - Decision-log convention.
  - Runbook and owner.
  - Observability and alerting.

### 2.4 Phased Plan

Every material plan SHOULD use discrete phases with this structure:

```markdown
### Phase N: <short title>
**Objective:** One sentence describing what this phase achieves.
**Inputs:** Prior approvals, artifacts, data, or environments required.
**Scope:** What is in scope and, when useful, explicitly out of scope.
**Deliverable:** The concrete artifact or state change produced.
**Exit criteria:** Observable proof the phase is complete and stable.
```

Planning rules:

- Each phase must be self-contained enough for an engineer or agent to pick up cold.
- Each phase must end with the branch, data state, or deployed environment stable.
- Exit criteria must name concrete checks: the repo's test command, its build command, its deploy
  command, validation queries, visual QA, or a real app interaction.
- User-visible behavior changes beyond the stated goal MUST be called out separately and approved.

### 2.5 Review Gates

- **G1 plan review:** review the plan before implementation.
- **G2 interim review:** review the implemented diff after tests pass and before QA/rollout cleanup.
- **G3 pre-closeout review:** review the full branch delta before production rollout.

External reviews are advisory data. The caller and human reviewer decide what to apply. Ask the
developer before each external call; if they decline, keep the same review discipline internally
and record that the gate was reviewed internally.

### 2.6 Rollout Inventory

Before any dev or production rollout, enumerate exactly what ships:

- Application bundle, container image, service, or static assets.
- Database and infrastructure objects: procedures, views, tables, jobs, policies, secrets,
  integrations, and grants.
- Config/environment changes.
- Manual steps not covered by the automated deploy.
- Execution identity and object owner for each step.
- Rollback or forward-fix action for every risky step.
- Post-deploy verification proving deployed source equals intended source and behavior changed.

