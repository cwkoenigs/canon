import pytest

from canon_lib.confined import create_new, inside, write_tree


@pytest.mark.parametrize("rel", ["../evil", "/etc/evil", "a/../../evil", ""])
def test_refuses_escapes(tmp_path, rel):
    with pytest.raises(ValueError):
        inside(tmp_path, rel)


def test_refuses_links_on_the_way(tmp_path):
    (tmp_path / "out").mkdir()
    (tmp_path / "repo").mkdir()
    (tmp_path / "repo" / ".git").symlink_to(tmp_path / "out")
    with pytest.raises(ValueError, match="symbolic link"):
        inside(tmp_path / "repo", ".git/hooks/pre-push")


def test_checks_all_before_writing_any(tmp_path):
    with pytest.raises(ValueError):
        write_tree(tmp_path, {"ok.txt": "x", "../bad.txt": "y"})
    assert not (tmp_path / "ok.txt").exists()


def test_create_new_never_overwrites(tmp_path):
    a = create_new(tmp_path, "note", "one")
    b = create_new(tmp_path, "note", "two")
    assert (a.name, b.name) == ("note.md", "note-2.md") and a.read_text() == "one"
