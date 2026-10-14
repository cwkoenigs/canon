# `ds` — Changes to Implement the Platform

`ds` is the delivery mechanism for both systems. The canon is files; the
agent system is a dispatcher. Nothing reaches a data scientist except
through `ds`.

Existing facts that do not change: Python, typer, distributed via pipx,
uv for dependencies, no devcontainers, provenance tags on every emitted
file, the agent-driven launcher pattern. `ds new` remains the entry point.

## Command surface (future state)

    ds new <name>            interview → curated docs → manifest → hooks → CoCo/MCP config
    ds explore               scratch dir where the interview runs before promotion
    ds docs [path]           render docs with pointers resolved
    ds reconcile             --check | --interactive | --apply
    ds canon list            standards that apply to this repo, with status
    ds canon read <id>       print a standard
    ds task "<text>"         create a queue item (GitLab issue labeled `agent`)
    ds status                what the agent system has done for this repo lately
    ds audit                 run the repo-level audit locally (subset of nightly)
    ds serve-mcp             expose read_standard / manifest_status / graph tools
    ds hooks install         idempotent; called by ds new

## Module layout

    ds/
      cli.py                 typer app; thin
      interview/
        questions.py         question set; defaults inferred from env
        render.py            answers → README, AGENTS.md, DECISIONS.md
        transcript.py        .ds/interview.md with provenance tags
      canon/
        client.py            fetch + cache index.json; resolve [[id]]; read text
        manifest.py          load/validate/write .ds/manifest.toml
        reconcile.py         the verb; --check / --interactive / --apply
        derived.py           regenerate derived sections from the code graph
      agent/
        config.py            write CoCo settings, MCP config, model pins
        task.py              `ds task` → GitLab issue
        status.py            read metrics table for this repo
      mcp/
        server.py            read_standard, manifest_status, graph_* tools
      hooks/
        pre_push.sh          runs `ds reconcile --check`; never blocks on pending
      audit/
        local.py             the checks that can run without Snowflake

## Data formats

### `.ds/manifest.toml`

    [repo]
    name = "claims-features"
    tags = ["python", "package", "snowflake"]
    created = "2026-10-01"
    interview = ".ds/interview.md"
    ds_version = "2.0.0"

    [standards.<id>]
    status  = "adopted" | "declined" | "pending"
    version = <int>
    by      = "<user>" | "agent:<model>"
    on      = "<date>"
    reason  = "<text>"          # required when declined
    revisit = "<date>"          # required when declined

### `canon/index.json` (read-only from `ds`)

    {
      "generated": "2026-10-01T02:00:00Z",
      "standards": [
        {"id": "adr-014", "version": 2, "hash": "…", "title": "uv, not pixi",
         "applies_to": ["python", "package"], "supersedes": null,
         "owner": "ckoenigs", "path": "adr/adr-014-uv-not-pixi.md"}
      ]
    }

### Pointer syntax

`[[id]]` current version; `[[id@N]]` pinned. Resolved by `ds docs`, by CI
into `docs/rendered/`, and by the `read_standard` MCP tool. Unknown or
retired IDs fail `ds reconcile --check`.

### Provenance comments

    <!-- ds:local interview 2026-10-01 -->
    <!-- ds:inherited [[layout@3]] -->
    <!-- ds:derived graph 2026-10-01 -->

One per block, not per line. The audit parses these.

## `ds new` — the interview

Questions, in order. Defaults in brackets are inferred, never hard-coded.

1. What does this repo do, in one line?
2. Who owns it? [git user]
3. Test command? [detected from pyproject/Makefile, else `uv run pytest -q`]
4. Lint/type command? [detected, else `uv run ruff check . && uv run mypy .`]
5. Which canon tags apply? [inferred from files: python, package, dbt, service, notebook…]
6. Does it talk to Snowflake? Which database.schema? [detected from env]
7. Anything future-you would want to know?
8. Any standard you already know you'll decline? (name + reason)

Output: README.md, AGENTS.md, DECISIONS.md (empty local ADR list is fine —
the file says "none yet"), `.ds/manifest.toml`, `.ds/interview.md`. Then
`ds hooks install`, then `ds agent config` (below). Total under five
minutes.

## `ds agent config` — what makes it seamless

Runs at the end of `ds new`. Writes, without asking:

- CoCo repo settings: `--mode code` default; MCP servers registered:
  `ds serve-mcp` (canon + graph), Serena (LSP), Cortex Search tool.
- Model pins for the dispatcher in `.ds/agent.toml`: T0 model, max local
  attempts, context window, token budget.
- Graph index built once (`codebase-memory-mcp` or equivalent) into
  `.ds/graph.db`, gitignored, rebuilt incrementally by the hook.
- AGENTS.md line: "Query the graph before reading any file. Read
  `manifest_status` first."

The data scientist runs `ds new` and CoCo is already better. That is the
whole point.

## `ds reconcile`

    --check        offline; validate manifest, resolve pointers against the cached
                   index, regenerate derived, list pending. Exit non-zero only on
                   broken pointer or malformed manifest.
    --interactive  for each pending: show title, why it applies, proposed change;
                   [a]dopt [d]ecline [s]kip [r]ead. Adopt applies the change and
                   runs tests; decline records reason + revisit.
    --apply        unattended; the agent decides. Declines get by="agent:<model>"
                   and are flagged for human confirmation within 14 days.

The proposed change comes from the standard's own `## Apply` section when
present (a codemod or checklist), otherwise from the agent reading the
standard and the repo.

## `ds task` and `ds status`

`ds task "<text>"` creates a GitLab issue in the repo's project with label
`agent`, body = text + the repo's tags + the test command. The dispatcher
polls that label. `ds status` reads `DS_OPS.AGENT.TASKS` for this repo:
last 10 tasks, tier, result, MR link.

## Hooks

`pre-push`: `ds reconcile --check`. Prints pending items as one line each.
Never blocks a push for pending. Blocks only on broken pointers or a
malformed manifest. Must run in under one second offline.

## MCP server (`ds serve-mcp`)

Tools:

- `read_standard(id, version?) -> text`
- `manifest_status() -> {adopted: [...], declined: [{id, reason}], pending: [...]}`
- `graph_symbol(name)`, `graph_callers(name)`, `graph_blast_radius(name)`
  — thin wrappers over `.ds/graph.db`, or delegate to the chosen graph
  MCP if it is installed.

Stdio transport. Registered by `ds agent config` in CoCo and OpenCode.

## Backwards compatibility

None required. Future state only. `ds new` v2 produces v2 repos; v1 repos
are untouched and out of scope.

## Acceptance

- `ds new` on an empty dir produces a repo that passes `ds reconcile
  --check`, has a manifest with every applicable standard `adopted`, and
  has CoCo configured with the MCP servers.
- Bumping a standard's version in a local canon clone makes
  `ds reconcile --check` list it as pending within one push.
- `ds reconcile --interactive` records a decline with reason and revisit,
  and `ds canon list` shows it.
- `ds docs` renders every `[[id]]` in AGENTS.md.
- `ds serve-mcp` answers `read_standard("adr-000")` from CoCo.
