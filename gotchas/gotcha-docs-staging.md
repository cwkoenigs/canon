---
id: gotcha-docs-staging
version: 2
title: Staging repository docs for a site build
applies_to: ["docs"]
default: adopt
owner: ckoenigs
status: proposed
kind: gotcha
date: 2026-10-17
source: ds-next build, 2026-10-16
---

# Staging repository docs for a site build

## Rules

1. **Stage every Markdown page at its relative path** so links between pages keep working.
2. **Rewrite links through a map of where each page landed.** When a README becomes `index.md`,
   links to it must follow. Which READMEs are renamed is the ticket's call, not this rule's: the
   docs-ds site renamed only the root README; a ticket that says "README.md becomes index.md"
   without qualifying it means every README (an independent judge read it that way, and the
   builds that followed v1 of this rule failed its tests). Follow the ticket and map accordingly.
3. **A repo's own `index.md` must not overwrite the README home page.** Stage it aside.
4. **Copy what pages link to** (images, downloads) inside the repo, or they render broken while
   the build still succeeds. Docusaurus inlines small images as data URIs, so look in the HTML,
   not for the file.
5. **The build empties its output directory:** see [[gotcha-confined-writes]].
