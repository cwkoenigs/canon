# The knowledge system

The whole system in one document: what it is, how a machine gets it and loses it, how a repository
joins, how standards reach repositories, how repositories know about each other, what every tool
answers, and what is not built yet. Written for someone who has never used it. The decisions behind
each part are the ADRs in `adr/`; this guide says what is, they say why.

Current as of 2026-11-02: ds-next 0.2.0, ds-code 0.1.0, canon-lib 0.2.0, 36 standards, five
accepted project types, five registered repositories.

## In one paragraph

The team's rules, lessons and accepted code are written once, in **canon**. Every repository points
at them instead of copying them, and is checked against them on every push. A standard is in force in
every repository it applies to unless that repository declined it with a reason, so rolling one out
is writing it. Every agent the team uses (Claude Code, Cortex Code, Codex) reads the canon through one
tool server, so answers come from the canon rather than the model's memory, and reads code through a
second one answered by real language servers. Each repository declares what it offers other
repositories and what it uses from them, and the canon compiles who depends on whom, so a change
shows which other repositories it touches before it is finished. What a session learns is captured
and sent back to the canon for review. One command installs, updates or removes all of it on a
machine.

## The five repositories

| Repository | What it is | You touch it when |
|---|---|---|
| **canon** | The source of truth: standards, gotchas, ADRs, project types (scaffolds), accepted code (blocks, built into the canon-lib package), the registry of repositories, and `index.json`, compiled from all of them. Also the install, update and remove scripts. | You write or review a standard, register a repository, release canon-lib |
| **ds-next** | The terminal (`ds-next`) and the `ds` tool server every agent reads the canon through (`ds-next mcp`). Python. | Every day: you run it, or your agent calls it |
| **ds-code** | The `code` tool server: eight read-only tools (definitions, references, callers, change impact…) answered by TypeScript's and Pyright's language servers. Node. | Rarely: it updates with everything else |
| **skills-os** | The procedures agents follow, as `/so-*` skills: capture, changes, feature and bug interviews, external review, and others. | You change how the team works |
| **docs-ds** | The Docusaurus shell that renders a repository's docs, or the whole canon, in the browser (`/docs`), and the team portal. No content of its own. | You change how the docs look |

On a machine they live side by side in `~/Developer`. Two files hold everything else:

- **`~/.ds/config.toml`**, one per machine: where the team's repositories live (`[world]`: GitHub at
  home, the team's GitLab group at work), where captures go (`[capture]`), and which agent the terminal
  drives. The installer writes it once; edit it by hand when a machine changes worlds.
- **`.ds/manifest.toml`**, one per repository: its name, tags, test and lint commands, the scaffold
  and blocks it came from, any decision on a standard someone typed, and what it provides to and uses
  from other repositories.

## How the pieces connect

```text
                  ┌──────────────────────────── canon ────────────────────────────┐
                  │ standards  gotchas/  adr/  scaffolds/  blocks/ ─build─▶ lib/   │
                  │ repos/<name>.toml (the registry)                               │
                  │ index.json: standards, scaffolds, blocks, code,                │
                  │             repos (who uses whom), adoption (who follows what) │
                  │ ds-system  install.sh  bootstrap.sh  uninstall.sh              │
                  └──────┬───────────────────────────────┬──────────────────▲─────┘
              reads      │                    points at  │                  │ merge request
              index.json │                    [[ids]],   │                  │ (/so-capture flush)
                         ▼                    imports    ▼                  │
┌────────────────────────────────────┐       canon-lib  ┌────────────────────┴──────┐
│ ds-next                            │                  │ every repository          │
│  terminal: /new /adopt /status ... │─── creates, ───▶ │  .ds/manifest.toml        │
│  `ds` tool server (ds-next mcp)    │    adopts,       │  AGENTS.md  DECISIONS.md  │
│  reconcile · decide · setup        │    checks        │  pre-push: reconcile      │
└───┬──────────────┬─────────────┬───┘                  │  .ds/captures/ (drafts)   │
    │ wires        │ registers   │ /docs                └───────────────────────────┘
    ▼              ▼             ▼
 Claude Code    ds-code       docs-ds
 Cortex Code    (`code`       (the canon and a repo's docs
 Codex           tools)        in the browser)
    ▲
    └── skills-os: /so-* procedures the agents follow
```

## A machine: install, update, remove

One command does all three. Clone the canon, then run it:

```sh
git clone https://github.com/cwkoenigs/canon ~/Developer/canon
bash ~/Developer/canon/ds-system --github
```

That is a personal machine. On a managed work Mac the clone comes from the team's GitLab and the
flag is left off (see "Which mode" below). After the first install every run is just
`bash ~/Developer/canon/ds-system`: the machine remembers its mode.

It reports what the machine has (the five clones, `ds-next` and `ds-code` on PATH, each agent's
wiring, the config) and offers the one step that fits: **install** on a bare machine, **update** on an
installed one, **r** to remove. Enter takes the offer. The verbs skip the menu:
`ds-system status | install | update | remove`. Every step is safe to run twice.

### Which mode

| Machine | Clone canon from | Run | What it means |
|---|---|---|---|
| **Personal** | GitHub | `ds-system --github` | GitHub is the home. No question asked; uv is installed if missing. |
| **Managed work Mac** | the team's GitLab | `ds-system` (or `--work-safe`) | **Work-safe**: nothing downloaded (uv, Python 3.12, Node.js and the agents come from Self Service first), only the team's GitLab, nothing pushed, only lockfile versions, no npm install scripts, nothing written outside your home folder. A canon that did not come from GitHub chooses this by itself. [security-review.md](security-review.md) is the page for a security team. |
| **Unmanaged work machine** | GitHub | `TEAM_HOST=<group address> bash ~/Developer/canon/ds-system` | Starts from GitHub, then points every clone at the team's GitLab and offers to push projects the group does not have yet. |

The mode is saved in `~/.ds/config.toml` (`install = "github"` or `"work-safe"`), and every later
install and update keeps it. A flag that contradicts it stops the run and names the line to edit, so
a managed Mac is never quietly switched out of work-safe.

It needs git and a terminal. uv is installed if missing (except in work-safe mode). Node.js 26 is
needed for `ds-code` and `/docs`. Install the agents you use (`claude`, `cortex`, `codex`) first:
setup wires the ones it finds.

| Step | What it does |
|---|---|
| **Install** | Clones the other four repositories beside the canon, from where the mode says. With no mode it asks one question, where the team's repositories live: Enter keeps GitHub, a group address points every clone there. Writes `~/.ds/config.toml` with the mode, then runs the update. |
| **Update** | Pulls every repository that has an upstream; installs and tests canon-lib and ds-next; links `ds-next` into `~/.local/bin`; builds docs-ds and ds-code and links `ds-code` (into `~/.local/bin` in work-safe mode); then wires every agent on PATH: the `ds` and `code` servers, the `/ds-new`, `/ds-terminal-design` and `/so-*` skills, and an allow rule for every read-only tool. Asks nothing. |
| **Remove** | Unwires every agent (`ds-next setup --remove`: only what setup registered; anything else of the same name is left alone), takes `ds-next` and `ds-code` off PATH, then asks before deleting the clones and `~/.ds`. A clone with uncommitted changes, a stash, a branch without an upstream or unpushed commits stays and is named. If unwiring fails, no clone is removed. `--yes` answers the questions; `--keep-repos` and `--keep-config` keep those. |

After any step, open a new terminal so `~/.local/bin` is on PATH, and restart any agent session that
was open so it sees the tools. `ds-next setup --check` shows an agent's wiring without changing it.
Removing leaves uv, Node.js and the agent CLIs: they are yours, not the system's.

**Snowflake, once per person.** Cortex Code signs in to Snowflake with SSO, which opens a browser for
every session and every search. `ds-next auth login` (or `/auth` in the terminal) signs in that way
once, mints a personal access token restricted to the role you land on (or `--role`), and keeps it in
the macOS Keychain; from then on every Cortex session and search ds-next starts runs on it, with no
browser, and the agent is refused any read of it. Account and user come from your own
`~/.snowflake/connections.toml`. `ds-next auth status` says which way sessions sign in and why; the
terminal's banner shows the same on its `snowflake` line. Until you sign in, SSO as before. The
Snowflake side (a network policy, an authentication policy allowing tokens, a role to restrict them
to) is one-time administrator work: `ds-next/docs/snowflake-pat-setup.sql`.

**Setting up the team's GitLab, once.** Create five empty projects (no README) in one group:
`canon`, `ds-next`, `skills-os`, `docs-ds`, `ds-code`, and push the five repositories there from a
machine that has them (`git -C ~/Developer/<repo> push <group address>/<repo>.git main --tags`).
Work-safe installs never push, so the group must have them before the first managed Mac installs.

The install scripts are bash and have been run on macOS. ds-next and ds-code are tested on macOS and
Windows in CI; installing on Windows by these scripts is not.

**From the web, on a bare personal machine.** The installer also runs without a clone first:
`curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh | bash -s -- --github`.
Never on a managed Mac: work-safe mode is clone, read, run.

## Every day

### The terminal

`ds-next` in any folder opens the terminal, a session with your agent plus these commands:

| Command | What it does | Asks first |
|---|---|---|
| `/new` | Pick an accepted project type, fill one form; the agent checks the answers against the canon, then creates the repository | yes, once |
| `/adopt` | Bring the repository you are in into the system (see "A repository joins") | yes |
| `/status` | Where this repository stands: standards in force, declined, waiting, and any error | no |
| `/canon`, `/canon <id>`, `/canon python,cli` | List the standards, read one, or list those that apply to some tags | no |
| `/skills`, `/skills <name>` | List the procedures, or read one | no |
| `/so-<name> [context]` | The agent follows that procedure, e.g. `/so-build-feature-interview add a refund report` | yes |
| `/docs` | Render this repository's docs (or, outside a repository, the whole canon) and serve them in the browser | no |
| `/captures` | Drafts waiting to go back to the canon | no |
| `/last`, `/model`, `/effort`, `/clear`, `/help`, `/exit` | The last tool output in full, the model, thinking effort, a fresh session, help, leave | no |

Anything else is a turn with the agent. Ctrl-C stops a turn and keeps the session; Ctrl-D leaves.

**What asks and what does not.** A tool that only reads runs without asking. A tool that writes shows
the whole request and waits for an explicit `y` (yes, once), `a` (yes to that tool for the rest of the
session) or `n`. Enter alone asks again, and no settings file skips the question.

### Inside Claude Code, Cortex Code or Codex

The same tools are in every agent, so the terminal is optional. Ask in plain words ("what's our
standard for retries", "is there accepted code for reading a manifest", "who uses this command") and
the agent answers from the tools.

**`ds`**, the canon (from `ds-next mcp`):

| Reads, never asks | Writes, always asks |
|---|---|
| `canon_list`, `canon_read`: the standards and gotchas, each with its default and how many repositories follow it | `scaffold_project`: create a repository from a project type |
| `skills_list`, `skill_read`: the procedures | `adopt_repo`: bring a repository into the system |
| `project_status`: this repository's standing, its contracts and who uses them | `decide_standard`: record a decline, or an answer to a standard that asks |
| `repo_graph`: who provides and who uses a command, name or path, across every registered repository | `block_add`, `code_add`: copy accepted code into the repository |
| `scaffold_list`, `scaffold_get`, `block_list`, `block_get`, `code_search`, `code_get`: project types and accepted code | `capture`: draft a lesson for the canon |
| `snowflake_search`: Snowflake docs and catalog | |

**`code`**, the code (from `ds-code mcp`), all read-only: `repo_overview` to learn a repository,
`file_symbols` before reading a file, `find_symbol` and `definition` for where something is defined,
`references` and `callers` before changing or removing anything, `callees`, and `change_impact` before
finishing a change. `change_impact` lists each changed symbol and everything that uses it, the files
that depend on the change, and, last, the contracts other repositories use that the change touches.

`/ds-new` in an agent creates a project the same way `/new` does. The `/so-*` skills are linked into
every agent. Any other MCP client can attach the same servers with `ds-next mcp` and `ds-code mcp`.

### Without the model: scripts, hooks, CI

```sh
ds-next new NAME --answers answers.toml     # create a repository from an answers file
ds-next adopt [PATH] [--tags a,b]           # bring an existing repository in
ds-next reconcile [PATH] [--quiet]          # check against the canon; exit 1 only on an error
ds-next decide decline ID --reason "…"      # record an exception (see "Standards")
ds-next canon list [--tags a,b] | canon read ID
ds-next blocks | ds-next add BLOCK          # accepted code: list, add to this repository
ds-next docs [--out DIR]                    # build the docs without serving
ds-next ask "PROMPT"                        # one agent turn, printed like the terminal
ds-next setup [--check | --remove] [--agent claude|cortex|codex|auto]
ds-next auth login [--paste] | status | rotate | logout   # Snowflake without a browser (see below)
```

## A repository joins

A repository made with `/new` is in the system from its first commit. An existing one joins with:

```sh
cd path/to/repo && ds-next adopt .
```

It reads what the files say: tags from the stack (`package.json`, `pyproject.toml`, `dbt_project.yml`,
`Dockerfile`), the test and lint commands from the project's own scripts, the purpose from the
README's first sentence, the owner from git. It writes four things and changes nothing else:

- `.ds/manifest.toml`;
- a standards section in `AGENTS.md`, or a new `AGENTS.md`, pointing at each standard as `[[id]]`;
- `DECISIONS.md`, if there is none;
- a pre-push hook that runs `ds-next reconcile --quiet`. A hook that was there before runs first.

It needs a git repository, a purpose and at least one tag. A repository of prose and shell has no
stack to detect: pass the tags (`--tags docs,bash`). Tags decide which standards apply, so choose
them as you would want the repository judged.

To appear in the cross-repository graph, a repository also needs its registry file in the canon,
`repos/<name>.toml`, added by merge request (its name and `group/project`), and the two tables below
in its manifest. `adopt` does not write the registry file yet.

## Standards: how they reach every repository

A standard is a Markdown file in the canon with an `id`, a `version` that only goes up, the tags it
`applies_to`, an `owner`, and a `default`:

- **`default: adopt`**: in force in every repository it applies to, unless that repository declined
  it. Nobody types anything. Every standard today is `adopt`: they are the team's rules.
- **`default: ask`**: waits for an answer from each repository's owner. For the few standards that
  are a real choice per repository.

`ds-next reconcile` works out a repository's standing from three things: the standards that apply to
its tags, their defaults, and what its manifest records. A decision someone typed wins. A decline
answers the version it was made against, so a new version asks the decliner again. An older explicit
adoption of a `default: adopt` standard carries forward: the team changed the rule, and the
repository follows unless it declines. `/status` and `reconcile` print the count, always saying how
many are in force by default:

```text
✓ ds-code  27 adopted (27 by default) · 0 declined · 0 pending
```

**Rolling out a standard** is writing it, setting its default and merging. From the next index, every
repository it applies to is held to it, and every machine's next push says so. There is no
announcement and no migration.

**An exception** is the only thing anyone types. Read the standard first (`/docs` in the terminal
renders the canon in the browser; `ds-next canon read <id>` prints one), then:

```sh
ds-next decide decline cicd --reason "no runner for this repository yet"   # revisit in 90 days unless --revisit
ds-next decide adopt <id…>                  # answer a standard whose default is ask
ds-next decide adopt --all                  # answer every one that asks
```

`decide` checks everything before it writes: an unknown id, a decline without a reason or a bad date
writes nothing. In a session, ask the agent; it records your answer with `decide_standard`, and it is
told never to decide on its own judgement.

**Pending never blocks a push.** The hook fails only on a broken `[[id]]` pointer, a malformed
manifest, or a `[uses]` entry that names nothing a provider declares (next section).

**Adopted means held to the standard, not that the repository complies.** Checking compliance is an
agent's job that is not built (see "Built and not built").

## Repositories that depend on each other

The edges between repositories are rarely imports, so no language server sees them: a script runs
another repository's command, a tool reads another's file, two repositories must agree on a name.
Each repository declares its side in its manifest, in the words the other side writes:

```toml
[provides]                 # what other repositories run, read or share
commands = ["ds-next setup [--remove|--check]", "ds-next mcp"]
names    = ["mcp__ds__*"]
paths    = ["skills/*/SKILL.md"]

[uses]                     # one key per registered repository, in the words its [provides] uses
canon   = ["index.json", "canon-lib"]
ds-code = ["ds-code mcp", "change_impact"]
```

Declare words that are distinctive: entries are matched as text, so `status` would match every
sentence with that word in it. A `[bracketed part]` is optional and a trailing `*` is a prefix.

The canon compiles the rest. `scripts/build_repos.py` reads every registered repository's manifest,
searches the other repositories for each provided entry, and writes the `repos` section of
`index.json`: every edge, declared or found or both, with file and line, and a report of contracts
nobody uses, uses nobody declared, and declarations that name nothing. A mention of a file the
mentioning repository has itself (its own `install.sh`) counts as its own, not another's. On a machine
with the clones side by side, it runs in under a second:

```sh
python ~/Developer/canon/scripts/build_repos.py ~/Developer           # print the graph and the report
python ~/Developer/canon/scripts/build_repos.py ~/Developer --write   # and write it into index.json
```

Where it is read:

- **`change_impact`** ends with the contracts the change touches and who uses each:
  ```text
  Across repos (canon graph compiled 2026-10-30): the change touches what other repositories use
    ds-next setup [--remove|--check]  used by canon (README.md:61, adr/adr-002-cross-repo-graph.md:33, …)
  ```
- **`repo_graph`** answers by repository (what it provides, uses, and is used by) or by text (who
  provides `ds-code mcp`, and who uses it).
- **`project_status`** carries the repository's graph.
- **`reconcile`** checks every `[uses]` entry against the provider's `[provides]`. A renamed command
  fails the consumer's next push, with the provider's list in the message. A use pointing at a
  repository that declares nothing yet is a note, not an error.

`ds-next mcp` fast-forwards the canon clone when an agent starts it, so a session reads the latest
index; a machine that cannot reach the host says so once and goes on with what it has.

## The team-wide view

The same compile computes every standard's standing in every registered repository and writes it as
the `adoption` section of `index.json`. Nothing is written into any repository, so the view costs the
same at ten thousand repositories as at five.

- `ds-next canon list` and the agent's `canon_list` show each standard's row, for example
  `testing  1  adopt  *  Testing and QA · 5 repos adopted, 0 declined, 0 pending`.
- `project_status` shows a repository's row.
- The declines, with their reasons, are listed per standard: the honest list of where the rules do
  not hold, and why.

Today: 36 standards across five repositories, 128 adoptions, 112 of them by default, no declines,
nothing pending.

## Knowledge flowing back

1. **Capture.** When a session hits a hard-won fix, a surprise or a decision with trade-offs, say
   "capture this" or run `/so-capture`. A draft in the canon's format lands in the repository's
   `.ds/captures/`. Nothing leaves the machine.
2. **Review your drafts** with `/captures` or `/so-capture list`.
3. **Flush.** `/so-capture flush` opens one merge request on the canon with the drafts: a GitLab
   merge request at work, a GitHub pull request at home, per `~/.ds/config.toml`. GitLab needs a token
   in the variable `[world] token_env` names (usually `GITLAB_TOKEN`), or a `glab` login.
4. **The owner reviews** it: edits, narrows `applies_to`, sets the default and the status, and merges.
5. **It reaches every repository by itself**, as any standard does.

Decisions local to one repository go in its `DECISIONS.md` (`/so-changes adr`); shipped changes in
its `CHANGELOG.md` (`/so-changes changelog`).

## Changing the canon

| Change | How |
|---|---|
| A standard or gotcha | Edit the file. Bump `version` when the meaning changes. Set `default`. Run `python scripts/build_index.py` and commit `index.json` with it. A mechanical step goes under an `## Apply` heading. |
| Accept a proposed one | Set `status: accepted`, rebuild the index, merge. |
| Register or retire a repository | Add or delete `repos/<name>.toml`. |
| A block (accepted code) | Edit `blocks/<id>/` (code, tests, `BLOCK.md`), bump its version, `python scripts/test_blocks.py`, `python scripts/build_lib.py` (`--check` shows drift), rebuild the index. Never edit a repository's copy. |
| Release canon-lib | Bump `lib/pyproject.toml`, build, commit, tag `canon-lib-v<version>`, push the tag everywhere repositories install from. Repositories move by changing the tag in their `pyproject.toml`. |
| A project type | `scaffolds/<id>/`: `SCAFFOLD.md` and `files/`. Bump the version when a template changes; only `accepted` ones appear in `/new`. |
| The graph and the team-wide view | `python scripts/build_repos.py <checkouts> --write`; the pipeline does this when it runs. |

`python scripts/build_index.py --check` fails on a stale index or a malformed standard; it is what
the pipeline's check job runs on every merge request.

## The pipeline

`.gitlab-ci.yml` in the canon has two jobs. `check_index` refuses a stale index or a malformed
standard on every merge request. `portal`, on `main` and on a schedule, clones every registered
repository, builds the team portal with docs-ds, compiles the graph and the team-wide view into
`index.json`, and commits that back to `main`. With it running, every machine's next session reads
who uses whom and who follows what, without anyone running anything.

**It has never run.** It needs, on the team's GitLab: a runner and its tag in place of
`<docs-runner-tag>`; a project access token with `write_repository` as `CANON_PUSH_TOKEN`; and the
canon's job token allowed to clone every registered project. Until then, one person runs the compile
on a machine with the clones and commits the result. The step that publishes the portal to Snowflake
is written as comments and is unverified.

## Built and not built

Built, tested, and running on the owner's machine:

- install, update and remove behind one command, with removal that never deletes unsaved work;
- the `ds` and `code` tool servers in Claude Code, Cortex Code and Codex, read-only tools approved;
- creating and adopting repositories; the pre-push check;
- standards in force by default, exceptions with `decide`, the team-wide view;
- the cross-repository graph, read by `change_impact`, `repo_graph`, `project_status` and `reconcile`;
- Snowflake without a browser: `ds-next auth login` once, then every Cortex session and search runs on
  a token in the Keychain that the agent cannot read (ds-next local-025).

Not built, or not yet true:

- **The Snowflake token flow has not run against a real account.** It is tested against a scripted
  Snowflake and the Cortex Code binary was read for what it honours; the first real `auth login`, and
  whether the account's policies let a person mint their own token, are the owner's to see.

- **The pipeline has never run** (above), so the graph and the team-wide view are as fresh as the
  last manual compile.
- **Compliance is unchecked.** Adopted means held to; whether a repository follows a standard is the
  unattended agent step [[adr-000]] describes, not built.
- **`adopt` does not register a repository** in `repos/`; that is a merge request by hand.
- **Inherited text is not regenerated.** A repository's `AGENTS.md` standards section is written once,
  when it joins; a new standard or a changed sentence reaches it only if someone edits it.
- **The terminal does not fast-forward the canon;** agents started through `ds-next mcp` do.
- **Most standards are `proposed`.** Accepted: `repo-naming` and `terminal-design`, and the five
  project types. ADR-000 to ADR-003 are all `proposed`.
- **The offline bundle folder** (`ds-system-v0.2.0`, for a machine that cannot reach GitHub) dates
  from 2026-10-28 and predates everything in this guide after the install; a new one needs cutting.
- **Windows** is tested for ds-next and ds-code, not for the install scripts.
- **`/docs` in work-safe mode is untested.** docs-ds installs without npm install scripts; whether
  it then renders needs a real `/docs` run on a managed Mac.
- **ds-next's Python packages are pinned by version, not by hash,** in work-safe mode. canon-lib's
  and every npm package's hashes are checked; ds-next's are not yet.

## When something is wrong

| Symptom | Cause and fix |
|---|---|
| `ds-next: command not found` | Open a new terminal, or add `~/.local/bin` to PATH. |
| `this machine is installed in work-safe mode …` | A flag contradicts the mode the machine saved. Run without the flag, or edit `install` under `[world]` in `~/.ds/config.toml` if the machine really changed. |
| `work-safe: … is missing` (uv, Python 3.12) | Work-safe downloads nothing. Install it from Self Service, then rerun. |
| An agent has no `ds` or `code` tools, or not the newest ones | Restart the agent session. Then `bash ~/Developer/canon/ds-system update`; `ds-next setup --check` shows the wiring. |
| `ds-code: permission denied` | An old build: `ds-system update` rebuilds it. |
| `adopt` says "tags: none detected" | Nothing at the top says the stack. Pass `--tags`. |
| A push fails with `[uses] … is not among what … provides` | Another repository renamed what you use, or you mistyped it. The message lists what it provides; fix your `[uses]`. |
| `reconcile` says a pointer is not in the canon | A `[[id]]` names nothing the canon has. Fix the id, or put example syntax in backticks. |
| A new repository's install fails fetching canon-lib at work | The `canon-lib-v…` tag is not on the team's GitLab: `git -C ~/Developer/canon push origin --tags`. |
| A session starts and hangs with no output | The agent's CLI is not on PATH (Cortex says nothing when `cortex` is missing). Install it, or `ds-next setup --agent claude`. |
| Cortex asks about a repository's hooks before starting | That repository's settings define hooks that would run commands. Read them, then answer. On purpose. |
| `/docs` fails | Node.js 26 or docs-ds is missing: install Node, then `ds-system update`. |
| `/so-capture flush` cannot open a merge request | No token in `$GITLAB_TOKEN` (or no `glab` login), or `[world]` names the wrong group. |
| `change_impact` has no "Across repos" section | No canon on this machine, no manifest in the repository, or the repository is not registered. It says which when it can. |

## The decisions behind it

- [[adr-000]] The repository knowledge system: standards written once, pointed at, recorded per
  repository, checked on every push.
- [[adr-001]] Accepted code ships as canon-lib, grown from real repositories; lessons live next to
  what they changed.
- [[adr-002]] The cross-repository graph: contracts declared in each manifest, compiled by the canon,
  read from `index.json`.
- [[adr-003]] A standard is in force by default; the manifest records exceptions; the canon rolls
  adoption up.

Each repository's `DECISIONS.md` holds its own, numbered `local-NNN`.

## Read more

- `canon/README.md`: how standards, gotchas, blocks, scaffolds and the registry are written.
- `ds-next/README.md`: the terminal in detail.
- `ds-code/README.md` and `ds-code/ARCHITECTURE.md`: the code tools and the rules they keep.
- `skills-os/README.md`: every procedure.
- `docs-ds/README.md`: the docs shell and its theme.
