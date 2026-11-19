# Keeping this folder and the Claude Design project in step

Source of truth for *design decisions*: the Claude Design project
(https://claude.ai/design/p/81fef9af-a683-4f05-a370-344af3d1ea9e). Source of truth for *what the
terminal does*: `src/ds_next/ui_style.py`. This folder is the version-controlled bridge.

## What lives where

| File | Role | Edited in |
| --- | --- | --- |
| `tokens.json` | machine-readable roles, glyphs, grid, mascot | here; hand-mirrored into `tokens/*.css` and `ui_style.py` |
| `tokens/*.css` | the same as CSS custom properties | here |
| `readme.md` | principles, content, visual foundations | the design project, then re-exported |
| `guidelines/*.html` | specimen cards (link `../styles.css`) | the design project |
| `components/terminal/` | React primitives + props contracts + usage notes | the design project |
| `ui_kits/terminal/index.html` | a full session composed from the components | the design project |
| `pages/*.html` | the two design pages (spec + screens), self-contained, open offline | re-exported from the design project |
| `SKILL.md` | the Claude Code skill entry | here |
| `code/` | the Python that renders the system (ui, widgets, cli, ui_style) | `src/ds_next/` is the live copy |

## Re-sync recipe

1. In the design project, ask for the design system zip (it regenerates `tokens.json`, pages and components).
2. Replace this folder wholesale; keep `SYNC.md`.
3. Diff `tokens.json` against `src/ds_next/ui_style.py` (`PALETTE`, `G`, `LABEL_W`, `MASCOT`) and reconcile by hand — they are the only two places a value lives.
4. Update the date and version at the top of `tokens.json`.

## Checks

- `python -c "import json; json.load(open('docs/design-system/tokens.json'))"`
- Every colour in `tokens.json` appears in `tokens/colors.css` and `ui_style.PALETTE`.
- `pages/*.html` open with no network.
