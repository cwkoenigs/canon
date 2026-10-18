---
id: adr-001
version: 1
title: Ship accepted code as canon-lib; redesign the lessons
applies_to: ["*"]
owner: ckoenigs
status: proposed
date: 2026-10-17
---

# ADR-001: Ship accepted code as canon-lib; redesign the lessons

## Status
Proposed

## Date
2026-10-17

## Context
The knowledge system was built in five versions and tested in three rounds with blind, validated
judges (ds-next `REPORT.md`, `HANDOFF.md`). The question was which way of giving agents the team's
knowledge pays: lessons as files, accepted code as one package (canon-lib), accepted code pulled one
function at a time over MCP, or both.

## Decision
1. **canon-lib is how accepted code reaches repos.** Blocks stay the source of truth; the package is
   built from them (`scripts/build_lib.py`). Append-only; a breaking change ships under a new name;
   heavy dependencies in extras; every symbol stands alone; a block's tests are the acceptance bar.
2. **Promotion is the growth loop:** `scripts/promote.py` from a real repo, status `proposed`, owner
   review flips it to `accepted`; only accepted code is served.
3. **The function library (`code_search`, `code_get`, `code_add`) stays** for discovery and for repos
   that cannot take the dependency. It is not the default.
4. **Lessons as files stop being served to builds as they are.** They are rewritten as short, scoped
   decisions ([[gotcha-tool-arguments]] and [[gotcha-proving-claims]] are the form), served by
   applicability, and an agent that overrides a ticket because of one must say so
   ([[gotcha-agent-trust]] rule 8).

## Alternatives Considered
1. Lessons only: 2× cost in every round, no judge points, one silent override of a ticket.
2. A package per function: rejected before testing; nothing to maintain it with.
3. Serving infrastructure first: nothing in the results depended on how canon was served.

## Consequences
Less code written from scratch (35 to 61% on the tasks tested), one place to fix a defect, the same
modules pulled by every build. Not more correct code: the control passed 96 to 100% without canon on
every task, so that claim is untested. Accepted code carries its defects to every consumer, so
review and judge-validated tests matter more, not less.

## Validation
A change ticket that must alter pulled behaviour; a task with a failing baseline (team-specific
knowledge); lessons alone in the new form against that baseline. Reuse, lines written and cost are
read from `~/.ds/usage.jsonl` and the bench.

## Review Date
2026-11-17
