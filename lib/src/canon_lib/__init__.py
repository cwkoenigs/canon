"""canon-lib: the team's accepted, tested code. Import what you need, e.g.
`from canon_lib.textsafe import json_literal`. Each module's docstring links the lessons
(gotchas) it encodes. Append-only: a breaking change ships under a new name.

- `canon_lib.approver`: Approvals for model tool calls  (from block-approver v1)
- `canon_lib.canonreader`: Read the canon's index and standards  (from block-canon-reader v1)
- `canon_lib.render`: Claude-Code-style message rendering  (from block-claude-render v1)
- `canon_lib.confined`: Confined file writes  (from block-confined-write v1)
- `canon_lib.cortex_session`: Cortex Code session with in-process tools  (from block-cortex-session v3)
- `canon_lib.githooks`: Git commands and hook installation  (from block-git-hooks v1)
- `canon_lib.pointers`: Markdown [[pointer]] reading  (from block-markdown-pointers v1)
- `canon_lib.outdir`: Safe build output directories  (from block-safe-outdir v1)
- `canon_lib.scaffoldrender`: Render an accepted canon scaffold  (from block-scaffold-render v1)
- `canon_lib.textsafe`: Text safety for generated files  (from block-text-safety v1)
- `canon_lib.widgets`: Inline picker and one-screen form  (from block-tui-widgets v1)
- `canon_lib.dotenv`: Dotenv file parsing  (from block-dotenv v1)
- `canon_lib.schema`: Typed dotenv schema and value checks  (from block-env-schema v1)
"""
