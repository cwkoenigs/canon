---
id: idempotency
version: 1
title: Idempotency and Resilience
applies_to: ["service", "pipeline", "dbt"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 6
---

# Idempotency and Resilience

### 6.1 Idempotency

Any retryable operation MUST be safe to retry or explicitly documented as not retryable.

Patterns:

- API calls use idempotency keys.
- Database writes use unique keys, upserts, transactional merges, or batch IDs.
- Pipelines use watermarks and checkpoints.
- Notifications record send history.
- Migrations record applied versions.
- Agent work happens on branches/worktrees and requires explicit human merge.

### 6.2 Retry Taxonomy

| Error type | Retry? | Pattern |
|---|---|---|
| Validation error | No | Fail fast with actionable error. |
| Auth/authz error | No | Fail closed; alert if unexpected. |
| Not found | Sometimes | Retry only if eventual consistency is expected. |
| Rate limit | Yes | Exponential backoff with jitter. |
| Network timeout | Yes | Bounded retry with idempotency key. |
| Deadlock/lock timeout | Yes | Bounded retry; monitor frequency. |
| Data quality failure | No automatic publish | Quarantine and alert. |
| Unknown exception | Limited | Retry only if the operation is idempotent. |

### 6.3 Fail Safely

- Security failures MUST fail closed.
- Data quality failures MUST prevent material bad data from publishing.
- User-facing applications SHOULD degrade gracefully instead of showing misleading results.
- Agents MUST stop or ask for review when a task exceeds authorized scope.

