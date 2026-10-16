"""Run every block's tests the way they run inside a repo: code as <package>/<module>.py, tests
with {{package}} filled in. Needs a Python with the blocks' requirements and pytest.

    python scripts/test_blocks.py [block-id ...]
"""
from __future__ import annotations

import json
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
            pkg = Path(tmp) / PACKAGE
            pkg.mkdir()
            (pkg / "__init__.py").write_text("")
            base = ROOT / b["dir"]
            (pkg / f"{b['module']}.py").write_text((base / "code" / f"{b['module']}.py").read_text())
            for t in b["tests"]:
                (Path(tmp) / t).write_text((base / "tests" / t).read_text().replace("{{package}}", PACKAGE))
            r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", tmp],
                               cwd=tmp, capture_output=True, text=True, check=False)
            last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
            print(f"{b['id']:28} v{b['version']}  {last}")
            if r.returncode != 0:
                failed.append(b["id"])
                print(r.stdout[-2500:])
    print(f"{'all blocks pass' if not failed else 'FAILED: ' + ', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
