import json

import pytest

from canon_lib.canonreader import Canon, canon_root, strip_front_matter


def make(root, data):
    root.mkdir(parents=True, exist_ok=True)
    (root / "index.json").write_text(json.dumps(data))
    return Canon.load(root)


def sample(root):
    (root / "gotchas").mkdir(parents=True)
    (root / "testing.md").write_text("---\nid: testing\nversion: 2\n---\n\n# Testing\n\nBody.\n")
    (root / "gotchas" / "g.md").write_text("---\nid: g\n---\n# G\n")
    return make(root, {
        "standards": [
            {"id": "testing", "version": 2, "title": "Testing", "status": "accepted", "owner": "o",
             "applies_to": ["*"], "path": "testing.md", "kind": "standard"},
            {"id": "g", "version": 1, "title": "G", "status": "proposed", "owner": "o",
             "applies_to": ["cortex"], "path": "gotchas/g.md", "kind": "gotcha"},
            {"id": "evil", "version": 1, "title": "E", "status": "accepted", "owner": "o",
             "applies_to": [], "path": "../outside.md"}],
        "scaffolds": [{"id": "python-cli", "version": 2, "status": "accepted", "title": "CLI"}],
        "blocks": [{"id": "block-a", "version": 3, "status": "accepted", "title": "A"},
                   {"id": "block-b", "version": 1, "status": "proposed", "title": "B"}]})


def test_root_from_env_else_home(tmp_path):
    assert canon_root({"DS_CANON": str(tmp_path)}) == tmp_path
    assert canon_root({}).parts[-2:] == ("Developer", "canon")


def test_counts_accepted_find_versions(tmp_path):
    c = sample(tmp_path / "canon")
    assert c.problems == []
    assert c.counts() == {"standards": 3, "scaffolds": 1, "blocks": 2}
    assert [b["id"] for b in c.accepted("blocks")] == ["block-a"]
    assert c.find("scaffolds", "python-cli")["version"] == 2
    assert c.versions()["block-a"] == 3 and c.versions()["testing"] == 2


def test_read_standard_strips_front_matter_and_stays_inside(tmp_path):
    c = sample(tmp_path / "canon")
    assert c.read_standard("testing").startswith("# Testing")
    with pytest.raises(KeyError):
        c.read_standard("nope")
    (tmp_path / "outside.md").write_text("secret")
    with pytest.raises(ValueError):
        c.read_standard("evil")


def test_applicable_matches_tag_patterns(tmp_path):
    c = sample(tmp_path / "canon")
    assert {s["id"] for s in c.applicable(["python"])} == {"testing"}
    assert {s["id"] for s in c.applicable(["cortex"])} == {"testing", "g"}


@pytest.mark.parametrize("content", ["not json", "[]", '{"standards": 5}', '{"blocks": [{"no": "id"}]}'])
def test_a_broken_index_never_raises(tmp_path, content):
    (tmp_path / "index.json").write_text(content)
    c = Canon.load(tmp_path)
    assert c.problems and c.counts()["standards"] == 0


def test_missing_index(tmp_path):
    c = Canon.load(tmp_path / "nowhere")
    assert c.counts() == {"standards": 0, "scaffolds": 0, "blocks": 0} and "no index.json" in c.problems[0]


def test_refresh_reloads_only_on_change(tmp_path):
    c = sample(tmp_path / "canon")
    assert c.refresh() is c
    data = json.loads((c.root / "index.json").read_text())
    data["blocks"].append({"id": "block-c", "version": 1, "status": "accepted"})
    import os
    (c.root / "index.json").write_text(json.dumps(data))
    os.utime(c.root / "index.json", ns=(c._stamp + 10**9, c._stamp + 10**9))
    assert c.refresh().counts()["blocks"] == 3


def test_strip_front_matter_leaves_plain_text():
    assert strip_front_matter("# Hi\n") == "# Hi\n"
