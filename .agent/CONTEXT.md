# RayFlow Context

**Goal:** AI-assisted lit version of a song in grandMA3 onPC, viewed in its built-in 3D viewer. Beginner user; AI generates, explains, user tweaks.

**Current milestone:** Compare the same jam-band stage in Blender and grandMA3 onPC. AI handles setup and inspection. The user judges the images and gives a design revision. Start with the files and verified results in [the stage comparison](../stage-comparison/README.md). “Climb to Safety” is the song choice. Its recording, section timing and cue design are undecided.

**Resume here:** Blender and its two looks have been verified after reopening. The local grandMA3 bridge moved and restored fixture 1 in the demo. The saved copy `RayFlow_Jam_Stage_01` was active at wrap-up. Import `RayFlow_Stage.mvr` from the user library into that copy through Partial Show Read with scene objects included. Verify the twelve fixtures, four scenery objects and both looks in the native viewer. See the [probe and handoff](../docs/research/ma3-probes/ma3_demo_bridge_2_5_1.md).

**Earlier work:** v1 is archived at `archive/rayflow-v1`. Designer research, the starter layout and learning modules remain available. The November 19 patch plugin imported fixture types on 2.5.1.1, but its failed readback left the full rig unverified. See the [original test record](../docs/research/ma3-probes/ma3_lua_patch_3d_spike_2_5_1.md).

**Rules for agents**
- Do not build a generator for a step that has not passed its spike. Record each spike result with the plugin source in `docs/research/ma3-probes/`.
- The 2.3.2 probes verified OSC command receipt and timecode XML round trips. Check the newer stage comparison for 2.5.1.1 evidence before relying on those results.
- Capture cannot be fed from onPC without MA hardware. Do not plan around it.
- Tooling: `make setup`, `make lint`; Python via `uv run`.

**Key files:** `docs/research/ma3-probes/ma3_timecode_xml_2_3_2.md`, `docs/ai/MA3_COMMAND_REFERENCE.md`, `docs/research/programming-workflows/02-cue-and-effect-syntax.md`, `03-timecode-automation.md`, `docs/research/design-concepts/`, `songs/climb-to-safety/song.yaml`.
