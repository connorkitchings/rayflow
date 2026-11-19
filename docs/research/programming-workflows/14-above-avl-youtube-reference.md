# Above AVL / Learn Stage Lighting — YouTube Reference Index

**Source:** YouTube channel — Above AVL / Learn Stage Lighting
**Playlists:** 3 playlists + 2 standalone videos
**Total:** 18 videos
**Raw transcripts:** `docs/research/raw_sources/above-avl-youtube/`
**Parsed:** 2026-05-26

---

## Content Clusters

### Cluster 1: Concert Lighting Fundamentals (1 video)

| # | Title | Duration | Notes |
|---|-------|----------|-------|
| — | Fundamentals of Lighting Design for Concerts with Craig Rutherford — Webinar | ~1.5 hr | Professional LD webinar. Covers design process, rig building, programming approach, and industry insights. |

**RayFlow value:** Professional concert lighting design fundamentals from a working LD. Directly applicable to the AI's design knowledge base.

### Cluster 2: Easy Setup Rig Configurations (8 videos)

| # | Title | Topic |
|---|-------|-------|
| — | Ground Supported Only | Rig setup with no flown truss — crank stands, T-bars, ground stacks |
| — | No Space Behind the Band | Rig design when the stage is against a wall — all fixtures must be front/side positioned |
| — | No Atmosphere, Haze or Fog | How to design a show when you can't use haze — fixtures must hit surfaces, not air |
| — | The Solo Artist | Rig design for a single performer — minimal fixtures, maximum impact |
| — | Mid-Size Stage, Ground Supported | Scaling up ground-supported rigs for larger stages |
| — | Mid-Size Stage, Installed Rig | Rig design for a permanently installed system (venue, church) |
| — | What in The Atmosphere is Going on? | Haze and fog guide — types, usage, when to use which |
| — | What DMX Mode Should I Put My Lights In? | DMX mode selection — how fixture mode choice affects channel count and capability |

**RayFlow value:** These are exactly the amateur/small-venue rig scenarios RayFlow targets. The "ground supported only" and "no space behind band" constraints are real-world limitations the rig builder should handle. The "DMX mode" video addresses a practical decision point for fixture patching.

### Cluster 3: Console Layout Design (3 videos)

| # | Title | Topic |
|---|-------|-------|
| — | Console Layout for Live Music | Busking layout for bands — faders, executors, what goes where |
| — | Console Layout for Corporate Events | Layout for corporate — minimalism, brand colors, speaker key light |
| — | Console Layout for Events with Cameras | Camera-aware layout — flicker considerations, exposure consistency, IMAG-safe |

**RayFlow value:** These map directly to the "what goes on which fader" decision that the AI should make when generating busking infrastructure. Each layout type (music, corporate, camera) has different priorities the AI needs to understand.

### Cluster 4: Console/Software Selection (5 videos)

| # | Title | Topic |
|---|-------|-------|
| — | Church Lighting | Console/software selection for houses of worship — volunteer operators, simplicity |
| — | Band Lighting | Selection for touring/playing bands — busking capability, portability |
| — | How to Choose (General) | Decision framework for console selection across use cases |
| — | DJ/EDM Lighting | Selection for electronic music — BPM sync, strobe control, pixel mapping |
| — | Theatre Lighting | Selection for theatrical — cue stacks, tracking, GO button workflow |

**RayFlow value:** Console selection is a prerequisite decision for RayFlow users. The AI should help users choose the right console for their use case, or default to the one RayFlow supports best (MA3 onPC).

### Cluster 5: Console Programming (1 video)

| # | Title | Topic |
|---|-------|-------|
| — | MA2 Crash Course — Program a Show From Scratch | Complete MA2 workflow: patch → groups → presets → sequences → playback |

**RayFlow value:** MA2 programming reference. While RayFlow targets MA3, MA2 knowledge is useful for venues/budgets still on MA2. The show-building workflow is the same pattern the AI must automate.

---

## Key Insights for RayFlow's Target User

These videos are aimed at exactly RayFlow's user: someone who wants to create lighting for music but may have limited budget, limited space, no rigging points, or volunteer operators.

### The "Ground Supported Only" Constraint
- No flown truss means all fixtures are on crank stands, tripods, or floor
- Trim heights are low (8–12 ft)
- Fixture weight matters (lighter fixtures on taller stands)
- Beam fixtures become problematic at low trim — they clip audience sightlines
- Washes and PARs become the workhorses

### The "No Haze" Constraint
- Without haze, beams are invisible. Every fixture must project onto a surface.
- Gobos on the floor/walls/ceiling become the primary texture tool
- Washes on the backdrop create the visual canvas
- Blinders and strobes work without haze (they're seen by their effect on the eye, not the beam shaft)

### The "No Space Behind Band" Constraint
- No backlight positions possible
- Side lighting becomes critical for depth
- Front wash must carry more color variation to compensate for missing backlight
- Floor uplighting behind the band creates some depth

### Console Layout Priorities by Use Case
- **Live music:** Speed and playability. Faders for intensity, buttons for color/position changes.
- **Corporate:** Clean, minimal, predictable. Pre-built looks, not live busking.
- **Camera:** Flicker-free fixtures, consistent exposure, no rapid intensity swings.

---

## Comparison to Our Existing Research

| Topic | Already Covered? | New from This Source |
|-------|-----------------|---------------------|
| Rig design fundamentals | ✅ (13-rig-design, 21-fixture-selection) | **Ground-supported constraints, no-haze constraints, no-backlight constraints** — real amateur limitations not covered |
| Busking layouts | ✅ (04-busking-layouts, 09-busking-architecture) | **Layout by event type** (corporate, camera) — extends beyond concert-only |
| Console choice | Partially (07-console-comparison covers capability differences) | **Selection by use case** — different decision framework |
| DMX modes | ✅ (protocols/02-fixture-types) | Practical mode selection guidance |
| MA3/MA2 programming | ✅ (3 series, longform tutorials) | Redundant (MA2 specific, already covered) |

## Implications for RayFlow

1. **The rig builder should handle amateur constraints.** "Ground supported only," "no haze," "no backlight positions," and "stage against a wall" should be checkboxes in the rig builder that adjust fixture placement rules.

2. **Busking layout generation should vary by event type.** A "Corporate Event" layout looks fundamentally different from a "Live Band" layout. The AI should generate different executor architectures per use case.

3. **Console selection is part of onboarding.** RayFlow should help new users choose the right console for their situation — or default them to MA3 onPC.

4. **DMX mode selection is a real-world friction point.** The rig builder should suggest appropriate DMX modes based on fixture count, universe budget, and needed features — not just default to the largest mode.

5. **The "no haze" design constraint is valid and common.** Many venues (churches, schools, some clubs) don't allow haze. The authoring system should generate haze-free cue strategies when this constraint is active.
