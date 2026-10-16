"""Put text a person typed into generated Python, TOML, YAML and Markdown safely. [[gotcha-generated-text]]"""
from __future__ import annotations

import json
import keyword
import re
import unicodedata

PLACEHOLDER_RE = re.compile(r"\{\{([a-z_]+)\}\}")
NAME_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")


def json_literal(s: str) -> str:
    """A string literal valid in JSON, Python, TOML and YAML (double-quoted) at once. Raw Unicode
    is kept (TOML rejects JSON's surrogate escapes); DEL is escaped (TOML and YAML refuse it raw)."""
    return json.dumps(s, ensure_ascii=False).replace("\x7f", "\\u007f")


def check_one_line(label: str, value: str) -> None:
    """Raise ValueError unless value is one line of printable text."""
    bad = next((c for c in value if unicodedata.category(c) in ("Cc", "Zl", "Zp")), None)
    if bad is not None:
        raise ValueError(f"{label}: one line of text, without control characters ({bad!r})")


def check_project_name(name: str, max_len: int = 41) -> str:
    """Lowercase words joined by single dashes, whose package name imports. Returns the package name."""
    if not (2 <= len(name) <= max_len) or not NAME_RE.match(name):
        raise ValueError(f"name {name!r}: lowercase letters, digits and single dashes, 2-{max_len} chars")
    package = name.replace("-", "_")
    if keyword.iskeyword(package) or keyword.issoftkeyword(package):
        raise ValueError(f"name {name!r}: {package!r} is a Python keyword, so it cannot be imported")
    return package


def fill_template(text: str, values: dict[str, str]) -> str:
    """Replace {{key}} in one pass, so a value containing {{other}} stays literal. Unknown keys stay."""
    return PLACEHOLDER_RE.sub(lambda m: values.get(m.group(1), m.group(0)), text)
