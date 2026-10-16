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

## Scaffolds

`scaffolds/<id>/` holds the accepted project shapes: `SCAFFOLD.md` (front matter `id`,
`version`, `title`, `path` for the `/new` menu, the `tags` a new repo gets, `owner`, `status`,
and default `test_cmd`/`lint_cmd`) and `files/`, the templates. Placeholders are `{{name}}`,
`{{package}}`, `{{purpose}}`, `{{purpose_json}}`, `{{test_cmd}}` and `{{lint_cmd}}`; a path segment
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
