# Agent rules

- Feature work happens in a `/workspaces/plonetheme.derico-<topic>` worktree on its own branch; `master` only takes merges. Merge into `master`, run the tests there, then `git worktree remove` the worktree and `git branch -d` the branch.
- `CODING_STANDARDS.md` holds the judgement calls a review checks: layout tests, upgrade steps, docstrings, the README. Read it before writing code, tests or the README.

## Tests

- `uv run invoke test` runs the Python tests in `tests/`. `uv run invoke test-blocks` typechecks and unit-tests the block bundles in `bundle-src/`; after changing them, `uv run invoke build-blocks` rebuilds the committed `static-blocks/`.
- Browser tests: see `e2e/README.md`. They test whatever the Plone at `DERICO_E2E_BASE` serves (default: 8081, the main checkouts), so a worktree's change needs a `worktree-instance` from `/workspaces/derico.de/derico.de` first. Set `DERICO_E2E_CHROMIUM=/usr/bin/google-chrome`.

## Coupled to the editor

`pyproject.toml` installs `../plone.blicca.auroraeditor` editable, so the tests read the editor's main checkout, from a worktree too. `test_aurora_rhythm.py` and `test_aurora_block_backgrounds.py` hold this sheet to the editor's `blocks_view.css`: an editor change can break them without touching this repo. Run them against an editor worktree before it merges with `PYTHONPATH=<editor worktree>/src`, or after merging.
