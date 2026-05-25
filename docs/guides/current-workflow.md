# Current RayFlow Workflow

RayFlow's current usable workflow is file-first, dry-run-first, and compatible
with grandMA3 without making MA3 the only runtime target.

Use this path to review generated cues, version show files, export handoff
bundles, and push only verified MA3-compatible commands when explicitly
requested.

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

## 4. Export An MA3 Compatibility Bundle

The export bundle writes files only. It does not contact grandMA3.

```bash
uv run rayflow show export "My Show" --output-dir exports/my-show --sequence 1
```

The bundle includes:

- `rig.mvr` — MVR rig export for MA3 or other MVR-aware tools.
- `ma3_push_commands.txt` — one MA3 command per line for review.
- `README.md` — import and push workflow notes.
- `metadata.json` — bundle details for automation and review.

This is a compatibility artifact. It is not the long-term core execution path.

## 5. Dry-Run And Push MA3 Commands

Always dry-run the push path before sending OSC:

```bash
uv run rayflow show push-to-ma3 "My Show" --sequence 1
```

Only send commands when the command list, MA3 target show, and OSC setup are
confirmed:

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

## 6. Export And Import MA3 Timecode

RayFlow generates MA3 Timecode XML for shows with cue timestamps:

```bash
uv run rayflow show export-timecode "My Show" \
  --output ~/MALightingTechnology/gma3_library/datapools/timecodes/my_show_timecode.xml \
  --sequence 1
```

Before importing Timecode XML, create or import the target sequence cues first.
For a clean replacement in MA3:

```text
Delete Timecode 1 /NoConfirmation
Import Timecode Library "my_show_timecode.xml" At Timecode 1
```

## 7. Current Boundary

The MA3-compatible path currently sends safe dimmer/intensity values only.
Color palette values are preserved in RayFlow show data, but fixture-aware color
mapping belongs in the new renderer layer.

The Phase 8 backend-neutral workflow is now:

1. Resolve fixture capabilities from the RayFlow rig and GDTF library.
2. Render cue intent into DMX universe frames:

```bash
uv run rayflow show render-cue sample_show 6 \
  --dir data/shows/samples \
  --rig "Sample Rig" \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --json
```

3. Dry-run backend output evidence before any live send:

```bash
uv run rayflow show output-cue sample_show 6 \
  --dir data/shows/samples \
  --rig "Sample Rig" \
  --backend artnet \
  --json
```

4. Apply only with `--execute`; add `--capture-evidence` when a receiver is
   available for Art-Net buffer comparison or sACN universe-state proof.
5. Use `show output-section` for ordered section-level dry-runs.
6. Use `show workflow-report` for a Phase 9 practice-show handoff that aggregates
   rendered cue groups, backend evidence, warnings, and readiness status. It is
   dry-run by default; live output requires `--execute`.
7. Use `show plan-cues --json` to propose deterministic renderer-safe cues for
   any show before applying them to the show YAML with `--apply`.
8. Use `show plan-practice-cues --json` for the Phase 9 practice workflow
   compatibility path.
9. Use `show qlc-spike --json` for experimental QLC+ WebSocket command/query
   evidence. Do not treat QLC+ as promoted until live query proof exists.
10. Keep MA3 as an export/playback adapter with explicit evidence gates.
