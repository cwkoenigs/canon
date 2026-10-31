---
id: compliance-rubric
version: 1
title: Compliance Rubric
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 15
---

# Compliance Rubric

Use this scoring model in project reviews.

| Area | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| Requirements | Undefined | Partial | Clear | Clear, testable, traceable |
| Architecture | Ad hoc | Some boundaries | Documented | Documented with ADRs and failure modes |
| Idempotency | Unsafe | Partial | Mostly retry-safe | Retry-safe with evidence |
| Testing | Manual only | Basic automated | Good coverage | Risk-based, automated, traceable |
| Observability | Minimal | Logs only | Logs plus metrics | Logs, metrics, dashboards, alerts |
| Security | Not reviewed | Basic review | Controls applied | Threat modeled and verified |
| Data quality | None | Ad hoc checks | Standard checks | Automated checks with alerts and evidence |
| UX | Developer-centric | Basic usable | User-tested | Accessible, observable, error-resilient |
| LLM/agent control | Uncontrolled | Manual review | Versioned prompts/tools | Evaluated, monitored, permissioned |
| CI enforcement | None | Manual checklist | CI runs tests | CI enforces generated artifacts and registries |
| Maintainability | High burden | Some docs | Clear docs | Low operational burden, clear ownership |

Production readiness target: no category below 2. High-risk systems should target 3 in security,
observability, idempotency, and testing.

