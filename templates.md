---
id: templates
version: 1
title: Templates
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 14
---

# Templates

### 14.1 ADR Template

```markdown
# ADR: <Decision title>

## Status
Proposed | Accepted | Deprecated | Superseded

## Date
YYYY-MM-DD

## Context
What problem are we solving? What constraints matter?

## Decision
What did we decide?

## Alternatives Considered
1. Option A
2. Option B
3. Option C

## Consequences
Positive, negative, operational, security, cost, maintenance.

## Validation
How will we know the decision worked?

## Review Date
YYYY-MM-DD
```

### 14.2 Data Contract Template

```markdown
# Data Contract: <Dataset name>

## Owner

## Purpose

## Source Systems

## Grain
One row represents...

## Primary Key / Uniqueness Rule

## Freshness Expectation

## Retention

## Sensitive Fields

## Tags / Classification

## Schema
| Column | Type | Required | Description | Quality rule |
|---|---|---:|---|---|

## Quality Checks

## Consumers

## Breaking Change Policy

## Backfill / Reprocessing Behavior

## Operational Dashboard or Query
```

### 14.3 Runbook Template

```markdown
# Runbook: <System/workflow>

## Owner

## Purpose

## Architecture Summary

## Dependencies

## Normal Schedule / Trigger

## Dashboard / Operational Queries

## Alert Conditions

## Common Failure Modes
| Symptom | Likely cause | Action | Escalation |
|---|---|---|---|

## Retry Procedure

## Rollback / Remediation

## Data Reconciliation

## Communication Plan

## Last Reviewed
YYYY-MM-DD
```

### 14.4 Prompt Card Template

```markdown
# Prompt Card: <Prompt name>

## Owner

## Use Case

## Model / Function Target

## Autonomy Level
0 | 1 | 2 | 3 | 4 | 5

## Input Schema

## Output Schema

## Prompt Version

## Prompt Text

## Examples

## Refusal / Safety Rules

## Evaluation Dataset

## Metrics

## Known Limitations

## Monitoring

## Changelog
```

