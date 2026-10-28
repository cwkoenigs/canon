---
id: repo-naming
version: 1
title: Repository Names
applies_to: ["*"]
owner: ckoenigs
status: accepted
date: 2026-10-20
---

# Repository Names

A repository name is lowercase words joined by single hyphens, like `ds-next`, `feed-model`,
`deaths-report`. It starts with a letter, uses only `a-z`, `0-9` and `-`, and is 2 to 41
characters. No capitals, spaces, underscores, dots or trailing hyphens.

| Name | |
|---|---|
| `feed-model` | yes |
| `barn-board` | yes |
| `Feed Model`, `feed_model`, `FeedModel` | no: `/new` rewrites them to `feed-model` |
| `-feed`, `feed-`, `feed--model` | no |
| `class`, `import` | no: the package name would be a Python keyword |

Why: the name becomes the folder, the GitLab project, the console command and, with hyphens
turned to underscores, the Python package. One spelling that works in all four avoids a rename
later, and a team that reads `deaths-report` and `feed-model` side by side can guess the third.

The purpose that goes with the name is one line: what it does and for whom, for example
"Weekly feed use per barn, for the barn managers". It becomes the README's first line and the
package description.

## Apply

`/new` in ds-next (and `ds-next new`) enforces this as you type: it lowercases, turns spaces and underscores into hyphens,
and refuses anything that still does not match. Nothing to do in an existing repository; a
rename is a decision for its owner.
