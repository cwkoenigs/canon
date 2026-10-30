"""scripts/build_repos.py on three small clones: declared and mentioned edges, and every report key."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "build_repos.py"
spec = importlib.util.spec_from_file_location("build_repos", SCRIPT)
br = importlib.util.module_from_spec(spec)
sys.modules["build_repos"] = br
spec.loader.exec_module(br)

GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": "/dev/null", "HOME": "/nonexistent"}


def clone(root: Path, name: str, files: dict[str, str]) -> Path:
    d = root / name
    d.mkdir()
    for rel, text in files.items():
        p = d / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "init"]):
        subprocess.run(["git", "-C", str(d), *args], check=True, env=GIT_ENV, capture_output=True)
    return d


@pytest.fixture
def world(tmp_path):
    """canon root with a registry of four repos; checkouts for three of them."""
    canon = tmp_path / "canon"
    (canon / "repos").mkdir(parents=True)
    for name in ("alpha", "beta", "gamma", "missing"):
        (canon / "repos" / f"{name}.toml").write_text(f'[repo]\nname = "{name}"\npath = "team/{name}"\n')
    checkouts = tmp_path / "checkouts"
    checkouts.mkdir()
    clone(checkouts, "alpha", {
        ".ds/manifest.toml": '[repo]\nname = "alpha"\ntags = ["python"]\n\n[provides]\n'
                             'commands = ["alpha serve [--port N]", "alpha-cli", "alpha nobody"]\n'
                             'names = ["mcp__alpha__*", "ab"]\npaths = ["skills/*/SKILL.md"]\n',
        "README.md": "alpha serve is ours; mcp__alpha__ too\n"})            # own mentions never count
    clone(checkouts, "beta", {
        ".ds/manifest.toml": '[repo]\nname = "beta"\n\n[uses]\nalpha = ["alpha serve", "alpha fly"]\ndelta = ["x"]\n',
        "run.sh": "alpha serve --port 80\n",
        "docs/notes.md": "the rules are mcp__alpha__read and mcp__alpha__list\n",
        "CHANGELOG.md": "- used alpha-cli once\n",                           # changelogs are skipped
        "poetry.lock": "alpha-cli\n"})
    clone(checkouts, "gamma", {"tool.py": "run('alpha-cli')\n"})           # no manifest at all
    return canon, checkouts


def test_literal():
    assert br.literal("alpha serve [--port N]") == "alpha serve"
    assert br.literal("mcp__alpha__*") == "mcp__alpha__"
    assert br.literal("  ds-next   setup ") == "ds-next setup"
    assert br.literal("skills/*/SKILL.md") is None                          # a glob in the middle
    assert br.literal("ab") is None                                          # too short to grep for


def test_registry_needs_name_and_path(tmp_path):
    (tmp_path / "repos").mkdir()
    (tmp_path / "repos" / "x.toml").write_text('[repo]\nname = "y"\npath = "t/x"\n')
    with pytest.raises(ValueError, match="repos/x.toml"):
        br.registry(tmp_path)


def test_graph(world):
    canon, checkouts = world
    section = br.compile_graph(checkouts, br.registry(canon))
    repos = {r["name"]: r for r in section["repos"]}
    assert set(repos) == {"alpha", "beta", "gamma"}
    assert repos["alpha"]["manifest"] and repos["alpha"]["tags"] == ["python"]
    assert not repos["gamma"]["manifest"]
    assert all(len(r["commit"]) >= 7 for r in repos.values())

    edges = {(e["from"], e["to"], e["what"]): e for e in section["edges"]}
    serve = edges[("beta", "alpha", "alpha serve [--port N]")]
    assert serve["declared"] and serve["mentioned"] and serve["count"] == 1 and serve["where"] == ["run.sh:1"]
    names = edges[("beta", "alpha", "mcp__alpha__*")]
    assert names["mentioned"] and not names["declared"] and names["count"] == 1   # one line, counted once
    cli = edges[("gamma", "alpha", "alpha-cli")]
    assert cli["where"] == ["tool.py:1"]                                      # not CHANGELOG.md, not the lock file
    assert len(edges) == 3

    rep = section["report"]
    assert rep["unused"] == [{"repo": "alpha", "what": "alpha nobody"}]
    assert [(u["from"], u["what"]) for u in rep["undeclared"]] == [("beta", "mcp__alpha__*"), ("gamma", "alpha-cli")]
    assert rep["unresolved"] == [{"repo": "beta", "uses": "alpha", "what": "alpha fly"},
                                 {"repo": "beta", "uses": "delta", "what": "x"}]
    assert rep["unscanned"] == [{"repo": "alpha", "what": "ab"}, {"repo": "alpha", "what": "skills/*/SKILL.md"}]
    assert rep["unreadable"] == ["missing"]
    assert rep["silent"] == ["gamma"]
    json.dumps(section)                                                      # it is plain JSON


def test_longer_literal_wins(world):
    """A line holding `alpha serve` is one edge for the command, not a second for a shorter literal."""
    canon, checkouts = world
    m = checkouts / "alpha" / ".ds" / "manifest.toml"
    m.write_text(m.read_text().replace('"alpha-cli"', '"alpha-cli", "alpha"'))
    subprocess.run(["git", "-C", str(checkouts / "alpha"), "commit", "-qam", "x"], check=True, env=GIT_ENV)
    section = br.compile_graph(checkouts, br.registry(canon))
    what = {(e["from"], e["what"]) for e in section["edges"] if e["from"] == "beta"}
    assert ("beta", "alpha serve [--port N]") in what and ("beta", "alpha") not in what


def test_cli_writes_section(world, monkeypatch, capsys):
    canon, checkouts = world
    monkeypatch.setattr(br, "ROOT", canon)
    (canon / "index.json").write_text(json.dumps({"generated": "x", "standards": []}) + "\n")
    assert br.main([str(checkouts), "--write"]) == 0
    index = json.loads((canon / "index.json").read_text())
    assert index["standards"] == [] and len(index["repos"]["edges"]) == 3
    out = capsys.readouterr().out
    assert "3 repos (2 with a manifest), 3 edges" in out and "unreadable (1)" in out
    assert br.main([]) == 2
