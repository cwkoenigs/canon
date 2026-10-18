"""Read [[id]] / [[id@N]] pointers in Markdown, ignoring code. [[gotcha-validation]]"""
from __future__ import annotations

import re

POINTER_RE = re.compile(r"\[\[([a-z0-9-]+)(?:@(\d+))?\]\]")
# fenced blocks (``` or ~~~, three or more, closed by at least as many of the same character)
# and inline spans with any number of backticks
CODE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[^\n]*\n.*?(?:^[ \t]{0,3}\1[`~]*[ \t]*$|\Z)"
                     r"|(`+)[^`\n].*?\2", re.DOTALL | re.MULTILINE)


def mask_code(text: str) -> str:
    return CODE_RE.sub("", text)


def pointers(text: str) -> list[tuple[str, int | None]]:
    """(id, pinned version or None) for every pointer in prose."""
    return [(m.group(1), int(m.group(2)) if m.group(2) else None) for m in POINTER_RE.finditer(mask_code(text))]


def pointer_problems(text: str, versions: dict[str, int]) -> list[str]:
    """What is wrong with the pointers, given {id: current version}: unknown ids, impossible pins."""
    problems = set()
    for sid, pin in pointers(text):
        if sid not in versions:
            problems.add(f"[[{sid}{f'@{pin}' if pin is not None else ''}]] is not in the canon")
        elif pin is not None and not 1 <= pin <= versions[sid]:
            problems.add(f"[[{sid}@{pin}]] pins a version the canon never had (current v{versions[sid]})")
    return sorted(problems)
