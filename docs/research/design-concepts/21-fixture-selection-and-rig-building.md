# Fixture Selection and Rig Building

**Purpose:** Given a venue and a show concept, which fixtures do you choose and where do you put them? This document provides heuristics for fixture selection, fixture mix by role, and the step-by-step rig building process — all encodable as software rules.

## Fixture Selection Matrix

### By Role

| Role | Fixture Type | Key Capabilities | Minimum Channel Count | Why This Role |
|------|-------------|-----------------|----------------------|---------------|
| **Key Light** | Spot profile (moving head) | Zoom, focus, gobo, iris, CMY/RGB, 16-bit pan/tilt | 20–30 | Precise control over beam shape. Can also serve as gobo texture. |
| **Front Wash** | LED PAR or Wash moving head | RGB/RGBW/RGBAW color mixing, wide beam (26°–50°) | 4–8 (PAR), 14–20 (wash MH) | Even color coverage front. LED PARs are lighter and cheaper. |
| **Backlight** | Wash moving head | CMY/RGB, zoom, 16-bit pan/tilt | 14–18 | Color and separation from background. Zoom for beam width control. |
| **Aerial Beam** | Beam moving head | Narrow angle (2°–5°), color wheel, prism, fast pan/tilt | 12–16 | Visible light shafts through haze. Brightness per watt matters. |
| **Blinder** | LED blinder / 2-lite / 4-lite | High output, warm white, dimmer, strobe | 2–4 | Audience-facing intensity hits. No color needed. |
| **Strobe** | LED strobe fixture | Flash rate, duration, color (optional), segmented control | 2–8 | Punctuation effect. Separate from blinders for independent control. |
| **Uplight** | LED PAR (floor) | RGB/RGBW, compact, battery or wired | 4–8 | Ambient room color. Corporate events, venue atmosphere. |
| **Pixel Effect** | LED pixel bar / multi-cell panel | Per-cell RGB/RGBW control, pixel mapping | 12–120 | Linear chases, video-like content, architectural shapes. |
| **Cyc / Backdrop** | Cyc light or asymmetric wash | Wide even throw, RGB/RGBW/RGBL | 4–8 per fixture | Even illumination of cyclorama or backdrop. |
| **Special** | Followspot, laser, haze machine | Varies | Varies | Single-purpose fixtures for specific show needs. |

### By Fixture Type Family

| Family | What It Does Best | What It Can't Do | Best Position |
|--------|------------------|-----------------|---------------|
| **Spot (profile)** | Sharp gobo projection, precise beam shaping, key light | Wide wash coverage (beam too narrow), aerial beams (not bright enough per angle) | FOH, mid truss, booms |
| **Wash** | Even color coverage, stage wash, backlight wash | Sharp gobos, tight beam aerial effects | All truss positions, booms |
| **Beam** | High-intensity visible light shafts, aerial effects, ballyhoos | Face light, gobo detail (too narrow, too intense) | Mid truss, upstage truss, audience truss |
| **LED PAR** | Budget wash, uplighting, static color | Movement, gobos, zoom | Floor, truss (fixed), booms |
| **Blinder / Strobe** | Audience engagement, intensity punctuation | Color, movement, subtlety | Floor, audience-facing truss |

## Fixture Mix by Show Scale

### Small Club (100–300 cap, 15×20 ft stage, 12 ft trim)

| Family | Count | Model Examples | Notes |
|--------|-------|---------------|-------|
| Spot MH | 4–6 | Chauvet Rogue R2, Martin Rush MH5 | Budget spots for key light and gobos |
| Wash MH | 4–6 | Chauvet Rogue R2 Wash, ADJ Vizi Wash | Color wash and backlight |
| Beam MH | 2–4 | Chauvet Intimidator Beam, ADJ Vizi Beam | Aerial effects, used sparingly at low trim |
| LED PAR | 4–8 | Chauvet COLORdash, ADJ 12P HEX | Static color wash, uplighting |
| Blinder | 2–4 | Chauvet STRIKE, ADJ COB Cannon | Audience engagement |
| Strobe | 1–2 | ADJ Mega Par Profile Plus, Chauvet COLORband Pix | Punctuation |
| Haze | 1 | Chauvet Amhaze, ADJ Entourage | Beam visibility |
| **Total** | **18–31** | | |

### Mid-Size Venue (500–3,000 cap, 30×40 ft stage, 20 ft trim)

| Family | Count | Model Examples | Notes |
|--------|-------|---------------|-------|
| Spot MH | 8–12 | Martin MAC Aura, Robe MMX Blade, Chauvet Maverick | Key light, gobos, stage texture |
| Wash MH | 10–16 | Martin MAC Aura Wash, Robe Spiider, Chauvet Rogue R3 Wash | Color backlight, stage wash |
| Beam MH | 6–12 | Robe Pointe, Martin MAC Viper | Aerial effects at higher trim |
| LED PAR | 8–16 | Elation SixPar, Chauvet COLORado | Front and side wash |
| Blinder | 4–8 | Martin Atomic, Chauvet STRIKE Array | Audience connection |
| Strobe | 2–4 | Martin Atomic 3000, SGM Q-7 | Punctuation |
| Pixel Bar | 2–4 | GLP Impression X4 Bar, Chauvet COLORband | Linear chases |
| Haze | 1–2 | Look Solutions Viper, MDG ATMe | Beam and atmosphere |
| **Total** | **41–74** | | |

### Large Club / Small Theater (600–2,000 cap, 30×50 ft stage, 25 ft trim)

| Family | Count | Model Examples | Notes |
|--------|-------|---------------|-------|
| Spot MH | 12–18 | Robe MegaPointe, Martin MAC Encore, Ayrton Ghibli | Full-featured profiles with animation wheels |
| Wash MH | 16–24 | Martin MAC Quantum, Robe LEDWash, Ayrton Mistral | High-output LED washes with zoom |
| Beam MH | 12–20 | Robe Pointe, Clay Paky Sharpy | Bright, fast aerial effects |
| LED PAR | 12–20 | GLP Impression, Elation SixPar | Zone washes, uplighting |
| Blinder | 6–10 | Martin Atomic, SGM Q-7 | Audience engagement |
| Strobe | 3–6 | Martin Atomic, SGM Q-7 | Punctuation |
| Pixel Bar / Panel | 4–8 | GLP X4 Bar, ROE Strip | Visual content, chases |
| Haze | 2 | DF-50, Look Solutions Unique | Continuous atmosphere |
| **Total** | **67–106** | | |

## Fixture Budget Allocation

When building a rig with a fixed budget or fixture count ceiling, allocate by priority:

| Priority | Family | % of Fixture Count | % of Budget | Reasoning |
|----------|--------|-------------------|-------------|-----------|
| 1 | Key Light (spots) | 20% | 30% | Non-negotiable. The audience must see the performers. |
| 2 | Backlight / Wash | 25% | 25% | Creates depth. Without backlight, everything is flat. |
| 3 | Beam / Aerial | 20% | 20% | Energy and spectacle. Can be reduced for theater. |
| 4 | Blinder / Strobe | 10% | 10% | Punctuation. Small fixture count, big impact. |
| 5 | Pixel / Special | 15% | 10% | Differentiator. Adds visual complexity beyond conventional fixtures. |
| 6 | Haze / Atmosphere | 2% | 2% | Enables beams. No haze = no beam visibility. |
| 7 | Uplight / Ambient | 8% | 3% | Room atmosphere. Optional but valuable. |

## The Rig Building Process (Encodable Steps)

```
1. LOAD VENUE
   → Get venue dimensions, type, trim heights, power budget

2. CHOOSE TRUSS POSITIONS
   → Based on venue type and size, place truss structures
   → FOH truss (always), DS/mid/US truss (by stage depth), booms (by width)
   → Each truss has: start_x, end_x, y_position, z (trim height)

3. SELECT FIXTURE MIX
   → Based on performance type and venue scale
   → Return: { "spot_mh": 8, "wash_mh": 12, "beam_mh": 6, ... }

4. ALLOCATE FIXTURES TO TRUSS POSITIONS
   → Apply rules:
     - Key light spots → FOH truss (best angle for face light)
     - Wash front → FOH and DS truss
     - Backlight wash → Mid and US truss
     - Beam MH → Mid and US truss (height for aerial)
     - Blinders → Floor and audience-facing positions
     - Strobe → Floor center
     - Pixel bars → Floor front or US truss
     - Haze → Floor upstage

5. CALCULATE POSITIONS
   → For each truss, auto-space fixtures evenly
   → Calculate pan/tilt to point at stage zones

6. ALLOCATE DMX ADDRESSES
   → Assign starting addresses per fixture
   → Validate within universe boundaries
   → Warn if fixture count exceeds universe capacity

7. VALIDATE
   → Do fixtures physically fit on truss?
   → Does total power draw exceed venue capacity?
   → Do throw distances match fixture capabilities?
   → Can all stage zones be covered by the allocated fixtures?

8. GENERATE RIG YAML + MVR
   → Export the rig as RayFlow YAML
   → Export MVR for pre-viz import
```

## Selection Rules (Heuristics for Software)

```
RULE: key_light_angle
  IF fixture.role == "key_light" THEN
    vertical_angle = atan2(throw_distance, fixture_z - target_z)
    ASSERT 30° <= vertical_angle <= 60°
    IF vertical_angle < 30° → fixture too flat, move fixture upstage
    IF vertical_angle > 60° → fixture too steep, move fixture downstage

RULE: beam_needs_height
  IF fixture.family == "beam" THEN
    ASSERT fixture.z >= 15 ft  # Beams need height for aerial visibility
    IF fixture.z < 15 → warn "Beams below 15 ft clip audience sightlines"

RULE: coverage_overlap
  beam_diameter = 2 * throw * tan(fixture.beam_angle / 2)
  spacing = beam_diameter * 0.7  # 30% overlap for even coverage
  fixtures_needed = ceil(zone_width / spacing)

RULE: key_light_face_height
  target_z = 5.5  # Average face height in feet
  For all key light fixtures, compute tilt to target (0, stage_center_y, 5.5)

RULE: backlight_color_vocabulary
  backlight fixtures must have color mixing (CMY or RGB)
  Color wheel only backlights are acceptable but limit palette flexibility
  Prefer LED wash MH for backlight (instant color, no wheel settling time)

RULE: universe_budget
  total_channels = sum(fixture.channel_count for fixture in rig)
  universes_needed = ceil(total_channels / 512)
  IF universes_needed > available_universes → warn, suggest sACN over Art-Net

RULE: busking_minimum
  IF show.style == "busking" THEN
    ASSERT rig has >= 2 fixture groups with >= 4 fixtures each
    # Busking requires independent control of spots vs washes vs beams
    # Single-group rig cannot create busking layers
```

## Implications for RayFlow

1. **Rig building as a guided wizard:** `rayflow rig create` should walk through venue → truss → fixture selection → positioning → addressing in sequence, applying rules at each step.
2. **Fixture catalog in the library:** The fixture library should include metadata about fixture family, role suitability, and typical placement so the builder can auto-suggest.
3. **Auto-placement algorithm:** Given a truss (start_x, end_x, y, z) and a fixture count, auto-space fixtures and compute pan/tilt toward the nearest stage zone.
4. **Rig template library:** Common rig configurations (small club, mid-size venue, large theater) should be stored as templates that can be instantiated with a venue and customized.
5. **Validation engine:** Post-placement, run all rules and produce a validation report — coverage gaps, throw distance issues, universe overflow, power exceedance.
