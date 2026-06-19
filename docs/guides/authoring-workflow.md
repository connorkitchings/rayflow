# Authoring Workflow

Phase 10 generalizes the Phase 9 practice-show authoring loop for any RayFlow
show. The workflow stays file-first and proposal-first: inspect context, propose
cues, apply only when intentional, then render or report backend evidence.

## Plan Cues

Use `plan-cues` to propose deterministic renderer-safe cues for one section or
the whole show:

```bash
uv run rayflow show plan-cues phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --section Chorus \
  --style vibe-palette \
  --cues-per-section 3 \
  --json
```

Proposal mode is the default. It does not modify the show YAML.

Supported styles are:

- `energy-arc` — uses section energy to build base/lift looks.
- `warm-cool` — alternates warm front and cool lift looks.
- `front-back` — splits numeric fixture channel groups into front and back looks.
- `vibe-palette` — uses the show vibe palette, with a documented fallback when no
  vibe exists.
- `look-ambient` — lower-intensity, stable complete looks.
- `look-groove` — medium-energy looks with slow movement and modest texture.
- `look-peak` — high-energy beam, shutter, movement, and gobo looks when the rig
  supports them.
- `look-psychedelic` — saturated movement and gobo texture looks for jam peaks.

Generated cues intentionally stay inside the current renderer-safe authoring
surface. The complete-look styles add only attributes the renderer already
supports, such as dimmer, color, pan/tilt, zoom, focus, shutter, gobo,
`movement.*`, `gobo.speed`, and `gobo.rotation`. Unsupported fixture families
are skipped instead of forcing warnings.

## Apply A Plan

Apply only when you want to replace cues in the selected scope:

```bash
uv run rayflow show plan-cues phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --section Chorus \
  --style vibe-palette \
  --cues-per-section 3 \
  --apply \
  --json
```

Section scope replaces only cues in that section. `--section all` replaces cues
for all song sections. The command renumbers cues after applying.

## Verify The Result

After applying an authoring plan, run a workflow report before any live output:

```bash
uv run rayflow show workflow-report phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --backend artnet \
  --json
```

Live output remains gated through `workflow-report --execute`,
`output-cue --execute`, or `output-section --execute`.

For the Capture path, export the handoff bundle:

```bash
uv run rayflow show export-capture phase9_practice_show \
  --dir data/shows/samples \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --output-dir exports/capture/phase9_practice_show \
  --dmx-protocol sacn
```

Import `exports/capture/phase9_practice_show/rig.mvr` into Capture, match any
prompted fixture types, enable the selected DMX input protocol, and use the cue
sheet in the same bundle to review the show by song section.

## Feedback Refinement

Use `refine-cues` to translate a critique into targeted cue edits without
regenerating the whole show:

```bash
uv run rayflow show refine-cues phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --section Chorus \
  --critique bigger-chorus \
  --json
```

Supported critiques are `too-busy`, `less-movement`, `more-psychedelic`, and
`bigger-chorus`. Proposal mode is the default. Add `--apply` only when the
proposed edits should replace the selected cues in the show YAML.

The intended refinement loop is:

1. Generate or apply cues with `plan-cues`.
2. Export the Capture handoff with `export-capture`.
3. User reviews the result and gives critique such as "too busy," "less
   movement," "more psychedelic," or "make the chorus bigger."
4. RayFlow proposes targeted cue edits for the affected sections, preserving
   unrelated cues.
5. The AI applies only after review, then reruns preview and Capture export.

Refinement reuses existing cue fields and `look-*` vocabulary rather than
introducing a new persistent show schema.

## Compatibility

`plan-practice-cues` remains available for the Phase 9 practice workflow, but it
now delegates to the generic authoring planner with two cues per section.
