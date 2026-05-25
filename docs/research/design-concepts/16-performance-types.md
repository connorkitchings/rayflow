# Lighting for Different Performance Types

**Source:** Web research, professional programming guides, lighting design literature
**Parsed:** 2026-05-25

## The Performance Shapes the Light

A lighting design that works for a rock concert fails in a theatrical drama. A corporate keynote needs a fundamentally different approach than a ballet. Each performance type has distinct goals, constraints, and visual vocabulary. Understanding the performance type is the first filter for design intent.

## Theater and Drama

### Primary Goals
1. **Visibility:** The audience must see the performers' faces clearly at all times. If dialogue is happening, the face must be illuminated.
2. **Mood and place:** Lighting establishes time of day, location, and emotional context. It supports the storytelling, it doesn't compete with it.
3. **Focus:** Lighting directs audience attention to the important action. The eye follows brightness — the brightest thing on stage is where the audience looks.

### Design Principles
- **Naturalistic motivation:** Light should appear to come from a logical source (window, lamp, fireplace, sun, moon).
- **Selective visibility:** You don't always light everything. Darkness shapes the composition as much as light does.
- **Color restraint:** Saturated colors (deep red, Congo blue) are used sparingly for specific effects. The workhorse palette is warm amber + cool lavender + open white.
- **Slow transitions:** Cue fades of 3–8 seconds are typical. The audience experiences the emotional shift, not the mechanics of the fade.
- **Tracking:** Theater consoles (ETC Eos) use tracking mode. Once a value is set, it stays until explicitly changed.

### Cue Density
- 100–500 cues for a 2-hour play
- Most cues are subtle intensity shifts, not dramatic changes
- Cue timing is often scene-dependent: faster in tense scenes, slower in lyrical passages

### RayFlow Authoring Implications
- Prefer warm-cool palette strategy
- Slow fades (3–8s default)
- Tracking-friendly cue model (don't repeat values)
- Diurnal simulation for scene transitions

## Concert and Live Music

### Primary Goals
1. **Energy:** Lighting amplifies the music's emotional intensity. Every cue should make the song feel bigger.
2. **Spectacle:** Beams, movement, color, and strobes create visual excitement. The lighting itself is part of the performance.
3. **Rhythm:** Lighting must land on the beat. Snaps on kick drums, sweeps on guitar solos, blackouts on breaks.

### Design Principles
- **No rules, only impact:** Unlike theater's naturalistic motivation, concert lighting can be purely abstract. The only measure is emotional response.
- **Movement is mandatory:** Static looks drain energy. Even a slow wash should have subtle color cycling or intensity breathing.
- **Contrast is the language:** Light ↔ Dark, Warm ↔ Cool, Still ↔ Moving, Sparse ↔ Dense. The biggest moments come from the biggest contrasts.
- **The rig IS the show:** The audience sees the truss, the fixtures, the haze. Industrial aesthetic is embraced, not hidden.
- **Snap timing:** 0-second fades on musical hits. The change should be instant and aggressive.

### Cue Density
- 20–80 cues per song (3–5 minutes)
- Density increases through the song: sparse intro → building verse → dense chorus → maximum climax
- Strobe accents (1–2 per chorus) as punctuation

### Section-by-Section Strategy
| Section | Lighting Strategy |
|---------|------------------|
| Intro | Sparse, atmospheric. Slow builds. Hint at mood without revealing full energy. |
| Verse | Rhythmic but restrained. Catching key moments (vocal entries, fills).  |
| Pre-Chorus | Building energy. Color shift, intensity increase, movement begins. |
| Chorus | Maximum energy. Full rig, beams on, movement, chases. |
| Bridge/Breakdown | Deliberate contrast — could be intimate (single spotlight) or chaotic (strobe frenzy). |
| Outro | Decay. Cooling colors, reducing intensity, sparser beams. Return to black. |

### RayFlow Authoring Implications
- Energy-arc style should be the default authoring style for concerts
- Snap timing on high-energy sections
- BPM-synced cue timing
- High cue density per section, varying by energy

## Dance and Ballet

### Primary Goals
1. **Reveal the body:** Side light is paramount. Front light alone flattens dancers into 2D silhouettes. Side light reveals muscle definition, movement arc, and spatial relationships.
2. **Define space:** Dancers move through three dimensions. Lighting must define up/down, forward/back, left/right.
3. **Atmosphere:** Dance lighting can be more abstract than theater but less aggressive than concert.

### Design Principles
- **Side light dominance:** Multiple heights on booms (shins, mids, head-highs, high-sides) are non-negotiable. More side light channels than front light.
- **Floor pools:** Top light creates pools on the floor that dancers move in and out of. This adds sculptural dimensionality.
- **Cool palette preference:** Dance lighting often favors cool colors (lavender, steel blue, no-color blue) because they reveal body form better than warm tones, which can wash out skin definition.
- **Cyclorama:** The cyc is the backdrop for the entire ballet. Color washes on the cyc establish the world.

### RayFlow Authoring Implications
- Side-light-heavy authoring style
- Multi-height boom programming (distinct cue values for shins vs mids vs head-highs)
- Floor-pool top light as a cue attribute
- Cool-dominant palette

## Corporate and Keynote

### Primary Goals
1. **Visibility above all:** The speaker/presenter must be perfectly lit at all times. This is non-negotiable.
2. **Professionalism:** The lighting should look expensive, clean, and intentional. Nothing distracting.
3. **Branding:** Event colors, logo projection, and brand identity through lighting.

### Design Principles
- **Key light is king:** Dedicated front light for the podium/stage, often with redundant fixtures. If the key light fails, there is no show.
- **Color minimalism:** White, warm white, and one or two brand colors. No rainbows, no chases.
- **Static looks preferred:** Movement draws attention away from the speaker. If moving lights are used, they're typically in static positions.
- **Uplighting:** LED uplights around the room perimeter set the brand color and room mood without affecting stage visibility.
- **GOBO projection:** Logo gobos on walls, floor, or set pieces. Glass gobos for sharpness.

### RayFlow Authoring Implications
- Dimmer-only cues for speaker areas
- Static position presets (no movement)
- Sparse cue list (1–5 cues per segment: walk-on, keynote, panel, Q&A, walk-off)
- Logo gobo support in authoring

## Broadcast and Livestream

### Primary Goals
1. **Camera exposure:** Lighting must serve the camera, not just the eye. What looks good in person often looks terrible on camera.
2. **Consistency:** Camera operators ride iris during the show. Drastic lighting changes make their job impossible. Transitions must be smooth and gradual.
3. **No flicker:** Every fixture must be camera-safe at the production's frame rate (24/25/30/60 fps).

### Design Principles
- **Flatter front light:** Cameras have less dynamic range than the human eye. Theater-style dramatic shadows look like exposure errors on camera. More even, slightly flatter front light than theater.
- **Color temperature lock:** All key lights at the same color temperature (typically 3200K or 5600K). Mixed color temperatures confuse camera white balance.
- **Continuous lighting:** No strobes unless the director specifically requests them. Even then, rate-limit to avoid camera shutter interaction.
- **Monitor calibration:** The LD and programmer need a calibrated broadcast monitor at FOH to see what the camera sees. The console's built-in screen lies.

### RayFlow Authoring Implications
- Camera-safe flag on all cues in broadcast shows
- Reduced contrast ratios (dimmer floor higher, dimmer ceiling lower)
- No strobe or flicker effects unless explicitly requested
- Consistent color temperature across all key light fixtures

## Implications for RayFlow (Cross-Cutting)

1. **Performance type as show-level metadata:** The `Show` model should carry a `performance_type` field that drives authoring defaults, fixture selection, and cue strategy.
2. **Authoring style by performance type:** Theater → warm-cool authoring style. Concert → energy-arc style. Dance → side-light emphasis style. Corporate → key-light priority style. Broadcast → camera-safe constraints.
3. **Cue density tiers:** Theater (sparse), concert (dense), corporate (very sparse), dance/broadcast (moderate). The cue generator should scale density by performance type.
4. **Palette selection by type:** Theater gets warm/cool/front/back palettes. Concert gets saturated color and movement palettes. Corporate gets white + brand color palettes.
5. **Conflict warnings:** If a show's `performance_type` conflicts with venue constraints (e.g., "concert" in a 12 ft trim ballroom), the system should warn.
