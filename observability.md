---
id: observability
version: 1
title: Observability and Operations
applies_to: ["service", "pipeline", "dbt"]
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 7
---

# Observability and Operations

### 7.1 Required Telemetry Fields

Production workflows SHOULD emit:

- `request_id` or `correlation_id`.
- `run_id` or `batch_id`.
- Environment.
- Version or commit SHA.
- Actor or service account.
- Start and end time.
- Status.
- Input count and output count.
- Failure count and error category.
- Retry count.
- Compute and cost indicators where available.

### 7.2 Logging

Logs MUST be:

- Structured where possible.
- Redacted for secrets and restricted data.
- Queryable by correlation ID.
- Actionable for operations.
- Retained according to policy.

Logs MUST NOT include passwords, API keys, tokens, private keys, unmasked restricted data, or
unnecessary raw LLM prompt/output payloads.

### 7.3 Dashboards and Alerts

Dashboards SHOULD answer:

- Is it running?
- Is it correct?
- Is it fresh?
- Is it fast enough?
- Is it within cost expectations?
- What changed recently?
- Who owns it?
- What should operations do next?

Alerts MUST be actionable and routed to an owner.

**Prefer event-driven monitoring over polling.** Reactive work — pipeline monitoring, alerting,
downstream reactions to new data — SHOULD be triggered by a change event rather than a tight polling
loop. Polling burns compute on empty executions and can miss fast transitions. Scheduled jobs are
for work that genuinely runs on a calendar.

- SHOULD NOT run a job on a tight schedule purely to detect changes.
- SHOULD NOT create per-entity alert objects that poll a shared table. Prefer one handler with a
  filter; add an entity by editing the filter, not by adding infrastructure.
- Record the platform's concrete event-trigger mechanism in the §17 appendix so this rule is
  actionable rather than aspirational.

### 7.4 Data Quality

Production datasets SHOULD have checks proportional to business impact:

- Row count and freshness.
- Required-field null checks.
- Duplicate checks.
- Accepted values.
- Referential integrity.
- Future timestamp checks.
- Distribution/anomaly checks.
- Source-to-target reconciliation.

Material quality failures SHOULD write evidence to an operational table and alert an owner.

