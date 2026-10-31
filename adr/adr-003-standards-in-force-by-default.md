---
id: adr-003
version: 1
title: A standard is in force by default; the manifest records exceptions; the canon's pipeline rolls adoption up
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-30
---

# ADR-003: A standard is in force by default; the manifest records exceptions; the canon's pipeline rolls adoption up

## Status
Proposed

## Date
2026-10-30

## Context
[[adr-000]] made every standard a question each repo answers in its manifest: adopted, or declined
with a reason, else pending. It designed the roll-up (one table, nightly) and an unattended weekly
`reconcile --apply`, and it left the default implicit: a standard nobody has answered is pending
for ever, and pending never blocks, so nothing ever answers it.

On 2026-10-30 the owner adopted three repos and met 21 to 25 pending standards in each, with the
one answer being a command typed per repo. Twelve repos would be twelve sessions of that; ten
thousand is not a process. The owner's words: a line to run in each repo is not something that can
be rolled out to a team.

Two facts shape the answer. The standards are the team's rules: a repo that applies to one is held
to it whether or not its owner has filed a form, and the honest exception is a decline with a
reason, which [[adr-000]] already made first-class. And the canon's pipeline already clones every
registered repo ([[adr-002]]), so it can compute every repo's standing without writing into any.

## Decision

**1. A standard carries its default.** `default: adopt` means in force in every repo it applies to
unless that repo declined it; `default: ask` means pending until the repo's owner decides. Set once,
in the standard's front matter, by its owner; `index.json` carries it. Every standard in the canon
today is `adopt`. `ask` is for the few that are a real choice per repo.

**2. The manifest records exceptions and explicit answers, never defaults.** `reconcile` computes
the effective standing: an entry in the manifest wins; otherwise the default. A repo with an empty
`[standards]` and twenty-five `default: adopt` standards is adopted on all twenty-five, at the
current version, with nothing to type. A decline still answers the version it was made against, so
a new version re-asks the decliner. An older explicit adoption of a `default: adopt` standard is
carried forward to the current version: the org changed the rule, and the repo follows unless it
declines.

**3. The pipeline is the roll-up.** `scripts/build_repos.py`, which already has every registered
repo checked out, computes the standing of every standard in every repo it applies to and writes
it as the `adoption` section of `index.json`: per standard, which repos are adopted (and which of
those by default), which declined with what reason, which pending. `canon_list` and `ds-next canon
list` show each standard's row; `project_status` shows a repo's. Nothing is written into any repo,
so the roll-up costs the same at ten thousand repos as at five.

**4. The pen stays for the exceptions.** `ds-next decide decline <id> --reason` is what anyone types,
and `decide adopt` answers a `default: ask` standard or pins an explicit adoption. Reading happens
in `/docs`, not in the terminal.

**5. Adopted is a claim, not compliance.** The repo is held to the standard; whether it follows it
is [[adr-000]]'s unattended `--apply` with an agent, still unbuilt and unclaimed.

## Alternatives Considered
1. **Write an adopted entry into every manifest by merge request from the pipeline**: ten thousand
   merge requests saying what the default already says, and a review queue of nothing. Rejected.
2. **An agent deciding per repo on a weekly cron** ([[adr-000]]'s `--apply` unattended): a model
   answering a question that has a default is a model guessing; keep the agent for compliance work.
3. **Keep pending as the default and make the per-repo command faster**: the owner's objection is to
   the per-repo step, not its speed. Rejected.
4. **Default `adopt` for everything, no `ask`**: simpler, but a standard that genuinely is a choice
   (a platform-specific one) would be silently claimed by repos it does not fit. `ask` kept.

## Consequences
Rolling out a standard is: write it, set its default, merge. Every repo it applies to is held to it
from the next index, and every machine's `reconcile` says so. Declines are the only per-repo
work, and they carry reasons the roll-up shows. The three repos adopted today drop from 25 pending
to 0 with no command. The meaning of "adopted" widens to "in force", and `reconcile` says how many
are by default so the distinction is never hidden. A `default: ask` standard behaves exactly as
before this ADR.

## Validation
canon: `scripts/tests/test_build_repos.py::test_adoption_rollup`. ds-next: `reconcile` tests for
the default carrying a repo forward, an asking standard still pending, a decline still answering one
version. On this Mac: `ds-next reconcile` in each of the five repos reports 0 pending with no entry
typed; `ds-next canon list` shows each standard's org-wide row.

## Review Date
2026-11-30
