---
id: llm-agents
version: 1
title: LLM and Agent Standards
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-14
source: guidebook v1.1 section 8
---

# LLM and Agent Standards

### 8.1 Allowed Uses

LLMs MAY be used for classification, extraction, summarization, translation, documentation drafting,
code review assistance, query generation with guardrails, semantic Q&A over governed data, and
agentic task execution in controlled environments.

LLMs MUST NOT be used as unreviewed final authority for:

- Security-sensitive access decisions.
- Clinical, legal, financial, or compliance determinations.
- Destructive production operations.
- Unverified data modification.
- Silent policy exceptions.

### 8.2 Prompt and Skill Contracts

Production prompts and reusable skills SHOULD define:

- Purpose and owner.
- Trigger conditions and non-goals.
- Input and output schema.
- Safety rules and refusal conditions.
- Model/function target when relevant.
- Evaluation set or review method.
- Changelog.

Skill descriptions SHOULD be short, action-oriented, and placed in YAML frontmatter. Update the
README table and installation script when adding or renaming shared skills.

New or refactored skills MUST be authored via the native `skill-development` skill
(`$skill-development`) before hand-writing a `SKILL.md`; it is the canonical authoring gate. Before
authoring any skill, confirm the need is not already met by a native skill or an existing shared
skill (see §1.2).

### 8.3 Structured Outputs

LLM outputs used by systems SHOULD be structured and validated:

- JSON schema or equivalent.
- Strict field names.
- Allowed categorical values.
- Refusal/error format.
- No downstream execution of unvalidated free text.

### 8.4 LLM Evaluation

Before production use, LLM workflows SHOULD have:

- Golden examples.
- Edge cases.
- Prompt-injection/adversarial cases.
- Regression tests for prompt or model changes.
- Schema validation.
- Human review sampling.
- Accuracy and failure thresholds.
- Drift monitoring.

### 8.5 Agent Autonomy Levels

| Level | Description | Production use |
|---|---|---|
| 0 | Suggest only | Safe default. |
| 1 | Draft artifacts | Allowed with human review. |
| 2 | Modify non-production files | Allowed with tests and review. |
| 3 | Open PRs or change requests | Allowed with human approval before merge. |
| 4 | Execute production changes | Requires scoped permissions, audit, rollback, and explicit approval. |
| 5 | Autonomous production operation | Generally prohibited unless approved for a narrow, low-risk workflow. |

### 8.6 Agent Repository Instructions

Every repo that expects agent help SHOULD include `AGENTS.md`:

```markdown
# AGENTS.md

## Project Overview

## Architecture Boundaries

## Directory Map

## Setup

## Required Checks

## Coding Standards

## Testing Standards

## Security and Privacy Rules

## Data Rules

## UX Rules

## Files Requiring Extra Care

## PR Response Format
- Summary
- Tests run
- Risks/limitations
- Files changed
```

