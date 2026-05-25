# Phase 9 Slice 1 Practice Workflow

Date: 2026-05-24
Branch: `codex/continue-development-session`

## Completed

- Added a clean checked-in practice rig, `Practice Small Club`, using four
  `LED PAR 64 RGBW` fixtures in the known-good `Default` mode.
- Added `phase9_practice_show`, a complete practice show that exercises
  sections, presets, cue overrides, dimmer values, RGB/RGBW color, and named
  sample colors.
- Added `rayflow show workflow-report`, a dry-run-only report command that
  aggregates rendered cue groups, Art-Net/sACN backend dry-run evidence,
  render/backend warnings, readiness status, cue/frame counts, and timestamp.
- Added optional `--output` support for writing workflow report JSON.
- Added renderer and CLI regression tests for the practice workflow.
- Added the practice workflow guide to MkDocs navigation and updated current
  workflow and implementation schedule docs.
- Updated `.agent/CONTEXT.md` so future sessions start from Phase 9 Slice 1
  being implemented.

## Verification

```bash
uv run ruff check .
uv run pytest -q tests/test_dmx_renderer.py tests/test_cli_show.py --no-cov
uv run pytest -q
uv run mkdocs build --strict
```

Results:

- Ruff: passed.
- Focused tests: 62 passed.
- Full tests: 527 passed.
- MkDocs strict build: passed with existing informational notices about unnaved
  docs and legacy anchors.

## Boundaries

- `workflow-report` is dry-run only and does not provide a hidden live output
  path.
- QLC+ remains an experimental WebSocket spike through `show qlc-spike`.
- MA3 remains on the compatibility/export path only.

## Recommended Next Step

Phase 9 Slice 2 should validate the practice workflow against optional live
Art-Net/sACN receiver proof, then improve show-generation ergonomics around the
proven practice rig/show path.
