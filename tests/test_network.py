import socket

from typer.testing import CliRunner

from sysops_cli.main import app
from sysops_cli.network.commands import check_port

runner = CliRunner()


def _unused_port() -> int:
    """Grabs an ephemeral port and immediately releases it, so it's guaranteed closed."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_check_port_closed():
    # A truly unused port should report "closed" (instant RST) on most Linux setups, but some
    # network stacks/firewalls (observed on Windows) silently drop the SYN instead, which reads
    # as "timeout" here. Both correctly mean "not open" — that's the only guarantee we can make
    # portably without a real listener.
    assert check_port("127.0.0.1", _unused_port(), timeout=1.0) in ("closed", "timeout")


def test_check_port_open():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]

    try:
        assert check_port("127.0.0.1", port, timeout=1.0) == "open"
    finally:
        server.close()


def test_port_check_command():
    port = _unused_port()

    result = runner.invoke(
        app, ["network", "port-check", "127.0.0.1", str(port), "--timeout", "1"]
    )

    assert result.exit_code == 0
    assert "closed" in result.stdout or "timeout" in result.stdout
