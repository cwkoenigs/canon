"""The report: the one declared output of this repo. Build it from rows, write it under reports/."""
from pathlib import Path


def build_report(title: str, rows: list[dict]) -> str:
    """Markdown: a title, a count, and one table row per input row (keys of the first row are the columns)."""
    if not rows:
        return f"# {title}\n\nNo rows.\n"
    cols = list(rows[0])
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    body = "".join("| " + " | ".join(str(r.get(c, "")) for c in cols) + " |\n" for r in rows)
    return f"# {title}\n\n{len(rows)} rows.\n\n{head}{body}"


def write_report(text: str, out_dir: Path, name: str = "report.md") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    path.write_text(text)
    return path
