# Rig Design and Fixture Placement

**Source:** Web research, stage lighting design literature, professional rigging guides
**Parsed:** 2026-05-25

## The Rig as an Instrument

A lighting rig is not a collection of fixtures — it is a single instrument with a specific voice, range, and character. Rig design determines what the show can express before a single cue is programmed. A well-designed rig provides the full palette of angles, colors, and beam types needed for the show's emotional range.

## Structural Elements of a Rig

### Truss Positions

| Position | Location | Typical Fixtures | Primary Function |
|----------|----------|-----------------|------------------|
| **Front Truss (FOH)** | Over audience, upstage edge | Spots, profiles, followspots | Key light, face light, gobo projection |
| **Mid Truss** | Over stage, downstage of performers | Washes, beams | Downstage wash, high backlight |
| **Upstage Truss** | Over upstage area | Beams, washes | Backlight, aerial effects |
| **Stage Left/Right Booms** | Vertical pipes in wings | PARs, strips, smaller washes | Side light, cross-stage coverage |
| **Floor Package** | On stage deck | Blinders, strobes, uplights, floor beams | Low-angle intensity, audience connection |
| **Audience Truss** | Over audience, further downstage | Beams, blinders | Audience engagement, crowd sweeps |

### Trim Heights

| Position | Typical Height | Why |
|----------|---------------|-----|
| FOH Truss | 20–35 ft (6–10m) | Above sightlines, steep enough angle for face modeling |
| Over-Stage Truss | 15–25 ft (4.5–7.5m) | Proximity to performers for intensity |
| Booms | Floor to 10 ft (3m) | Multiple heights for full-body coverage |
| Ground Support | 0–3 ft (0–1m) | Uplight, audience blinder proximity |

## Fixture Angle Principles

### Front Light (McCandless)
- Two fixtures per zone at 45° horizontal separation, 30–60° vertical
- Warm (left) + Cool (right) for facial modeling
- Too steep (>70°) = deep eye socket shadows
- Too flat (<30°) = flat, uninteresting shadows on backdrop

### Backlight
- 45–90° vertical behind performer
- Separates performer from background
- High backlight (>70°) for rim effect
- Lower backlight (45°) for fuller body illumination

### Side Light
- 0–90° horizontal from wings
- Mounted at multiple heights on booms: shins, mids, head-highs, high-sides
- Critical for dance — reveals body form from audience perspective

### Top Light
- Directly overhead, 90° vertical
- Creates dramatic top-down pools
- Used for isolation, specials, and dramatic scenes

## Throw Distance and Beam Angle

Throw distance (fixture to target) and beam angle determine coverage:

```
beam_diameter = 2 * throw_distance * tan(beam_angle / 2)
lux_at_target = fixture_lumens / (beam_diameter² * π / 4)
```

| Beam Angle | At 20 ft throw | At 40 ft throw | At 60 ft throw |
|-----------|---------------|---------------|---------------|
| 10° (narrow spot) | 3.5 ft diameter | 7.0 ft | 10.5 ft |
| 19° (medium) | 6.7 ft | 13.4 ft | 20.1 ft |
| 26° (medium-wide) | 9.2 ft | 18.5 ft | 27.7 ft |
| 36° (wide) | 13.0 ft | 26.0 ft | 39.0 ft |
| 50° (very wide) | 18.7 ft | 37.3 ft | 56.0 ft |

### Selection Heuristics
- **Face light:** 19–26° at typical FOH throw (30–50 ft). Covers 1–2 performers.
- **Zone wash:** 26–36° at stage throw. Covers a 12–15 ft zone.
- **Full-stage color wash:** 50° or fresnel. Covers 20+ ft from stage electrics.
- **Aerial beam:** 2–5° beam fixture. Narrowest possible for visible shafts.

## Fixture Count Planning

### Minimum Per Show Type

| Show Type | Front | Backlight | Side | Wash | Beam | Specials | Total (approx) |
|-----------|-------|-----------|------|------|------|----------|----------------|
| Small theater | 8–12 | 6–10 | 4–8 | 4–6 | 0 | 2–4 | 24–40 |
| Concert (small club) | 4–6 | 6–10 | 0–4 | 4–8 | 2–4 | 2–4 | 18–36 |
| Concert (mid-size) | 8–12 | 12–20 | 4–8 | 12–20 | 6–12 | 4–8 | 46–80 |
| Concert (arena) | 16–24 | 24–40 | 8–16 | 20–40 | 16–30 | 8–16 | 92–166 |
| Corporate event | 8–12 | 6–10 | 0 | 8–12 | 2–4 | 4–6 | 28–44 |

## Fixture Mix by Role

| Role | Fixture Type | Key Channels | Quantity Ratio |
|------|-------------|-------------|----------------|
| **Key Light** | Profile spot (moving or fixed) | Dimmer, pan/tilt | 15–20% |
| **Wash** | Wash moving head or LED PAR | Dimmer, RGB/CMY, zoom | 25–35% |
| **Beam/Effect** | Beam moving head | Dimmer, pan/tilt, color wheel | 15–25% |
| **Blinder/Strobe** | LED blinder, strobe fixture | Dimmer, flash rate | 5–10% |
| **Special** | Followspot, laser, haze | Varies | 5–10% |

## Weight and Rigging Constraints

- Truss loading limits (lbs/ft or kg/m) must not be exceeded
- Point loads at truss junctions are higher than distributed loads
- Moving heads are heavier than LED PARs (40–80 lbs vs. 5–15 lbs each)
- Safety cables required for every fixture
- Wind loading for outdoor stages reduces allowable truss capacity

## DMX Universe Planning

Fixture addresses must fit within universe boundaries:

```
fixtures_per_universe = floor(512 / fixture_channel_count)
universes_needed = ceil(total_fixtures / fixtures_per_universe)
```

| Fixture Type | Channels | Per Universe |
|-------------|---------|-------------|
| Dimmer (1-ch) | 1 | 512 |
| LED PAR (8-ch) | 8 | 64 |
| Wash moving head (16-ch) | 16 | 32 |
| Spot moving head (24-ch) | 24 | 21 |
| Pixel bar (40-ch) | 40 | 12 |

## Implications for RayFlow

1. **Venue-aware rig templates:** Rig templates should include suggested fixture counts and positions based on venue dimensions and show type.
2. **Throw distance calculation:** The rig model should validate that fixtures can physically cover their assigned zones given throw distance and beam angle.
3. **Universe auto-allocation:** When fixtures are added to a rig, the system should auto-allocate starting addresses and warn when a universe is full.
4. **Fixture mix recommendations:** The authoring system should suggest fixture mixes (ratio of spots to washes to beams) based on the show's vibe and venue.
5. **Truss position metadata:** The `Position3D` model carries x/y/z but doesn't indicate *which truss* a fixture hangs on. Adding truss/boom metadata would enable zone-based cue programming (e.g., "all upstage truss fixtures go red").
