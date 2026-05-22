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
