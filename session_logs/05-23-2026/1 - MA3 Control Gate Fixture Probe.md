# Session Log — 2026-05-23 (Session 01)

## TL;DR

- **Goal**: Implement the MA3 control gate and fixture import probe workflow.
- **Accomplished**: Added command-acceptance probing, explicit disposable-show
  confirmation metadata, fixture probe evidence output, and sample MVR artifact
  generation.
- **Live result**: Command acceptance failed; MA3 did not write the expected
  Sequence export file, so show isolation and live fixture import were not run.
- **Next**: Fix MA3 OSC row command receive or command-export path, then rerun
  `console probe command-acceptance`.
- **Branch**: `codex/continue-development-session`

**Tags**: ["ma3", "probe", "fixture-import", "osc", "phase7"]

---

## Context

- **User Request**: Implement the accepted MA3 Control Gate + Fixture Import
  Probe Plan for options 1 and 2.
- **Current State**: MA3 onPC 2.3.2.0 is the local baseline. Previous probes
  showed UDP listener evidence but not reliable `/cmd` acceptance in the active
  session.

## Work Completed

### Files Modified

- `src/rayflow/console/probe.py` — Added command-acceptance plan, result
  metadata, disposable confirmation guard, and probe MVR entry inspection.
- `src/rayflow/cli_console.py` — Added `console probe command-acceptance`,
  `--assume-disposable`, fixture import evidence modes, result JSON output, and
  IP/port options for CLI import probing.
- `tests/test_console_probe.py` — Added coverage for command acceptance,
  disposable confirmation, result JSON failure output, and MVR contents.
- `docs/research/ma3_disposable_show_and_fixture_probe_2_3_2.md` — Documented
  the two-gate workflow, live failed command-acceptance evidence, and generated
  fixture MVR artifact.
- `docs/research/ma3_control_matrix_2_3_2.md` — Updated evidence notes without
  upgrading unproven capability statuses.
- `.agent/PLAYBOOK.md` — Added the rule to prove command acceptance before live
  MA3 mutation probes.

### Artifacts Added

- `data/ma3_exports/probes/rayflow_control_probe.mvr`
- `docs/research/ma3_command_acceptance_probe_result.json`
- `docs/research/ma3_fixture_import_probe_result.json`

## Live Probe Results

Command acceptance:

```bash
uv run rayflow console probe command-acceptance \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_command_acceptance_probe_result.json \
  --execute
```

Result: failed. RayFlow sent:

```text
Export Sequence 1 "rayflow_command_acceptance_probe_sequence"
```

Expected export was not created:

```text
~/MALightingTechnology/gma3_library/datapools/sequences/rayflow_command_acceptance_probe_sequence.xml
```

No show-file mtimes changed. Show isolation and live fixture import were blocked
by the failed command-acceptance gate.

Fixture MVR generation:

```bash
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_fixture_import_probe_result.json \
  --execute
```

Result: passed for local MVR generation only. The MVR contains:

- `myvirtualrig.xml`
- `BlenderDMX_LED_PAR_64_RGBW.gdtf`
- `Robe_Robin_MMX_Blade.gdtf`

## Verification

- `uv run ruff check .` — passed.
- `uv run pytest -q tests/test_console_probe.py tests/test_cli.py::TestConsoleCommands --no-cov` — 34 passed.
- `uv run pytest -q` — 495 passed, coverage threshold met.
- `uv run mkdocs build --strict` — passed with existing docs nav/anchor notices.

## Next Steps

1. In MA3 OSC settings, reconfirm row-level `Receive Command` is enabled for the
   row listening on UDP 8000.
2. Rerun `uv run rayflow console probe command-acceptance --target-show rayflow_control_probe --result-json docs/research/ma3_command_acceptance_probe_result.json --execute`.
3. If command acceptance passes, run `show-isolation`.
4. If show isolation cannot be proven by `.show` mtime but the UI clearly shows
   the disposable target, rerun with `--assume-disposable` and keep that status
   recorded in the result JSON.
5. Only then attempt CLI-first or UI-assisted fixture MVR import evidence.

---

**Session Owner**: Codex  
**User**: Connor Kitchings

## Follow-Up: Command Acceptance Unblocked

The user enabled row-level `Receive Command` in the MA3 OSC sheet. The first
manual `About` probe showed that `/cmd` was accepted but inherited the
`Fixture` command destination:

```text
Illegal object: Fixture "About"
```

RayFlow probe plans were updated to prepend:

```text
ChangeDestination Root
```

The corrected command-acceptance probe passed and wrote
`docs/research/ma3_command_acceptance_probe_result.json`.

Show isolation still failed. `NewShow "rayflow_control_probe"` + `SaveShow`
modified `NewShow_2026.05.22_13.36.00UTC.show` instead of creating
`rayflow_control_probe.show`, and a direct `SaveShow "rayflow_control_probe"`
did not create the target file. Fixture import remains blocked until the user
creates/loads a disposable target show through UI or explicitly uses
`--assume-disposable` based on visible UI confirmation.

## Follow-Up: Disposable Show Loaded

The user loaded `rayflow_control_probe.show` manually through MA3. The harness
was corrected so `show-isolation --assume-disposable` no longer sends `NewShow`;
it records the confirmed disposable state with:

```text
ChangeDestination Root
SaveShow
```

The corrected isolation result was written to
`docs/research/ma3_show_isolation_probe_result.json`.

Generated a UI-assisted fixture import evidence packet:

```bash
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --import-method ui-assisted \
  --assume-disposable \
  --result-json docs/research/ma3_fixture_import_probe_result.json \
  --execute
```

Next step is manual MA3 import of
`data/ma3_exports/probes/rayflow_control_probe.mvr`, followed by export/readback
evidence.

## Follow-Up: MVR Imported By User

The generated MVR was copied into MA3's internal MVR library:

```text
~/MALightingTechnology/gma3_library/mvr/rayflow_control_probe.mvr
```

The user imported it from the Patch menu's **Import MVR** button. After saving,
`rayflow_control_probe.show` was the newest modified show and recent
`rayflow_control_probe.backup_*.show` files existed, indicating the disposable
show changed after import.

Attempted command-line readback:

```text
Export MVR "rayflow_control_probe_after_import"
```

No exported MVR was found under `~/MALightingTechnology`, so MA3-side
export/readback evidence remains pending.

## Follow-Up: MVR Format Corrected

The first imported MVR only showed a `Univ` merge row and no visible fixtures.
RayFlow's exporter was compared against MA3's bundled `Demostage_MVR.mvr`.

Fixes applied:

- Changed archive XML member from `myvirtualrig.xml` to
  `GeneralSceneDescription.xml`.
- Changed fixture XML from simplified attributes to MA3/GDTF-style child
  elements: `GDTFSpec`, `GDTFMode`, `Addresses/Address`, `FixtureID`, and
  related fixture metadata.
- Added unique FixtureIDs for generated fixtures.

Regenerated and copied the corrected probe MVR to:

```text
~/MALightingTechnology/gma3_library/mvr/rayflow_control_probe.mvr
```

Targeted verification after the exporter change:

```bash
uv run ruff check .
uv run pytest -q tests/test_mvr_export.py tests/test_ma3_integration.py::TestMvrExport tests/test_console_probe.py tests/test_cli.py::TestConsoleCommands --no-cov
```

Result: 49 passed.
