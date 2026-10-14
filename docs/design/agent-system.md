# The Agent System

Future state. Designed so the data scientists do not have to know it
exists.

## One sentence

Work gets done by the cheapest thing that can do it, and only the result
reaches a person.

## What a data scientist experiences

Nothing new to learn. They keep using Cortex Code the way they do today.
Three things are different, none of which they have to think about:

1. **CoCo is better in every repo.** `ds new` configured it: `--mode code`
   by default, the code graph and LSP wired in, the canon resolver
   available, AGENTS.md on one screen. CoCo answers faster, reads fewer
   files, and knows which standards apply. They notice it got cheaper
   only if someone shows them the bill.

2. **They can hand work off.** Two ways, both familiar:

       $ ds task "add tests for load_claims and make coverage > 80%"

   or label a GitLab issue `agent`. That is the entire API. The task
   shows up the next morning as an MR with a one-paragraph summary, or as
   a comment on the issue saying what blocked it and what it needs.

3. **A digest exists.** One Slack message per morning per team: what
   shipped overnight, what needs a human, one line each. Nobody has to
   read it.

That's it. No tiers, no models, no dispatcher, no CLM. Success arrives as
an MR; failure arrives as a question; everything in between is invisible.

## Design principles

- Defaults, not choices. If a data scientist is asked to pick a model,
  the system has failed.
- Results as MRs, not chat. The MR is the unit of delivery and review.
- Only two things reach a person: a finished thing to approve, or a
  specific question the system could not answer.
- Everything measured. One row per task: which tier closed it, tokens per
  tier, tool calls by tool, pass/fail, wall time. No number, no decision.
- Test-gated or not a task. A task without a mechanical pass/fail is
  routed to a person with a note, not attempted.

## Architecture

### Tiers

| Tier | What | Marginal cost | Used for |
|------|------|---------------|----------|
| T0 | Local worker: OpenCode headless, mlx-serve, Qwen3-Coder 30B-A3B | ~0 | execute the spec, run tests, retry |
| T1 | Mid: Sonnet-class via Cortex REST, or Codex | low | first escalation |
| T2 | Opus via Cortex Code Agent SDK, `--mode code` | high | plan (one call), review (one call), last resort |

T0 runs on whatever host is approved: a Mac on a desk, or nothing yet, in
which case T1 is the floor and the design is unchanged.

### The loop, per task

    queue ─▶ route ─▶ plan(T2) ─▶ execute(T0, N attempts) ─▶ rank ─▶ gate
                                                                     │
               ┌────────────── escalate(T1, then T2) ◀── fail ───────┤
               │                                                     │
               └─▶ review(T2, only if gate says so) ─▶ MR + summary ─▶ digest

- **route**: is it test-gated? which repo tags? which tier starts? Typed
  decisions, sub-100 ms, no LLM tokens.
- **plan**: one Opus call. Output: a short spec and the files that
  matter. The only place Opus sees raw context, and it's small.
- **execute**: OpenCode in a fresh git worktree, model pinned per repo,
  tools limited to file/shell/test plus the context stack. Local is free,
  so it runs the task several times.
- **rank**: the decision layer picks the best of N diffs.
- **gate**: high confidence and green tests → skip Opus review. Low
  confidence → review. Opus goes from two calls per task toward one.
- **escalate**: on repeated failure, send spec + diff + test output — never
  the repo — up one tier.
- **MR + summary**: the deliverable. Summary is one paragraph a human can
  read in ten seconds.

### Context stack (per repo, configured by `ds new`)

| Layer | Tool | Answers | Share of calls |
|-------|------|---------|----------------|
| Canon | `read_standard`, `manifest_status` | what rules apply here | first, always |
| Graph | tree-sitter → SQLite, MCP | what calls what, blast radius | ~70% |
| LSP | Serena | exact definitions, references, safe edits | ~25% |
| Semantic | Cortex Search over all repos, symbol-level | "have we solved this anywhere" | ~5% |

Agents read the manifest and AGENTS.md before touching code, then query the
graph before reading any file. Vector search is last, and it lives in
Snowflake because CI already puts it there.

### Decision layer (optional)

CLM — an open contrastive model, 8B encoder plus a 20M head — answers
typed questions: choose, score, true/false, with calibrated probabilities
in milliseconds. Used at route, rank, gate, and digest triage. Its head is
fine-tuned on this system's own metrics table (accepted vs rejected diffs)
once there is a month of data. Jev is the hosted equivalent; CLM is the
one that satisfies "Snowflake or local". Every use is replaceable by an
if-statement or a Sonnet call at higher cost; the design doesn't depend on
it.

### Harness

- **Dispatcher**: cron-driven Python in `agent-system/dispatcher/`. Pops a
  task, creates a worktree, runs the loop, opens the MR, writes the
  metrics row. A few hundred lines.
- **Queue**: GitLab issues labeled `agent`, plus `ds task`, which creates
  one.
- **Workers**: OpenCode headless. Anthropic-compatible wire to mlx-serve
  or an OpenAI-compatible wire to Cortex REST — same harness either way.
- **Opus**: Cortex Code Agent SDK, `--mode code`, called as a function:
  `plan(task) -> spec`, `review(diff) -> verdict`.
- **Memory** (later): Hermes as scheduler, cross-session memory, and Slack
  delivery, if the dispatcher turns out to want them. Not required.
- **Metrics**: SQLite locally, mirrored to `DS_OPS.AGENT.TASKS`. Cost by
  tier, by repo, by person, in one query.

### What runs where

| Piece | Host |
|-------|------|
| Dispatcher, queue polling, digest | any always-on box; the local host if one exists |
| T0 workers, graph, LSP | the local host |
| T1, T2 | Snowflake |
| Semantic index, metrics, adoption table, audits | Snowflake |
| CoCo for interactive work | the data scientist's laptop, configured by `ds` |

## What "seamless" costs

- `ds new` must configure CoCo and the MCP servers without asking. That
  is the single most important piece of glue.
- The MR summary must be good. A bad summary makes people open the diff,
  and then the system is just a slower colleague.
- The "needs you" message must be specific: not "task failed" but "I need
  the expected output for the 2024 cohort; the fixture is missing".
- Cost has to be reported to the manager, not the user. Users should never
  see a token count.

## Metrics row

    task_id, repo, task_type, created_at, closed_tier, local_attempts,
    escalations, tokens_t0, tokens_t1, tokens_t2, calls_canon,
    calls_graph, calls_lsp, calls_search, calls_file_read, tests_passed,
    gate_confidence, review_verdict, human_review_minutes, wall_seconds

## Non-goals

- A chat UI. CoCo already is one.
- Letting users pick models or tiers.
- Migrating old repos. The system works in repos born through `ds`.
- Depending on the local host. Without one, T1 is the floor and the design
  holds.
