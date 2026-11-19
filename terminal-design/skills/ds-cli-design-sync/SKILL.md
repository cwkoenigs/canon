---
name: ds-cli-design-sync
description: "Use when a new terminal design system export arrives."
---

# Sync the terminal design export

The Claude Design project named in `terminal-design/design-system/tokens.json` produces the export. Use the canon checkout at `DS_CANON` or `~/Developer/canon`.

1. Find the export zip and run `make -C <canon>/terminal-design sync ZIP="<path>"`. This replaces `terminal-design/design-system/`, copies the export's code into `terminal-design/examples/ds-next/`, prints the token diff, and runs the parity check. Local notes belong in `terminal-design/design-system/SYNC.local.md`, which the importer preserves.
2. If the tokens moved, update `blocks/block-ui-style/code/ui_style.py` in canon. Run `make -C terminal-design check` from canon. Port any new Python helpers or widgets into the appropriate blocks. Preserve the named banner, rounded session prompt with its tag, agent transcript text, fixed-width frames, and `widgets.resize_safe` for applications.
3. When the Python implementation changes, bump the affected block versions and the canon-lib version. In canon, run `scripts/build_index.py`, `scripts/build_lib.py`, and `scripts/test_blocks.py block-ui-style block-tui-widgets block-tui-picker` with Python. Commit the export and implementation together. Release canon-lib from the merged commit and update ds-next and atlas to the new tag. Refresh their locks and run their tests.
4. When token values change, run `DS_CANON=<canon> make tokens` and `DS_CANON=<canon> make check` in Great GUI. Verify the rendered terminal in both themes at 80 columns before shipping visual changes.

Make design edits in Claude Design and re-export so the next import carries them forward.
