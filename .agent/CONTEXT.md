# RayFlow Context

**Goal:** AI-assisted lit version of a song in grandMA3 onPC, viewed in its built-in 3D viewer. Beginner user; AI generates, explains, user tweaks.

**State:** Restart after v1 (archived at tag `archive/rayflow-v1`). Phase 0 done. Phase 1 (user updates onPC to 2.5, follows `docs/learn/01-first-hour-ma3.md`, confirms 3D beams render) gates everything.

**Phases:** 1 learn → 2 Lua spikes (patch+3D, groups/presets, cues, song sync) → 3 minimal generator (`rig.yaml`, `song.yaml`, `design.yaml` → Jinja templates → Lua plugin + timecode XML).

**Rules for agents**
- Do not build a generator for a step that has not passed its spike. Record each spike result with the plugin source in `docs/research/ma3-probes/`.
- Verified facts: OSC `/cmd` works; timecode XML import/export round-trips on 2.3.2; MVR import blocked; timecode track/event creation by command line was UI-only; Lua plugins are untried.
- Capture cannot be fed from onPC without MA hardware. Do not plan around it.
- Tooling: `make setup`, `make lint`; Python via `uv run`.

**Key files:** `docs/research/ma3-probes/ma3_timecode_xml_2_3_2.md`, `docs/ai/MA3_COMMAND_REFERENCE.md`, `docs/research/programming-workflows/02-cue-and-effect-syntax.md`, `03-timecode-automation.md`, `docs/research/design-concepts/`, `songs/climb-to-safety/song.yaml`.
