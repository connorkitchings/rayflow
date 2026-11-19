# Haze, Fog, and Atmospheric Effects

**Source:** Web research, manufacturer documentation, professional lighting guides
**Parsed:** 2026-05-25

## Why Atmosphere Matters

Projected beams of light are invisible in clean air. A beam fixture's sharp shaft of light, a gobo's textured cone, or a laser's geometric pattern only becomes visible when light scatters off suspended particles. Atmospheric effects are not optional decoration — they are the medium that makes beam-based lighting design visible.

## Types of Atmospheric Effects

| Type | Particle Size | Hang Time | Visibility | Best For |
|------|-------------|-----------|------------|----------|
| **Haze** | Microscopic (<1 micron) | Long (30 min–hours) | Subtle, even, reveals beams uniformly | Concert lighting, theater, any beam-heavy show |
| **Fog** | Larger (1–10 microns) | Short (1–5 min) | Dense clouds, opaque | Dramatic entrances, hiding scene changes, "burst" effects |
| **Low-Lying Fog** | Cooled fog, stays at floor level | Short (1–3 min) | Ground-level blanket | Creating a "walking on clouds" effect, dance, fantasy scenes |
| **CO₂ Jets** | Cryogenic vapor | Very short (seconds) | Dense white plume, instant dissipation | High-energy moments, stage cannons, festival effects |
| **Cracked Oil / Hazer** | Ultra-fine mineral oil | Very long (hours) | Invisible until light hits it | Large venues, touring, broadcast |

## Fluid Types: Oil-Based vs. Water-Based

### Oil-Based Haze
- **How it works:** Mineral oil is atomized by a compressor into microscopic droplets.
- **Particle size:** Sub-micron. Particles remain suspended almost indefinitely.
- **Pros:** Longest hang time, most uniform coverage, least visible to the eye without light.
- **Cons:** Leaves residue on surfaces and equipment over time. Can trigger smoke alarms. Some performers find it irritating to breathe.
- **Examples:** DF-50 (industry standard for decades), Look Solutions Unique.

### Water-Based Haze / Fog
- **How it works:** Glycol/water mixture is heated into vapor, which condenses into visible droplets.
- **Particle size:** 1–5 microns. Larger than oil = more visible but shorter hang time.
- **Pros:** No residue. Generally considered safer for performers and equipment. Faster dissipation for quick scene changes.
- **Cons:** Shorter hang time requires continuous output. More visible as "haze" to the naked eye. Refractive index differences can slightly soften gobo sharpness.
- **Examples:** Look Solutions Viper, Martin JEM series, Chauvet Amhaze.

## DMX Control Channels

Professional hazers and foggers typically use 1–3 DMX channels:

| Channel | Function | Values |
|---------|----------|--------|
| **Output / Pump** | Controls fluid output rate | 0–255 (0% = off, 255 = maximum output) |
| **Fan Speed** | Controls dispersion fan | 0–255 (0% = off, 255 = max spread) |
| **Special / Mode** | Timer mode, burst mode, DMX/standalone | Varies by fixture |

### Fog Machine DMX Profile
Typically 2 channels: output + fan. Short bursts for dramatic effect.

### Hazer DMX Profile
Typically 2 channels: output + fan. Run continuously at low output for even haze. The art is maintaining consistent atmospheric density without over-hazing.

## Interaction with Lighting Design

### Beam Visibility
- **Without haze:** Beam fixtures produce a spot on the floor/wall. The beam shaft is invisible.
- **With light haze:** Beam shafts become subtly visible, adding depth to the stage picture.
- **With heavy haze:** Beam shafts dominate the visual field. Gobos cast visible cones. Multiple layers of beams create architectural forms in the air.
- **With fog:** Beams become opaque white cones. Gobos project sharply defined shafts.

### Cue Timing and Haze Density
- A venue takes time to fill with haze (5–15 minutes depending on size and HVAC).
- A blackout followed by a beam cue in an un-hazed room produces only a floor spot — the beam is invisible until the room fills.
- **Best practice:** Run haze continuously throughout a show at low output. Increase output 30–60 seconds before a beam-intensive section.

### Haze and Lighting Layering
Haze creates a three-dimensional canvas:
1. **Foreground layer:** Beams crossing close to the audience (ballyhoos, audience sweeps) — thickest haze, brightest visibility.
2. **Midground layer:** Beams crossing stage-level (side light, backlight) — medium visibility.
3. **Background layer:** Beams projected on the cyc or backdrop — subtle, adds depth.

## Health and Safety

- **Performers:** Prolonged exposure to glycol fog can cause respiratory irritation in sensitive individuals. Position fog output away from performers' faces.
- **Smoke alarms:** Both oil and water-based haze can trigger particulate and beam-type smoke detectors. Coordinate with venue management to isolate or temporarily disable affected zones.
- **Slip hazards:** Glycol fog condenses on floors, creating a thin slippery film. Use low-lying fog with caution on dance/stage floors.
- **Visibility:** Dense fog can reduce emergency exit visibility. Always maintain a clear line of sight to exit signs.

## Implications for RayFlow

1. **Haze as a fixture type:** Fog and haze machines should be patched as fixtures with output/fan channels, enabling the authoring system to include haze density in cues.
2. **Pre-beam haze ramp:** The cue planning system should insert a haze ramp (increase output to 30–50%) 30–60 seconds before the first beam-intensive section.
3. **Haze level metadata:** Sections with beam-heavy cues should carry haze density metadata so the renderer can warn if no haze fixture is patched.
4. **Venue-aware haze timing:** Large venues require longer haze fill times. The `Venue` model could carry `haze_fill_time_minutes` to inform cue planning.
