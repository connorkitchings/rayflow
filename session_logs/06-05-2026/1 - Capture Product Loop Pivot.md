# Session Log — 2026-06-05 (Session 01)

## TL;DR

- **Goal**: Prove the `Climb to Safety Studio` product loop and pivot away from QLC+ when it failed visual review.
- **Accomplished**: Added Capture handoff export, generated Capture artifacts, refined chorus cues, documented Capture research, and removed QLC+ from the active visual path.
- **Blockers**: Capture desktop import was not verified yet because the app/install workflow is still pending.
- **Next**: Import `exports/capture/climb-to-safety/rig.mvr` into Capture, document fixture matching, then prove one RayFlow cue visibly changes Capture over sACN or Art-Net.
- **Branch**: `codex/climb-to-safety-product-loop`

**Tags**: ["capture", "product-loop", "docs", "cli", "testing", "visualization"]

---

## Context

- **Started**: ~10:00 EDT
- **Ended**: ~10:55 EDT
- **Duration**: ~1 hour
- **User Request**: Implement the plan to prove the RayFlow product loop, troubleshoot QLC+, then pivot fully to Capture and document/research the Capture integration path.

## Work Completed

### Files Modified

- `data/shows/Climb to Safety Studio.yaml` - Applied chorus-lift refinement so chorus cues read bigger and use capability-aware movement/beam additions.
- `src/rayflow/cli/show/export.py` - Added `show export-capture`, which writes `rig.mvr`, `README.md`, `cue_sheet.md`, and `metadata.json`; marked QLC+ export docstring as legacy compatibility.
- `src/rayflow/cli/show/main.py` - Improved recording dry-run/live report timing semantics so simulated vs observed trigger times are explicit.
- `src/rayflow/design/authoring.py` - Made `refine-cues` fixture-capability aware so unsupported movement/beam/gobo attributes are not added to incapable fixtures.
- `tests/cli/test_show.py` - Added command registration coverage for `export-capture`, Capture handoff bundle assertions, and record timing assertions.
- `README.md` - Repositioned Capture/MVR as the primary pre-viz path.
- `docs/guides/capture-workflow.md` - Added user-facing Capture workflow, sample project findings, and next proof tasks.
- `docs/research/capture-integration/README.md` - Added dedicated Capture research dossier covering official docs, sample project inspection, MVR import, sACN/Art-Net, CITP/CAEX, risks, and next implementation steps.
- `docs/implementation/climb_to_safety_product_loop.md` - Added pilot handoff/status doc for the Climb to Safety loop.
- `docs/guides/recording-a-show.md` - Replaced QLC+ recording path with Capture handoff and Capture visualizer recording steps.
- `docs/guides/authoring-workflow.md` - Replaced QLC+ export/validation loop with Capture export/review loop.
- `docs/guides/current-workflow.md` - Marked Capture handoff as current visual review path and QLC+ as legacy compatibility.
- `docs/guides/qlcplus-setup.md` - Downgraded QLC+ guide to legacy setup.
- `docs/cli-reference.md` - Added `show export-capture`; moved QLC+ commands to legacy compatibility wording.
- `docs/ai_interaction_contract.md` - Replaced planned QLC+ output action with Capture handoff/DMX actions.
- `docs/project_charter.md` - Added decision log entry for QLC+ removal from product visual path.
- `docs/implementation_schedule.md` - Updated Capture research and product-loop status.
- `.agent/tasks/lessons.md` - Captured lesson: prove visual usefulness before deepening a visualizer integration.

### Generated Artifacts

- `exports/capture/climb-to-safety/rig.mvr`
- `exports/capture/climb-to-safety/README.md`
- `exports/capture/climb-to-safety/cue_sheet.md`
- `exports/capture/climb-to-safety/metadata.json`
- `exports/ma3/`
- `exports/recordings/`
- `exports/visualizations/`
- `data/show_library/`

Tracked generated QLC+ artifacts under `exports/qlc/climb_to_safety/` were removed from the repo output set.

### Tests Added/Modified

- `tests/cli/test_show.py::TestShowExportMvr::test_show_export_capture_bundle`
- `tests/cli/test_show.py::TestShowRecord` timing assertions
- `tests/cli/test_show.py::TestShowRefineCues` capability-scope assertion for bigger chorus on PAR-only rig

### Commands Run

```bash
git checkout -b codex/climb-to-safety-product-loop
uv run rayflow rig info 'Rig 1' --dir data/rigs --json
uv run rayflow show preview 'Climb to Safety Studio' --dir data/shows --rig 'Rig 1' --rig-dir data/rigs --fixture-dir data/fixtures/samples --json
uv run rayflow show export-qxw 'Climb to Safety Studio' --dir data/shows --rig-dir data/rigs --fixture-dir data/fixtures/samples --output exports/qlc/climb_to_safety/climb_to_safety_studio.qxw --qxf-dir exports/qlc/climb_to_safety
uv run rayflow show validate-qxw exports/qlc/climb_to_safety/climb_to_safety_studio.qxw --qxf-dir exports/qlc/climb_to_safety --json
uv run rayflow show export-capture 'Climb to Safety Studio' --dir data/shows --rig-dir data/rigs --fixture-dir data/fixtures/samples --output-dir exports/capture/climb-to-safety --dmx-protocol sacn
uv run pytest -q tests/cli/test_show.py tests/design/test_authoring.py tests/engine/test_dmx_renderer.py --no-cov
uv run ruff check .
uv run pytest
uv run ruff format .
uv run ruff check .
uv run pytest -q
```

## Health Check

- `uv run ruff format .` - passed; 1 file reformatted.
- `uv run ruff check .` - passed.
- `uv run pytest -q` - passed: 666 tests, 83.24% total coverage.

## Decisions Made

- QLC+ is no longer the active product-loop visual path. It remains legacy compatibility/adapter evidence only.
- Capture/MVR is the primary visual-review path because it aligns with professional pre-viz workflows and supports MVR plus Art-Net/sACN.
- RayFlow should not generate native Capture `.c2p` or `.c2s` files yet. Local samples show they are proprietary binary project formats and often depend on sidecar media/assets.
- The first Capture proof should stay simple: import MVR, map fixtures, prove one live DMX cue changes Capture, then build timed playout/recording.
- CITP/CAEX is a future research path for live view capture, fixture feedback, and deeper Capture automation, but should not block MVR plus sACN/Art-Net proof.

## Issues Encountered

- QLC+ imported/generated enough structure to satisfy file validation, but its 2D/3D views did not provide useful visible review for the user.
- QLC+ on macOS did not present an obvious File > Open workflow and was not a good fit for the non-programmer review loop.
- Capture native project files are binary; direct generation is intentionally deferred.
- Capture desktop import has not yet been verified in this environment.
- `.DS_Store` is modified in the working tree; likely OS-generated and not part of the intended product work.

## Next Steps

1. Open Capture 2026 or Student Edition and import `exports/capture/climb-to-safety/rig.mvr`.
2. Record every fixture matching prompt and save the resulting native Capture project if the edition allows.
3. Configure Capture universes for sACN and prove one `Climb to Safety Studio` cue visibly changes fixtures from RayFlow output.
4. If sACN fails on local loopback, repeat with Art-Net and document exact network/interface settings.
5. Generalize `show record` or add a backend-neutral timed playout command for Capture.
6. Record the Capture visualizer, gather timestamped critique, and run the refinement loop again.

## Handoff Notes

- **For next session**: Start with `docs/research/capture-integration/README.md`, then `docs/guides/capture-workflow.md`, then the generated bundle in `exports/capture/climb-to-safety/`.
- **Open questions**: Does Student Edition map the current `Rig 1` fixture types well enough? Does macOS Capture 2026 receive sACN from localhost reliably? Does the MVR stage need additional truss/stage geometry?
- **Dependencies**: Capture desktop installation/import verification.
- **Do not revert**: The branch intentionally deletes tracked `exports/qlc/climb_to_safety/*` files and leaves QLC+ code/tests as legacy compatibility.

## Proposed Commit Message

```text
feat: pivot Climb to Safety loop to Capture

- add Capture handoff export command and generated pilot bundle
- mark QLC+ artifacts and docs as legacy compatibility
- refine Climb to Safety chorus cues with fixture-aware safeguards
- document Capture research, sample project findings, and next proof steps
- update product loop docs and roadmap for MVR plus sACN/Art-Net review

Refs: session_logs/06-05-2026/1 - Capture Product Loop Pivot.md
```

---

**Session Owner**: Codex
**User**: Connor
