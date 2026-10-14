"""Split the skills-os guidebook into canon standards, one per numbered section.

    python scripts/split_guidebook.py --source ../skills-os/shared/guidebook.md

IDs are fixed here and never change; re-running overwrites the bodies and keeps versions at
the value already in each file's front matter (bump a version by hand when the text changes).
Section 17 is skipped: it is project-defined and lives in each repo's interview and manifest.
"""
from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

SECTIONS = {   # section number -> (id, applies_to)
    0: ("normative-language", ["*"]),
    1: ("operating-principles", ["*"]),
    2: ("change-cadence", ["*"]),
    3: ("decision-logs", ["*"]),
    4: ("lifecycle", ["*"]),
    5: ("architecture", ["*"]),
    6: ("idempotency", ["service", "pipeline", "dbt"]),
    7: ("observability", ["service", "pipeline", "dbt"]),
    8: ("llm-agents", ["*"]),
    9: ("security", ["*"]),
    10: ("testing", ["*"]),
    11: ("cicd", ["*"]),
    12: ("error-handling", ["service", "package"]),
    13: ("code-review", ["*"]),
    14: ("templates", ["*"]),
    15: ("compliance-rubric", ["*"]),
    16: ("review-cadence", ["*"]),
}
HEADING = re.compile(r"^## (\d+)\. (.+?)\s*$", re.M)


def front_matter(path: Path) -> dict:
    if not path.exists():
        return {}
    m = re.match(r"\A---\n(.*?)\n---\n", path.read_text(), re.S)
    out = {}
    for line in (m.group(1).splitlines() if m else []):
        k, _, v = line.partition(":")
        out[k.strip()] = v.strip()
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--out", default=Path(__file__).resolve().parents[1], type=Path)
    ap.add_argument("--owner", default="ckoenigs")
    args = ap.parse_args()
    text = args.source.read_text()
    version_line = re.search(r"\*\*Version:\*\*\s*(\S+)", text)
    source_version = version_line.group(1) if version_line else "unknown"
    heads = list(HEADING.finditer(text))
    written = 0
    for i, h in enumerate(heads):
        n, title = int(h.group(1)), h.group(2).strip()
        if n not in SECTIONS:
            continue
        sid, applies = SECTIONS[n]
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[h.end():end].strip("\n")
        body = re.sub(r"\n---\s*$", "", body)                 # trailing rule between sections
        path = args.out / f"{sid}.md"
        existing = front_matter(path)
        version = existing.get("version", "1")
        fm = (f"---\nid: {sid}\nversion: {version}\ntitle: {title}\napplies_to: {applies!r}\n"
              f"owner: {args.owner}\nstatus: proposed\ndate: {date.today().isoformat()}\n"
              f"source: guidebook v{source_version} section {n}\n---\n\n").replace("'", '"')
        path.write_text(fm + f"# {title}\n\n{body}\n")
        written += 1
    print(f"wrote {written} standards from {args.source} (guidebook v{source_version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
