# Contributing (i.e. how to practice this)

This repo exists as much to practice the git/PR workflow as to build a useful CLI. The loop
below is meant to be run once per command, so each one becomes a real (small) pull request.

## The loop

1. **Pick an open issue.** Each one specifies a command signature and expected behavior — that's
   your spec. Comment on it (or assign yourself) so it's clear you're working on it.

2. **Branch off `main`:**
   ```bash
   git checkout main
   git pull
   git checkout -b add-<command-name>
   ```

3. **Implement it**, following the pattern already in the codebase (`sysadmin/commands.py`'s
   `disk-usage`, `network/commands.py`'s `port-check`, or `devops/commands.py`'s `git-health` —
   pick whichever is closest to what you're building):
   - A small pure-Python helper function that does the actual work and returns data (not prints)
     — this is what makes it testable.
   - A thin `@app.command("your-command-name")` function that calls the helper and renders the
     result with `rich`.
   - Add the command to the right category's `commands.py` (`sysadmin/`, `network/`, or
     `devops/`) — don't create a new category without discussing it first, the issue will say
     which one it belongs to.

4. **Add a test** in the matching `tests/test_<category>.py`. At minimum: one test for the
   helper function's logic, one test invoking the command through `typer.testing.CliRunner` and
   checking `result.exit_code` and `result.stdout`. Look at the existing tests for the pattern —
   `test_devops.py`'s use of a real `git init` in a `tmp_path` fixture is a good example of
   testing something that shells out, without needing a live network or a real cloud account.

5. **Run the checks locally before pushing:**
   ```bash
   ruff check .
   pytest -v
   ```

6. **Open a PR against `main`.** Reference the issue number (`Closes #N`) in the description.
   CI (`ruff check` + `pytest`, across Python 3.10–3.12) has to pass before merging.

## A few conventions

- Anything that **deletes or modifies** something (not just reads/reports) must default to a
  dry run and require an explicit `--execute` flag to actually act. Look at how the bash
  versions in `wfm-scripts/sysadmin/log-cleanup.sh` and `wfm-scripts/devops/docker-cleanup.sh`
  handle this — same idea, just in Python.
- Commands that touch real infrastructure (an SSH-managed appliance, a Kubernetes cluster, a
  cloud API) should fail with a clear, specific error message when that infrastructure isn't
  reachable — not a raw stack trace.
- Keep the helper function and the `@app.command` wrapper separate (see point 3 above). It's the
  difference between a command you can actually unit test and one you can only test by running
  the whole CLI.
