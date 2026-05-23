# MA3 Disposable Show And Fixture Probe

**Date:** 2026-05-22
**grandMA3 onPC version:** 2.3.2.0
**Target show:** `rayflow_control_probe`

## Commands

Attempt 1:

```text
NewShow
SaveShow As "rayflow_control_probe"
```

Result: failed isolation. MA3 created `As.show`, which indicates `As` was
parsed as the show name or Assign shortcut rather than as a SaveShow modifier.

Attempt 2:

```text
NewShow
SaveShow "rayflow_control_probe"
```

Result: failed isolation. No `rayflow_control_probe.show` file was created.
The only recently modified show remained `As.show`.

Attempt 3:

```text
NewShow "rayflow_control_probe"
SaveShow
```

Result: failed isolation. The commands were sent to `127.0.0.1:8000`, but
no `.show` file mtime changed and `rayflow_control_probe.show` was not created.
The MA3 UI title remained
`Display 1 onPC 2.3.2.0 [NewShow_2026.05.22_13.36.00UTC]`.

Attempt 4:

```text
SaveShow "rayflow_control_probe"
```

Result: failed. This command matches MA's documented save-as syntax, but the
active show title and show directory did not change. This indicates the current
session still has an OSC command-acceptance problem, despite UDP 8000 being
bound by `app_gma3`.

## Filesystem Evidence

Observed show directory after both attempts:

```text
~/MALightingTechnology/gma3_2.3.2/shared/shows/As.show
~/MALightingTechnology/gma3_2.3.2/shared/shows/rayflow_test.show
~/MALightingTechnology/gma3_2.3.2/shared/shows/Rescue.show
```

Recent files after attempt 2:

```text
~/MALightingTechnology/gma3_2.3.2/shared/shows/As.show
~/MALightingTechnology/gma3_2.3.2/shared/backups/As.backup_2026.05.22_09.52.00UTC.show
```

No `rayflow_control_probe.show` file was observed.

Additional live evidence after enabling MA3 OSC input:

```text
app_gma3 UDP *:8000
```

Latest guarded result:

```text
docs/research/ma3_show_isolation_probe_result.json
```

That result records identical pre/post show mtimes for:

```text
As.show
Rescue.show
rayflow_test.show
```

## Fixture Import / Patch Evidence

Not attempted. The harness correctly blocked deeper live mutation because
disposable-show isolation did not pass.

## Capability Updates

| Capability | Status | Evidence |
| --- | --- | --- |
| Probe runner dry-run | Verified | Dry-run commands render without OSC send. |
| Probe runner mutation guard | Verified | Live probe stopped after isolation failure. |
| Disposable show creation by OSC command | Not proven | Both SaveShow command variants failed to produce `rayflow_control_probe.show`. |
| OSC `/cmd` acceptance in current MA3 session | Not proven | UDP 8000 is bound, but `About`/`SaveShow` produced no observable MA3 title or file change. Confirm `Receive Command All` or row-level Receive Command before retry. |
| Fixture import / patch proof | Blocked | Requires verified disposable show or explicit UI confirmation first. |

## Next Step

Resolve disposable show setup through one of:

1. Use MA3 UI to create/load `rayflow_control_probe` and then let the harness
   verify the active show by file mtime.
2. Find a documented non-interactive `NewShow`/`SaveShow` sequence that creates
   `rayflow_control_probe.show` without creating `As.show` or modifying another
   show.
3. Confirm MA3 OSC row command receive is active. In the OSC sheet, `Receive`
   alone is not sufficient for `/cmd`; the row must also allow command receive
   via `Receive Command All` or the corresponding row setting.
4. Extend the harness with an explicit user-confirmed `--assume-disposable`
   mode only for cases where the UI has already been verified manually.

## Harness Update — 2026-05-23

RayFlow now has a two-gate probe workflow before deeper MA3 programming:

```bash
uv run rayflow console probe command-acceptance \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_command_acceptance_probe_result.json \
  --execute

uv run rayflow console probe show-isolation \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_show_isolation_probe_result.json \
  --execute
```

The command-acceptance probe sends an OSC `/cmd` export request and requires an
observable MA3 export file. UDP listener presence remains informational only.

Live result on 2026-05-23, first run:

```text
uv run rayflow console probe command-acceptance \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_command_acceptance_probe_result.json \
  --execute
```

Status: failed. The OSC row had `Receive Command=No`, so MA3 ignored `/cmd`.

After enabling `Receive Command`, MA3 accepted `/cmd`, but the visible command
line was in the `Fixture` destination. Sending `About` produced:

```text
Illegal object: Fixture "About"
```

RayFlow now prepends `ChangeDestination Root` to generated command-acceptance
and show-isolation plans. The corrected command-acceptance probe passed and
wrote:

```text
~/MALightingTechnology/gma3_library/datapools/sequences/rayflow_command_acceptance_probe_sequence.xml
```

Show isolation remains blocked. `NewShow "rayflow_control_probe"` followed by
`SaveShow` modified the current `NewShow_2026.05.22_13.36.00UTC.show` file
instead of creating `rayflow_control_probe.show`. A direct
`SaveShow "rayflow_control_probe"` command also did not create the target file.
Use a UI-created/loaded disposable target show or record explicit
`--assume-disposable` confirmation before live fixture import evidence.

Follow-up: the user loaded `rayflow_control_probe.show` through the MA3 Backup /
Load Show UI. The corrected `show-isolation --assume-disposable` path now sends
only:

```text
ChangeDestination Root
SaveShow
```

and records the user-confirmed disposable state without attempting `NewShow`.

If command acceptance works but show-file mtimes still cannot prove isolation,
`show-isolation --assume-disposable` can record explicit user confirmation that
the active MA3 show is disposable. This is a safety bypass, not automation proof.

Fixture import proof is split from live programming:

```bash
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --execute
```

This builds `data/ma3_exports/probes/rayflow_control_probe.mvr` with:

- `Probe LED PAR 1` from `BlenderDMX_LED_PAR_64_RGBW.gdtf`
- `Probe MMX Blade 1` from `Robe_Robin_MMX_Blade.gdtf`

Local artifact result on 2026-05-23:

```text
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --result-json docs/research/ma3_fixture_import_probe_result.json \
  --execute
```

Status: passed for MVR generation only. The MVR contains `myvirtualrig.xml`,
`BlenderDMX_LED_PAR_64_RGBW.gdtf`, and `Robe_Robin_MMX_Blade.gdtf`. No live MA3
import was attempted because command acceptance failed.

For import evidence, the CLI-first path is:

```bash
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --import-method cli \
  --assume-disposable \
  --result-json docs/research/ma3_fixture_import_probe_result.json \
  --execute
```

The CLI import command is recorded as inconclusive until MA3 export/UI evidence
proves the patch exists. If that command path remains unverified, use:

```bash
uv run rayflow console probe fixture-import \
  --target-show rayflow_control_probe \
  --import-method ui-assisted \
  --assume-disposable \
  --result-json docs/research/ma3_fixture_import_probe_result.json \
  --execute
```

The UI-assisted path records the intended import method and remains pending
verification until separate MA3 import/readback evidence is captured. It does
not mark fixture-aware programming complete.

Current `docs/research/ma3_fixture_import_probe_result.json` records
`import_method=ui-assisted` for the generated MVR. The next evidence step is to
import `data/ma3_exports/probes/rayflow_control_probe.mvr` in MA3 and capture
patch/fixture evidence.

Follow-up: the MVR was copied to MA3's internal MVR library folder:

```text
~/MALightingTechnology/gma3_library/mvr/rayflow_control_probe.mvr
```

The user imported it from the Patch menu using **Import MVR**. A subsequent
`SaveShow` updated `rayflow_control_probe.show` and created recent
`rayflow_control_probe.backup_*.show` files, so the import likely changed the
disposable show. A command-line `Export MVR "rayflow_control_probe_after_import"`
did not produce a readback MVR, so export/readback proof is still pending.

The first generated MVR did not create visible fixtures in Patch. Investigation
against MA3's bundled `Demostage_MVR.mvr` showed two compatibility problems in
RayFlow's exporter:

- MA3 expects `GeneralSceneDescription.xml` inside the `.mvr` archive.
- Fixture data should use MA3/GDTF child elements such as `GDTFSpec`,
  `GDTFMode`, `Addresses/Address`, and `FixtureID`, not RayFlow's earlier
  simplified attributes.

RayFlow now regenerates `rayflow_control_probe.mvr` with the MA3-compatible
shape and unique FixtureIDs. The corrected file has been copied to:

```text
~/MALightingTechnology/gma3_library/mvr/rayflow_control_probe.mvr
```

Second import attempt still showed only a single `Univ` row in MA3's MVR Merge
screen, with no `Probe LED PAR 1` or `Probe MMX Blade 1` fixture rows. Treat MVR
fixture import as still blocked; continue with command-line patching as the next
fallback proof path now that OSC `/cmd` acceptance is working.

Fallback path: the user manually patched a `Generic` / `Dimmer` / `Mode 0`
fixture with FID `1` and patch `1.001`. The show file
`rayflow_control_probe.show` updated after `SaveShow`, confirming the disposable
show is active and being saved. RayFlow sent `Fixture 1 At Full`, `Store
Sequence 1 Cue 1 /Overwrite /NoConfirmation`, and `Label Sequence 1 "RayFlow
Dimmer Proof"`. However, subsequent `Export Sequence 1 ...` commands did not
write a sequence XML file, so stored-cue readback remains pending. The next
check is MA3 Command Line History for parser feedback from `List Sequence 1` or
the failed `Export Sequence 1` command.
