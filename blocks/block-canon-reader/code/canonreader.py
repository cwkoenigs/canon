"""Find the canon, load its index.json, read a standard. Never raises on a bad index."""
from __future__ import annotations

import fnmatch
import json
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

KINDS = ("standards", "scaffolds", "blocks")


def canon_root(env: Mapping[str, str] | None = None) -> Path:
    env = os.environ if env is None else env
    return Path(env["DS_CANON"]).expanduser() if env.get("DS_CANON") else Path.home() / "Developer" / "canon"


def strip_front_matter(text: str) -> str:
    if text.startswith("---\n"):
        _, sep, body = text[4:].partition("\n---\n")
        if sep:
            return body.lstrip("\n")
    return text


class Canon:
    def __init__(self, root: Path, data: dict[str, Any], problems: list[str], stamp: int | None):
        self.root, self.problems, self._stamp = Path(root), problems, stamp
        self.standards: list[dict] = data.get("standards", [])
        self.scaffolds: list[dict] = data.get("scaffolds", [])
        self.blocks: list[dict] = data.get("blocks", [])

    @classmethod
    def load(cls, root: Path | None = None) -> Canon:
        root = Path(root) if root is not None else canon_root()
        path = root / "index.json"
        try:
            stamp = path.stat().st_mtime_ns
            data = json.loads(path.read_text())
        except FileNotFoundError:
            return cls(root, {}, [f"no index.json in {root}"], None)
        except (OSError, ValueError) as e:
            return cls(root, {}, [f"{path}: {e}"], None)
        if not isinstance(data, dict):
            return cls(root, {}, [f"{path}: not a JSON object"], stamp)
        problems, clean = [], {}
        for kind in KINDS:
            rows = data.get(kind, [])
            if not isinstance(rows, list):
                problems.append(f"{kind}: not a list")
                rows = []
            good = [r for r in rows if isinstance(r, dict) and isinstance(r.get("id"), str)]
            if len(good) != len(rows):
                problems.append(f"{kind}: {len(rows) - len(good)} entries without an id skipped")
            clean[kind] = good
        return cls(root, clean, problems, stamp)

    def refresh(self) -> Canon:
        """This canon, or a fresh load if index.json changed since."""
        try:
            stamp = (self.root / "index.json").stat().st_mtime_ns
        except OSError:
            stamp = None
        return self if stamp == self._stamp else Canon.load(self.root)

    def counts(self) -> dict[str, int]:
        return {kind: len(getattr(self, kind)) for kind in KINDS}

    def accepted(self, kind: str) -> list[dict]:
        return [r for r in getattr(self, kind) if r.get("status") == "accepted"]

    def find(self, kind: str, rid: str) -> dict | None:
        return next((r for r in getattr(self, kind) if r["id"] == rid), None)

    def versions(self) -> dict[str, int]:
        out = {}
        for kind in KINDS:
            for r in getattr(self, kind):
                try:
                    out[r["id"]] = int(r.get("version", 0))
                except (TypeError, ValueError):
                    continue
        return out

    def applicable(self, tags: list[str]) -> list[dict]:
        def applies(s: dict) -> bool:
            return any(p == "*" or any(fnmatch.fnmatchcase(t, p) for t in tags) for p in s.get("applies_to", []))
        return [s for s in self.standards if applies(s)]

    def read_standard(self, sid: str) -> str:
        s = self.find("standards", sid)
        if s is None:
            raise KeyError(f"no standard {sid!r} in the canon")
        root = self.root.resolve()
        path = (root / str(s.get("path", ""))).resolve()
        if not path.is_relative_to(root) or path == root:
            raise ValueError(f"standard {sid!r}: path {s.get('path')!r} is outside the canon")
        return strip_front_matter(path.read_text())
