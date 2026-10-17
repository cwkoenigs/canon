from pathlib import Path

import pytest

from canon_lib.outdir import check_out_dir, mark_out_dir


def test_refuses_the_repo_its_parents_home_and_foreign_dirs(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".git" / "HEAD").write_text("ref: refs/heads/main\n")      # a real .git has files
    monkeypatch.chdir(repo)
    for bad in (repo, tmp_path, Path.home(), repo / ".git"):
        with pytest.raises(ValueError):
            check_out_dir(bad, protect=[repo])
    other = tmp_path / "other"
    other.mkdir()
    (other / "keep.txt").write_text("mine")
    with pytest.raises(ValueError, match="not a previous build"):
        check_out_dir(other, protect=[repo])


def test_allows_new_and_previous_builds(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    site = tmp_path / "work" / "site"
    assert check_out_dir(site, protect=[]) == site.resolve()
    mark_out_dir(site)
    (site / "index.html").write_text("<html/>")
    assert check_out_dir(site, protect=[]) == site.resolve()
