"""Render an accepted canon scaffold into {path: text}. [[gotcha-generated-text]] [[gotcha-confined-writes]]

Self-contained: the few text helpers it needs are inlined so this block works on its own."""
from __future__ import annotations

import hashlib
import json
import keyword
import re
import unicodedata
from pathlib import Path, PurePosixPath
from typing import Any

PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def _literal(s: str) -> str:
    return json.dumps(s, ensure_ascii=False).replace("\x7f", "\\u007f")


def _one_line(label: str, value: str) -> str:
    if any(unicodedata.category(c) in ("Cc", "Zl", "Zp") for c in value):
        raise ValueError(f"{label}: one line of text, without control characters")
    return value


def scaffold_digest(canon_root: Path, entry: dict[str, Any]) -> str:
    """SCAFFOLD.md, then each template's path under the scaffold dir and its bytes, as build_index.py hashes."""
    base = Path(canon_root) / entry["dir"]
    digest = hashlib.sha256((base / "SCAFFOLD.md").read_bytes())
    for rel in entry["files"]:
        digest.update(f"files/{rel}".encode() + (base / "files" / rel).read_bytes())
    return digest.hexdigest()[:12]


def _target(rel: str, package: str) -> str:
    parts = PurePosixPath(rel).parts
    if PurePosixPath(rel).is_absolute() or not parts or any(p in ("..", ".", "") for p in parts):
        raise ValueError(f"template path {rel!r} is not a plain relative path")
    out = [("." + p[4:]) if p.startswith("dot-") else p for p in parts]      # only a leading dot-
    return "/".join(p.replace("__package__", package) for p in out)


def render_scaffold(canon_root: Path, entry: dict[str, Any], name: str, purpose: str,
                    test_cmd: str | None = None, lint_cmd: str | None = None) -> dict[str, str]:
    if entry.get("status") != "accepted":
        raise ValueError(f"scaffold {entry.get('id')} is {entry.get('status')!r}, not accepted")
    for rel in entry["files"]:
        _target(rel, "x")                                                   # refuse unsafe paths before hashing reads them
    if entry.get("hash") and scaffold_digest(canon_root, entry) != entry["hash"]:
        raise ValueError(f"scaffold {entry['id']}: templates changed since index.json was built")
    if not (2 <= len(name) <= 41 and NAME_RE.match(name)):
        raise ValueError(f"name {name!r}: lowercase letters, digits and single dashes, 2-41 chars")
    package = name.replace("-", "_")
    if keyword.iskeyword(package) or keyword.issoftkeyword(package):
        raise ValueError(f"name {name!r}: {package!r} is a Python keyword")
    defaults = entry.get("defaults", {})
    test_cmd = _one_line("test_cmd", test_cmd or defaults.get("test_cmd", "uv run pytest -q"))
    lint_cmd = _one_line("lint_cmd", lint_cmd or defaults.get("lint_cmd", "uv run ruff check ."))
    purpose = _one_line("purpose", purpose.strip())
    if not purpose:
        raise ValueError("purpose: one line on what the repo does")
    values = {"name": name, "package": package, "purpose": purpose, "purpose_json": _literal(purpose),
              "test_cmd": test_cmd, "test_cmd_json": _literal(test_cmd),
              "lint_cmd": lint_cmd, "lint_cmd_json": _literal(lint_cmd)}
    base = Path(canon_root) / entry["dir"] / "files"
    targets = {rel: _target(rel, package) for rel in entry["files"]}     # every path checked before any read
    out = {}
    for rel, target in targets.items():
        text = (base / rel).read_text()
        out[target] = PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), text)
    return out
