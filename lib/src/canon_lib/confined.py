"""Write files only where asked: never outside a destination, never through a link. [[gotcha-confined-writes]]"""
from __future__ import annotations

from pathlib import Path, PurePosixPath


def inside(dest: Path, rel: str) -> Path:
    """The path for `rel` under `dest`. Refuses absolute paths, `..`, any symbolic link on the way
    (dest/.git -> elsewhere redirects everything beneath it), and anything resolving outside dest."""
    dest = Path(dest)
    parts = PurePosixPath(rel).parts
    if PurePosixPath(rel).is_absolute() or not parts or any(p in ("..", ".", "") for p in parts):
        raise ValueError(f"refusing to write {rel!r}: not a plain relative path")
    if dest.is_symlink():
        raise ValueError(f"refusing to write into {dest}: it is a symbolic link")
    p = dest
    for part in parts:
        p = p / part
        if p.is_symlink():
            raise ValueError(f"refusing to write {rel!r}: {p} is a symbolic link")
    target = dest / Path(*parts)
    if dest.resolve() not in target.resolve().parents:
        raise ValueError(f"refusing to write {rel!r}: it resolves outside {dest}")
    return target


def write_tree(dest: Path, files: dict[str, str]) -> list[Path]:
    """Write {relative path: text} under dest, checking every path before writing any."""
    targets = {rel: inside(dest, rel) for rel in files}
    for rel, text in files.items():
        targets[rel].parent.mkdir(parents=True, exist_ok=True)
        targets[rel].write_text(text)
    return [targets[rel] for rel in files]


def create_new(folder: Path, stem: str, text: str, suffix: str = ".md", limit: int = 99) -> Path:
    """Create folder/stem.md, or stem-2.md, stem-3.md ... never overwriting or following a link."""
    folder = Path(folder)
    if folder.is_symlink():
        raise ValueError(f"refusing to write into {folder}: it is a symbolic link")
    folder.mkdir(parents=True, exist_ok=True)
    for n in range(1, limit + 1):
        path = folder / (f"{stem}{suffix}" if n == 1 else f"{stem}-{n}{suffix}")
        try:
            with open(path, "x") as f:
                f.write(text)
            return path
        except FileExistsError:
            continue
    raise FileExistsError(f"{limit} files named {stem} already exist in {folder}")
