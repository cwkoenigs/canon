# BUILD.md — Overnight Build Brief

You are building the platform described in this directory. Work
unattended. Clark reads `BUILD-REPORT.md` in the morning. Everything you
produce must be runnable and verified by a command before you call it
done; anything you could not verify goes in the report as "unverified",
never as "done".

## Read first, in this order

1. `docs/knowledge-system.md` — what the system is and how people meet it.
2. `docs/agent-system.md` — the harness, tiers, context stack, seamlessness.
3. `docs/ds-cli-updates.md` — the spec you are implementing in `ds`.
4. `bench/README.md` — the benchmark you will run to prove it.
5. `adr-000-knowledge-system.md` if present — the original design record.

Do not redesign. Where the docs are silent, choose the simplest thing and
write the choice down in the report under "Decisions I made".

## Ground rules

- Future state only. No migration of existing repos, no backwards
  compatibility shims. `ds new` v2 makes v2 repos.
- Python 3.12, typer, uv. No new frameworks. No devcontainers.
- Every emitted file carries provenance comments (`<!-- ds:local … -->`,
  `<!-- ds:inherited … -->`, `<!-- ds:derived … -->`).
- Snowflake or local. Nothing calls a third-party hosted model. If a piece
  needs a model, take it from `--model` and default to Cortex Code
  (`cortex --print --mode code`) when available, else skip that piece
  and note it.
- Deterministic pieces first, model-dependent pieces last.
- Commit after each deliverable with a message naming it. Never force-push.
- If something takes more than 90 minutes, stop, write what you have and
  what blocked you, and move to the next deliverable.

## Deliverables, in order

### D1. `canon/` — the standards repo (30 min)

Create `canon/` as a real repo, seeded from `bench/bench/canon.py`
`STANDARDS` (adr-000, layout, naming, glossary, adr-014, adr-015,
adr-016) plus:

- `scripts/build_index.py` → `index.json` (id, version, hash, title,
  applies_to, supersedes, owner, path). Same schema as the bench's.
- `.gitlab-ci.yml` that rebuilds `index.json` on merge to main and fails
  if a standard's front matter is missing `id`, `version`, `applies_to`,
  `owner`.
- `README.md`: three paragraphs — what canon is, how to propose a
  standard, how a standard reaches repos. Nothing else.

Verify: `python scripts/build_index.py && python -c "import json; json.load(open('index.json'))"`.

### D2. `ds` — canon client, manifest, reconcile --check (2 h)

In the existing `ds` repo (or `ds/` here if that is where you were
pointed), implement per `docs/ds-cli-updates.md`:

- `ds/canon/client.py`: fetch `index.json` from a configurable path or
  URL (`DS_CANON` env, default `../canon`), cache under `~/.ds/canon/`,
  `resolve(id, version=None) -> text`, `applicable(tags) -> [standard]`.
- `ds/canon/manifest.py`: load/validate/write `.ds/manifest.toml`.
  Validation: required fields, `declined` requires `reason` and `revisit`,
  unknown ids are errors.
- `ds/canon/reconcile.py` + `ds reconcile --check`: offline; lists
  pending; regenerates the derived block; exit 1 only on broken pointer
  or malformed manifest. Must run in under one second.
- `ds canon list`, `ds canon read <id>`.
- `ds docs`: print README.md and AGENTS.md with `[[id]]` resolved inline.

Verify: on a `bench init` system repo, `ds reconcile --check` prints 0
pending; after `bench drift`, it prints the same pending list `bench
reconcile` prints. Add a test that asserts this.

### D3. `ds new` — the interview (2 h)

- `ds/interview/questions.py`: the eight questions from the spec with
  inferred defaults (git user, detected test command from
  pyproject/Makefile, tags from file types).
- `ds/interview/render.py`: answers → README.md, AGENTS.md, DECISIONS.md,
  `.ds/manifest.toml` (every applicable standard `adopted` at current
  version), `.ds/interview.md`. Only sections the answers justify.
- `ds hooks install`: writes `.git/hooks/pre-push` calling
  `ds reconcile --check`; idempotent.
- `ds new` runs interview → render → hooks → `ds agent config` (D5, stub
  it if D5 isn't done: write `.ds/agent.toml` with defaults and stop).
- Non-interactive mode: `ds new --answers answers.toml` for tests and for
  the overnight run.

Verify: `ds new --answers tests/fixtures/answers.toml demo && cd demo &&
ds reconcile --check` exits 0 with 0 pending. AGENTS.md is under 40 lines.

### D4. `ds reconcile --interactive` and `--apply` (1.5 h)

- `--interactive`: per pending item, show title, why it applies, the
  standard's `## Apply` section; `[a]dopt [d]ecline [s]kip [r]ead`.
  Adopt runs the test command and updates the manifest; decline records
  reason + revisit (default 90 days).
- `--apply`: unattended. If a model is available (`cortex --print`),
  ask it to apply the `## Apply` section in the repo, run tests, adopt on
  green, decline with `by = "agent:<model>"` on red. If no model,
  `--apply` only adopts standards whose `## Apply` section is empty
  (documentation-only) and leaves the rest pending. Say which in the
  report.

Verify: a decline round-trips through `ds canon list`; an adopt bumps the
manifest version; both leave `ds reconcile --check` at exit 0.

### D5. `ds agent config` + `ds serve-mcp` (2 h)

- Write CoCo repo settings for `--mode code` and register MCP servers.
  Look up the current CoCo settings file format with `cortex --help` and
  the docs; if you cannot determine it, write `.ds/coco-settings.json`
  with your best guess and mark it unverified.
- `ds serve-mcp`: stdio MCP server exposing `read_standard(id, version?)`
  and `manifest_status()`. Graph tools: if `codebase-memory-mcp` or
  equivalent is installed, delegate; otherwise expose
  `graph_symbols(path)` backed by the AST walker from `bench/repos.py`
  `public_symbols`, and say so.
- `.ds/agent.toml`: T0 model, max attempts, context window, token budget,
  from defaults in `docs/agent-system.md`.

Verify: an MCP client (write a 20-line stdio test) calls
`read_standard("adr-000")` and gets the text.

### D6. Dispatcher skeleton (2 h)

`agent-system/dispatcher/`:

- `queue.py`: read tasks from a local `TASKS.yaml` (same schema as
  `bench/tasks.yaml`); GitLab adapter stubbed with the interface and a
  TODO.
- `worktree.py`: create/clean a git worktree per task.
- `ladder.py`: T0 → T1 → T2 with attempts and escalation payload (spec,
  diff, test output; never the repo). Tiers are shell commands from
  `.ds/agent.toml`; `dry` tier for tests.
- `metrics.py`: SQLite with the row from `docs/agent-system.md`; a
  `to_snowflake.sql` DDL for the mirror.
- `run.py`: `python -m dispatcher.run --once` processes the queue once.
- `digest.py`: prints the morning digest from the metrics DB; Slack
  posting stubbed.

Verify: `--once` against a bench repo with the `dry` tier writes one
metrics row per task and a digest.

### D7. Run the benchmark (as long as it takes, but start it by hour 8)

    bench init ./sb
    bench run ./sb --variant mash   --runner dry --tasks-only
    bench run ./sb --variant system --runner dry --tasks-only
    # if cortex is available:
    bench run ./sb --variant mash   --runner coco
    bench run ./sb --variant system --runner coco
    # if a local or mid-tier endpoint is configured in opencode:
    bench run ./sb --variant system --runner opencode --model <it>
    bench run ./sb --variant mash   --runner opencode --model <it>
    bench drift ./sb --n 15
    bench reconcile ./sb
    bench score ./sb

Copy `sb/report.md` into `BUILD-REPORT.md`. If a runner isn't available,
say so; do not fake rows.

### D8. `BUILD-REPORT.md`

Sections, in this order:

1. What is done and verified (one line per deliverable, with the verify
   command and its output's last line).
2. What is done but unverified, and why.
3. What is not done, and where you stopped.
4. Decisions I made (things the docs didn't specify).
5. The benchmark table, or why there isn't one.
6. Three things Clark should look at first, in priority order.
7. Total wall time, and rough token spend if you can see it.

Keep it under two screens. No prose about how hard it was.

## Definition of done

- `ds new` (non-interactive) → repo → `ds reconcile --check` exit 0.
- `bench drift` → `ds reconcile --check` lists pending; `--interactive`
  or `--apply` clears at least one.
- `ds serve-mcp` answers `read_standard`.
- Dispatcher `--once` with the dry tier writes metrics and a digest.
- `BUILD-REPORT.md` exists and is honest.

## What to leave for the morning

Anything that needs Clark's account: Cortex Code SDK access, GitLab
tokens, Slack webhooks, the Snowflake mirror. Stub the interface, write
the TODO with exactly what credential or decision is needed, and move on.
