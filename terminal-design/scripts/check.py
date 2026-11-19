#!/usr/bin/env python3
"""Check that the canon's terminal code says what design-system/tokens.json says.

tokens.json is the design system's machine-readable source. The canon's block-ui-style
(blocks/block-ui-style/code/ui_style.py, built into canon-lib as canon_lib.ui_style) mirrors it by
hand (the upstream SYNC.md says so), so this check is what keeps the two from drifting: every colour
role in both themes and the ANSI fallback, every glyph, the grid, the mascot, and frames exact at 80
and 60 columns. Exit 1 on any mismatch.

    make check
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANON = ROOT.parent
CODE = CANON / "blocks" / "block-ui-style" / "code"
if not (CODE / "ui_style.py").is_file():
    sys.exit(f"no canon at {CANON} (blocks/block-ui-style/code/ui_style.py)")
sys.path.insert(0, str(CODE))
T = json.loads((ROOT / "design-system" / "tokens.json").read_text())
problems = []

try:
    import ui_style as S
except ImportError as e:
    sys.exit(f"cannot import the canon's ui_style ({e}); it needs rich: make check")


def hexes(style: str) -> list[str]:
    return re.findall(r"#[0-9a-fA-F]{6}", style)


# colours: each PALETTE role's foreground (or background for on_/hl roles) is the token's value
dark, light, ansi = T["color"]["dark"], T["color"]["light"], T["color"]["ansi16"]
for role in ("text", "muted", "dim", "rule", "accent", "strong", "brand", "ok", "warn", "err"):
    d, l, a = S.PALETTE[role]
    if dark[role] not in hexes(d):
        problems.append(f"color {role} dark: tokens {dark[role]}, ui_style {d!r}")
    if light[role] not in hexes(l):
        problems.append(f"color {role} light: tokens {light[role]}, ui_style {l!r}")
    if ansi[role] != a:
        problems.append(f"color {role} ansi16: tokens {ansi[role]!r}, ui_style {a!r}")
for role, token in (("hl", "hl"), ("surface", "surface")):
    d, l, _ = S.PALETTE[role]
    if dark[token] not in hexes(d) or light[token] not in hexes(l):
        problems.append(f"color {role}: tokens {dark[token]}/{light[token]}, ui_style {d!r}/{l!r}")
for role, spec in (("band", T["color"]["semantic"]["band"]), ("key", T["color"]["semantic"]["key"])):
    d, l, _ = S.PALETTE[role]
    if hexes(d) != [dark[spec["fg"]], dark[spec["bg"]]] or hexes(l) != [light[spec["fg"]], light[spec["bg"]]]:
        problems.append(f"color {role}: expected {spec['fg']} on {spec['bg']}, ui_style {d!r} / {l!r}")

# glyphs
g = T["glyphs"]
for name in ("prompt", "agent", "run", "result", "rail", "close", "ok", "warn", "err", "select", "sep", "fold"):
    if getattr(S.G, name) != g[name]:
        problems.append(f"glyph {name}: tokens {g[name]!r}, ui_style {getattr(S.G, name)!r}")
spin = S.SPINNERS[S.SPINNER]["frames"]
if list(spin) != list(g["spinner"]):
    problems.append(f"spinner: tokens {g['spinner']}, ui_style {spin}")

# grid
grid = T["grid"]
for name, value in (("cols", S.DESIGN_WIDTH), ("indent", S.INDENT), ("resultIndent", S.RESULT_INDENT),
                    ("labelWidth", S.LABEL_W)):
    if grid[name] != value:
        problems.append(f"grid {name}: tokens {grid[name]}, ui_style {value}")

# mascot
if [r for r in T["mascot"]["grid"]] != S.MASCOT:
    problems.append("mascot: the pixel grid in ui_style differs from tokens.json")

# the frames are exactly the width they are given, at the design width and the narrowest
for w in (80, 60):
    rows = S.banner("v1", [("cwd", "~/x")], ["hint"], "~/Developer/canon", "tagline", w=w, name="atlas")
    if {r.cell_len for r in rows} != {w}:
        problems.append(f"banner at {w}: rows of {sorted({r.cell_len for r in rows})} cells")
    if {r.cell_len for r in S.prompt_box("New session", "x" * 200, w)} != {w}:
        problems.append(f"prompt_box at {w}: not {w} cells wide")

# every colour in tokens.json is also in tokens/colors.css (the CSS mirror)
css = (ROOT / "design-system" / "tokens" / "colors.css").read_text().lower()
for theme in ("dark", "light"):
    for role, v in T["color"][theme].items():
        if v.lower() not in css:
            problems.append(f"tokens/colors.css is missing {theme} {role} {v}")

if problems:
    print(f"check: FAILED against {CODE / 'ui_style.py'}")
    print("\n".join(f"  {p}" for p in problems))
    sys.exit(1)
print(f"check: ok (tokens {T['version']} of {T['updated']}: 13 roles x 2 themes + ansi16, "
      f"{len(g) - 2} glyphs, grid, mascot)")
