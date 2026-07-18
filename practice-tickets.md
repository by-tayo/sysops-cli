# Practice ticket backlog

The GitHub tool I have access to can't create issues (same auth limitation hit earlier creating
PRs) — paste each section below into **github.com/by-tayo/sysops-cli/issues/new** as its own
issue (title as the issue title, everything below it as the body). Delete this file once they're
all filed, or keep it as a personal reference — either's fine.

---

## sysadmin: service-status command

### Goal
Add `sysops sysadmin service-status [SERVICE...]` in `src/sysops_cli/sysadmin/commands.py`.

### Expected behavior
- With no arguments: report all failed systemd units (`systemctl --failed`).
- With one or more service names given: also report `is-active`/`is-enabled` for each.
- Linux-only — this command should fail with a clear error message (not a stack trace) if
  `systemctl` isn't found, rather than assuming it's always available.

### Reference
Python port of `wfm-scripts/sysadmin/service-health-check.sh` in the companion repo — same
behavior, ported to Typer + `subprocess`.

---

## sysadmin: log-cleanup command

### Goal
Add `sysops sysadmin log-cleanup [PATH] [--days N] [--pattern GLOB] [--execute]` in
`src/sysops_cli/sysadmin/commands.py`.

### Expected behavior
- Finds files matching `--pattern` (default `*.log`) older than `--days` (default 30) under
  `PATH` (default `/var/log`).
- **Defaults to a dry run** — reports what would be deleted and exits without deleting.
- Only deletes when `--execute` is passed, and prompts for confirmation before doing so.
- This is the repo's convention for anything destructive — see `docker-cleanup` issue below for
  the other example, and `wfm-scripts/sysadmin/log-cleanup.sh` for the bash version this mirrors.

---

## sysadmin: user-audit command

### Goal
Add `sysops sysadmin user-audit` in `src/sysops_cli/sysadmin/commands.py`.

### Expected behavior
- Lists local user accounts (`/etc/passwd` on Linux, or `pwd` module), each with last login time
  and whether they're in the sudo/admin group.
- Read-only — no modifications.
- Consider using Python's `pwd` and `grp` modules rather than shelling out where possible.

---

## network: dns-lookup command

### Goal
Add `sysops network dns-lookup DOMAIN [RECORD_TYPE] ` in
`src/sysops_cli/network/commands.py`.

### Expected behavior
- Resolves `DOMAIN` for `RECORD_TYPE` (default `A`) against several public resolvers (Google
  `8.8.8.8`, Cloudflare `1.1.1.1`, Quad9 `9.9.9.9`) side by side, plus the system default.
- Add `dnspython` as a dependency (`pyproject.toml`) — don't shell out to `dig`.
- Useful for spotting DNS propagation lag or a misconfigured record.

### Reference
Python port of `wfm-scripts/network-engineering/dns-lookup-report.sh`.

---

## network: traceroute command

### Goal
Add `sysops network traceroute HOST` in `src/sysops_cli/network/commands.py`.

### Expected behavior
- Wraps the OS's `traceroute` (Linux/macOS) or `tracert` (Windows) binary via `subprocess`,
  parses the hop-by-hop output into a Rich table (hop #, IP/hostname, latency).
- Fails with a clear message if the underlying binary isn't available/permitted, rather than a
  raw stack trace.

---

## network: snmp-poll command

### Goal
Add `sysops network snmp-poll HOST OID [--community STRING]` in
`src/sysops_cli/network/commands.py`.

### Expected behavior
- SNMP GET against a real network appliance (router, switch, managed AP, printer — anything with
  SNMP enabled) for a given OID, using `pysnmp`.
- Read-only GETs only — no SET operations.
- `--community` defaults to `public` (SNMPv2c) but should be overridable; note in the command's
  docstring that this is meant for a lab/test device, not production infrastructure, since
  community strings are sent in cleartext.

---

## network: ssh-appliance-run command

### Goal
Add `sysops network ssh-appliance-run HOST COMMAND [--username NAME] [--port N]` in
`src/sysops_cli/network/commands.py`.

### Expected behavior
- SSHes into a network device (router/switch, or any SSH-reachable host for testing) and runs
  one command, printing the output. Use `netmiko` (preferred, has device-type-aware handling) or
  `paramiko`.
- Prompt for a password interactively (don't accept it as a plaintext CLI argument — that leaks
  into shell history).
- Document in the docstring that this is intended for read-only diagnostic commands (e.g. `show
  version`), not configuration changes.

---

## devops: docker-report command

### Goal
Add `sysops devops docker-report [--prune]` in `src/sysops_cli/devops/commands.py`.

### Expected behavior
- Reports stopped containers, dangling images, and unused networks/volumes via the `docker`
  Python SDK (add as a dependency).
- **Defaults to report-only** — pruning only happens with `--prune`, following the same
  dry-run-by-default convention as `log-cleanup` above.

### Reference
Python port of `wfm-scripts/devops/docker-cleanup.sh`.

---

## devops: k8s-namespace-report command

### Goal
Add `sysops devops k8s-namespace-report [NAMESPACE]` in `src/sysops_cli/devops/commands.py`.

### Expected behavior
- Pod/deployment/PVC status for `NAMESPACE` (default `default`) via the `kubernetes` Python
  client (add as a dependency), using the current kubeconfig context.
- Flag pods that aren't `Running`/`Completed`, or that have restarted 5+ times.
- Read-only — no cluster state changes.

### Reference
Python port of `wfm-scripts/devops/k8s-namespace-report.sh`.

---

## devops: ci-status command

### Goal
Add `sysops devops ci-status OWNER/REPO [--limit N]` in `src/sysops_cli/devops/commands.py`.

### Expected behavior
- Queries a GitHub repo's Actions run history via the REST API
  (`GET /repos/{owner}/{repo}/actions/runs`) and reports the last N runs (default 10) with
  status/conclusion/branch/date in a table.
- Should work unauthenticated for public repos (same as the manual `curl` calls used to debug
  `acc-audit`'s and `CloudLink`'s CI pipelines earlier), but support an optional `GITHUB_TOKEN`
  env var for private repos or higher rate limits.
- Use the `requests` library (add as a dependency) rather than a heavier GitHub SDK.

---

## devops (stretch): terraform-plan-summary command

### Goal
Add `sysops devops terraform-plan-summary PLAN_JSON_PATH` in
`src/sysops_cli/devops/commands.py`.

### Expected behavior
- Takes the path to a `terraform show -json <planfile>` (or `terraform plan -json` piped to a
  file) output and renders a summary table: resource address, action (create/update/destroy/
  replace), and resource type.
- This one's a stretch ticket — the Terraform plan JSON schema has some nesting to work through.
  Generate a sample plan JSON locally against a throwaway `.tf` file to test against (don't
  require real cloud credentials for the test suite — check in a small fixture JSON file under
  `tests/fixtures/` instead).
