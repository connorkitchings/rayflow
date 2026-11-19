# Venue Types and Constraints

**Source:** Web research, professional touring workflows, venue tech specs
**Parsed:** 2026-05-25

## How Venue Shapes Design

Every design decision — fixture count, trim height, throw distance, cue density, even the choice between subtle and aggressive lighting — is constrained by the venue. A rig designed for a 200-cap club is physically and aesthetically wrong for a 15,000-seat arena. Understanding venue types is the starting point of rig design.

## Theater (Proscenium)

| Property | Typical Range |
|----------|--------------|
| Capacity | 200–3,000 seats |
| Stage dimensions | 30–60 ft wide, 25–40 ft deep |
| Proscenium height | 18–35 ft |
| Grid height | 50–80 ft above stage |
| Typical trim | 20–35 ft for FOH, 18–25 ft for overhead electrics |

### Design Constraints
- **Fixed architecture:** The proscenium arch defines the visual frame. Lights must be positioned to avoid obstructing sightlines from balcony and orchestra seating.
- **Deep stage:** Multiple electrics pipes (1st through 5th) provide layers of overhead positions for zone-based area lighting.
- **FOH positions:** Dedicated catwalks or beam slots 40–80 ft from the stage. Long throws require narrow-angle fixtures.
- **Side positions:** Box booms and balcony rails for steep side light. Stage-level booms in wing space.
- **Cyclorama:** Most theaters have a permanent cyc at the upstage wall requiring dedicated ground row and overhead cyc lights.

### Programming Style
- Cue-heavy (100–500 cues per show). Tracking-based consoles (ETC Eos) dominate.
- Subtle, motivated changes: 4–8 second fades are common. Audience should feel the shift, not see the mechanics.
- Color temperature realism: tungsten emulation, warm/cool balance, diurnal simulation.

### Rig Example (600-seat theater)
- FOH catwalk: 12–18 ellipsoidals (19°–26°), 4 followspots
- 1st–4th Electrics: 8–12 fixtures per pipe (ellipsoidals + fresnels)
- Box booms: 4–6 fixtures per side (6×9 or 6×12 ellipsoidals)
- Cyc: 6–8 cyc lights top + bottom
- Total: ~80–120 fixtures

## Concert Venue / Music Hall

| Property | Small Club | Mid-Size | Arena |
|----------|-----------|----------|-------|
| Capacity | 100–500 | 500–5,000 | 5,000–20,000+ |
| Stage | 15×20 ft | 30×40 ft | 60×80 ft |
| Trim | 10–15 ft | 15–25 ft | 25–45 ft |
| Throw distances | 10–30 ft | 20–60 ft | 40–120 ft |

### Design Constraints
- **Low trim (club):** Fixtures are close to performers. Wide-angle fixtures needed. Beams hit audience sightlines easily.
- **Mid trim (mid-size):** Sweet spot for moving lights. Enough height for aerial effects without losing intensity.
- **High trim (arena):** Long throws demand high-output fixtures. Narrow beams become wider at distance. A 2° beam at 100 ft = 3.5 ft diameter — still tight.
- **No fixed architecture:** Truss is the architecture. Ground-supported or flown truss defines positions.
- **Audience engagement:** Club shows often use blinders and audience sweeps. Arena shows use massive audience trusses.

### Programming Style
- Cue lists (20–80 cues per song) for headliners. Busking for support acts and festivals.
- High-energy vocabulary: snaps, ballyhoos, strobes, audience blinders, color sweeps.
- grandMA3 dominates the touring market. Avolites and Chamsys common in clubs.

## Outdoor Festival

| Property | Typical Range |
|----------|--------------|
| Stage size | 40–80 ft wide, 30–60 ft deep |
| Trim | 25–60 ft (high for sightlines over crowd) |
| Throw to FOH | 80–150 ft |
| Wind load | Significant — reduces truss capacity |

### Design Constraints
- **Daylight:** First acts play in daylight or dusk. Lighting is invisible until sunset. Front light must compete with ambient.
- **Wind:** Moving heads catch wind. Truss loading reduced by 30–50% for outdoor structures with wind bracing.
- **Weather:** IP65-rated fixtures mandatory for uncovered positions. Haze/fog dissipates faster outdoors.
- **Power:** Generator power with voltage fluctuation. Fixtures and consoles need power conditioning.
- **Multiple acts:** No soundcheck lighting time. Busking layout is essential — the operator needs instant access to looks for bands they've never heard.
- **Wide stage:** Extreme side positions need wide-throw fixtures (36°–50°) to reach center.

## House of Worship

| Property | Typical Range |
|----------|--------------|
| Capacity | 100–5,000 seats |
| Ceiling height | 15–40 ft |
| Throw to stage | 15–60 ft |

### Design Constraints
- **IMAG/broadcast:** Almost all churches use video screens and/or live stream. Every fixture choice must be camera-safe (high PWM, no flicker, CRI ≥ 90).
- **Mixed lighting:** Combines theatrical front light (for speaker visibility), concert energy (for worship band), and architectural lighting (for the room itself).
- **Low ceilings:** Many churches have acoustic ceiling tiles or low steel. Moving lights require careful placement to avoid beam clipping.
- **Volunteer operators:** The console interface must be simple enough for volunteers. Magic sheets, simplified layouts, and clearly labeled faders.

## Corporate / Ballroom

| Property | Typical Range |
|----------|--------------|
| Venue | Hotel ballroom, convention center |
| Ceiling | 12–30 ft (often low) |
| Stage | 12–40 ft wide portable stage |
| Power | Limited circuits. 200A 3-phase typical |

### Design Constraints
- **Low trim:** 12–15 ft is common. Fixtures are in audience sightlines. Moving lights at low trim look aggressive — use sparingly.
- **Clean aesthetic:** Corporate clients want "professional" not "concert." White light, brand colors, uplighting. No ballyhoos, no strobes.
- **Fast setup:** 4–8 hour load-in. Pre-rigged truss on crank-up stands. Minimal focus time.
- **IMAG:** Cameras everywhere. All fixtures must be flicker-free. Key light must be bright and even across the stage.
- **Logo projection:** GOBO projection of corporate logos is a staple. Glass gobos with sharp focus are required.

## Implications for RayFlow

1. **Venue type as a first-class attribute:** The `Venue` model should include a `venue_type` field (theater, club, mid_size_concert, arena, festival, worship, corporate, ballroom) that drives downstream defaults.
2. **Type-based constraints:** Each venue type implies trim height ranges, throw distance limits, fixture count ceilings, and available power. The rig builder should validate against these.
3. **Cue strategy defaults:** Theater = slow fades, tracking, motivated changes. Club/concert = snaps, chases, high density. Corporate = clean, minimal, brand colors. The authoring system should select different defaults by venue type.
4. **Fixture mix by venue:** Available trim height determines whether beam fixtures (need height) or wash fixtures (work anywhere) should dominate. The authoring system should recommend fixture ratios by venue type.
5. **Camera safety flag:** Venues with IMAG/broadcast need the `camera_safe` flag on fixtures, triggering high-PWM-only fixture selection and S-curve dimmer preference.
