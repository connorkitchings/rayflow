# Session Log — 2026-05-26 (Session 04)

## TL;DR (≤5 lines)
- **Goal**: Implement QLC+ export hardening and repeatable live validation.
- **Accomplished**: QXW exports now copy generated QXF files beside the workspace for direct QLC+ opening; `show validate-qxw --live` merges static QXW checks with QLC+ WebSocket function evidence.
- **Live proof**: QLC+ 5.2.1 opened the sidecar-copied practice workspace and `validate-qxw --live` observed all 8 exported Scene functions with no missing names.
- **Verification**: `uv run ruff check .` and `uv run pytest -q` passed; full suite reported 643 passed at 83.62% coverage.
- **Next**: Consider using the live validation report as the standard acceptance artifact for generated show exports.

**Tags**: ["feature", "qlcplus", "export", "validation", "live-proof"]

---

## Context
- **Branch**: `codex/continue-development-session`
- **User Request**: Do next steps 1 and 2: QLC+ export hardening and live validation report capture.

## Work Completed

### Files Modified
- `src/rayflow/engine/fixtures/qlcplus_export.py` — added QXF sidecar copy helper and live function comparison fields in validation reports.
- `src/rayflow/cli/show/export.py` — copies generated QXF files beside show QXW exports when `--qxf-dir` is elsewhere.
- `src/rayflow/cli/rig.py` — applies the same sidecar copy behavior for rig QXW exports.
- `src/rayflow/cli/show/main.py` — added `show validate-qxw --live --endpoint --timeout`.
- `tests/engine/test_qlcplus_export.py`, `tests/cli/test_cli_rig.py`, `tests/cli/test_show.py` — added QXF copy, static validation, and live validation tests.
- `docs/cli-reference.md`, `docs/guides/current-workflow.md`, `docs/guides/qlcplus-setup.md`, `docs/implementation_schedule.md` — documented safer export and live validation behavior.

## Commands Run
```bash
uv run pytest tests/engine/test_qlcplus_export.py tests/cli/test_cli_rig.py::TestRigQlcExports tests/cli/test_show.py::TestShowExportBundle -q --no-cov
uv run ruff format .
uv run ruff check .
uv run pytest -q
uv run rayflow show export-qxw phase9_practice_show --output tmp/qlc-validation/live-copy/phase9_practice_show.qxw --dir data/shows/samples --fixture-dir data/fixtures/samples --qxf-dir tmp/qlc-validation/live-copy/fixtures
uv run rayflow show validate-qxw tmp/qlc-validation/live-copy/phase9_practice_show.qxw --qxf-dir tmp/qlc-validation/live-copy --json
/Applications/QLC+.app/Contents/MacOS/qlcplus-qml --open tmp/qlc-validation/live-copy/phase9_practice_show.qxw --web --web-port 9999
uv run rayflow show validate-qxw tmp/qlc-validation/live-copy/phase9_practice_show.qxw --qxf-dir tmp/qlc-validation/live-copy --live --json
killall qlcplus-qml
```

## Evidence
- Export printed `QXF workspace copies: 1 in tmp/qlc-validation/live-copy`.
- Static validation reported 4 fixtures, 8 Scene functions, 8 buttons, 8 linked buttons, no missing QXF definitions, readiness `ready`.
- Live validation reported function count 8, all expected function names from `1 Intro Warm Front` through `8 Blackout`, no missing scene names, readiness `ready`.

## Decisions Made
- Keep `--qxf-dir` semantics intact, but also copy generated QXF sidecars beside the QXW for direct QLC+ opening.
- Keep live validation opt-in with `--live` so static validation remains fast and does not require a running QLC+ instance.
- Compare live QLC+ function names against exported Scene names rather than relying only on counts.

## Handoff Notes
- Direct QLC+ open no longer needs the user to manually move generated QXF files beside the workspace.
- Virtual Console button click behavior remains a possible future UI-level validation, but function import is now repeatably query-proven.

---

**Session Owner**: Codex
**User**: Connor
