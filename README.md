# canon

The one place the team's standards are written. Every standard is a Markdown file with a
stable `id`, a `version` that only goes up, the tags it `applies_to`, and an `owner`.
Repositories never copy a standard's text; they point at it with `[[id]]`, and their
`.ds/manifest.toml` records whether each applicable standard is adopted, declined with a
reason, or pending. `index.json` is generated from the front matter and is the only thing
`ds` reads for lookups.

To propose a standard or change one, open a merge request: add or edit the file, bump
`version` when the text changes meaning, run `python scripts/build_index.py`, and commit
`index.json` with it. The listed owner approves. A standard may `supersede` another; adopting
the new one resolves the old. Where a standard has a mechanical step, put it under an
`## Apply` heading so `ds reconcile` can show or run it; without one, adoption is a
documentation change.

A standard reaches repositories by itself: the next push in any repository whose tags match
prints a one-line nudge, and `ds reconcile` lets the owner adopt or decline. There is no
announcement and no migration project. The adoption table shows who adopted, who declined
and why, and who has not decided.

Status of this checkout: seeded from the skills-os guidebook v1.1 by
`scripts/split_guidebook.py`, every standard marked `proposed` with `applies_to` set
broadly. Review each file, narrow `applies_to`, set `status: accepted`, and bump nothing
until the text changes. Section 17 of the guidebook is deliberately absent: it is answered
per repository by `ds new`.

## Where this stands (2026-10-17)

Tested with blind, validated judges (`~/Developer/ds-next/REPORT.md`). **canon-lib**, the accepted
code as one package, is what pays: the same modules pulled by every build, 35 to 61% less code
written, one place to fix a defect. The lessons as files cost 2× and bought nothing, and are being
rewritten as short scoped decisions (see [[adr-001]]). Correctness did not move because the model
already passed every judge without canon. Nothing here has owner review yet.

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

`.gitlab-ci.yml` has a `portal` job (main and schedules) that clones the docs shell and every
repository in `repos.txt`, runs `ds docs portal`, and keeps `site/` as an artifact. The publish
step to SPCS is written as comments and is unverified: it needs the Snowflake image repository,
`docker`, and `snow` on the runner, and should reuse `ds deploy service` rather than a bespoke
`ALTER SERVICE`. `docs-ds/Dockerfile.static` packages a prebuilt `site/` with nginx.

## Design documents

`docs/design/` holds the September design this repository implements: `knowledge-system.md`,
`agent-system.md`, `ds-cli-updates.md`, the original overnight brief `BUILD.md`, and the
benchmark's README. They are reference, not standards; `adr/adr-000` is the standard.
