# The Knowledge System

Future state only. Every repo is born through `ds`; nothing here concerns
repos that already exist.

## One sentence

Every fact about how we build software exists in exactly one place, and
everything else points at it.

## What a data scientist experiences

Day one, new project:

    $ ds new claims-features
    ds: a few questions. Defaults are in brackets; Enter accepts.
      What does this repo do (one line)?            > Feature store for claims models
      Who owns it? [ckoenigs]                       >
      Test command? [uv run pytest -q]              >
      Which canon tags apply? [python, package]     > python, package, snowflake
      Anything future-you would want to know?       > Uses the CLM-adjudication table, not raw claims
    ds: created README.md, AGENTS.md, DECISIONS.md, .ds/manifest.toml
    ds: 6 standards apply; all adopted at current versions.

Day forty, a standard changed:

    $ git push
    ds: 1 standard pending — adr-021 (uv lock policy). Run `ds reconcile`.
    [push proceeds]

    $ ds reconcile
    adr-021 v1 — "Commit uv.lock in every package repo"
      applies because: tags include python
      proposed change: add uv.lock to git, remove from .gitignore
      [a]dopt  [d]ecline  [s]kip for now  [r]ead full text
    > a
    ds: applied, tests pass, manifest updated (adopted, ckoenigs, 2026-10-14)

Or:

    > d
    reason: > Lockfile churn breaks the nightly SPCS image build; revisit after image v3
    revisit [90d]: >
    ds: recorded. adr-021 declined by ckoenigs — visible in the adoption table.

That is the whole interface. Three moments: an interview at birth, a
one-line nudge on push, a decision when a standard changes. Nobody edits
boilerplate, nobody copies a README from the last project, nobody wonders
whether a doc is current.

## The three kinds of doc line

| Kind | Truth lives in | In the repo as | Who changes it |
|------|----------------|----------------|----------------|
| Inherited | `canon` | a pointer, never text | whoever edits the standard, once |
| Local | this repo | text, from the interview | the team that owns the repo |
| Derived | the code | generated, never hand-edited | regeneration |

Every line carries provenance. Provenance is what makes drift detectable:
a local line is a claim someone made; a derived line is a claim the code
makes; a pointer is not a claim at all.

## Primitives

### Canon

The one repo where org knowledge is written. `canon/` holds standards,
each with a stable ID and a version:

    canon/
      adr/adr-000-knowledge-system.md
      adr/adr-014-uv-not-pixi.md
      glossary.md          id: glossary
      layout.md            id: layout
      naming.md            id: naming
      index.json           generated on merge: id, version, hash, title,
                           applies_to, supersedes, owner

Rules: IDs never change, versions only go up, `applies_to` is a tag glob so
a dbt decision is never pending on a Python package, and a standard can
supersede another. Anyone can propose; the listed owner approves. The
canon is the most-reviewed repo in the org, by design.

### Pointer

`[[adr-014]]` anywhere in a doc. Resolved on read by `ds docs` (humans),
by CI into `docs/rendered/` (GitLab), and by the `read_standard` tool
(agents). A repo never holds a standard's prose, so changing a standard
changes every repo's docs at once, silently. `[[adr-014@2]]` pins a
version and is a deliberate, recorded choice.

### Manifest

`.ds/manifest.toml`. For each applicable standard: `adopted`, `declined`,
or `pending`, with who, when, and — for declines — why and when to
revisit.

    [standards.adr-021]
    status  = "declined"
    version = 1
    by      = "ckoenigs"
    on      = "2026-10-14"
    reason  = "Lockfile churn breaks the nightly SPCS image build; revisit after image v3"
    revisit = "2027-01-12"

Declining by name with a reason is a first-class outcome. A standard nobody
can decline gets ignored; one you can decline gets an honest answer, and
the org can see who said no and why. Manifests roll up nightly to
`DS_OPS.CANON.ADOPTION`, one row per repo per standard.

### Interview

`ds new` asks; it does not copy. Six to ten questions, defaults inferred
from the environment, transcript kept at `.ds/interview.md`. Output is the
curated set — README, AGENTS.md, DECISIONS.md, manifest — containing only
sections the answers justify. No empty headers, no placeholder prose.
AGENTS.md is mostly pointers and fits on one screen.

### Reconcile

The one verb, same code everywhere:

    ds reconcile --check        offline, deterministic, sub-second
    ds reconcile --interactive  a human decides each pending item
    ds reconcile --apply        an agent decides, unattended

`--check` runs from the pre-push hook and CI: manifest well-formed,
pointers resolve, derived docs regenerated, pending items listed. It never
fails a push for a pending item; it fails only on a broken pointer or a
malformed manifest. `--apply` is the only mode that needs a model, and an
agent's decline is flagged for human confirmation within 14 days.

## How a standard is born

1. Someone notices three repos made the same local decision. The adoption
   table shows it; so does the nightly audit.
2. They open an MR in `canon` with a new ADR: context, decision,
   `applies_to`, owner.
3. The owner approves; CI regenerates `index.json`.
4. Every applicable repo's next push shows the nudge. Every repo answers
   within its own time. The adoption table shows the spread.

There is no announcement, no migration project, no "please update your
READMEs" email. The standard exists once and the system carries it.

## What the team sees

- `ds docs` — the repo's docs with pointers resolved, in the terminal.
- GitLab — the same, rendered by CI.
- The adoption dashboard — one Snowflake view: for every standard, who
  adopted, who declined and why, who is pending. This is also how a
  manager sees which decisions are actually in force.
- The nightly audit's findings — as tasks in the queue, most of which the
  agent system closes before anyone reads them.

## Nightly audit

SQL over the adoption table and the code-graph tables that CI already
pushes. Findings become queue tasks.

- Derived contradicts local: a doc names a symbol or command the code lacks.
- A pointer targets a superseded standard and hasn't been re-pinned.
- A decline is past its revisit date.
- An agent-made decline is older than 14 days with no human confirmation.
- A repo has not reconciled in 30 days.
- A new public symbol whose name is not a glossary term or an allowed
  compound.

## Non-goals

- A wiki. There is nowhere to write prose that is not a standard, a local
  doc, or derived.
- Forcing adoption. Visibility, not enforcement.
- Migrating old repos. Out of scope; the system is defined for repos born
  through `ds`.
- Depending on the agent system. This works with people alone. Agents make
  it cheaper.

## Why this is the pure form

One place to write. One verb to run. One table to look at. Every doc line
is either a pointer, a thing a person said, or a thing the code says — and
you can always tell which.
