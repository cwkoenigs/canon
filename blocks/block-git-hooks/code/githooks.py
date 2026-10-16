"""Run git and install hooks without losing anyone's work. [[gotcha-git-hooks]]"""
from __future__ import annotations

import shlex
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str) -> str:
    """Run git in repo; raise GitError with its message on failure. Returns stdout."""
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise GitError(f"git {' '.join(args[:2])} failed in {repo}: {(r.stderr or r.stdout).strip()[:300]}")
    return r.stdout


def init_own_repo(repo: Path) -> None:
    """git init repo if needed, then make sure git resolves it to itself and not to a parent repo."""
    repo = Path(repo)
    repo.mkdir(parents=True, exist_ok=True)
    repo = repo.resolve()
    if not (repo / ".git").exists():
        git(repo, "init", "-q", "-b", "main")
    top = git(repo, "rev-parse", "--show-toplevel").strip()
    if Path(top).resolve() != repo:
        raise GitError(f"{repo} resolves to the repository at {top}")


def hook_script(marker: str, command: list[str], fallback: str = "") -> str:
    """A POSIX hook that runs a kept-aside earlier hook first, then `command`. The command's first
    word is found on PATH, else at `fallback`; if neither exists it says so instead of skipping
    silently. Every embedded value is shell-quoted."""
    exe, rest = command[0], " ".join(shlex.quote(a) for a in command[1:])
    fb = f'[ -z "$EXE" ] && [ -x {shlex.quote(fallback)} ] && EXE={shlex.quote(fallback)}\n' if fallback else ""
    return f"""#!/bin/sh
{marker}
HERE="$(dirname "$0")"
NAME="$(basename "$0")"
if [ -x "$HERE/$NAME.local" ]; then
  "$HERE/$NAME.local" "$@" || exit $?
fi
EXE="$(command -v {shlex.quote(exe)} 2>/dev/null)"
{fb}if [ -z "$EXE" ]; then
  echo "hook: {exe} not found, so its check did not run" >&2
  exit 0
fi
exec "$EXE" {rest}
"""


def install_hook(repo: Path, name: str, script: str, marker: str) -> str | None:
    """Install `script` as hook `name` where git runs hooks. An existing hook that is not ours
    (no `marker` line) is kept as <name>.local, which our script runs first. Returns why it could
    not install, or None."""
    repo = Path(repo).resolve()
    git_dir = repo / ".git"
    if git_dir.is_symlink() or not git_dir.is_dir():
        return f"{git_dir} is not this repository's own git directory"
    hooks = repo / git(repo, "rev-parse", "--git-path", "hooks").strip()
    if hooks.is_symlink():
        return f"{hooks} is a symbolic link"
    hooks = hooks.resolve()
    if git_dir.resolve() not in (hooks, *hooks.parents):
        return f"git runs hooks from {hooks} (core.hooksPath), outside this repository"
    hooks.mkdir(parents=True, exist_ok=True)
    hook = hooks / name
    if hook.is_symlink():
        hook.unlink()
    if hook.exists() and marker not in hook.read_text(errors="replace"):
        local = hooks / f"{name}.local"
        if local.exists() or local.is_symlink():
            return f"{hook} and {local} both exist, so they were left alone"
        hook.rename(local)
    hook.write_text(script)
    hook.chmod(0o755)
    return None
