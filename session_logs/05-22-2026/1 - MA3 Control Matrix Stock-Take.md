# Session Log — 2026-05-22 (Session 01)

## TL;DR

- **Goal**: Take stock of RayFlow's actual control over grandMA3 onPC before
  building more features or starting MCP work.
- **Accomplished**: Added a MA3 control capability matrix and updated project
  status to make basic-look programming proof the next gate.
- **Blockers**: Fixture-aware color/position/preset programming and runtime
  state readback still need live MA3 proof in a disposable show.
- **Next**: Run the basic looks milestone against repo sample fixtures in a
  throwaway MA3 show.
- **Branch**: `codex/continue-development-session`

**Tags**: ["ma3", "control-matrix", "mcp", "research", "phase7"]

---

## Context

- **User Request**: Implement the MA3 Control Capability Stock-Take Plan.
- **Current State**: RayFlow has verified OSC command send, sequence command
  generation, MVR export, and Timecode XML import/playback evidence, but not a
  complete fixture-aware programming layer.
- **Strategic Decision**: Continue control research before building an MCP
  server. MCP should expose verified MA3 operations, not paper over unknowns.

## Work Completed

### Files Modified

- `docs/research/ma3_control_matrix_2_3_2.md` — New control capability matrix
  covering verified automation, open proof gaps, next basic-look milestone, and
  MCP implications.
- `.agent/CONTEXT.md` — Updated current focus from general Phase 7 timecode
  work to MA3 control stock-take before more features or MCP.
- `docs/implementation_schedule.md` — Added MA3 control matrix row and updated
  the MA3 API/readback risk.
- `session_logs/05-22-2026/1 - MA3 Control Matrix Stock-Take.md` — This log.

### Commands Run

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
uv run rayflow show push-to-ma3 sample_show --sequence 1
uv run mkdocs build --strict
```

## Findings

- Installed grandMA3 onPC still reports `2.3.2.0`.
- The initial sandboxed `uv run rayflow ...` invocation hit a macOS
  system-configuration panic; rerunning outside the sandbox worked but the
  requested sample show name was not found in the default show directory.
- The matrix therefore relies on existing code/tests/docs plus prior MA3
  capture evidence rather than claiming new live MA3 mutations.
- Current RayFlow MA3 push remains intentionally conservative: dimmer/intensity
  commands are emitted, while color values are preserved in show data but not
  pushed as direct MA3 commands.

## Verification

- `uv run mkdocs build --strict` — passed.
- MkDocs reported the new research page is not in nav, consistent with existing
  research notes.

## Next Steps

1. Create a disposable MA3 show named `RayFlow Control Probe`.
2. Import or patch the LED PAR and Robe moving-head sample fixtures.
3. Prove dimmer, color preset, position preset, group, cue, executor, and
   current-cue/readback behavior with exported or observable evidence.
4. Only after that, design MCP tools/resources around verified operations.

## Follow-Up Live Probe

After the stock-take, a first live OSC probe was run against MA3 onPC
2.3.2.0 at `127.0.0.1:8000`.

Artifacts:

- `docs/research/ma3_basic_looks_probe_2_3_2.md`
- `~/MALightingTechnology/gma3_library/datapools/groups/rayflow_control_probe_group.xml`
- `~/MALightingTechnology/gma3_library/datapools/sequences/rayflow_control_probe_sequence.xml`
- `~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_dimmer.xml`
- `~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_position.xml`
- `~/MALightingTechnology/gma3_library/datapools/presets/rayflow_control_probe_preset_color.xml`

Findings:

- OSC command send and export commands worked.
- Sequence 1 exported with Cue 1 and `CueInFade="1.000"`.
- Group 1 exported with one selected object ID.
- Preset exports were labeled but empty, so fixture-aware look programming was
  not proven.
- The intended disposable show name was not created; the recently modified show
  file was `rayflow_test.show`. Future live probes must verify active show
  isolation before mutating MA3.
- A later rerun of the show-isolation harness proved why: MA3 parses
  `SaveShow As "rayflow_control_probe"` as `SaveShow "As"`, creating `As.show`.
  The harness was corrected to use MA's documented syntax:
  `SaveShow "rayflow_control_probe"`.

## Safe Probe Harness Implementation

Implemented the next safety slice after the failed disposable-show proof:

- Added `src/rayflow/console/probe.py` with probe plan/result models,
  show-file mtime snapshots, export validation, target-show guardrails, and
  dedicated sample-fixture MVR generation.
- Added `rayflow console probe show-isolation`, `rayflow console probe run`,
  and `rayflow console probe fixture-import`.
- Added `tests/test_console_probe.py` for show isolation, wrong-show failure,
  expected export validation, dry-run behavior, command ordering, CLI mutation
  guards, and probe MVR generation.
- Added `docs/research/ma3_disposable_show_and_fixture_probe_2_3_2.md` as the
  live acceptance evidence template.
- Added `docs/research/ma3_show_isolation_probe_result.json` with the latest
  failed show-isolation evidence packet.
- Updated `.agent/tasks/lessons.md` with the `app_gma3` targeting lesson from
  this live probe.

Verification:

- `uv run ruff format .` — passed; one file reformatted.
- `uv run pytest -q tests/test_console_probe.py tests/test_cli.py::TestConsoleCommands --no-cov` — 26 passed.
- `uv run ruff check .` — passed.
- `uv run pytest -q` — 487 passed; coverage threshold met.
- `uv run rayflow console probe fixture-import` — dry-run passed.
- `uv run rayflow console probe show-isolation --target-show rayflow_control_probe` — dry-run passed.
- `uv run mkdocs build --strict` — passed with existing docs nav/anchor notices.

Live acceptance:

- `uv run rayflow console probe show-isolation --target-show rayflow_control_probe --execute` with the original `SaveShow As "rayflow_control_probe"` command failed and created `As.show`.
- The harness was corrected to `SaveShow "rayflow_control_probe"` based on MA's documented SaveShow syntax.
- Rerunning the corrected live command also failed to create `rayflow_control_probe.show`; no fixture-import or programming probe was attempted.
- `docs/research/ma3_disposable_show_and_fixture_probe_2_3_2.md` now records both failed attempts and keeps fixture proof blocked until show isolation is solved.
- The harness was then adjusted to the documented `NewShow "rayflow_control_probe"` creation form followed by `SaveShow` for the next guarded attempt.
- After the user enabled OSC input and identified the real MA3 UI as
  `app_gma3`, `lsof` confirmed `app_gma3` was bound to UDP 8000.
- A fresh guarded run sent `NewShow "rayflow_control_probe"` and `SaveShow`,
  but `docs/research/ma3_show_isolation_probe_result.json` recorded identical
  pre/post show mtimes and no `rayflow_control_probe.show`.
- The visible `app_gma3` window title remained
  `Display 1 onPC 2.3.2.0 [NewShow_2026.05.22_13.36.00UTC]`.
- Sending the documented save-as command `SaveShow "rayflow_control_probe"`
  also produced no title or file change.
- Current conclusion: UDP listener setup is proven, but `/cmd` command
  acceptance in this MA3 session is not. Before fixture import or programming,
  confirm `Receive Command All` or row-level `Receive Command` is active and
  rerun the show-isolation harness.

---

**Session Owner**: Codex  
**User**: Connor Kitchings
