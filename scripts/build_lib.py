"""Build canon-lib from the blocks, so the two cannot drift. Every served block (accepted or proposed;
retired ones are left out, --all takes everything) has its module copied to lib/src/canon_lib/<module>.py
and its tests to lib/tests/test_<module>.py with `{{package}}` replaced by `canon_lib`; the package
docstring lists the modules. pyproject.toml (extras,
dependencies) is kept by hand. --check only reports what would change (for CI). Exit 1 on drift.

Usage: python scripts/build_lib.py [--check] [--all]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

CANON = Path(__file__).resolve().parent.parent
LIB = CANON / "lib"
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def front_matter(text: str) -> dict[str, str]:
    m = FRONT.match(text)
    out: dict[str, str] = {}
    for line in (m.group(1) if m else "").splitlines():
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip().strip('"')
    return out


def planned(include_all: bool) -> tuple[dict[Path, str], list[tuple[str, str, str, str, str]]]:
    files: dict[Path, str] = {}
    rows = []
    for block in sorted((CANON / "blocks").glob("block-*")):
        meta = front_matter((block / "BLOCK.md").read_text())
        if meta.get("status") not in ("accepted", "proposed") and not include_all:
            continue
        mod = meta["module"]
        files[LIB / "src" / "canon_lib" / f"{mod}.py"] = (block / "code" / f"{mod}.py").read_text()
        for test in sorted((block / "tests").glob("test_*.py")):
            files[LIB / "tests" / test.name] = test.read_text().replace("{{package}}", "canon_lib")
        rows.append((mod, meta.get("title", mod), meta["id"], meta.get("version", "?"),
                     "" if meta.get("status") == "accepted" else ", unreviewed"))
    lines = "\n".join(f"- `canon_lib.{mod}`: {title}  (from {bid} v{ver}{status})"
                      for mod, title, bid, ver, status in rows)
    files[LIB / "src" / "canon_lib" / "__init__.py"] = (
        '"""canon-lib: the team\'s accepted and proposed (unreviewed) tested code. Import what you need, e.g.\n'
        "`from canon_lib.textsafe import json_literal`. Each module's docstring links the lessons\n"
        "(gotchas) it encodes. Append-only: a breaking change ships under a new name.\n"
        "Built from canon/blocks by scripts/build_lib.py; do not edit here.\n\n" + lines + '\n"""\n')
    return files, rows


def main() -> None:
    check = "--check" in sys.argv
    files, rows = planned("--all" in sys.argv)
    changed = []
    for path, text in files.items():
        if not path.exists() or path.read_text() != text:
            changed.append(path.relative_to(CANON))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text)
    wanted = {p.name for p in files}
    stray = [p.relative_to(CANON) for d in ("src/canon_lib", "tests")
             for p in (LIB / d).glob("*.py") if p.name not in wanted]
    for s in stray:
        print(f"not from any block (left alone): {s}")
    verb = "would change" if check else "wrote"
    for c in changed:
        print(f"{verb} {c}")
    print(f"{len(rows)} blocks -> canon-lib; {len(changed)} file(s) {verb}")
    if check and changed:
        sys.exit(1)


if __name__ == "__main__":
    main()
