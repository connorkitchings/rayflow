# Show CLI Split Cleanup and Local Merge

## Summary

- **Date**: 2026-05-20
- **Branch**: `codex/split-show-cli`
- **Goal**: Finish the show CLI split cleanup, add command registration coverage, and prepare the branch for local merge to `main`.
- **Blockers**: Timecode XML generation remains blocked until an event-bearing MA3 2.3.2.0 Timecode export is captured.

## Changes

### CLI Cleanup

- Added `src/rayflow/cli_show_paths.py` for shared show path helpers.
- Replaced duplicated `_show_dir_path()` and `_show_path()` helpers across the split show CLI modules.
- Kept command names, options, and behavior unchanged.

### Tests

- Added a `rayflow show --help` smoke test that asserts the full show command surface remains registered across the split modules.

### Context

- Updated `.agent/CONTEXT.md` to mark CLI organization complete and return the active branch target to `main` after the local merge.

## Verification

- `uv run ruff check .` — passed.
- `uv run pytest tests/test_cli_show.py tests/test_show_library.py -q` — 44 passed.
- `uv run pytest -q` — 441 passed, 83.01% coverage.

## Next Steps

1. Commit this cleanup on `codex/split-show-cli`.
2. Merge `codex/split-show-cli` locally into `main` with `--no-ff`.
3. Rerun `uv run ruff check .` and `uv run pytest -q` on `main`.
4. Keep Timecode XML blocked until event schema capture.
