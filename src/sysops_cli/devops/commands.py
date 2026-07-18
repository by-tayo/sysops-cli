"""DevOps commands.

Example command: git-health. Follow this pattern for new commands — a small
pure-Python helper function (easy to unit test) plus a thin @app.command
wrapper that handles I/O and Rich rendering.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


def find_git_repos(root: Path) -> list[Path]:
    """Directories directly containing a .git dir, without descending into it."""
    repos = []
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            repos.append(Path(dirpath))
            dirnames.remove(".git")
    return sorted(repos)


def _git(args: list[str], cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    return result.stdout.strip()


def repo_status(repo: Path) -> tuple[str, str]:
    """Returns (branch, status) — status is "clean" or a comma-joined list of issues."""
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"], repo) or "?"
    dirty = _git(["status", "--porcelain"], repo)

    upstream_result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    upstream = upstream_result.stdout.strip()

    bits: list[str] = []
    if dirty:
        bits.append("uncommitted changes")

    if upstream:
        counts = _git(["rev-list", "--left-right", "--count", "HEAD...@{u}"], repo)
        if counts:
            ahead_str, behind_str = counts.split()
            ahead, behind = int(ahead_str), int(behind_str)
            if ahead:
                bits.append(f"{ahead} ahead")
            if behind:
                bits.append(f"{behind} behind")
    else:
        bits.append("no upstream")

    status = "clean" if not bits else ", ".join(bits)
    return branch, status


@app.command("git-health")
def git_health(
    root: Path = typer.Argument(Path.home(), help="Directory to scan for git repositories."),
) -> None:
    """Scan ROOT for git repositories and report uncommitted/unpushed/no-upstream status."""
    if not root.is_dir():
        console.print(f"[red]No such directory: {root}[/red]")
        raise typer.Exit(code=1)

    repos = find_git_repos(root)

    table = Table(title=f"Git repo health under {root}")
    table.add_column("Status", no_wrap=True)
    table.add_column("Branch", no_wrap=True)
    table.add_column("Path", overflow="fold")

    for repo in repos:
        branch, status = repo_status(repo)
        color = "green" if status == "clean" else "yellow"
        table.add_row(f"[{color}]{status}[/{color}]", branch, str(repo))

    console.print(table)

    if not repos:
        console.print(f"No git repositories found under {root}.")
    else:
        suffix = "y" if len(repos) == 1 else "ies"
        console.print(f"Scanned {len(repos)} repositor{suffix}.")
