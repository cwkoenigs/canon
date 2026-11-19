# Terminal design export

This directory holds the Claude Design export for the canon's [terminal design standard](../terminal-design.md). Start with the [design guide](design-system/readme.md). The export includes the tokens, specimen cards, component kit, screen previews, and mascot. The [exported Python examples](examples/ds-next/) are reference code. The maintained implementation lives in [the canon's blocks](../blocks/block-ui-style/BLOCK.md) and ships through `canon-lib[tui]`.

From the canon checkout:

| Command | What it does |
|---|---|
| `make -C terminal-design check` | Checks the export against the Python implementation and CSS |
| `make -C terminal-design sync ZIP=/path/to/export.zip` | Imports a new export, reports token changes, and runs the check |
| `make -C terminal-design install` | Links the optional design sync skill in existing Claude Code, Codex, and Hermes skill folders |

The [sync skill](skills/ds-cli-design-sync/SKILL.md) covers updating canon-lib and carrying changes to ds-next, atlas, and Great GUI.
