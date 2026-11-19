# Advanced Cue Structures: Parts, Mark Cues, Crossfades, and Blocking

**Source:** Web research, console manuals, professional programming workflows
**Parsed:** 2026-05-25

## Beyond Basic Cue Lists

A basic cue stores a snapshot of fixture values with a fade time. Professional productions require richer cue structures. This document covers the advanced cue behaviors that inform a production-grade cue data model.

## Part Cues

A **Part Cue** splits a single cue point into multiple sub-components, each with independent timing:

```
Cue 5: "Verse 1 Hit"
  Part 1: Dimmer @ Full, Fade 0s, Delay 0s      (instant snap)
  Part 2: Color → Red, Fade 1s, Delay 0s         (color sweep over 1s)
  Part 3: Position → Sweep, Fade 2s, Delay 0.5s  (move begins after 0.5s delay)
```

### Why Parts Matter
- **Musical phrasing:** A drum fill needs instant strobes (Part 1) while washes bloom in slower (Part 2).
- **Layered transitions:** Dimmer snaps, color fades, and position moves can have different timing profiles within the same musical moment.
- **Console efficiency:** Programmed in one cue rather than three separate cues close together, reducing cue count and improving readability.

### RayFlow Implication
The current `Cue` model has a single `fade_time` per cue. Supporting part cues requires either a `parts: list[PartCue]` field or `delay_attributes: dict[str, float]` per-attribute delay offsets.

## Mark Cues / Move-In-Black (MIB)

**Mark Cues** pre-position fixtures silently (with dimmer at zero) before they are needed, so when the actual cue fires, the fixture is already in position:

```
Cue 3.5 (MARK): Position → Stage Right, Dimmer @ 0       (fixture moves in dark)
Cue 4:          Dimmer @ Full                             (fixture already in position, instant snap)
```

### Move-In-Black Variants

| Type | Behavior |
|------|----------|
| **Auto-Mark** | Console automatically inserts mark moves before any cue that references a fixture for the first time in a sequence |
| **Manual Mark** | Programmer explicitly creates a mark cue with dimmer at zero |
| **Mark Flag** | Per-fixture setting: "Mark this fixture before next cue" |
| **Pre-Mark** | Mark timed to complete before the referenced cue's trigger (console calculates required lead time) |

### Why Marking Matters
- **Silent repositioning:** Moving heads make noise and draw attention during movement. Marking hides this.
- **Tight musical timing:** If a cue needs a fixture pointing at the lead singer, it must be there when the dimmer opens. A 1-second pan move + 0-second fade = 1 second of visible movement. Marking makes it instant.
- **Tracking integration:** Marked fixtures' positions track forward through subsequent cues until deliberately changed, just like visible values.

### Challenges
- **Gobo/color settling:** Some fixtures have mechanical settling time (gobo wheels, color wheels) that exceeds pan/tilt movement time. Mark timing must account for the slowest parameter.
- **Multiple sequences:** A fixture can only be in one position at a time. If two sequences both mark the same fixture to different positions, the last mark wins.
- **Priority conflicts:** MA3 resolves this via executor priority levels and "Assert" behavior.

## Crossfade Types (X-Fade, Y-Fade, Z-Fade)

Different attribute families fade differently between cues. Consoles split crossfades into types:

| Crossfade Type | Attributes | Behavior |
|---------------|-----------|----------|
| **X-Fade (HTP)** | Dimmer, shutter, strobe | Highest-Takes-Precedence during the fade. Incoming and outgoing intensities overlap smoothly. |
| **Y-Fade (LTP)** | Position, color, beam, gobo, focus | Latest-Takes-Precedence. Incoming values snap at the start of the fade (or smoothly transition via fade time). |
| **Z-Fade (Split)** | Mixed | Some channels fade (dimmer), others snap (gobo wheel can't crossfade — it's a discrete index). |

### Crossfade Timing Table

| Parameter | Fade Behavior | Why |
|-----------|--------------|-----|
| Dimmer | Smooth crossfade (HTP) | Perceptual smoothness, no mechanical constraints |
| Pan/Tilt | Smooth crossfade (LTP with fade time) | Motorized movement can interpolate |
| Color Mix (CMY/RGB) | Smooth crossfade | Electronic/mechanical color mixing supports interpolation |
| Color Wheel | Snap at start of fade | Discrete wheel positions cannot crossfade |
| Gobo Wheel | Snap at start of fade | Discrete wheel. Gobo rotation can crossfade. |
| Prism | Snap | Discrete insertion/removal |
| Iris | Smooth crossfade | Continuous mechanical iris |
| Zoom | Smooth crossfade | Continuous motorized zoom |
| Strobe Rate | Smooth crossfade | Continuous frequency parameter |

## Assert, Release, and Block Cues

### Assert
Forces all values in a cue to be stored as absolute, even if they were tracked from previous cues. Used at the start of a new scene to establish a known baseline.

### Release
Removes a fixture from the current sequence's control, returning it to its default (home) state or allowing another sequence to take over.

### Block Cues
Stops all tracked values from the previous cue from propagating forward. Every parameter is stored explicitly in a block cue, creating a clean break. Block cues are placed:
- At the start of each act/scene to prevent cross-scene contamination
- After dark/blackout cues to reset the tracking state
- Before a sequence that re-uses fixtures in different configurations

### Assert vs. Block
- **Block:** Prevents *future* tracking (values stop here)
- **Assert:** Establishes *current* values explicitly (ensures known state now)
- Often used together: Block + Assert at the top of a new scene

## Tracking Across Multiple Sequences

A single fixture can be controlled by multiple sequences simultaneously via HTP/LTP priority rules:

| Priority Rule | Applies To | Behavior |
|---------------|-----------|----------|
| **HTP (Highest Takes Precedence)** | Dimmer, intensity | If two sequences both control a fixture's dimmer, the highest dimmer value wins |
| **LTP (Latest Takes Precedence)** | Position, color, beam, gobo | The most recently executed cue controls non-intensity parameters |

This allows layered programming: Sequence 1 handles the base show, Sequence 2 adds a wash overlay, and Sequence 3 handles strobe hits — all controlling overlapping fixtures without conflict.

## Cue Macros and Conditional Logic

**Cue Macros** execute console commands (store, delete, go, pause, etc.) when a cue fires:

```
Cue 5: "Chorus"
  Macro 1: Go Executor 2.1
  Macro 2: Fade Master 3.1 At 50
```

**Conditional Logic** (MA3 Recipe system):
- Cue content can be conditional on runtime state (time of day, fixture availability, operator choice).
- Recipe cues contain a "recipe" (which groups, which presets) rather than hard-coded fixture/channel values.
- The actual DMX values are resolved at playback time based on the current fixture patch.

## Cue Data Model Comparison

| Console | Primary Model |
|---------|--------------|
| **ETC Eos** | Tracking, cue-only mode available, part cues, mark flags, block/assert |
| **grandMA3** | Tracking + Recipes, MIB auto-mark, part cues with per-attribute delay, conditional recipes |
| **Avolites Titan** | Cue-linking (non-tracking), each cue is independent, keys/shapes for movement |
| **Chamsys MagicQ** | Tracking, cue stacks, execute windows for busking, extensive macro support |

## Implications for RayFlow

1. **Part cues in the data model:** The `Cue` dataclass should support multiple parts with independent timing (`delay`, `fade`) and attribute scoping.
2. **Mark/MIB awareness:** The authoring system should insert mark cues before position-changing cues, accounting for the slowest-moving parameter (pan, tilt, gobo select, color wheel settle).
3. **Block cue generation:** When generating cues per section, insert an assert cue at the top of each section to prevent tracking contamination between sections.
4. **Crossfade type hints:** Cues should carry metadata about which attributes crossfade and which snap. The renderer should respect these hints when generating DMX transition frames.
5. **Macro support:** Cue macros (triggering other sequences, adjusting masters) should be supported in the cue model for MA3 export compatibility.
