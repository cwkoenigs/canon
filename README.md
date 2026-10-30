# canon

The one place the team's standards are written. Every standard is a Markdown file with a
stable `id`, a `version` that only goes up, the tags it `applies_to`, and an `owner`.
Repositories never copy a standard's text; they point at it with `[[id]]`, and their
`.ds/manifest.toml` records whether each applicable standard is adopted, declined with a
reason, or pending. `index.json` is generated from the front matter and is the only thing
`ds` reads for lookups.

## Start here

```sh
git clone https://github.com/cwkoenigs/canon ~/Developer/canon
bash ~/Developer/canon/ds-system
```

`ds-system` is the one command. It reports what this machine has (the five repos, `ds-next`, `ds-code`,
each agent's wiring, the config) and offers the one step that fits: install on a bare machine, update
on an installed one, remove on either. The verbs work without the menu, for scripts and for people who
know: `ds-system status | install | update | remove`. Under it are three scripts, each with `--help`:

| Script | When | What it does |
|---|---|---|
| `install.sh` | Once, on a new machine | Clones the other four repos beside this one, asks one question (where the team's repos live), writes `~/.ds/config.toml`, then runs `bootstrap.sh`. |
| `bootstrap.sh` | Whenever you want the latest | Pulls every repo, reinstalls and tests canon-lib and ds-next, builds docs-ds and ds-code, wires every agent CLI on PATH (Claude Code, Cortex Code, Codex). `install.sh` ends by running it. |
| `uninstall.sh` | When it should be gone | Unwires the agents, takes `ds-next` and `ds-code` off PATH, then asks before removing the clones and `~/.ds`. |

Why three: install needs to ask about your world once; update must never ask; removal must ask before
deleting anything. [docs/GUIDE.md](docs/GUIDE.md) is the map of the whole system and how to use it day to day.

## Install

One command puts the system on a Mac: this repository, `ds-next` (the terminal and the MCP
server, `ds-next` on PATH), `ds-code` (the code tools ds-next attaches) and every agent CLI on PATH
(Cortex Code, Claude Code, Codex) wired to them (the `ds` tool server, `/ds-new`, read-only tools
allowed). It needs git and [uv](https://docs.astral.sh/uv/); Node.js for docs-ds and ds-code.

```sh
curl -fsSL https://raw.githubusercontent.com/cwkoenigs/canon/main/install.sh | bash
```

`install.sh` clones canon, ds-next, skills-os, docs-ds and ds-code, then asks one question: do these
live somewhere other than GitHub? On a personal machine press Enter and GitHub stays the home.
At work answer with the GitLab group URL (or set `TEAM_HOST`; a clone already on the machine
with a non-GitHub remote, or a `glab` login, answers it too): every clone's origin is pointed
there, and team copies that do not exist yet are pushed on a yes. What it settled goes into the
machine's one config, `~/.ds/config.toml`, as `[world]` (`host`, `group`, `token_env`) and
`[capture]` (where `/so-capture` sends captures), unless that file already has a `[world]`; edit it
there when a machine's world differs. Then it runs `bootstrap.sh`,
which also installs docs-ds's Node dependencies (Node.js 26) so `/docs` renders.

Or clone first and run the same script from the clone: `git clone https://github.com/cwkoenigs/canon
~/Developer/canon && bash ~/Developer/canon/install.sh`.

**Updating:** rerun the same line, or `bash ~/Developer/canon/bootstrap.sh`. Both pull every
repository that has an upstream, including skills-os and docs-ds, and redo the install steps. From a checkout, `bash ~/Developer/canon/bootstrap.sh` does the install step
alone. Rerunning either pulls where there is an upstream and re-checks. `CANON_URL` and `DS_NEXT_URL` override where the two
repositories come from; `DEV` where they go (default `~/Developer`). Then `ds-next` in any
directory, or `cortex` and `/ds-new`.

**Removing:** `bash ~/Developer/canon/uninstall.sh`. It unwires the agents (`ds-next setup --remove`:
the `ds` and `code` servers, the skills, the allow rules), takes `ds-next` and `ds-code` off PATH, then
asks before removing the five clones (one with unsaved or unpushed work stays) and `~/.ds`. uv, Node and
the agent CLIs are left. Reinstalling is the install line again.

To propose a standard or change one, open a merge request: add or edit the file, bump
`version` when the text changes meaning, run `python scripts/build_index.py`, and commit
`index.json` with it. The listed owner approves. A standard may `supersede` another; adopting
the new one resolves the old. Where a standard has a mechanical step, put it under an
`## Apply` heading, which says what adopting it takes; without one, adoption is a
documentation change.

A standard reaches repositories by itself: the next push in any repository whose tags match
prints a one-line nudge (`ds-next reconcile` in the pre-push hook), and `/status` in ds-next
lets the repo owner adopt or decline, recorded in its `.ds/manifest.toml`. There is no
announcement and no migration project.

Most standards were seeded from the skills-os guidebook v1.1 by `scripts/split_guidebook.py`,
marked `proposed` with `applies_to` set broadly. Review each one, narrow `applies_to`, set
`status: accepted`, and bump nothing until the text changes. Section 17 of the guidebook is
deliberately absent: `/new` answers it per repository.

## Where this stands (2026-10-28, v0.2.0)

canon is the source of truth; canon-lib carries the code projects import (the terminal look
included: `ui_style`, `widgets`, `picker` under the `tui` extra), and the MCP carries the knowledge
([[adr-001]], still `proposed` until the owner accepts it). canon-lib is released by tag
(`canon-lib-v0.2.0`), and new repos take it from git at that tag. Five accepted project types
(`/new` offers nothing else), two accepted standards (`repo-naming`, `terminal-design`), the rest
`proposed` for review; `proposed` blocks (`block-tui-picker` among them) are built into canon-lib,
marked unreviewed, and hidden from `block_list` until accepted. What differs between machines
(home on GitHub, work on the team's GitLab) is in `~/.ds/config.toml`. The proof behind the
package-first design is in `~/Developer/ds-next/REPORT.md`.

v0.1.0 (2026-10-20) was the first release a team could install.

## Gotchas and accepted code

`gotchas/` holds what building things here taught the hard way: each a standard with
`kind: gotcha`, a rule, what actually happened, and how to check for it. They are indexed,
pointed at and adopted like any standard, so a new repo's AGENTS.md lists the ones whose tags
match. The first ten come from building ds-next on 2026-10-16.

`blocks/<id>/` holds accepted code: small, tested modules that encode those lessons, so a repo
pulls the right implementation instead of rediscovering it. Each has `BLOCK.md` (front matter
`id`, `version`, `title`, `module`, `requires`, `tags`, `owner`, `status`), `code/<module>.py`,
and `tests/test_*.py` written against `{{package}}`. `ds-next` adds a block with `block_add`,
records its version in the repo's manifest, and reports it pending when the canon's version
moves. `python scripts/test_blocks.py` runs every block's tests as they run inside a repo. Change
a block here, bump its version, rebuild the index; never edit a repo's copy in place.
A repo's manifest records each block it took as `[blocks.<id>]`, with its `version` and
`files = [...]`, every file `block_add` wrote; an update replaces only those files and refuses any
other in its way.

`lib/` is canon-lib: the served blocks built into one package by `scripts/build_lib.py`
(`--check` reports drift), with the terminal look under the `tui` extra. Each release is tagged
`canon-lib-v<version>`, and a repo takes it from git at that tag, under `[tool.uv.sources]`:
`canon-lib = { git = "<canon's remote>", tag = "canon-lib-v0.2.0", subdirectory = "lib" }`.
`ds-next new` writes that line from the canon checkout's own origin, so a repo made at work points
at the team's copy; push the tag along with the commit (`git push origin canon-lib-v0.2.0`). Without
the tag it falls back to the checkout's path, which only works on the machine that made the repo.

## Scaffolds

`scaffolds/<id>/` holds the accepted project shapes: `SCAFFOLD.md` (front matter `id`,
`version`, `title`, `path` for the `/new` menu, the `tags` a new repo gets, `owner`, `status`,
and default `test_cmd`/`lint_cmd`) and `files/`, the templates. Placeholders are `{{name}}` and
`{{package}}` (both safe identifiers), and `{{purpose_json}}`, `{{test_cmd_json}}` and
`{{lint_cmd_json}}`: each a JSON string, which is also a valid Python, TOML and YAML double-quoted
string, so user text can never break the generated file. Use those inside code and config;
`{{purpose}}`, `{{test_cmd}}` and `{{lint_cmd}}` are raw text for prose only; a path segment
`__package__` becomes the package name and a leading `dot-` becomes `.`. `build_index.py` lists
them in `index.json` with a hash over every template, so an edited template needs a version bump.
`ds-next` creates repositories only from a scaffold whose status is `accepted`, and records its
id and version in the repository's manifest. Adding or changing one is a merge request like a
standard. The two seeded here, `python-cli` and `python-package`, came from ds-next's built-in
templates and are marked accepted so it works today; the owner should review them.

## Portal pipeline

Not running yet. `.gitlab-ci.yml` has a `check_index` job (refuses a stale index or a malformed
standard) and a `portal` job (main and schedules) that clones the docs shell and every
repository in `repos.txt`, runs `ds docs portal`, and keeps `site/` as an artifact. The publish
step to SPCS is written as comments and is unverified: it needs the Snowflake image repository,
`docker`, and `snow` on the runner, and should reuse `ds deploy service` rather than a bespoke
`ALTER SERVICE`. `docs-ds/Dockerfile.static` packages a prebuilt `site/` with nginx. Both jobs carry a placeholder
runner tag (`<docs-runner-tag>`), and `portal` calls the older `ds` CLI rather than ds-next, so on
GitLab set a real runner tag before expecting a pipeline.

## Design documents

`docs/design/` holds the September design this repository implements: `knowledge-system.md`,
`agent-system.md`, `ds-cli-updates.md`, the original overnight brief `BUILD.md`, and the
benchmark's README. They are reference, not standards; `adr/adr-000` is the standard.
