"""Build index.json from every standard's front matter, or check that it is current.

    python scripts/build_index.py          # write index.json
    python scripts/build_index.py --check  # exit 1 if index.json is stale or a standard is malformed

Required front matter: id, version, title, applies_to, owner. Optional: supersedes, status.
IDs never change; versions only go up. `ds` reads only this file for lookups.

Gotchas (gotchas/*.md, `kind: gotcha`) are standards: indexed, pointed at, adopted. Blocks live
in blocks/<id>/: BLOCK.md (front matter: id, version, title, module, requires, tags, owner;
optional status), code/<module>.py and tests/test_*.py; scripts/test_blocks.py runs them.

Scaffolds live in scaffolds/<id>/: SCAFFOLD.md (front matter: id, version, title, path, tags,
owner; optional status, type, outputs, test_cmd, lint_cmd) and files/, the templates. Only an accepted scaffold
may be used to create a repository. Its hash covers every template, so a template edited without
a version bump makes the index stale.

The `repos` section (the cross-repo graph, adr-002) is written by scripts/build_repos.py from the
registered repos' checkouts; this script carries it over untouched.
"""
from __future__ import annotations

import ast
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOT_STANDARDS = {"README.md", "AGENTS.md", "DECISIONS.md", "CHANGELOG.md"}   # the repo's own pages at the root; every other root .md is a standard
REQUIRED = ("id", "version", "title", "applies_to", "owner")
SCAFFOLD_REQUIRED = ("id", "version", "title", "path", "tags", "owner")
BLOCK_REQUIRED = ("id", "version", "title", "module", "requires", "tags", "owner")


def front_matter(path: Path) -> dict:
    m = re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S)
    if not m:
        raise ValueError(f"{path.relative_to(ROOT)}: no front matter")
    fm: dict = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


def parse_scaffold(path: Path) -> dict:
    fm = front_matter(path)
    missing = [k for k in SCAFFOLD_REQUIRED if k not in fm]
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)}: front matter missing {', '.join(missing)}")
    files = sorted(p for p in (path.parent / "files").rglob("*") if p.is_file())
    if not files:
        raise ValueError(f"{path.relative_to(ROOT)}: no templates under files/")
    digest = hashlib.sha256(path.read_bytes())
    for f in files:
        digest.update(f.relative_to(path.parent).as_posix().encode() + f.read_bytes())
    return {
        "id": fm["id"], "version": int(fm["version"]), "title": fm["title"],
        "path": json.loads(fm["path"]), "tags": json.loads(fm["tags"]), "owner": fm["owner"],
        "status": fm.get("status", "proposed"),
        "type": fm.get("type", ""),
        "outputs": json.loads(fm["outputs"]) if fm.get("outputs") else [],
        "defaults": {k: fm[k] for k in ("test_cmd", "lint_cmd") if fm.get(k)},
        "hash": digest.hexdigest()[:12], "dir": path.parent.relative_to(ROOT).as_posix(),
        "files": [f.relative_to(path.parent / "files").as_posix() for f in files],
    }


def parse_block(path: Path) -> dict:
    """blocks/<id>/BLOCK.md plus code/<module>.py and tests/. The hash covers all of them."""
    fm = front_matter(path)
    missing = [k for k in BLOCK_REQUIRED if k not in fm]
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)}: front matter missing {', '.join(missing)}")
    base = path.parent
    code = base / "code" / f"{fm['module']}.py"
    tests = sorted((base / "tests").glob("test_*.py"))
    if not code.is_file() or not tests:
        raise ValueError(f"{path.relative_to(ROOT)}: needs code/{fm['module']}.py and at least one tests/test_*.py")
    digest = hashlib.sha256(path.read_bytes())
    for f in [code, *tests]:
        digest.update(f.relative_to(base).as_posix().encode() + f.read_bytes())
    return {
        "id": fm["id"], "version": int(fm["version"]), "title": fm["title"], "module": fm["module"],
        "requires": json.loads(fm["requires"]), "test_requires": json.loads(fm.get("test_requires", "[]")),
        "tags": json.loads(fm["tags"]), "owner": fm["owner"],
        "status": fm.get("status", "proposed"), "hash": digest.hexdigest()[:12],
        "dir": base.relative_to(ROOT).as_posix(), "tests": [t.name for t in tests],
    }


POINTER_RE = re.compile(r"\[\[([a-z0-9-]+)(?:@\d+)?\]\]")


def _names(node: ast.AST) -> set[str]:
    return {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}


def _symbols(tree: ast.Module) -> dict[str, ast.stmt]:
    """Top-level functions, classes and assigned constants, by name."""
    out: dict[str, ast.stmt] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = node
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for tg in targets:
                for n in (tg.elts if isinstance(tg, ast.Tuple) else [tg]):
                    if isinstance(n, ast.Name):
                        out[n.id] = node
    return out


def _signature(node: ast.stmt) -> str:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        return f"{prefix} {node.name}({ast.unparse(node.args)}){ret}"
    if isinstance(node, ast.ClassDef):
        bases = f"({', '.join(ast.unparse(b) for b in node.bases)})" if node.bases else ""
        return f"class {node.name}{bases}"
    return ast.unparse(node).splitlines()[0][:120]


def parse_code(block: dict) -> list[dict]:
    """Every top-level function, class and constant in a block's module: what it is, what it needs
    from the same module, which of the block's tests use it, and the lessons it carries. Lets a
    model search and pull one function instead of reading a whole block."""
    base = ROOT / block["dir"]
    source = (base / "code" / f"{block['module']}.py").read_text()
    tree = ast.parse(source)
    syms = _symbols(tree)
    uses = {name: _names(node) & set(syms) - {name} for name, node in syms.items()}
    about = (base / "BLOCK.md").read_text()
    block_lessons = sorted(set(POINTER_RE.findall(about)) - {block["id"]})
    tests: dict[str, list[str]] = {name: [] for name in syms}
    for tf in block["tests"]:
        ttree = ast.parse((base / "tests" / tf).read_text().replace("{{package}}", "pkg"))
        for node in ttree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
                for name in _names(node) & set(syms):
                    tests[name].append(f"{tf}::{node.name}")
    out = []
    for name, node in syms.items():
        if name.startswith("_") and not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue                                # private helpers come along as needs, not on their own
        needs, todo = set(), list(uses[name])
        while todo:
            n = todo.pop()
            if n not in needs:
                needs.add(n)
                todo += list(uses[n])
        doc = ast.get_docstring(node) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else None
        seg = ast.get_source_segment(source, node) or ""
        lessons = sorted(set(POINTER_RE.findall(doc or "")) | set(block_lessons))
        out.append({
            "id": f"{block['id']}:{name}", "name": name, "block": block["id"], "version": block["version"],
            "module": block["module"], "status": block["status"],
            "kind": "class" if isinstance(node, ast.ClassDef) else "constant" if isinstance(node, (ast.Assign, ast.AnnAssign)) else "function",
            "signature": _signature(node), "summary": (doc or "").strip().split("\n\n")[0].replace("\n", " ")[:300],
            "needs": sorted(needs), "tests": sorted(tests[name]), "lessons": lessons, "tags": block["tags"],
            "lines": seg.count("\n") + 1, "hash": hashlib.sha256(seg.encode()).hexdigest()[:12],
        })
    return sorted(out, key=lambda s: s["id"])


def parse(path: Path) -> dict:
    text = path.read_text()
    fm = front_matter(path)
    missing = [k for k in REQUIRED if k not in fm]
    if missing:
        raise ValueError(f"{path.relative_to(ROOT)}: front matter missing {', '.join(missing)}")
    entry = {
        "id": fm["id"], "version": int(fm["version"]), "title": fm["title"],
        "applies_to": json.loads(fm["applies_to"]), "owner": fm["owner"],
        "supersedes": fm.get("supersedes") or None, "status": fm.get("status", "accepted"),
        "kind": fm.get("kind", "standard"),
        "hash": hashlib.sha256(text.encode()).hexdigest()[:12], "path": path.relative_to(ROOT).as_posix(),
    }
    if not re.fullmatch(r"[a-z0-9-]+", entry["id"]):
        raise ValueError(f"{path.relative_to(ROOT)}: id must be lowercase letters, digits, hyphens")
    return entry


def build() -> dict:
    paths = sorted(list((ROOT / "adr").glob("*.md")) + list((ROOT / "gotchas").glob("*.md"))
                   + [p for p in ROOT.glob("*.md") if p.name not in NOT_STANDARDS])
    standards = [parse(p) for p in paths]
    ids = [s["id"] for s in standards]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate ids: {', '.join(sorted(dupes))}")
    scaffolds = [parse_scaffold(p) for p in sorted((ROOT / "scaffolds").glob("*/SCAFFOLD.md"))]
    sids = [s["id"] for s in scaffolds]
    if len(sids) != len(set(sids)):
        raise ValueError("duplicate scaffold ids")
    blocks = [parse_block(p) for p in sorted((ROOT / "blocks").glob("*/BLOCK.md"))]
    if len({b["id"] for b in blocks}) != len(blocks):
        raise ValueError("duplicate block ids")
    code = [s for b in blocks for s in parse_code(b)]
    known = set(ids)
    for s in code:
        s["lessons"] = [x for x in s["lessons"] if x in known]
    return {"generated": date.today().isoformat(), "standards": standards, "scaffolds": scaffolds,
            "blocks": blocks, "code": code}


def main() -> int:
    check = "--check" in sys.argv
    try:
        index = build()
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    out = ROOT / "index.json"
    current = json.loads(out.read_text()) if out.exists() else {}
    if "repos" in current:
        index["repos"] = current["repos"]       # the pipeline's section (scripts/build_repos.py); a rebuild keeps it
    if check:
        if any(current.get(k) != index[k] for k in ("standards", "scaffolds", "blocks", "code")):
            print("index.json is stale: run python scripts/build_index.py and commit it", file=sys.stderr)
            return 1
        print(f"index.json is current ({len(index['standards'])} standards, {len(index['scaffolds'])} scaffolds, "
              f"{len(index['blocks'])} blocks)")
        return 0
    out.write_text(json.dumps(index, indent=2) + "\n")
    print(f"wrote index.json ({len(index['standards'])} standards, {len(index['scaffolds'])} scaffolds, "
          f"{len(index['blocks'])} blocks, {len(index['code'])} code symbols)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
