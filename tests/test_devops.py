import subprocess
from pathlib import Path

from typer.testing import CliRunner

from sysops_cli.devops.commands import find_git_repos, repo_status
from sysops_cli.main import app

runner = CliRunner()


def _init_repo(path: Path) -> None:
    subprocess.run(["git", "init"], cwd=path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    (path / "README.md").write_text("hello\n")
    subprocess.run(["git", "add", "."], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=path, capture_output=True, check=True)


def test_find_git_repos(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    assert find_git_repos(tmp_path) == [repo]


def test_repo_status_clean(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    _, status = repo_status(repo)
    assert status == "no upstream"  # no remote configured in this fixture


def test_repo_status_dirty(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / "README.md").write_text("changed\n")

    _, status = repo_status(repo)
    assert "uncommitted changes" in status


def test_git_health_command(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)

    result = runner.invoke(app, ["devops", "git-health", str(tmp_path)])

    assert result.exit_code == 0
    assert "repo" in result.stdout
