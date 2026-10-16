"""Build index.json from every standard's front matter, or check that it is current.

    python scripts/build_index.py          # write index.json
    python scripts/build_index.py --check  # exit 1 if index.json is stale or a standard is malformed

Required front matter: id, version, title, applies_to, owner. Optional: supersedes, status.
IDs never change; versions only go up. `ds` reads only this file for lookups.

Scaffolds live in scaffolds/<id>/: SCAFFOLD.md (front matter: id, version, title, path, tags,
owner; optional status, test_cmd, lint_cmd) and files/, the templates. Only an accepted scaffold
may be used to create a repository. Its hash covers every template, so a template edited without
a version bump makes the index stale.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("id", "version", "title", "applies_to", "owner")
SCAFFOLD_REQUIRED = ("id", "version", "title", "path", "tags", "owner")


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
        "defaults": {k: fm[k] for k in ("test_cmd", "lint_cmd") if fm.get(k)},
        "hash": digest.hexdigest()[:12], "dir": path.parent.relative_to(ROOT).as_posix(),
        "files": [f.relative_to(path.parent / "files").as_posix() for f in files],
    }


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
        "hash": hashlib.sha256(text.encode()).hexdigest()[:12], "path": path.relative_to(ROOT).as_posix(),
    }
    if not re.fullmatch(r"[a-z0-9-]+", entry["id"]):
        raise ValueError(f"{path.relative_to(ROOT)}: id must be lowercase letters, digits, hyphens")
    return entry


def build() -> dict:
    paths = sorted(list((ROOT / "adr").glob("*.md")) + [p for p in ROOT.glob("*.md") if p.name != "README.md"])
    standards = [parse(p) for p in paths]
    ids = [s["id"] for s in standards]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"duplicate ids: {', '.join(sorted(dupes))}")
    scaffolds = [parse_scaffold(p) for p in sorted((ROOT / "scaffolds").glob("*/SCAFFOLD.md"))]
    sids = [s["id"] for s in scaffolds]
    if len(sids) != len(set(sids)):
        raise ValueError("duplicate scaffold ids")
    return {"generated": date.today().isoformat(), "standards": standards, "scaffolds": scaffolds}


def main() -> int:
    check = "--check" in sys.argv
    try:
        index = build()
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    out = ROOT / "index.json"
    if check:
        current = json.loads(out.read_text()) if out.exists() else {}
        if current.get("standards") != index["standards"] or current.get("scaffolds") != index["scaffolds"]:
            print("index.json is stale: run python scripts/build_index.py and commit it", file=sys.stderr)
            return 1
        print(f"index.json is current ({len(index['standards'])} standards, {len(index['scaffolds'])} scaffolds)")
        return 0
    out.write_text(json.dumps(index, indent=2) + "\n")
    print(f"wrote index.json ({len(index['standards'])} standards, {len(index['scaffolds'])} scaffolds)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
