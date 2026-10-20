---
id: terminal-design
version: 1
title: Terminal Design System
applies_to: ["cli", "terminal"]
owner: ckoenigs
status: accepted
date: 2026-10-20
---

# Terminal Design System

One rail, three voices, nothing moves that didn't change. Every terminal the team ships, from
`ds-next` to a one-command tool from the `python-cli` type, prints through the same roles, glyphs
and grid, so a person who has read one of them can read all of them. The reference screens, the
written rationale and the full package (tokens, specimen cards, component specs) live in ds-next
under `docs/design-system/`; the `ds-terminal-design` skill, installed by `ds-next setup`, walks an
agent through building to it.

## Principles

1. **One rail per turn.** Everything an agent does in a turn hangs off one vertical line: `●` what
   it says, `→` what it runs, `⎿` what came back, `╰` the footer. Turns are numbered so they can be
   referred to. Local commands (no model) print flat, closed by one outcome line.
2. **Three voices.** You (`›`, strong), the agent (`●`, text with an accent glyph), the tools
   (`→` and `⎿`, muted and dim). Colour names a voice or an outcome, never decoration. Only
   `✓ ⚠ ✗` use ok, warn and err, plus the one line that explains them.
3. **A frame means "needs you".** Boxes are rare and always mean input: a form, an approval, a
   question. Output is never boxed. The banner is the one decorative exception, shown once.
4. **Everything is addressable.** Tool results collapse to one line with a count and the key that
   opens them; standards and files are written as ids you can type back; `/last` prints the last
   result in full.
5. **Append, don't reflow.** Nothing printed is reprinted. The status line is the only live line
   and it sits at the rail tip. Widgets erase themselves whole and leave one static line behind.
6. **Same grammar without the model.** The CLI in CI prints the same glyphs and columns as the
   terminal, minus colour when stdout is not a TTY. One renderer, two outputs.
7. **Errors say the fix.** Red only on the line that failed, followed by what to do in dim. Never
   a stack trace for a user mistake.

## Content

Lowercase, terse, no trailing periods on single lines: `16 adopted · 0 pending`. Facts are joined
with ` · `. Hints are second person and imperative: `/new starts a project · /help lists commands`.
Errors name what failed and then the fix, never a stack trace. Tool names are bold and exactly as
the tool is called; arguments are muted. No emoji; the twelve glyphs and nothing else. Keys are
written `Tab next · ↑ back` with the one submit key as a filled band. Retired: `◆`, `▼`, braille
spinners, rounded panels.

## Tokens

Twelve colour roles with dark and light truecolor values from the Industry steel ramp and an
ANSI-16 fallback; eleven glyphs, each with one meaning, one colour and one column; a grid of two
indents (column 3 for what is said or run, column 5 for what came back) and a 12-wide label
column; frames exact at 80 columns, degrading to 60; and the team mascot, a dog and a cat with
their arms around each other, for a banner's left pane. They ship as `block-ui-style`
(`ui_style.py`) and the picker and form that use them as `block-tui-widgets`.

## Apply

A new CLI from the `python-cli` type already prints through `canon_lib.ui_style`. In an existing
repo: `block_add block-ui-style`, then route every print through its builders (`outcome`, `error`,
`labelled`, `hint`; `run`, `result`, `footer` for an agent); use `console(color=sys.stdout.isatty())`
so logs stay readable. A picker or form comes from `block-tui-widgets` v4.
