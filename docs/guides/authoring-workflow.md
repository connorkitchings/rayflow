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

Generated cues intentionally stay inside the current renderer-safe authoring
surface: dimmer, color, channels, preset, and fade time.

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

## Compatibility

`plan-practice-cues` remains available for the Phase 9 practice workflow, but it
now delegates to the generic authoring planner with two cues per section.
