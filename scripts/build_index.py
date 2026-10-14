"""Build index.json from every standard's front matter, or check that it is current.

    python scripts/build_index.py          # write index.json
    python scripts/build_index.py --check  # exit 1 if index.json is stale or a standard is malformed

Required front matter: id, version, title, applies_to, owner. Optional: supersedes, status.
IDs never change; versions only go up. `ds` reads only this file for lookups.
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


def parse(path: Path) -> dict:
    text = path.read_text()
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path.relative_to(ROOT)}: no front matter")
    fm: dict = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
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
    return {"generated": date.today().isoformat(), "standards": standards}


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
        if current.get("standards") != index["standards"]:
            print("index.json is stale: run python scripts/build_index.py and commit it", file=sys.stderr)
            return 1
        print(f"index.json is current ({len(index['standards'])} standards)")
        return 0
    out.write_text(json.dumps(index, indent=2) + "\n")
    print(f"wrote index.json ({len(index['standards'])} standards)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
