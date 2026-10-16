"""Build output directories that cannot cost anyone their files. [[gotcha-confined-writes]]

Docusaurus (and many builders) empty --out-dir before building. Call check_out_dir before the
build starts and mark_out_dir after it succeeds."""
from __future__ import annotations

from pathlib import Path

MARKER = ".built-site"


def check_out_dir(out: Path, protect: list[Path], marker: str = MARKER) -> Path:
    """The resolved output directory, or ValueError when emptying it could delete something:
    it is or contains a protected path, home or the root, or it holds files that are not a
    previous build carrying the marker."""
    out = Path(out).expanduser()
    if out.is_symlink() or (out.exists() and not out.is_dir()):
        raise ValueError(f"refusing to build into {out}: not a plain directory")
    out = out.resolve()
    for p in [Path.home(), Path(out.anchor), Path.cwd(), *protect]:
        p = Path(p).resolve()
        if out == p or out in p.parents:
            raise ValueError(f"refusing to build into {out}: it would delete {p}")
    if out.is_dir() and any(out.iterdir()) and not (out / marker).is_file():
        raise ValueError(f"refusing to build into {out}: it has files that are not a previous build")
    return out


def mark_out_dir(out: Path, marker: str = MARKER) -> None:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    (out / marker).write_text("built here; safe to rebuild into\n")
