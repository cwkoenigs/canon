"""Promote a module from a real repo into the canon: a block (code + tests + BLOCK.md) and the same
module in canon-lib, then rebuild the index. The module must stand alone (standard library only; no
imports from its own package), because a block is copied into other repos by itself.

Usage: python scripts/promote.py --repo <path> --module src/<pkg>/<mod>.py --tests tests/test_<mod>.py
                                 --id block-<name> --title "..." [--tags python,cli] [--source "..."]
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

CANON = Path(__file__).resolve().parent.parent
STDLIB = set(sys.stdlib_module_names)


def stand_alone(module: Path) -> list[str]:
    """Imports that are not standard library (a block cannot have them)."""
    tree = ast.parse(module.read_text())
    bad = []
    for node in ast.walk(tree):
        names = []
        if isinstance(node, ast.Import):
            names = [a.name.split(".")[0] for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module.split(".")[0]]
        elif isinstance(node, ast.ImportFrom):
            names = ["." * node.level + (node.module or "")]
        bad += [n for n in names if n not in STDLIB]
    return sorted(set(bad))


def rewrite_imports(text: str, pkg: str, mod: str, target: str) -> str:
    """`from <pkg>.<mod> import x` / `from <pkg> import <mod>` / `import <pkg>.<mod>` -> target package."""
    text = re.sub(rf"^from {re.escape(pkg)}\.{re.escape(mod)} import", f"from {target}.{mod} import", text, flags=re.MULTILINE)
    text = re.sub(rf"^from {re.escape(pkg)} import {re.escape(mod)}\b", f"from {target} import {mod}", text, flags=re.MULTILINE)
    text = re.sub(rf"^import {re.escape(pkg)}\.{re.escape(mod)}\b", f"import {target}.{mod}", text, flags=re.MULTILINE)
    return text


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--module", required=True, help="path inside the repo, src/<pkg>/<mod>.py")
    p.add_argument("--tests", required=True, help="path inside the repo, tests/test_<mod>.py")
    p.add_argument("--id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--tags", default="python")
    p.add_argument("--source", default="")
    p.add_argument("--lessons", default="", help="comma-separated gotcha ids this code encodes")
    a = p.parse_args()
    repo = Path(a.repo).resolve()
    module, tests = repo / a.module, repo / a.tests
    pkg, mod = module.parent.name, module.stem
    bad = stand_alone(module)
    if bad:
        sys.exit(f"{module} does not stand alone; it imports {', '.join(bad)}")
    text = module.read_text()
    test_text = tests.read_text()
    if f"{pkg}.{mod}" not in test_text and f"from {pkg} import {mod}" not in test_text:
        sys.exit(f"{tests} does not import {pkg}.{mod}")
    block = CANON / "blocks" / a.id
    if block.exists():
        sys.exit(f"{block} exists; bump a version by hand instead")
    (block / "code").mkdir(parents=True)
    (block / "tests").mkdir()
    (block / "code" / f"{mod}.py").write_text(text)
    (block / "tests" / f"test_{mod}.py").write_text(rewrite_imports(test_text, pkg, mod, "{{package}}"))
    today = dt.date.today().isoformat()
    doc = ast.get_docstring(ast.parse(text)) or a.title
    lessons = " ".join(f"[[{x.strip()}]]" for x in a.lessons.split(",") if x.strip())
    (block / "BLOCK.md").write_text(f"""---
id: {a.id}
version: 1
title: {a.title}
module: {mod}
requires: []
tags: [{', '.join(f'"{t.strip()}"' for t in a.tags.split(',') if t.strip())}]
owner: ckoenigs
status: proposed
date: {today}
---

# {a.title}

{doc.strip()}

## Why it is shaped this way

Promoted from a real repo ({a.source or repo.name}) on {today}: its judge-validated tests are the block's
tests. {lessons}

## Use

`code_search`/`code_add` from a ds-next session, or `from canon_lib.{mod} import ...` with canon-lib.
Do not edit the copy in place: change the block in the canon and bump its version.
""")
    lib = CANON / "lib"
    (lib / "src" / "canon_lib" / f"{mod}.py").write_text(text)
    (lib / "tests" / f"test_{mod}.py").write_text(rewrite_imports(test_text, pkg, mod, "canon_lib"))
    init = lib / "src" / "canon_lib" / "__init__.py"
    t = init.read_text()
    line = f"- `canon_lib.{mod}`: {a.title}  (from {a.id} v1)\n"
    if line not in t:
        t = t.rstrip("\n").rstrip('"') .rstrip("\n") + "\n" + line + '"""\n' if t.rstrip().endswith('"""') else t + line
        init.write_text(t)
    subprocess.run([sys.executable, str(CANON / "scripts" / "build_index.py")], check=True)
    print(f"promoted {pkg}.{mod} -> {a.id} v1 and canon_lib.{mod}")


if __name__ == "__main__":
    main()
