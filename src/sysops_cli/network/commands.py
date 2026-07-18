"""Network engineering commands.

Example command: port-check. Follow this pattern for new commands — a small
pure-Python helper function (easy to unit test) plus a thin @app.command
wrapper that handles I/O and Rich rendering.
"""

from __future__ import annotations

import socket
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()

COMMON_PORTS = [22, 80, 443, 3389, 3306, 5432, 6379, 8080]


def check_port(host: str, port: int, timeout: float) -> str:
    """Returns "open", "timeout", or "closed" for a single host/port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except socket.timeout:
        return "timeout"
    except OSError:
        return "closed"


@app.command("port-check")
def port_check(
    host: str = typer.Argument(..., help="Hostname or IP to check."),
    ports: Optional[List[int]] = typer.Argument(
        None, help="Ports to check (defaults to a common-ports list)."
    ),
    timeout: float = typer.Option(3.0, "--timeout", help="Connection timeout in seconds."),
) -> None:
    """TCP connectivity check against HOST for each PORT."""
    target_ports = ports or COMMON_PORTS

    table = Table(title=f"Port check: {host}")
    table.add_column("Port", justify="right")
    table.add_column("Status")

    colors = {"open": "green", "timeout": "yellow", "closed": "red"}
    for port in target_ports:
        result = check_port(host, port, timeout)
        color = colors[result]
        table.add_row(str(port), f"[{color}]{result}[/{color}]")

    console.print(table)
