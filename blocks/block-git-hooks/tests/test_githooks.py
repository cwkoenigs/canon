import subprocess

import pytest

from {{package}}.githooks import GitError, git, hook_script, init_own_repo, install_hook

MARK = "# managed-by-test"


def make_repo(path):
    init_own_repo(path)
    return path


def test_git_failures_raise(tmp_path):
    with pytest.raises(GitError):
        git(tmp_path, "not-a-command")


def test_init_refuses_a_parent_repo(tmp_path, monkeypatch):
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "child" / ".git").mkdir(parents=True)          # looks initialised, is not a repo
    with pytest.raises(GitError):
        init_own_repo(tmp_path / "child")


def test_foreign_hook_is_kept_and_runs_first(tmp_path):
    repo = make_repo(tmp_path / "r")
    theirs = repo / ".git" / "hooks" / "pre-push"
    theirs.write_text("#!/bin/sh\necho theirs\nexit 3\n")
    theirs.chmod(0o755)
    assert install_hook(repo, "pre-push", hook_script(MARK, ["true"]), MARK) is None
    r = subprocess.run(["sh", str(theirs)], capture_output=True, text=True, check=False)
    assert "theirs" in r.stdout and r.returncode == 3
    assert install_hook(repo, "pre-push", hook_script(MARK, ["true"]), MARK) is None      # idempotent


def test_hooks_path_outside_is_reported(tmp_path):
    repo = make_repo(tmp_path / "r")
    git(repo, "config", "core.hooksPath", str(tmp_path / "global"))
    assert "outside this repository" in install_hook(repo, "pre-push", "#!/bin/sh\n", MARK)


def test_embedded_paths_never_run_as_shell(tmp_path):
    evil = tmp_path / "$(touch pwned)"
    evil.mkdir()
    (evil / "tool").write_text("#!/bin/sh\necho fallback-ran\n")
    (evil / "tool").chmod(0o755)
    hook = tmp_path / "hook"
    hook.write_text(hook_script(MARK, ["no-such-tool-xyz"], fallback=str(evil / "tool")))
    r = subprocess.run(["sh", str(hook)], cwd=tmp_path, env={"PATH": "/usr/bin:/bin"},
                       capture_output=True, text=True, check=False)
    assert "fallback-ran" in r.stdout and not (tmp_path / "pwned").exists()


def test_missing_tool_says_so(tmp_path):
    hook = tmp_path / "hook"
    hook.write_text(hook_script(MARK, ["no-such-tool-xyz", "check"]))
    r = subprocess.run(["sh", str(hook)], env={"PATH": "/usr/bin:/bin"}, capture_output=True, text=True, check=False)
    assert r.returncode == 0 and "did not run" in r.stderr
