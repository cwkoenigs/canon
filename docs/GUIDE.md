# The knowledge system: map and how to use it

What it is, what each piece does, how to set up a machine, and what to type on day one and every
day after. v0.2.0, 2026-10-28.

## In one paragraph

The team's standards, lessons and accepted code are written once, in **canon**. Every agent the
team uses (Cortex Code, Claude Code, Codex) reads them through one tool server, so the answers come
from the canon rather than the model's memory. **ds-next** is the terminal that drives those agents
and creates and checks repos. Every repo it creates or adopts points at the canon instead of
copying it, and is checked against it on every push. When a session learns something worth keeping,
it is captured as a draft and sent back to the canon as a merge request. The owner reviews it, and
the next push in every repo the change applies to shows it. Knowledge is written once, read
everywhere, and flows back to where it is written.

## The map

```text
                    ┌───────────────────────── canon ─────────────────────────┐
                    │ standards (*.md)   gotchas/   adr/   scaffolds/          │
                    │ blocks/ ──build──▶ lib/ = canon-lib (tag canon-lib-vX)  │
                    │ index.json (built) install.sh bootstrap.sh uninstall.sh  │
                    └───────┬──────────────────────┬──────────────────▲───────┘
                  reads     │           imports    │                  │ merge request
                            ▼           at a tag   ▼                  │ (/so-capture flush)
┌──────────────────────────────────┐   ┌────────────────────┐   ┌─────┴──────────────┐
│ ds-next: the terminal and the    │   │ every repo made    │   │ .ds/captures/*.md   │
│ `ds` tool server (`ds-next mcp`) │──▶│ with /new or       │   │ drafts in canon     │
│  /new /status /docs /captures    │   │ joined with adopt  │   │ format              │
└───┬──────────┬──────────┬────────┘   │ .ds/manifest.toml  │   └─────▲──────────────┘
    │ drives   │ attaches │ /docs      │ AGENTS.md [[ids]]  │         │ capture
    ▼          ▼          ▼            │ pre-push: reconcile│─────────┘
 Cortex     ds-code    docs-ds         └────────────────────┘
 Claude     (code      (renders a repo's docs, with every [[id]] linked to its standard)
 Codex       tools)
    ▲
    └── skills-os: how we work (/so-* procedures the agents follow)
```

## The pieces

| Repo | What it is | On disk | You touch it when |
|---|---|---|---|
| **canon** | The source of truth: standards, gotchas, ADRs, scaffolds, blocks, and canon-lib built from the blocks. Also the installer. | `~/Developer/canon` | You review or change a standard, accept a capture, release canon-lib |
| **ds-next** | The terminal (`ds-next`) and the `ds` tool server every agent reads the canon through (`ds-next mcp`). Python. | `~/Developer/ds-next`, `ds-next` in `~/.local/bin` | Every day: you run it |
| **skills-os** | The procedures agents follow: `/so-capture`, `/so-changes`, `/so-build-feature-interview`, `/so-bug-review-interview`, `/so-codex-review`, and others | `~/Developer/skills-os` | You change how the team works |
| **ds-code** | Eight read-only code tools (definition, references, callers, change impact…) from TypeScript's and Pyright's language servers. `ds-next setup` registers it with every agent as `code`; the terminal attaches it too. | `~/Developer/ds-code`, `ds-code` on PATH | Rarely: it updates with the installer |
| **docs-ds** | The Docusaurus shell behind `/docs` and the team portal. No content of its own; its theme is `design-system/tokens.json`. | `~/Developer/docs-ds` | You change the docs' look |
| **canon-lib** | Not a repo: the Python package in `canon/lib/`, built from `canon/blocks/`. New repos install it from git at its tag. | `canon/lib` | You accept a block, or release a new version |

Two files on every machine:

- **`~/.ds/config.toml`** holds what differs between home and work: which agent the terminal uses, where the team's repos live (`[world]`), and where captures go (`[capture]`). The installer writes it; edit it by hand when a machine's world changes.
- **`.ds/manifest.toml`**, in every connected repo, records which standards that repo adopted, declined (with a reason) or hasn't decided yet, plus the scaffold and blocks it came from.

## Set up a machine

It needs git and a terminal. The installer gets [uv](https://docs.astral.sh/uv/) if it's missing. Node.js 26 is for `/docs` and ds-code, and the agents are Cortex Code (`cortex`), Claude Code (`claude`) and Codex (`codex`): install whichever you use first, because the installer wires up the ones it finds.

**A new machine at work:**

1. In GitLab, create five **empty** projects (no README): `canon`, `ds-next`, `skills-os`, `docs-ds`, `ds-code`. Put them anywhere you can create projects, your own space or a team group, but all in the same place.
2. Run the installer with `TEAM_HOST` set to the address the five share, which is a project's address without its name. For `https://gitlab.example.com/you/canon`, that's `https://gitlab.example.com/you`:

   ```sh
   curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh \
     | TEAM_HOST=https://<your GitLab>/<where the projects are> bash
   ```

3. When it lists the projects that are empty and asks to push, say **yes**.

GitHub is only where the first download comes from. Each copy's remote is then switched to your
GitLab project, so nothing points back at GitHub: pulls, pushes, captures and new projects all
go to GitLab, and ds-next gets canon-lib from the local canon. To check, run
`git -C ~/Developer/canon remote -v`: it shows only GitLab. If the work computer shouldn't touch
GitHub at all, use the release folder of git bundles instead (below).

**At home:** the same line without `TEAM_HOST=…`. GitHub stays the home.

**A machine that already has the repos:** move them aside first, then run the same line. Moving
them keeps any unsaved work:

```sh
mkdir -p ~/old-Developer
for r in canon ds-next skills-os docs-ds ds-code; do [ -d ~/Developer/$r ] && mv ~/Developer/$r ~/old-Developer/; done
```

Or take the old install off first, `bash ~/Developer/canon/uninstall.sh --keep-config`, and run the
install line: that removes the clones too, except any with unsaved or unpushed work.

**A machine that can't reach GitHub:** use the release folder of git bundles (`ds-system-v0.2.0`).
Its DEPLOY.md has the same command with the bundles as sources.

What the installer does, in order:

1. Checks git, installs uv if missing, and reports Cortex Code and Node if they aren't found.
2. Clones canon, ds-next, skills-os, docs-ds and ds-code into `~/Developer`.
3. With `TEAM_HOST`, points every clone's `origin` at the team group. It offers to push any repo the group doesn't have yet. Say **yes**: that pushes `main` and the tags, including the `canon-lib-v…` tag new repos install from.
4. Writes `[world]` and `[capture]` into `~/.ds/config.toml`, unless that file already has a `[world]`.
5. Runs `canon/bootstrap.sh`, which:
   - installs and tests canon-lib and ds-next;
   - links `ds-next` into `~/.local/bin`;
   - installs docs-ds and ds-code;
   - wires every agent it finds: the `ds` and `code` tool servers, `/ds-new`, `/ds-terminal-design`, the `/so-*` skills, and the read-only tools approved.

**Check it worked:** the installer's last lines read `ds-next 0.2.0 at …` and `Done.`. Open a
**new** terminal (so `~/.local/bin` is on PATH) and run `ds-next`.

**If your GitLab group already had older copies** of canon or ds-next, the installer points at them
and doesn't push. Bring them up to date with `git -C ~/Developer/canon push origin main --tags`
(the same for ds-next). If that's rejected, the team copy has commits of its own: pull, merge, push.

## Day one

```sh
ds-next                       # the terminal, in any folder
```

| To | Type |
|---|---|
| Start a new project from an accepted scaffold | `/new`, pick one, fill the form, Enter. The model reviews your answers against the canon, then creates the repo. |
| Connect a repo that already exists | `cd` into it, then `/adopt`. This adds the manifest, AGENTS.md, DECISIONS.md and the pre-push hook. Nothing else changes. |
| See where a repo stands against the canon | `/status` |
| Read the standards | `/canon`, `/canon <id>`, `/canon python,cli` |
| See the team's procedures | `/skills`, `/skills <name>` |
| Have the agent follow one | `/so-<name> [context]`, e.g. `/so-build-feature-interview add a refund report` |
| Read this repo's docs with every standard linked | `/docs` (serves on a local port) |
| See drafts waiting to go back to the canon | `/captures` |
| Change speed/thinking | `/effort low\|medium\|high`, `/model` |
| Anything else | Type it: it's a turn with the agent |

Ctrl-C stops a turn and keeps the session. Ctrl-D leaves.

The accepted scaffolds `/new` offers: `python › cli`, `python › package`, `analysis`,
`ml-pipeline`, `streamlit-app`. A new repo gets:

- the code, with canon-lib as a dependency, pinned at its tag;
- a README and an AGENTS.md that point at standards as `[[id]]`, never copying their text;
- DECISIONS.md;
- `.ds/manifest.toml`;
- a pre-push hook that runs `ds-next reconcile`.

**What asks and what doesn't.** Tools that only read run without asking. That covers reading the canon, skills, blocks and scaffolds, `/status`, the code tools, and Snowflake search. Anything that writes asks first and shows the whole request: creating or adopting a repo, adding a block or code, a capture, and the agent's own shell commands and file edits. Answer with an explicit `y` (yes, once), `a` (yes to that tool for the rest of the session) or `n`; Enter alone asks again. No settings file skips this.

## Inside Cortex Code, Claude Code or Codex

The installer gives each agent the same `ds` tools, so you don't need ds-next open to use the
knowledge:

- `/ds-new` in an agent creates a project the same way `/new` does in the terminal.
- Asking "what's our standard for X", "is there accepted code for Y" or "what does this repo still need to adopt" makes the agent answer from the canon with `canon_list`, `canon_read`, `code_search`, `block_list` and `project_status`.
- The `/so-*` skills from skills-os are linked into the agents by the same setup.
- With ds-code installed, the agent also has the `code` tools (`ds-next setup` registers them). These are surer than text search for "who calls this" or "what does this change touch".

Another agent can attach the same tools with `ds-next mcp` (stdio MCP).

## Without the model (scripts, hooks, CI)

```sh
ds-next new NAME --answers answers.toml     # scaffold from an answers file
ds-next adopt [PATH] [--adopt-all]          # connect an existing repo
ds-next reconcile [PATH] [--quiet]          # check against the canon; exit 1 only on a broken pointer or bad manifest
ds-next blocks / ds-next add BLOCK          # list accepted code / add a block to this repo
ds-next canon list [--tags a,b] | canon read ID
ds-next docs [--out DIR]                    # build docs; outside a repo, the whole knowledge base
ds-next ask "PROMPT"                        # one agent turn, printed like the terminal
ds-next setup --agent cortex|claude|codex   # which agent the terminal drives (DS_AGENT overrides once)
```

## How knowledge flows back

1. **Capture.** When a session hits a hard-won fix, a surprising behaviour or a decision with trade-offs, say "capture this", or run `/so-capture`. A draft in the canon's format lands in the repo's `.ds/captures/`. Nothing leaves the machine yet.
2. **Review your drafts.** `/captures` in ds-next, or `/so-capture list`.
3. **Flush.** `/so-capture flush` opens one merge request on the canon with the drafts, wherever `~/.ds/config.toml` says: a GitLab MR at work, a GitHub PR at home. GitLab needs a token in the variable `token_env` names (`GITLAB_TOKEN`), or a `glab` login.
4. **The owner reviews** the MR: edits, narrows `applies_to`, sets `status`, bumps `version` if the meaning changed, runs `python scripts/build_index.py`, and merges.
5. **It reaches every repo by itself.** The next push in any repo whose tags match prints a one-line nudge (pending standards never block). `/status` there shows them; after reading one in `/docs`, `ds-next decide adopt <id>` or `ds-next decide decline <id> --reason "…"` records the answer in `.ds/manifest.toml`, a decline with a 90-day revisit by default. `decide adopt --all` takes every pending one, for a repo written under the standards.

Decisions local to one repo go in that repo's `DECISIONS.md` (`/so-changes adr`). Shipped
changes go in its `CHANGELOG.md` (`/so-changes changelog`).

## Changing the canon (owner)

| Change | How |
|---|---|
| A standard or gotcha | Edit the `.md`. Bump `version` when the meaning changes. `python scripts/build_index.py`, then commit `index.json` with it. A mechanical step goes under `## Apply`. |
| Accept a proposed one | Set `status: accepted`, rebuild the index, merge. |
| A block (accepted code) | Edit `blocks/<id>/code/`, its tests and `BLOCK.md`. Bump its version, run `python scripts/test_blocks.py`, then `python scripts/build_lib.py` (`--check` shows drift) and rebuild the index. Never edit a repo's copy. |
| Release canon-lib | Bump `lib/pyproject.toml`'s version, build, commit, tag `canon-lib-v<version>`, and push the tag to every host repos install from (`git push origin canon-lib-v<version>`). Repos move up by changing the tag in their `pyproject.toml`. |
| A scaffold | `scaffolds/<id>/`: `SCAFFOLD.md` and `files/`. Bump the version when a template changes; only `accepted` scaffolds appear in `/new`. |

## Install, update, reinstall, remove

One command knows them all. After a clone of canon, run it with nothing after it: it reports what the
machine has and offers the step that fits (install, update or remove), Enter takes it.

```sh
git clone https://github.com/cwkoenigs/canon ~/Developer/canon
bash ~/Developer/canon/ds-system             # status, then: install on a bare machine, update on an installed one, r removes
bash ~/Developer/canon/ds-system status      # the report alone
```

The verbs (`ds-system install | update | remove`) skip the menu and run the scripts below directly.
Every one is safe to run twice.

| | Command | What happens |
|---|---|---|
| **Install** | `curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh \| bash` | Clones the five repos, writes `~/.ds/config.toml`, runs `bootstrap.sh` (see "Set up a machine"). |
| **Update** | `bash ~/Developer/canon/bootstrap.sh` (or the install line again) | Pulls every repo that has an upstream, reinstalls and retests, rewires the agents. `~/.ds/config.toml` is kept. |
| **Reinstall** | `bash ~/Developer/canon/uninstall.sh --keep-config`, then the install line | A clean copy of everything, with your config. A clone with unsaved or unpushed work is kept and named: move it aside or push it, then rerun. |
| **Remove** | `bash ~/Developer/canon/uninstall.sh` | Unwires the agents (`ds-next setup --remove`: the `ds` and `code` servers, the skills, the allow rules), takes `ds-next` and `ds-code` off PATH, then asks before removing the clones and `~/.ds`. `--yes` skips the questions. |

What stays after a remove: uv, Node.js and the agent CLIs (yours, not the system's), and any clone the
script named as having work in it. To check an agent's wiring at any time: `ds-next setup --check`.

## Waiting on the owner

- **adr-001** (canon-lib carries the code, the tool server carries the knowledge) is still `proposed`.
- **adr-002** (the cross-repo graph: contracts declared in each manifest, compiled by the canon's pipeline into `index.json`, read by `project_status` and `change_impact`) is `proposed`. Built: the registry (`repos/`), the compiler (`scripts/build_repos.py`, run by the portal job), ds-next's and ds-code's manifests, ds-next's `repo_graph` and `reconcile` check, ds-code's `change_impact` section. All five repos are adopted and declare their contracts; the compiled graph has 53 edges, 47 of them declared and mentioned. The pipeline itself has not run on GitLab.
- **To review:** `block-tui-picker` (proposed), `gotcha-approvals` v4 and `gotcha-cortex-sdk` v4.
- Most standards are still `proposed`. Accepted so far: `repo-naming`, `terminal-design`, and the five scaffolds.
- canon has no CI of its own yet. Its checks run in the installer.

## When something's wrong

| Symptom | Cause and fix |
|---|---|
| `ds-next: command not found` | Open a new terminal, or add `~/.local/bin` to PATH. |
| A new repo's install fails fetching canon-lib at work | The `canon-lib-v…` tag isn't on the team's GitLab. Run `git -C ~/Developer/canon push origin --tags`. |
| A session starts and then hangs with no output | The agent's CLI isn't on PATH (Cortex says nothing when `cortex` is missing). Install it, or `ds-next setup --agent claude`. |
| Cortex asks about a repo's hooks before starting | That repo's settings define hooks that would run commands. Read them, then answer. This is on purpose. |
| `ds-code: permission denied`, or an agent has no `code` tools | An older ds-code build; `bash ~/Developer/canon/bootstrap.sh` rebuilds it and rewires the agents (`ds-next setup` alone does the wiring). |
| `/docs` fails | Node.js 26 isn't installed, or docs-ds wasn't installed: rerun the installer after installing Node. |
| `/so-capture flush` can't open an MR | No GitLab token in `$GITLAB_TOKEN` (or no `glab` login), or `[world]` in `~/.ds/config.toml` names the wrong group. |
| `/status` shows many pending standards | Expected on a new or adopted repo. Read each in `/docs`, then `ds-next decide adopt <ids>` or `decide decline <id> --reason "…"`; `decide adopt --all` for a repo written under them. Pending never blocks a push. |

## Read more

- `canon/README.md` (this guide is `canon/docs/GUIDE.md`): how standards, gotchas, blocks and scaffolds are written.
- `canon/adr/adr-000-knowledge-system.md`, `adr-001-ship-canon-lib.md` and `adr-002-cross-repo-graph.md`: why it's built this way, and what comes next.
- `ds-next/README.md`: the terminal in detail, and what was learned building against Cortex Code.
- `skills-os/README.md`: every procedure.
- `ds-code/README.md`: the code tools.
- `docs-ds/README.md`: the docs shell and its theme.
