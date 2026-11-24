# RayFlow

Take a song, build a stage, and make a lit version of the song in real console software, with AI help, as a beginner.

The current milestone is an editable jam-band stage in Blender and grandMA3 onPC. Compare the same twelve fixture positions from the audience, give one design note, and judge how easily the AI can make that change. The stage files and test results are in the [stage comparison](stage-comparison/README.md).

## Earlier show-programming plan

1. **Stage** – `rig.yaml` lists fixtures and positions. AI turns it into a grandMA3 Lua plugin that patches, places fixtures in 3D and creates groups.
2. **Song** – the audio file plus `song.yaml` (sections with timestamps). AI drafts the map, you correct it.
3. **Design** – you describe the vibe. AI writes `design.yaml`: per section, the look, color, movement and timing, with plain-English reasoning.
4. **Build** – a small generator fills templates of proven Lua plugins and a timecode XML.
5. **Watch and iterate** – play the timecode in onPC, watch the 3D viewer, give feedback or edit in MA3 yourself.

## Status

Restarted from scratch. The previous Python/DMX implementation is preserved at git tag `archive/rayflow-v1`.

| Phase | What | State |
|---|---|---|
| 0 | Archive and prune | done |
| 1a | Pre-work: sourced LD research, style guide, learn index, starter rig, glossary, skills | done |
| Stage comparison | AI builds the rig, checks the editable files and presents two lighting looks | Blender verified. MA demo fixture control verified. Custom MA show copy saved and ready for import. |
| 1b | Hands-on modules 1-7 in onPC | available for learning on demand |
| 2 | Lua plugin spikes in MA3: (a) patch + 3D placement, (b) groups/presets/cues plus one slow position phaser, (c) sound + timecode playback | (a) run 2026-11-19, partial (`ma3/plugins/spike_patch_3d/`, results in `docs/research/ma3-probes/ma3_lua_patch_3d_spike_2_5_1.md`): imports and mover patch worked, wash patch and readback failed, 3D beams not yet confirmed; needs a fix and re-run. (b) and (c) blocked on phase 1b |
| 3 | Minimal generator, Climb to Safety end to end | blocked on phase 2 |

Rule: no generator is built for a step that has not passed its spike.

## Layout

- `docs/research/` – lighting design and grandMA3 research (kept from v1)
- `docs/research/ma3-probes/` – what was verified on onPC 2.3.2
- `docs/ai/MA3_*.md` – grandMA3 command and operation references
- `songs/climb-to-safety/song.yaml` – earlier draft timing map. The song selection is confirmed. The recording, timestamps and musical design await review.
- `ma3/plugins/` – Lua plugins (spike results go to `docs/research/ma3-probes/`)

## Development

```
make setup   # uv sync
make lint    # ruff format + check
```
