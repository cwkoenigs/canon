"""Run every block's tests the way they run inside a repo: code as <package>/<module>.py, tests
with {{package}} filled in. Needs a Python with the blocks' requirements and pytest.

    python scripts/test_blocks.py [block-id ...]
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "blockpkg"


def main() -> int:
    index = json.loads((ROOT / "index.json").read_text())
    wanted = set(sys.argv[1:])
    failed = []
    for b in index.get("blocks", []):
        if wanted and b["id"] not in wanted:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            # the layout of a scaffolded repo, so tests import and lint exactly as they will there
            repo = Path(tmp)
            pkg = repo / "src" / PACKAGE
            pkg.mkdir(parents=True)
            (repo / "tests").mkdir()
            (repo / "pyproject.toml").write_text(f'[project]\nname = "{PACKAGE}"\nversion = "0.1.0"\n')
            (pkg / "__init__.py").write_text("")
            base = ROOT / b["dir"]
            (pkg / f"{b['module']}.py").write_text((base / "code" / f"{b['module']}.py").read_text())
            for t in b["tests"]:
                (repo / "tests" / t).write_text((base / "tests" / t).read_text().replace("{{package}}", PACKAGE))
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                               cwd=tmp, env={**os.environ, "PYTHONPATH": str(repo / "src")},
                               capture_output=True, text=True, check=False)
            last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
            # accepted code must also pass the lint of the repo it lands in
            ruff = shutil.which("ruff") or shutil.which("uvx")
            lint = None
            if ruff:
                cmd = [ruff, "check", "-q", "."] if ruff.endswith("ruff") else [ruff, "-q", "ruff", "check", "-q", "."]
                lint = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, check=False)
            lint_ok = lint is None or lint.returncode == 0
            print(f"{b['id']:28} v{b['version']}  {last}  lint {'ok' if lint_ok else 'FAILED'}"
                  f"{'' if lint is not None else ' (ruff not found, skipped)'}")
            if r.returncode != 0 or not lint_ok:
                failed.append(b["id"])
                print(r.stdout[-2500:] if r.returncode else lint.stdout[-2500:])
    print(f"{'all blocks pass' if not failed else 'FAILED: ' + ', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
