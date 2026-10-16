import tomllib

import pytest

from {{package}}.scaffoldrender import render_scaffold, scaffold_digest

FILES = {"pyproject.toml": 'name = "{{name}}"\ndescription = {{purpose_json}}\n',
         "src/__package__/__init__.py": "{{purpose_json}}\n",
         "dot-gitignore": ".venv/\n", "docs/robot-dot-x.md": "keep {{test_cmd}}\n"}


def canon(tmp_path, status="accepted"):
    d = tmp_path / "scaffolds" / "s"
    for rel, text in FILES.items():
        (d / "files" / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / "files" / rel).write_text(text)
    (d / "SCAFFOLD.md").write_text("---\nid: s\n---\n")
    entry = {"id": "s", "status": status, "dir": "scaffolds/s", "files": sorted(FILES), "defaults": {}}
    entry["hash"] = scaffold_digest(tmp_path, entry)
    return entry


def test_renders_paths_and_values(tmp_path):
    out = render_scaffold(tmp_path, canon(tmp_path), "my-app", 'Says "hi" \\ 🚀 """ {{name}}')
    assert set(out) == {"pyproject.toml", "src/my_app/__init__.py", ".gitignore", "docs/robot-dot-x.md"}
    assert tomllib.loads(out["pyproject.toml"])["description"] == 'Says "hi" \\ 🚀 """ {{name}}'
    compile(out["src/my_app/__init__.py"], "x.py", "exec")
    assert out["docs/robot-dot-x.md"] == "keep uv run pytest -q\n"


def test_refusals(tmp_path):
    entry = canon(tmp_path)
    with pytest.raises(ValueError, match="not accepted"):
        render_scaffold(tmp_path, {**entry, "status": "proposed"}, "my-app", "p")
    for bad in ("class", "My-App", "a--b"):
        with pytest.raises(ValueError):
            render_scaffold(tmp_path, entry, bad, "p")
    with pytest.raises(ValueError, match="one line"):
        render_scaffold(tmp_path, entry, "my-app", "two\nlines")
    (tmp_path / "scaffolds/s/files/dot-gitignore").write_text("edited without a bump\n")
    with pytest.raises(ValueError, match="changed since"):
        render_scaffold(tmp_path, entry, "my-app", "p")


def test_template_paths_are_checked(tmp_path):
    entry = canon(tmp_path)
    entry = {**entry, "files": [*entry["files"], "../escape"], "hash": ""}
    (tmp_path / "scaffolds/escape").write_text("x")
    with pytest.raises(ValueError, match="plain relative path"):
        render_scaffold(tmp_path, entry, "my-app", "p")
