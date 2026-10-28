---
id: block-tui-picker
version: 1
title: Filterable picker for long lists
module: picker
requires: ["prompt-toolkit>=3.0.40"]
tags: ["cli"]
owner: ckoenigs
status: proposed
date: 2026-10-28
---

# Filterable picker for long lists

`widgets.pick` takes up to nine options picked by digit; `browse` takes tens or hundreds: type to
filter, ↑↓ to move, Enter chooses, Esc quits. Drawn with the terminal design system's roles in a
square frame, like the other widgets.

## API

`await browse(title, [Item(value, label, detail, outcome, number, search)], visible=10, width=80) -> value | None`.
`outcome` is `""`, `"ok"`, `"warn"` or `"err"` (the glyph before the label); typing a number filters
to the items whose `number` starts with it; `search` holds extra words the filter matches.

## Why it is shaped this way

[[gotcha-terminal-ui]]: held to the grid inside a filler VSplit, and `resize_safe` from
`block-tui-widgets`, so a resize in VS Code's terminal redraws it whole. Imports `ui_style` and
`widgets` from the same package: add `block-ui-style` and `block-tui-widgets` first.

Taken from ds-cli-design 1.1.0 (`ds_cli_design.picker`), where atlas used it for its card list.

## Use

From canon-lib: `from canon_lib.picker import Item, browse` (the `tui` extra). Or `block_add
block-tui-picker` from a ds-next session, which copies `picker.py` into the repo's package and its
tests into `tests/`, and records the version and files in `.ds/manifest.toml`. Do not edit the copy
in place: change the block in the canon and bump its version.
