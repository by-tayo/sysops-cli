# sysops-cli
---

<img width="3837" height="1027" alt="SYSOPS" src="https://github.com/user-attachments/assets/eb478bbd-8cb9-4f72-acbb-4983cb940bcd" />

---

A Typer-based CLI for practicing sysadmin, network engineering, and devops commands — and,
just as much, for practicing the git branch → implement → PR → CI workflow. See
[CONTRIBUTING.md](CONTRIBUTING.md) for how that works.

Companion project: [wfm-scripts](https://github.com/by-tayo/wfm-scripts) has bash/PowerShell
versions of some of the same ideas as standalone scripts rather than a CLI.

## Install

```bash
python3 -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

## Usage

```bash
sysops --help
sysops sysadmin disk-usage . --top 10
sysops network port-check github.com 22 443
sysops devops git-health ~/projects
```

## Commands

| Category | Command | Description |
|---|---|---|
| sysadmin | `disk-usage [PATH] [--top N]` | Filesystem summary + top-N largest subdirectories. |
| network | `port-check HOST [PORTS...] [--timeout SEC]` | TCP connectivity check per port. |
| devops | `git-health [ROOT]` | Scans ROOT for git repos, flags uncommitted/unpushed/no-upstream. |

More commands are tracked as [open issues](https://github.com/by-tayo/sysops-cli/issues) — each
one is a self-contained practice ticket with an expected command signature and behavior. See
CONTRIBUTING.md to pick one up.

## Development

```bash
ruff check .      # lint
pytest -v         # test
```

CI runs both on every push/PR (`.github/workflows/ci.yml`), across Python 3.10–3.12.

## Project layout

```
src/sysops_cli/
├── main.py           # root Typer app, registers one sub-app per category
├── sysadmin/commands.py
├── network/commands.py
└── devops/commands.py
tests/                # one test file per category, mirrors src/ layout
```

Each command is a small pure-Python helper function (unit-testable on its own) plus a thin
`@app.command(...)` wrapper that handles argument parsing and Rich output. New commands should
follow that split.
