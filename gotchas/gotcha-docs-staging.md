---
id: gotcha-docs-staging
version: 1
title: Staging repository docs for a site build
applies_to: ["docs"]
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-16
source: ds-next build, 2026-10-16
---

# Staging repository docs for a site build

## Rules

1. **Stage every Markdown page at its relative path** so links between pages keep working.
2. **Rewrite links through a map of where each page landed.** README becomes `index.md`, so
   links to it must follow; but only links that resolve to the root README, not a sibling
   `docs/README.md`.
3. **A repo's own `index.md` must not overwrite the README home page.** Stage it aside.
4. **Copy what pages link to** (images, downloads) inside the repo, or they render broken while
   the build still succeeds. Docusaurus inlines small images as data URIs, so look in the HTML,
   not for the file.
5. **The build empties its output directory:** see [[gotcha-confined-writes]].
