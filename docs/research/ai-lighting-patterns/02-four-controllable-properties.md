# The Four Controllable Properties of Light — A Design Framework for AI Authoring

**Source:** ETC Blog — "Stage Lighting Design" series (Parts 1–9), Vectorworks concert lighting guide
**Parsed:** 2026-05-26

## The Framework

Every lighting decision — every cue, every preset, every effect — is a choice about four controllable properties of light. This framework, adapted from the ETC lighting design curriculum, gives the AI authoring system a clean mental model for translating user intent into technical output.

| Property | What It Controls | User Language | AI Action |
|----------|-----------------|---------------|-----------|
| **Intensity** | How bright | "Make it brighter," "Fade to black," "Bring up the backlight" | Map to dimmer DMX values (0–255), apply dimmer curve |
| **Color** | What hue/saturation | "Warm amber," "Deep blue wash," "Red to blue sweep" | Map to RGB/CMY/color wheel channels per fixture |
| **Distribution** | Where light falls — position, angle, beam shape, focus, gobo | "Point at the drummer," "Wide stage wash," "Tight spot on the vocalist" | Pan/tilt to target, zoom, focus, iris, gobo select, framing |
| **Movement** | Changes over time — fades, chases, sweeps, effects | "Slow fade," "Snap on the beat," "Circle movement," "Strobe on the kick" | Fade time, delay, follow, effect parameters (rate, size, phase, waveform) |

## Why This Framework Works for AI

### 1. Every User Request Maps to One or More Properties

```
User: "I want a warm amber front wash that slowly builds to a blue backlight peak"
  → Intensity:  build (low → high), fade time
  → Color:      warm amber (front), blue (back)
  → Distribution: front wash, backlight positions
  → Movement:   slow fade (intensity change over time)
```

The AI parses the request into the four properties, confirms with the user, then resolves each one through the renderer.

### 2. A Cue Is Complete When All Four Properties Are Addressed

A cue that only specifies intensity and color but not distribution is incomplete — the fixtures may illuminate the wrong area. A cue that specifies all four is a fully-resolved lighting state.

The AI should validate every generated cue against these four properties and warn when one is unspecified or defaults.

### 3. Critique Happens Per Property

When the user says "the blue feels too cold," they're critiquing color — not intensity, distribution, or movement. The AI should isolate the critique to the correct property and adjust only that one, leaving the others untouched.

This prevents the common AI mistake of regenerating an entire cue when only one property needs adjustment.

## Property 1: Intensity

### What the AI Needs to Know
- DMX dimmer channel per fixture (from GDTF channel map)
- Dimmer curve (linear, square law, S-curve) per fixture type
- The difference between DMX value (0–255) and perceived brightness (Stevens' law)
- HTP (Highest Takes Precedence) behavior: multiple sequences controlling the same fixture's dimmer use the highest value

### Intensity as a Design Tool
- **Visibility:** Intensity is the primary way to make performers visible. If the audience can't see the face, nothing else matters.
- **Focus:** The brightest area of the stage is where the audience looks. Intensity directs attention.
- **Contrast:** The difference between the brightest and darkest moments defines the show's emotional range. A show with no intensity variation has no drama.
- **The "too much light" problem:** When everything is bright, nothing is bright. The audience can't find a focal point. Reserve full intensity for peak moments.

### AI Authoring Heuristics
```
energy_to_dimmer(energy):
    # Energy 0.0–1.0 → Dimmer 25–95%
    return 25 + (energy * 70)

section_to_intensity_range(section):
    intro:    25–50%
    verse:    40–65%
    chorus:   65–95%
    bridge:   30–55%
    outro:    50% → 0%
```

### Common User Intensity Requests → AI Translation
| User Says | AI Does |
|-----------|---------|
| "Make it brighter" | Increase target fixture dimmer by 10–15% |
| "Fade to black" | Set dimmer to 0, apply fade time |
| "The verse feels too hot" | Reduce verse section dimmer floor by 5–10% |
| "I want the backlight to pop more" | Increase backlight group dimmer relative to front light |
| "Add a slow build" | Program dimmer ramp: start → end over N seconds/beats |

## Property 2: Color

### What the AI Needs to Know
- Color mixing model per fixture: RGB (additive), CMY (subtractive), color wheel (indexed), or hybrid
- Gel reference equivalents for named colors (Rosco/Lee → approximate RGB/hex)
- Color temperature (Kelvin) → mood mapping
- Color palette libraries (complementary, analogous, triadic, monochromatic)

### Color as a Design Tool
- **Mood:** Warm = intimate, energetic, sunrise/sunset. Cool = calm, melancholy, night, mystery.
- **Separation:** Different colors on different fixture groups (warm front, cool back) create depth.
- **Time and place:** Color temperature signals time of day (3200K = indoor/tungsten, 5600K = daylight).
- **Information:** Color changes can signal song sections (verse = amber, chorus = blue).

### AI Authoring Heuristics
```
mood_to_palette(mood_keywords):
    warm_keywords    → amber, gold, straw, warm white
    cool_keywords    → lavender, steel blue, deep blue
    energy_keywords  → red, magenta, cyan, saturated
    dark_keywords    → deep blue, congo blue, purple
    ethereal_keywords → lavender, light blue, pink, pastels

section_to_color_temp(section):
    intro:    warm (3200K)
    verse:    warm or neutral
    chorus:   saturated (energy-dependent)
    bridge:   cool contrast
    outro:    cooling to warm fade
```

### Common User Color Requests → AI Translation
| User Says | AI Does |
|-----------|---------|
| "Warm amber front light" | Map "amber" → Rosco 02 or Lee 162 equivalent in fixture's color model |
| "The blue is too cold" | Shift blue toward lavender (add red to RGB, or reduce saturation) |
| "I want a rainbow chase" | Build absolute color chase cycling through 7 color presets |
| "Match the band's branding colors" | Accept hex values, translate to per-fixture color channels |
| "Make it look like sunset" | Program warm amber/orange wash, fading to cooler backlight |

## Property 3: Distribution

### What the AI Needs to Know
- Fixture position (x, y, z) and target position per cue
- Pan/tilt range and 16-bit resolution
- Beam angle and zoom range
- Focus, iris, frost, framing shutter channels
- Gobo wheel index and rotation
- Prism selection and rotation

### Distribution as a Design Tool
- **Visibility:** Light must reach the performer's face (approximately 5.5 ft above deck at center stage).
- **Revelation of form:** Side light and backlight reveal three-dimensional shape. Flat front light flattens.
- **Composition:** Where light falls defines the visual composition. Lighting only part of the stage directs focus.
- **Texture:** Gobos, breakup patterns, and beam shaping add visual interest to otherwise uniform light.

### The Distribution Hierarchy

```
1. WHERE does the light fall?          → Pan/tilt to target position
2. HOW BIG is the beam?                → Zoom angle, iris
3. HOW SHARP are the edges?            → Focus (hard or soft edge)
4. WHAT TEXTURE is in the beam?        → Gobo selection
5. WHAT SHAPE is the beam?             → Framing shutters, barndoors
6. IS THE BEAM modified optically?     → Prism, frost, animation wheel
```

### AI Authoring Heuristics
```
target_face_height = 5.5  # feet above deck

fixture_groups_by_role:
    key_light:  FOH truss spots → target (0, stage_center_y, 5.5)
    backlight:  US truss washes → target (0, stage_center_y, 5.5)
    side_light: boom fixtures → target (0, stage_center_y, 5.5)
    aerial:     beam fixtures → target: into the air (high tilt)
    audience:   audience-facing positions → target: crowd

gobo_for_vibe(vibe_keywords):
    organic, nature → breakup gobos (leaves, branches)
    geometric, modern → linear, grid gobos
    corporate, branded → custom logo gobo
    psychedelic, trippy → abstract, swirl gobos
    clean, minimal → open (no gobo)
```

### Common User Distribution Requests → AI Translation
| User Says | AI Does |
|-----------|---------|
| "Point the spots at the lead singer" | Set pan/tilt to DSC position (0, ~10, 5.5) for FOH spots |
| "I want a tight beam on the drummer" | Narrow zoom, small iris, hard focus on drum riser position |
| "Add leaf-pattern breakup on the stage" | Select breakup gobo on spot fixtures, medium zoom, soft focus |
| "The wash doesn't cover the whole stage" | Widen zoom on wash fixtures or add more fixtures to zone coverage |
| "Fan the beams out wider" | Apply pan fan distribution across beam fixture group |

## Property 4: Movement

### What the AI Needs to Know
- Fade time (seconds or beats)
- Delay per attribute
- Follow time (auto-advance to next cue)
- Effect engines: waveform, rate, size, phase, grouping, offset
- Speed master BPM linkage
- Crossfade behavior (HTP for dimmer, LTP for attributes)

### Movement as a Design Tool
- **Time:** Fade speed signals energy — snaps = aggressive, slow fades = atmospheric.
- **Rhythm:** Changes on the beat connect lighting to music. Off-beat changes feel disconnected.
- **Kinetic energy:** Fixture movement (pan/tilt effects) creates visual excitement. Static looks drain energy.
- **Contrast:** The difference between stillness and movement is as powerful as the difference between dark and bright.

### Movement Types

| Type | What Changes | Example |
|------|-------------|---------|
| **Fade** | Intensity or color over time | Wash fades from amber to blue over 4 seconds |
| **Snap** | Instant change (0s fade) | Blinder flash on the downbeat |
| **Chase** | Sequential parameter change across fixtures | Dimmer chase through spots, left to right |
| **Effect** | Continuous oscillator-driven change | Sine wave intensity pulse, circle movement |
| **Physical** | Fixture pan/tilt over time | Sweep from stage left to stage right |

### AI Authoring Heuristics
```
bpm_to_fade_time(bpm, musical_duration):
    beat_duration = 60 / bpm
    return beat_duration * musical_duration_in_beats

energy_to_fade_type(energy):
    energy > 0.8  → snap (0s)
    energy > 0.5  → short fade (0.5–1 bar)
    energy > 0.25 → medium fade (1–4 bars)
    energy < 0.25 → long fade (4–8 bars)

section_to_movement(section):
    intro:    static or very slow
    verse:    subtle (slow intensity breathing)
    chorus:   active (chases, movement generators)
    bridge:   varies (contrast with surrounding sections)
    climax:   maximum (all effects active, fast chases)
```

### Common User Movement Requests → AI Translation
| User Says | AI Does |
|-----------|---------|
| "Snap on the kick drum" | 0s fade, cue triggered on beat 1 and 3 |
| "Slowly fade to blue" | 4–8 second color crossfade on wash group |
| "The movement is too fast" | Reduce effect rate or link to slower BPM divider |
| "Add a chase through the spots" | Build step-based or sine dimmer chase with sequential phase |
| "Freeze the movement here" | Set speed master to 0% or disable effect engine |

## Using the Framework for Cue Validation

Before the AI commits a generated cue, validate all four properties:

```
validate_cue(cue):
    errors = []

    if not cue.intensity_specified:
        errors.append("No intensity specified — fixtures may be at unexpected levels")

    if not cue.color_specified:
        errors.append("No color specified — fixtures may retain previous color (tracking)")

    if not cue.distribution_specified:
        errors.append("No position/beam specified — fixtures may point at wrong target")

    if not cue.movement_specified:
        # Movement can legitimately be omitted (static look)
        cue.movement = {"fade_time": default_fade_for_section(cue.section)}

    return errors
```

## The Framework as AI Prompt Structure

When the AI generates cues, structure the output around the four properties:

```
Cue 12: "Chorus Peak"
  Intensity:  Spots 90%, Washes 85%, Beams 100%, Blinders FIRE
  Color:      Front=Amber, Back=Deep Blue, Beams=White
  Distribution: Spots=DSC, Washes=Full Stage, Beams=Aerial fan
  Movement:   Snap in, dimmer chase on spots (sine, 120 BPM, size=40%),
              beams circle (size=60%, linked to speed master)
  Fade: 0s (snap on downbeat)
```

This is readable by the AI, translatable to code, and reviewable by the user.

## Implications for RayFlow

1. **The four properties should be first-class in the Cue model.** Currently the `Cue` dataclass has `attributes` (dict) and `fade_time` but doesn't structure around intensity/color/distribution/movement. A cue with structured property fields is easier for the AI to generate and validate.

2. **User intent parsing should map to property categories.** When the user says anything about lighting, the AI should classify it: "Is this about intensity, color, distribution, or movement?" Then route to the appropriate resolver.

3. **Critique should be per-property.** The AI's feedback loop ("the blue is too cold") should adjust only the relevant property, not regenerate the entire cue.

4. **The authoring system should validate all four properties before rendering.** A cue with missing distribution (where do the lights point?) produces undefined DMX output.

5. **The prompt template for AI sessions should use this framework.** Instead of a flat list of cue attributes, organize the context bundle around the four controllable properties.
