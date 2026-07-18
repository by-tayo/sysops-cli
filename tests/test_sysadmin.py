from pathlib import Path

from typer.testing import CliRunner

from sysops_cli.main import app
from sysops_cli.sysadmin.commands import dir_size, human_size

runner = CliRunner()


def test_human_size():
    assert human_size(500) == "500.0 B"
    assert human_size(2048) == "2.0 KB"
    assert human_size(1024 * 1024) == "1.0 MB"


def test_dir_size(tmp_path: Path):
    (tmp_path / "a.txt").write_bytes(b"x" * 100)
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "b.txt").write_bytes(b"y" * 200)

    assert dir_size(tmp_path) == 300


def test_disk_usage_command(tmp_path: Path):
    big = tmp_path / "big"
    big.mkdir()
    (big / "file.bin").write_bytes(b"0" * 1000)
    small = tmp_path / "small"
    small.mkdir()
    (small / "file.bin").write_bytes(b"0" * 10)

    result = runner.invoke(app, ["sysadmin", "disk-usage", str(tmp_path)])

    assert result.exit_code == 0
    assert "big" in result.stdout
    assert "small" in result.stdout


def test_disk_usage_missing_path():
    result = runner.invoke(app, ["sysadmin", "disk-usage", "/no/such/path"])
    assert result.exit_code == 1
