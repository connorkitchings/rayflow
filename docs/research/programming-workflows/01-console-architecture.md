# Console Architecture and Tracking

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## The Two-Layer Console Architecture

Professional consoles separate control into two primary layers:

- **Programmer:** Temporary workspace. Changes are output to the stage for evaluation but are not yet saved.
- **Executor (Playback):** Physical or virtual button, fader, or cue list mapped to playback. Once a look is recorded here, clearing the programmer returns the console to idle, and recorded cues drive live output.

## Building Blocks: Palettes, Presets, and Tracking

### Palettes

Modular references containing specific attribute data for selected fixtures (Position, Color, Gobo, Beam). When a cue is recorded, the console saves a reference pointer to the palette rather than absolute DMX values. If a tour moves to a venue with different trim height, the programmer updates the "Lead Singer" Position Palette and the console propagates the correction to every cue referencing it.

### Tracking

Professional consoles operate in tracking mode by default. When a value is recorded in a cue, it "tracks forward" through subsequent cues until a deliberate instruction changes it. Example: if Cue 1 turns a backlight on to 80%, that light remains at 80% in Cues 2, 3, and 4. This reduces show file data and simplifies editing.

### Snowballing and Block Cues

Tracking can introduce "snowballing" where an edit in an early cue unintentionally modifies subsequent scenes. **Block Cues** stop tracked values from affecting subsequent scenes, keeping the cue list predictable.

### Cue-Only Mode

Every cue is treated as an entirely independent snapshot. Changes apply only to that specific cue; the console automatically restores the previous state in the next cue.
