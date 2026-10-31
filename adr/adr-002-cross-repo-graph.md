---
id: adr-002
version: 1
title: The cross-repo graph is compiled by the canon's pipeline from declared contracts and mentions, and read from index.json
applies_to: ["*"]
default: adopt
owner: ckoenigs
status: proposed
date: 2026-10-30
---

# ADR-002: The cross-repo graph is compiled by the canon's pipeline from declared contracts and mentions, and read from index.json

## Status
Proposed

## Date
2026-10-30

## Context
[[adr-000]] names three kinds of line in a repo's docs and calls the third *derived*: "the code
(graph, API surface)". Its nightly audit queries "code graph tables already pushed to Snowflake by
CI", and its AGENTS.md tells agents to "query the graph before reading files". It never says what
the graph is or who builds it.

Within one repo the question is settled. ds-code answers definitions, references, callers and
change impact from the language servers, which hold the exact, type-resolved graph of that repo
for the session, and ds-code local-010 chose not to store a copy of it (a stored graph drifts; the
packaged graph tools fetch binaries around the registry mirror). That answer stops at the repo's
edge.

The edges between repos are not imports, so no language server and no syntax-tree graph sees
them. In the five repos of this system they are commands (`canon/uninstall.sh` runs
`ds-next setup --remove`; ds-next starts `ds-code mcp`), paths (ds-next reads the canon's
standards and skills-os's `so-*/SKILL.md`), and shared names that two repos must agree on (the
servers `ds` and `code`, the rule prefix `mcp__ds__`). A count of files that name another repo
finds about forty such edges, all in text, and one of them failed in review this week because the
two sides had drifted. At work the same edges are HTTP calls, Snowflake tables, scheduled jobs and
shared packages, across repos that are created, renamed and archived every week, used by some
twenty people on their own machines.

Three facts shape the answer. A graph built on one laptop from whatever is cloned beside the
current repo cannot see repos that are not there. A graph stored per laptop goes stale and needs
invalidation, which is where graph tools spend most of their code. The canon's `portal` job already
clones every registered repo on each run and compiles `index.json`, which [[adr-000]] makes "the
only thing repos read".

## Decision

**1. The registry is one file per repo.** `repos/<name>.toml` replaces `repos.txt`. It holds the
host path and nothing a repo could say about itself better in its own manifest. `adopt_repo`
(ds-next) writes it and opens the merge request, the same path `/so-capture` uses; archiving a repo
deletes the file. Twenty people adopting repos in a week never edit the same line.

**2. A repo declares its contracts in its manifest.** `.ds/manifest.toml` grows two tables:

```toml
[provides]
commands = ["ds-next setup [--remove]", "ds-next mcp"]
names    = ["mcp server ds", "mcp server code", "rules mcp__ds__*"]
paths    = ["skills/*/SKILL.md"]

[uses]
canon     = ["standards/*.md", "index.json"]
skills-os = ["so-*/SKILL.md"]
ds-code   = ["ds-code mcp"]
```

Keys under `[uses]` are registered repo names; values name what is used, in the words the
provider used. For work repos the same two tables carry HTTP routes, tables and jobs. A contract
is declared by the repo that owns it; a dependency by the repo that has it.

**3. The canon's pipeline compiles the `repos` section of `index.json`.** The `portal` job already
has every registered repo checked out. One more step reads each manifest and runs a mention scan
(`git grep` across the checkouts for every provided command, name and path), then writes:

- `repos`: name, path, commit, tags, and the `provides` and `uses` tables as declared;
- `edges`: declared (`uses` entries that resolve to a `provides`), mentioned (a file in one repo
  naming what another provides, with file and line), and both;
- `report`: declared but never mentioned anywhere (a contract nobody uses), mentioned but not
  declared (an undeclared dependency), `uses` naming a repo or contract that does not exist.

It is rebuilt from scratch on every run, so nothing is invalidated. It runs on every merge to the
canon and on a nightly schedule, not on every merge of every registered repo; a repo that changes
a contract and wants the index now triggers the canon pipeline from its own CI. Edges carry the
commit they were computed from. The same rows roll up to Snowflake beside the adoption table of
[[adr-000]], when that rollup exists; `index.json` is what machines read.

**4. ds-next serves it; every session reads the current index.** `project_status` gains
*provides*, *uses* and *used by*, with the file and line of each mention. A `repo_graph` tool
answers "who provides X" and "who uses what this repo provides" for any registered repo, cloned on
this machine or not. `ds-next mcp` fast-forwards the canon clone on start, quietly, with a short
timeout; a machine that cannot reach the host keeps the index it has and says how old it is. Each
machine's graph is then as fresh as the last pipeline, not the last time its owner remembered to
pull.

**5. ds-code stays local and exact, and looks sideways through the index.** `change_impact` adds a
last section: for each changed symbol, command, name or path that the index lists as provided,
the repos and lines that use it. ds-code reads the index the same way ds-next does and never scans
other clones; it stays read-only and needs no store.

**6. Access is granted on adoption.** The canon's job token must be able to clone every registered
repo. `adopt_repo` adds the canon to the repo's job-token allowlist (or the group token covers it);
a repo the pipeline could not read is listed in `report`, never silently missing.

**7. Not built, on purpose.** Semantic resolution across repos (a Python caller of a TypeScript
handler through HTTP resolved to the handler): the declared contract is the resolution, and the
mention scan finds its consumers. A graph database or a per-laptop graph store. A scan of sibling
clones on the developer's machine. A pipeline per registered repo.

## Alternatives Considered
1. **A stored whole-repo graph on each machine** (codebase-memory-mcp, Serena and kin): sees one
   repo at a time, drifts between runs, resolves by syntax rather than type, and the packages fetch
   binaries around the registry mirror (ds-code local-010). Rejected.
2. **Scan the clones beside the current repo** on the developer's machine: cheap and exact for what
   is there, blind to what is not, and every machine answers differently. Rejected as the design;
   kept as the technique the pipeline runs where every repo is there.
3. **Declared contracts only, no mention scan**: exact and always stale, because nobody declares
   every dependency. Rejected alone; the `report` of undeclared mentions is what keeps declarations
   honest.
4. **Mention scan only, no declarations**: finds everything named and nothing meant; cannot tell a
   contract from a comment. Rejected alone.
5. **Graph tables in Snowflake as the primary store**, as [[adr-000]] sketched: every agent would
   need a warehouse connection to ask what calls what. Kept as the rollup for the audit; the file
   every machine already reads is the store.

## Consequences
An agent changing a contract sees who depends on it before it finishes, on any machine, for repos
it has never cloned. Teams declare their contracts once, in the manifest they already keep, and the
pipeline tells them when a declaration is unused or a dependency undeclared. The registry scales by
files, not lines. The per-repo cost is two tables in the manifest. The canon's pipeline grows one
step and its runtime by the time to grep two hundred shallow clones, which is minutes. The graph is
one pipeline run old at worst, and text-based: a dependency reached through a URL built at runtime
is invisible until declared. `[uses]` rots unless the review checklist asks for it, and the
`report` is how that rot is seen.

## Migration
1. This ADR, reviewed. 2. `repos/<name>.toml` for the five repos of this system and the pipeline
step that compiles `repos`, `edges` and `report` into `index.json`, with the system's own repos as
its first subjects. 3. `[provides]` and `[uses]` in their five manifests; a test in each repo that
its `uses` resolve against the index. 4. `project_status`, `repo_graph` and the fast-forward in
ds-next; `adopt_repo` writing the registry file. 5. `change_impact` reading the index in ds-code.
Work repos follow by the order of [[adr-000]]'s migration: most touched first.

## Validation
The edge that drifted this week (canon's by-hand uninstall mirroring what ds-next's setup writes)
appears in `edges` as mentioned-and-declared, and a change to `setup --remove` shows it in
`change_impact`. `report` is empty for the five repos once their manifests are filled. On the
bench of [[adr-000]], the cold-start question "what calls `load_claims`" gains a cross-repo
variant with a known answer.

## Review Date
2026-11-30
