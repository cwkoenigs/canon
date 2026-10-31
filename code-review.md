---
id: code-review
version: 1
title: Code Review Standards
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 13
---

# Code Review Standards

Reviewers SHOULD evaluate:

- Correctness and stated intent vs actual diff.
- Simplicity and maintainability.
- Test coverage and validation evidence.
- Restricted-data, privacy, and security posture.
- Idempotency and retry safety.
- Error handling and observability.
- Data quality and semantic definitions.
- Performance and compute cost.
- UX and accessibility.
- Backward compatibility.
- Rollback/remediation.
- Documentation and runbook updates.

### 13.1 Pull Request Template

```markdown
## Summary
What changed and why?

## Scope
- [ ] Application code
- [ ] Database/data platform
- [ ] Infrastructure
- [ ] UX
- [ ] LLM/prompt/agent behavior
- [ ] Documentation

## Decision Log
- Decision log:

## User-Visible Behavior Changes
- <none | list approved changes>

## Validation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Data quality checks
- [ ] Security checks
- [ ] Accessibility checks
- [ ] LLM evals
- [ ] Manual QA

## Deploy Surface
- App/service:
- Data objects:
- Config/env:
- Manual steps:
- Execution identity / owner:

## Operational Impact
- [ ] Logs/metrics updated
- [ ] Dashboard/alert updated
- [ ] Runbook updated
- [ ] Rollback/remediation documented

## Notes for Reviewer
Known tradeoffs, limitations, or follow-up work.
```

