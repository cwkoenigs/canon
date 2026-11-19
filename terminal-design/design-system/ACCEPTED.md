# Accepted — ds-next terminal design system v1 (2026-10-23)

Only what was chosen. Nothing here is an option.

- **Direction:** Rail — one vertical line per turn, three voices, numbered turns, folded results.
- **Chrome:** Cortex-style framed two-pane banner (shown once), framed prompt with session tag, slash-command menu under it, one toolbar band.
- **Mascot:** the dog (brand steel) and cat (accent strong), arms around each other, 28×20 half-blocks, in the banner's left pane.
- **Colour:** full truecolor, dark default + light, ANSI-16 fallback — `tokens.json`.
- **Type:** JetBrains Mono 12.5/19 in the terminal; Barlow / Barlow Condensed for docs.
- **Grid:** 80 columns (60 min), indents at col 3 and col 5, label column 12.

Not carried forward (kept only in the design project's `archive/`): the Ledger and Plate
directions, the thin / bold / dot-matrix `ds` marks, and the baseline (before) screens.

Known gap: the prompt has no closing rule while typing (prompt_toolkit limit) — phase 2.
