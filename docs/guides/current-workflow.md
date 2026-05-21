# Current RayFlow Workflow

RayFlow can already support a practical MA3 show-building workflow without
native Timecode XML. Use this path to review generated cues, version show files,
export a handoff bundle, and push cues into grandMA3 when ready.

Native MA3 Timecode XML generation is still blocked until an event-bearing
grandMA3 2.3.2.0 Timecode export is captured and documented.

## 1. Check Available Rigs And Shows

```bash
uv run rayflow rig list
uv run rayflow show list
```

Inspect a show before making changes:

```bash
uv run rayflow show info "My Show"
uv run rayflow show context "My Show" --json
```

## 2. Save A Version Before Editing

Use the show library as a local safety net. It stores YAML snapshots under
`data/show_library` by default.

```bash
uv run rayflow show save "My Show" --message "before cue polish"
uv run rayflow show versions "My Show"
```

Compare current work against a saved version:

```bash
uv run rayflow show diff "My Show" --version 20260520T120000Z
```

Restore only when you intentionally want to overwrite the current show file:

```bash
uv run rayflow show restore "My Show" --version 20260520T120000Z --force
```

## 3. Generate Or Edit Cues

Create cue skeletons from an existing section:

```bash
uv run rayflow show generate-cues "My Show" \
  --section "Chorus" \
  --preset "warm_wash" \
  --count 4 \
  --spacing 4 \
  --fade 1.5
```

Adjust individual cues or batch-edit a section:

```bash
uv run rayflow show update-cue "My Show" --number 3 --label "Chorus lift"
uv run rayflow show batch-update-cues "My Show" --section "Chorus" --set-fade 1.0
```

Save another version after a useful edit checkpoint:

```bash
uv run rayflow show save "My Show" --message "chorus cue pass"
```

## 4. Export An MA3 Review Bundle

The export bundle writes files only. It does not contact grandMA3.

```bash
uv run rayflow show export "My Show" --output-dir exports/my-show --sequence 1
```

The bundle includes:

- `rig.mvr` — MVR rig export for MA3 patch and 3D import.
- `ma3_push_commands.txt` — one MA3 command per line for review.
- `README.md` — import and push workflow notes.
- `metadata.json` — bundle details for automation and review.

## 5. Dry-Run And Push Cues

Always dry-run the push path before sending OSC:

```bash
uv run rayflow show push-to-ma3 "My Show" --sequence 1
```

When the command list looks correct and MA3 OSC input is configured:

```bash
uv run rayflow show push-to-ma3 "My Show" --sequence 1 --execute
```

For local onPC testing, use the MA3 interface IP if loopback is not active:

```bash
uv run rayflow show push-to-ma3 "My Show" --sequence 1 --ip 10.0.0.241 --execute
```

To push only one section:

```bash
uv run rayflow show push-section "My Show" --section "Chorus" --sequence 1
uv run rayflow show push-section "My Show" --section "Chorus" --sequence 1 --execute
```

## 6. Export And Import Timecode

RayFlow generates MA3 Timecode XML for shows with cue timestamps:

```bash
uv run rayflow show export-timecode "My Show" \
  --output ~/MALightingTechnology/gma3_library/datapools/timecodes/my_show_timecode.xml \
  --sequence 1
```

Before importing Timecode XML, push the target sequence cues first. For a clean
replacement in MA3:

```text
Delete Timecode 1 /NoConfirmation
Import Timecode Library "my_show_timecode.xml" At Timecode 1
```

## Current Boundary

RayFlow's Timecode XML has clean import/re-export validation against grandMA3
onPC 2.3.2.0, but final playback observation is still pending. The current
MA3-native path is:

1. Import the MVR rig.
2. Push or review sequence/cue commands.
3. Import Timecode XML into a clean Timecode pool object.
4. Verify event playback in the Timecode Viewer.

The push path currently sends safe dimmer/intensity values only. Color palette
values are preserved in RayFlow show data, but fixture-aware color mapping is a
separate implementation step.
