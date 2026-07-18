"""Sysadmin commands.

Example command: disk-usage. Follow this pattern for new commands — a small
pure-Python helper function (easy to unit test) plus a thin @app.command
wrapper that handles I/O and Rich rendering.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


def human_size(size: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def dir_size(path: Path) -> int:
    """Recursive size of a directory in bytes. Skips entries it can't stat."""
    total = 0
    for entry in path.rglob("*"):
        try:
            if entry.is_file() and not entry.is_symlink():
                total += entry.stat().st_size
        except OSError:
            continue
    return total


def largest_subdirs(path: Path, top: int) -> list[tuple[Path, int]]:
    subdirs = [p for p in path.iterdir() if p.is_dir() and not p.is_symlink()]
    sizes = [(p, dir_size(p)) for p in subdirs]
    sizes.sort(key=lambda item: item[1], reverse=True)
    return sizes[:top]


@app.command("disk-usage")
def disk_usage(
    path: Path = typer.Argument(Path("."), help="Directory to report on."),
    top: int = typer.Option(15, "--top", help="Number of largest subdirectories to show."),
) -> None:
    """Filesystem summary + top-N largest immediate subdirectories under PATH."""
    if not path.is_dir():
        console.print(f"[red]No such directory: {path}[/red]")
        raise typer.Exit(code=1)

    total, used, free = shutil.disk_usage(path)
    console.print(
        f"[bold]Filesystem:[/bold] total={human_size(total)} "
        f"used={human_size(used)} free={human_size(free)}"
    )

    table = Table(title=f"Top {top} largest subdirectories under {path}")
    table.add_column("Size", justify="right", no_wrap=True)
    table.add_column("Path", overflow="fold")
    for subdir, size in largest_subdirs(path, top):
        table.add_row(human_size(size), str(subdir))

    console.print(table)
