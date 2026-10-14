---
id: architecture
version: 1
title: Architecture and Abstraction
applies_to: ["*"]
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 5
---

# Architecture and Abstraction

### 5.1 Boundaries

- Separate domain logic from transport, storage, UI, and platform adapters.
- Keep dependency direction explicit and avoid cycles.
- Access external systems through adapters or shared clients, not scattered direct calls.
- Standardize cross-cutting concerns: auth, query execution, caching, error handling, logging,
  telemetry, and configuration.

### 5.2 DRY, WET, and AHA

DRY means do not duplicate knowledge, policy, and business logic. It is appropriate for:

- Authentication and authorization.
- Data access helpers.
- Logging and telemetry.
- Design tokens and shared UI.
- Security controls.
- Stable business metric definitions.
- Tested prompt templates and skill patterns.

WET is acceptable when the domain is still changing:

- Prototypes.
- Unproven prompts.
- Early UX workflows.
- One-off data remediation scripts.
- Business rules likely to diverge.

Create a shared abstraction only when:

- The duplicated behavior is stable.
- At least three uses exist or are clearly imminent.
- Tests exist.
- Ownership and versioning are clear.
- The abstraction reduces complexity instead of hiding it.

### 5.3 Shared Internal Packages

When the organization maintains shared packages for platform access, auth, design tokens, or UI
components, new projects SHOULD use them rather than reimplementing the same concerns. Record the
canonical package list in `AGENTS.md` so agents and new contributors find it without asking.

Reciprocally: when a project hand-rolls something a shared package already covers, that is a
finding, not a style preference.

### 5.4 Data and Interface Contracts

Production datasets and published interfaces SHOULD define:

- Owner.
- Source system.
- Grain — what one row or one record represents.
- Primary key or uniqueness rule.
- Freshness expectation.
- Retention requirement.
- Sensitive fields and classification.
- Allowed consumers.
- Quality checks.
- Backfill behavior.
- Breaking change policy.
- Operational dashboard or validation query.

Transformation rules that apply regardless of engine:

- Transformations MUST be deterministic unless nondeterminism is explicitly required.
- Use explicit column/field lists for production interfaces; avoid `SELECT *` or equivalent
  wildcard projection in stable published interfaces.
- Avoid hidden ordering assumptions.
- Every incremental model MUST define deduplication and late-arriving-data behavior.
- Windowed logic MUST anchor on fixed calendar/clock boundaries when the business definition is
  calendar-based. Do not infer "recent" solely from the newest available data row.

Consume telemetry and shared datasets through **stable curated views or documented interfaces**, not
raw internal tables. This gives consumers a contract and isolates them from schema churn.

