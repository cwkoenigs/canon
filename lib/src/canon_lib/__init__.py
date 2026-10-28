"""canon-lib: the team's accepted and proposed (unreviewed) tested code. Import what you need, e.g.
`from canon_lib.textsafe import json_literal`. Each module's docstring links the lessons
(gotchas) it encodes. Append-only: a breaking change ships under a new name.
Built from canon/blocks by scripts/build_lib.py; do not edit here.

- `canon_lib.confined`: Confined file writes  (from block-confined-write v1, unreviewed)
- `canon_lib.dotenv`: Dotenv file parsing  (from block-dotenv v1, unreviewed)
- `canon_lib.schema`: Typed dotenv schema and value checks  (from block-env-schema v1, unreviewed)
- `canon_lib.pointers`: Markdown [[pointer]] reading  (from block-markdown-pointers v2, unreviewed)
- `canon_lib.outdir`: Safe build output directories  (from block-safe-outdir v1, unreviewed)
- `canon_lib.textsafe`: Text safety for generated files  (from block-text-safety v1, unreviewed)
- `canon_lib.picker`: Filterable picker for long lists  (from block-tui-picker v1, unreviewed)
- `canon_lib.widgets`: Inline picker and one-screen form  (from block-tui-widgets v7)
- `canon_lib.ui_style`: Terminal design system tokens  (from block-ui-style v6)
"""
