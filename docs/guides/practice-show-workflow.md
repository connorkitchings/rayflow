# Practice Show Workflow

Phase 9 starts with a deterministic practice workflow that uses only checked-in
RayFlow data and fixture samples. The first goal is to prove the whole path from
show intent to backend dry-run evidence, then optionally capture live receiver
proof when Art-Net or sACN hardware/software is available.

## Inputs

Use the Phase 9 practice files:

- Rig: `data/rigs/Practice Small Club.yaml`
- Show: `data/shows/samples/phase9_practice_show.yaml`
- Fixtures: `data/fixtures/samples`

The practice rig uses four `LED PAR 64 RGBW` fixtures in the `Default` mode. It
does not depend on external fixture downloads, QLC+, or grandMA3.

## Render a Cue

Render one cue to sparse universe/channel DMX values:

```bash
uv run rayflow show render-cue phase9_practice_show 5 \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --json
```

Cue 5 is the chorus cyan look. A clean render should include universe `0`
channel values for all four PAR fixtures and no render warnings.

## Report the Workflow

Generate the dry-run workflow report for the full show:

```bash
uv run rayflow show workflow-report phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --backend artnet \
  --json
```

The report includes:

- selected show, rig, backend, section, and mode
- ordered rendered cue groups
- backend dry-run evidence packets
- render and backend warnings
- readiness status
- timestamp

Use a section filter when validating a smaller part of the song:

```bash
uv run rayflow show workflow-report phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --section Chorus \
  --backend sacn \
  --json
```

Write the same JSON to disk for handoff:

```bash
uv run rayflow show workflow-report phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --backend artnet \
  --output reports/phase9-practice-workflow.json \
  --json
```

## Plan Practice Cues

Use `plan-practice-cues` to scaffold deterministic renderer-safe cues from the
show sections. Proposal mode is the default and does not modify the show file:

```bash
uv run rayflow show plan-practice-cues phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --section Chorus \
  --style energy-arc \
  --json
```

Apply the plan only when you want to replace the selected section's cues:

```bash
uv run rayflow show plan-practice-cues phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --rig-dir data/rigs \
  --section Chorus \
  --style energy-arc \
  --apply \
  --json
```

Supported styles are `energy-arc`, `warm-cool`, and `front-back`. The generated
cues intentionally stay within the v1 renderer surface: dimmer, color, channels,
preset, and fade time.

## Evidence Boundary

`workflow-report` is dry-run by default. It proves that RayFlow can resolve show
data, render fixture-aware DMX frames, and produce backend evidence plans without
touching live output.

Use `--execute` only when live Art-Net or sACN output is intentionally required.
Add `--capture-evidence` when a receiver is available:

```bash
uv run rayflow show workflow-report phase9_practice_show \
  --dir data/shows/samples \
  --rig "Practice Small Club" \
  --backend artnet \
  --section Chorus \
  --execute \
  --capture-evidence \
  --evidence-timeout 0.25 \
  --json
```

Art-Net evidence compares receiver buffers against rendered sparse channel
values. sACN evidence records observed universe presence; channel-level sACN
proof remains future hardening unless the library exposes channel data.

The Phase 9 closure proof used local Art-Net loopback and is archived at
`session_logs/05-25-2026/phase9-loopback-evidence.json`. A passing Art-Net proof
has `readiness.status` set to `ready`, each evidence packet marked
`receiver-buffer`, and each receiver capture marked `matches_rendered: true`.

QLC+ remains an experimental WebSocket spike through `show qlc-spike`. MA3
remains a compatibility/export path, not the mainline Phase 9 workflow.
