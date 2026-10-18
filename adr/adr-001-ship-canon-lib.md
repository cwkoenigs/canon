---
id: adr-001
version: 2
title: Accepted code as canon-lib, grown from real repos; lessons live next to what they changed
applies_to: ["*"]
owner: ckoenigs
status: proposed
date: 2026-10-18
---

# ADR-001: Accepted code as canon-lib, grown from real repos; lessons live next to what they changed

## Status
Proposed (v2, revised for simplicity and organic growth after the owner's review of v1)

## Date
2026-10-18

## Context
The idea: a team's software becomes plug and play; the AI pulls the same accepted code every time
and the system gets better as the code base grows. Five design versions were built and tested in
three rounds with blind, validated judges (ds-next `REPORT.md`). Findings: accepted code as one
package pays (same modules pulled every time, 35 to 61% less code written, one place to fix a
defect, promotion from a real build picked up by the next); lessons as files cost 2× and bought
nothing; correctness could not be measured because the model already passed every judge alone.

The owner's direction for this decision: keep it simple, let it grow on its own, and make every
new repo connected to the knowledge from its first commit.

## Decision

**1. A new repo is born connected.** `ds-next new` scaffolds from canon with `canon-lib` as a
dependency, records the canon and its index version in `.ds/manifest.toml`, and tells agents in
`AGENTS.md` to import from canon-lib before writing their own code. The pre-push hook runs
`reconcile`, which nudges when canon has moved. (Scaffolds v3.)

**2. canon-lib is how accepted code reaches repos.** The blocks (`blocks/<id>/`: code, tests,
`BLOCK.md`) are the source of truth; `scripts/build_lib.py` builds the package from them and
`--check` fails when they drift. Append-only; a breaking change ships under a new name; heavy
dependencies in extras; every symbol stands alone; a block's tests are its acceptance bar.

**3. Growth is one command and no gate.** `scripts/promote.py` lifts a stand-alone module and its
tests out of any real repo into a block, status `proposed`. Proposed code is **served at once**
(canon-lib, `code_search`, `code_add`), labelled *unreviewed*. The owner's review makes it
`accepted`; `retired` takes it out of the package. Nothing waits on a person; a person can always
veto. An agent may propose at the end of a build; the judge-validated tests are what qualify it.

**4. A lesson lives next to what it changed.** In the block's `BLOCK.md` ("why it is shaped this
way") or in the standard it refined. A standalone gotcha only when there is no code or standard to
attach it to, and then ten lines, with its scope (`applies_to`) and the ticket it came from.
Agents read a lesson when they touch that code or that scope, not as a corpus up front.

**5. The ticket decides.** Where a ticket and a canon rule disagree, the agent follows the ticket,
says which rule it set aside and why, and the owner decides whether the rule or the ticket changes
([[gotcha-agent-trust]] rule 8). Canon's rules apply where the ticket is silent. This settles the
two cases the judges raised: emptying an output folder we did not build, and which READMEs
become `index.md`.

**6. The function library stays as the second door.** `ds-next mcp` serves `code_search`,
`code_get`, `code_add` and the lessons to any agent that cannot read files or take the dependency.
Not the default.

**7. Not built, on purpose:** serving infrastructure (a local editable package is the deployment
until there is a second machine), a package per function, anything Cortex-specific.

## Alternatives Considered
1. Owner review before anything is served (v1 of this ADR): safe, and a bottleneck on every
   promotion; rejected for growth.
2. Lessons as a corpus every build reads: 2× cost in every round, no gain, one silent override of
   a ticket; rejected.
3. Copies only (`code_add`), no package: same correctness, more turns, fixes need a re-pull; kept
   as the second door.

## Consequences
Less code written from scratch and one place to fix it, with no human in the loop for growth.
Unreviewed code reaches repos labelled as such, so a defect in it reaches every consumer until
fixed once; `reconcile` shows which repos carry which version. Correctness gains are unproven and
stay unclaimed until a task exists where the model fails without team knowledge.

## Validation
In use: pulls, lines written and pending versions from `~/.ds/usage.jsonl` and `reconcile`. In the
bench: a change ticket that must alter pulled code; a task with team-specific knowledge the model
cannot infer, with a failing baseline.

## Review Date
2026-11-18
