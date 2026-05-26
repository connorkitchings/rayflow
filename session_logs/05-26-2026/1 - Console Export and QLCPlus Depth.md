# Session Log — 2026-05-26 (Session 01)

## TL;DR (≤5 lines)
- **Goal**: Implement the console export + QLC+ depth plan.
- **Accomplished**: Added QLC+ QXF fixture definition export, QXW references to generated QXF files, QLC+ function/scene query/trigger evidence, and explicit MA3 native `.show.gz` boundary metadata.
- **Interfaces**: Added `rayflow rig export-qxf`, `rayflow rig export-qxw --qxf-dir`, and `rayflow show qlc-function`.
- **Verification**: `uv run ruff format .`, `uv run ruff check .`, and `uv run pytest -q` passed; full suite reported 620 passed at 83.47% coverage.
- **Next**: Validate generated QXW/QXF import against a local QLC+ install and, separately, continue console export hardening with verified MA3 artifacts.

**Tags**: ["feature", "qlcplus", "export", "backend", "ma3-boundary", "cli"]

---

## Context
- **Branch**: `codex/continue-development-session`
- **User Request**: Implement the proposed Console Export + QLC+ Depth Plan.
- **Product Direction**: Keep console export as the product priority while deepening QLC+ as the practical open-source import/control path.

## Work Completed

### Files Created
- `src/rayflow/engine/fixtures/qlcplus_qxf.py` — QLC+ fixture definition XML builder/exporter from parsed GDTF profiles.
- `tests/engine/test_qlcplus_qxf.py` — QXF structure, metadata, file output, moving-head type, and dedupe tests.

### Files Modified
- `src/rayflow/cli/rig.py` — added `export-qxf`; added `export-qxw --qxf-dir` to emit and reference generated fixture definitions.
- `src/rayflow/engine/fixtures/qlcplus_export.py` — added optional QXF reference metadata in QXW fixture entries.
- `src/rayflow/engine/backends/qlcplus.py` — added function list, status query, and gated start/stop evidence.
- `src/rayflow/cli/show/main.py` — added `show qlc-function`.
- `src/rayflow/engine/console/export_bundle.py` — added explicit native `.show.gz` non-generation notes and import-validation metadata.
- CLI/backend/QXW tests and docs/status files updated.

## Commands Run
```bash
uv run pytest tests/engine/test_qlcplus_qxf.py tests/engine/test_qlcplus_export.py tests/engine/test_qlcplus_backend.py -q --no-cov
uv run pytest tests/cli/test_cli_rig.py::TestRigQlcExports tests/cli/test_show.py::TestShowQlcFunction tests/cli/test_show.py::test_show_help_registers_all_commands -q --no-cov
uv run ruff format .
uv run ruff check .
uv run pytest -q
```

## Decisions Made
- QXF export preserves GDTF-derived manufacturer/model/modes/channels and pragmatic channel groups without inventing unsupported QLC+ capability ranges.
- QXW references generated QXF filenames only when `--qxf-dir` is provided, preserving existing workspace export behavior by default.
- QLC+ function start/stop remains dry-run by default and requires `--execute`.
- MA3 bundle export documents that native `.show.gz` generation is not attempted until the writable binary format is verified.

## Live Validation Addendum
- QLC+ 5.2.1 is installed at `/Applications/QLC+.app`.
- Generated QXW/QXF artifacts were opened with `--web --web-port 9999`.
- Live validation exposed and fixed QXF filename/location, QXF schema, QXW unknown-tag, function-list parsing, channel-record parsing, and Web API universe-numbering issues.
- Final channel send/query proof passed with `observed_matches=true`.
- Moving-head QXF import was validated with Robe Robin MMX Blade after duplicate/fine channel names were made unique.
- A disposable QLC+ Scene was hand-added to the validation workspace; function list, start, and stop status roundtrips passed with `observed_matches=true`.
- See `session_logs/05-26-2026/qlcplus-live-validation-report.json`.

## Handoff Notes
- **Current state**: QLC+ PAR import, moving-head import, channel WebSocket evidence, function listing, and function start/stop are validated against local QLC+ 5.2.1.
- **Next validation**: Try a high-channel-count pixel/multi-break fixture such as Robe Robin iSpiiderX if QLC+ pixel fixture support becomes important.
- **Open question**: Whether RayFlow should generate QLC+ Scene/Function XML as a first-class export feature or keep function control limited to existing QLC+ workspaces.

---

**Session Owner**: Codex
**User**: connorkitchings
