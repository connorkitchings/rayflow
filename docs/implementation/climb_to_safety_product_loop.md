# Climb to Safety Product Loop Handoff

**Date:** 2026-06-05

## Status

`Climb to Safety Studio` now has a reproducible RayFlow product-loop pass:

- Rig: `data/rigs/Rig 1.yaml`
- Show: `data/shows/Climb to Safety Studio.yaml`
- Primary visual path: Capture handoff via MVR
- Compatibility path: MA3/MVR export bundle
- Cue count: 16
- Fixture count: 14
- Final preview readiness: `ready`
- QLC+ finding: not suitable as the product visual-review path

## What Was Reviewed

Baseline preview showed the current pilot as renderer-clean: 16 cues, 14 fixtures,
37 rig presets, and no warnings. The review focus was whether chorus and final
chorus sections clearly lifted above verses.

Applied feedback:

- `Chorus 1`: cues 5 and 6 were brightened and labeled `(bigger)`.
- `Chorus 2`: cues 9 and 10 were brightened and labeled `(bigger)`.
- `Final Chorus`: cues 13 and 14 were brightened and labeled `(bigger)`.

The first refinement pass added unsupported moving-light controls to front PAR
cues. That was corrected, and `refine-cues` now scopes capability-aware additions
to the fixtures targeted by each cue.

## Evidence Artifacts

- Capture handoff: `exports/capture/climb-to-safety/`
- MA3 compatibility bundle: `exports/ma3/climb-to-safety/`
- Dry-run recording report:
  `exports/recordings/climb_to_safety/post_refinement_recording_report.json`
- Pre-refinement snapshot:
  `data/show_library/climb-to-safety-studio/20260605T124425Z/show.yaml`
- Post-refinement snapshot:
  `data/show_library/climb-to-safety-studio/20260605T130214Z/show.yaml`

## Reproduce

```bash
uv run rayflow rig info 'Rig 1' --dir data/rigs --json

uv run rayflow show preview 'Climb to Safety Studio' \
  --dir data/shows \
  --rig 'Rig 1' \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --json

uv run rayflow show export-capture 'Climb to Safety Studio' \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --output-dir exports/capture/climb-to-safety \
  --dmx-protocol sacn

uv run rayflow show export 'Climb to Safety Studio' \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --output-dir exports/ma3/climb-to-safety \
  --sequence 1

uv run rayflow show record 'Climb to Safety Studio' \
  --rig 'Rig 1' \
  --dir data/shows \
  --rig-dir data/rigs \
  --output exports/recordings/climb_to_safety/post_refinement_recording_report.json \
  --video-path exports/recordings/climb_to_safety/manual_capture.mov \
  --audio-path audio/climb_to_safety_studio.wav \
  --json \
  --yes
```

## Manual Capture Checklist

1. Open Capture 2026 or Capture 2026 Student Edition.
2. Import `exports/capture/climb-to-safety/rig.mvr`.
3. Map any prompted fixture types to Capture library fixtures.
4. Configure Capture to receive sACN or Art-Net.
5. Start the screen recorder and the studio track.
6. Trigger RayFlow cues over the selected DMX protocol.
7. Save the captured video at `exports/recordings/climb_to_safety/manual_capture.mov`.
8. Keep the cue sheet and recording report with the video as the audit trail.

## Remaining Gaps

- This is a Capture handoff and dry-run playout loop, not yet a captured video.
- Capture is now the primary visual target, but native Capture project generation
  is not implemented yet.
- The next quality pass should be visual/taste-driven from an actual recording:
  timing, brightness, chorus scale, texture density, and color temperature by
  section.
