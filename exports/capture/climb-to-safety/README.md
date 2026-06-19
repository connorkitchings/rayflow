# RayFlow Capture Handoff: Climb to Safety Studio

This bundle is the primary visual-review path for RayFlow. QLC+ is not used for
this workflow.

## Contents

- `rig.mvr` — MVR rig export for Capture import.
- `cue_sheet.md` — Cue list for review against the song.
- `metadata.json` — Machine-readable handoff metadata.

## Capture Import

1. Open Capture 2026 or Capture 2026 Student Edition.
2. Import `rig.mvr`.
3. If Capture prompts for fixture matching, map imported GDTF fixture types to
   available Capture library fixtures.
4. Confirm the imported rig uses `Rig 1` fixture positions and DMX patch.

## DMX Review Path

Use `sACN` for live visual review unless your local Capture setup is
configured for a different DMX input protocol.

RayFlow can render cue DMX frames directly. The next review loop should connect
RayFlow's DMX output to Capture, then watch Capture while cues are triggered in
song time.

## Current Boundary

This bundle imports the rig and cue review context. It does not create a native
Capture project file and does not yet automate Capture fixture matching or
camera setup.
