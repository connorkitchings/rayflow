# RayFlow

Take a song, build a stage, and make a lit version of the song in real console software, with AI help, as a beginner.

RayFlow targets **grandMA3 onPC** and its **built-in 3D viewer**. No hardware or visualizer purchase is needed. (grandMA3 onPC cannot feed Capture without MA hardware, so Capture is deferred.)

## Workflow

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
| 1a | Pre-work: sourced LD research, style guide, learn index, starter rig, glossary, skills | in progress |
| 1b | Hands-on modules 1-7 in onPC (start: `docs/learn/01-first-hour-ma3.md`), confirm 3D viewer renders on this Mac | next (user) |
| 2 | Lua plugin spikes in MA3: patch + 3D placement, groups/presets, cues, song sync | blocked on phase 1b |
| 3 | Minimal generator, Climb to Safety end to end | blocked on phase 2 |

Rule: no generator is built for a step that has not passed its spike.

## Layout

- `docs/research/` – lighting design and grandMA3 research (kept from v1)
- `docs/research/ma3-probes/` – what was verified on onPC 2.3.2
- `docs/ai/MA3_*.md` – grandMA3 command and operation references
- `songs/climb-to-safety/song.yaml` – pilot song section map
- `ma3/plugins/` – Lua plugins (spike results go to `docs/research/ma3-probes/`)

## Development

```
make setup   # uv sync
make lint    # ruff format + check
```
