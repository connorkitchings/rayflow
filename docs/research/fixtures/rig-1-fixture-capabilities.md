# Rig 1 Fixture Capability Research

**Rig:** `Rig 1`  
**Purpose:** Understand the creative and technical range of the fixtures currently
selected for the reusable RayFlow pilot rig.

This document is grounded in the checked-in GDTF profiles in
`data/fixtures/samples/`, the patched modes in `data/rigs/Rig 1.yaml`, official
Robe fixture references for the two Robe units, and the user's inspiration
photos.

## Rig 1 Fixture Inventory

| Role | Count | Fixture | Patched mode | Channels each | Rig channels |
|------|------:|---------|--------------|--------------:|--------------|
| Front/side wash | 6 | BlenderDMX LED PAR 64 RGBW | Default | 5 | 1-30 |
| Back wash / beam fans | 4 | Robe Robin iSpiiderX | Mode 2 - Basic | 27 | 33-140 |
| Texture/profile / beam shaping | 4 | Robe Robin MMX Blade | Mode 1 - Standard | 45 | 145-324 |

## Global Design Lessons From Inspiration Photos

The reference images point toward a beam-and-atmosphere rig language:

- Use **symmetrical fan presets** as a core visual vocabulary, especially from
  upstage fixtures aimed forward and upward.
- Build **crossed X presets** where left and right fixtures meet over center
  stage or over the drummer/lead position.
- Keep **low backline glow** active during saturated looks so the stage has a
  visible floor horizon.
- Treat **white/blue aerials** as peak punctuation, not a base state.
- Use **magenta/lime, amber/cyan, red/aqua, and blue/cyan** as primary palette
  families.
- Design for haze. Most of these looks only read because the air is visible.
- Maintain performer visibility selectively: the images often silhouette the
  band while beams carry the drama, but key moments still need warm front or
  white specials.

## LED PAR 64 RGBW

### What It Is In Rig 1

The PARs are the simple, reliable foundation fixtures. They do not move, zoom,
frame, or project gobos. Their value is color wash, front visibility, side glow,
and low-complexity color accents.

### Patched Mode: `Default`

| Slot | Attribute |
|-----:|-----------|
| 1 | Dimmer |
| 2 | Red additive |
| 3 | Green additive |
| 4 | Blue additive |
| 5 | White additive |

### Practical Capabilities

- **Intensity:** direct dimmer control, useful for smooth fades and bumps.
- **Color:** RGBW additive mixing. Good for warm amber, lavender, cyan, blue,
  magenta, red, and open white.
- **White support:** the white emitter can make front light less synthetic than
  RGB-only mixes.
- **Reliability:** simple five-channel footprint means no mode complexity and no
  accidental parameter families.

### Creative Use Cases

- Warm front/key light so the band remains visible.
- Side amber or side magenta glow.
- Floor/backline color bed if moved or duplicated in future rigs.
- Section-level color identity, especially for verses and lower-energy parts.
- Audience-readable color shifts when moving fixtures are reserved for aerial
  geometry.

### Limits

- No pan/tilt: all positions are physical placement decisions.
- No beam control: cannot create narrow aerial shafts or fan geometry.
- No gobo, prism, iris, frost, or animation.
- Not the right fixture for the dramatic beam looks in the photos unless it is
  acting as a saturated wash behind them.

### RayFlow Authoring Guidance

Use PARs for `front_warm`, `side_glow`, `floor_glow`, `verse_visibility`, and
`color_bed` presets. Avoid assigning movement, gobo, zoom, focus, iris, or
shutter-special looks to them.

## Robe Robin iSpiiderX

### What It Is In Rig 1

The iSpiiderX is the main wash/beam hybrid layer. In this rig it is patched as a
basic moving RGBW wash with zoom, shutter, dimmer, movement, CTO, color macros,
and built-in effect controls. Official Robe material describes the iSpiiderX as
an IP65-rated version of the Spiider concept with the MCFE multi-colored flower
effect, making it useful for both wash coverage and aerial flower/beam texture.
Official specifications list 18 x 40W RGBW LED multichips plus a center 60W
RGBW source, a 4-50 degree zoom range, 10 DMX protocol modes, 16-bit pan/tilt,
540 degree pan, and 220 degree tilt.

### Patched Mode: `Mode 2 - Basic`

| Slot | Attribute |
|-----:|-----------|
| 1-2 | Pan, fine pan |
| 3-4 | Tilt, fine tilt |
| 5 | Position movement speed |
| 6 | Control |
| 7 | Color wheel / color control |
| 8-11 | Main RGBW additive color |
| 12 | CTO |
| 13 | Color mix mode |
| 14 | Effect |
| 15 | Effect rate |
| 16 | Effect fade |
| 17 | Flower effect |
| 18-21 | Secondary RGBW additive color |
| 22 | Color macro |
| 23 | Shutter |
| 24 | Dimmer |
| 25 | Zoom |
| 26 | Secondary shutter |
| 27 | Secondary dimmer |

### Practical Capabilities

- **16-bit movement:** pan and tilt have fine channels, so slow sweeps and
  precise fan positions should be smooth.
- **Zoom:** can shift between broad wash and tighter beam-like shafts.
- **RGBW color mixing:** supports the photo-inspired blue/cyan, magenta, amber,
  red, and white-blue peak palettes.
- **CTO:** can warm the output for organic front/back wash looks.
- **Flower/effects layer:** can produce multi-colored flower or texture behavior
  without requiring pixel-level control.
- **Dual dimmer/shutter families:** the profile exposes primary and secondary
  shutter/dimmer controls, likely separating wash and flower/effect engines.
- **Multiple richer modes exist:** the local GDTF includes pixel, pattern, zones,
  full RGBW, and pattern-full modes from 33 to 123 channels. Rig 1 deliberately
  uses the 27-channel basic mode to keep patching manageable.

### Creative Use Cases

- Upstage fan presets: `fan_upstage_wide`, `fan_upstage_tight`.
- X looks: `cross_center_x`, `cross_high_x`.
- Blue/cyan aerial bed behind the band.
- Magenta/lime or amber/cyan counterpoint against MMX Blade texture.
- White/blue peak looks with zoom tightened and dimmer high.
- Slow Hoffman-style color evolution across the upstage row.
- Flower effect accents during jams, bridges, and psychedelic peaks.

### Limits

- In the current basic mode, RayFlow does not get the full pixel/pattern
  vocabulary exposed by the larger iSpiiderX modes.
- No true framing blades or profile shutters.
- Built-in effects are fixture-specific, so they should be wrapped in named
  presets rather than scattered as raw values through cues.
- If the intended visual language becomes very pixel-pattern heavy, Rig 1 should
  consider switching iSpiiderX to a richer mode and repatching.

### RayFlow Authoring Guidance

Use iSpiiderX as the primary moving wash/beam family. Create position presets
for wide fans, tight fans, center crosses, high crosses, audience rake, and
overhead bloom. Create color presets around `electric_blue_cyan`,
`magenta_lime`, `amber_cyan`, `white_blue_peak`, and `purple_blue_cyan`.

Keep raw effect channels out of normal cues until we define named effect
presets such as `flower_soft`, `flower_peak`, `wash_chase_slow`, and
`aerial_pulse`.

## Robe Robin MMX Blade

### What It Is In Rig 1

The MMX Blade is the precision profile layer. Official Robe material presents
the MMX Blade as a high-output moving profile with CMY color mixing, CTO, color
wheel, gobos, animation, prism, frost, iris, zoom, focus, framing blades, hot
spot control, shutter, and dimmer. In Rig 1, these fixtures are the strongest
tools for texture, shaped beams, aerial X looks, and controlled specials.
Official Robe references describe the fixture as MMX-discharge based with output
comparable to 1200W luminaires, a framing shutter system, rotating gobo wheel,
dual animation wheel, 5-facet rotating prism, CMY/CTO, and an 8.5-45.5 degree
zoom range.

### Patched Mode: `Mode 1 - Standard`

| Slot | Attribute |
|-----:|-----------|
| 1-2 | Pan, fine pan |
| 3-4 | Tilt, fine tilt |
| 5 | Position movement speed |
| 6 | Control |
| 7-8 | Color wheel, fine color wheel |
| 9-11 | CMY subtractive color |
| 12 | CTO |
| 13 | Color macro |
| 14 | Gobo wheel movement speed |
| 15 | Animation wheel |
| 16 | Animation wheel position |
| 17 | Animation wheel macro |
| 18 | Gobo |
| 19-20 | Gobo position / rotation, fine |
| 21 | Prism |
| 22 | Prism position / rotation |
| 23 | Frost |
| 24-25 | Iris, fine iris |
| 26-27 | Zoom, fine zoom |
| 28-29 | Focus, fine focus |
| 30 | Focus adjust |
| 31 | Framing module rotation |
| 32-39 | Four framing blade insertion/rotation pairs |
| 40 | Framing macro |
| 41 | Framing macro speed |
| 42 | Hot spot |
| 43 | Shutter |
| 44-45 | Dimmer, fine dimmer |

### Practical Capabilities

- **16-bit movement:** accurate pan/tilt for repeatable fan and cross positions.
- **CMY color mixing:** smoother theatrical color control than simple RGB for
  profile beams.
- **Color wheel and color macros:** fast saturated choices and repeatable
  fixture-native color looks.
- **Gobo system:** projected texture, beam breakup, rotating texture, and
  pattern identity.
- **Animation wheel:** motion texture, water/fire/cloud-like movement, and
  atmospheric surface breakup.
- **Prism:** multiplies beams for photo-style multi-ray aerial looks.
- **Frost:** softens profile output into a washier beam.
- **Iris:** controls beam aperture and punch.
- **Zoom/focus:** essential for switching between sharp aerial shafts, textured
  projection, and soft atmosphere.
- **Four framing blades:** can shape beams, trim spill, make slash looks, or
  create architectural rectangles.
- **Hot spot:** helps flatten or emphasize beam intensity distribution.

### Creative Use Cases

- Primary texture layer for `gobo_cloud`, `gobo_breakup`, `slow_animation`, and
  `psychedelic_texture`.
- Sharp white/yellow aerial beams during peaks.
- Prism fan accents, especially in magenta/lime and white/blue looks.
- Cross-stage X looks with focus/zoom tuned to read in haze.
- Framed shafts that avoid hitting performers' faces while still filling the air.
- Center specials or silhouette accents when front PARs are dimmed.
- Red/magenta/aqua or amber/cyan profile layers over iSpiider wash.

### Limits

- Unlike iSpiiderX, MMX Blade is not a soft wash-first fixture. It can frost and
  zoom, but its best value is profile texture and beam shaping.
- Framing blades add expressive power but also complexity. Use named presets
  rather than raw blade values in song cues.
- CMY color behavior differs from RGBW. Palette translation must account for
  subtractive color rather than treating it like the PARs or iSpiiderX.
- The current renderer supports core families like pan, tilt, zoom, focus,
  shutter, gobo, dimmer, and color, but deep blade/prism/animation semantics
  should be modeled as explicit named presets before heavy cue use.

### RayFlow Authoring Guidance

Use MMX Blade for `texture`, `profile_beam`, `gobo`, `prism`, `iris`,
`framed_special`, and `animation` presets. For the inspiration-image language,
these are the fixtures that should create crisp diagonal shafts, X intersections,
breakup texture in haze, and white/yellow peak punches.

## Recommended Preset Vocabulary

### Position Presets

| Preset | Primary fixtures | Description |
|--------|------------------|-------------|
| `fan_upstage_wide` | iSpiiderX, MMX Blade | Symmetric wide fan from upstage toward FOH. |
| `fan_upstage_tight` | iSpiiderX, MMX Blade | Narrower fan centered above drums/lead. |
| `cross_center_x` | iSpiiderX, MMX Blade | Left/right fixtures cross at center stage. |
| `cross_high_x` | iSpiiderX, MMX Blade | Higher aerial X for peak moments. |
| `outer_wings` | iSpiiderX, MMX Blade | Far left/right beams rake diagonally inward. |
| `ceiling_bloom` | iSpiiderX | High tilt and wider zoom for overhead canopy. |
| `floor_glow_backline` | PARs, iSpiiderX | Low saturated horizon behind performers. |
| `silhouette_band` | PARs low, back fixtures high | Back/side emphasis with reduced front wash. |

### Color Palettes

| Palette | Fixture emphasis | Use |
|---------|------------------|-----|
| `electric_blue_cyan` | iSpiiderX RGBW, PAR RGBW | Cool aerial bed and modern saturated wash. |
| `magenta_lime` | iSpiiderX, MMX Blade | Psychedelic contrast from the reference photos. |
| `amber_cyan` | PAR amber, iSpiiderX cyan | Warm organic band light with cool aerial contrast. |
| `red_magenta_aqua` | PAR red, MMX/iSpiider magenta+aqua | Hot jam/bridge look with opposing accents. |
| `white_blue_peak` | MMX white, iSpiider blue/cyan | Big peak punctuation and photo-style aerial shafts. |
| `purple_blue_cyan` | iSpiiderX, PARs | Cooler atmospheric verses or spacey sections. |
| `hot_red_white` | MMX Blade, PARs | High-intensity dramatic climax. |

### Beam / Texture Presets

| Preset | Primary fixtures | Description |
|--------|------------------|-------------|
| `soft_wide_wash` | iSpiiderX | Wide zoom, low/medium dimmer, no hard beam. |
| `tight_aerial` | iSpiiderX, MMX Blade | Narrower zoom for visible shafts. |
| `breakup_gobo_slow` | MMX Blade | Gobo texture with slow rotation. |
| `animation_cloud` | MMX Blade | Animation wheel for moving haze texture. |
| `prism_peak` | MMX Blade | Beam multiplication for climactic sections. |
| `framed_slash` | MMX Blade | Blade-shaped diagonal/architectural shaft. |
| `flower_soft` | iSpiiderX | Subtle flower effect layer. |
| `flower_peak` | iSpiiderX | Brighter multi-color flower effect for jams. |

## Implementation Implications

1. **Do not treat Rig 1 as only wash + gobo.** The iSpiiderX and MMX Blade
   profiles expose enough movement, zoom, shutter, color, and beam controls to
   support a much richer image vocabulary.
2. **Named presets should come before song cues.** The deep fixture-specific
   families, especially iSpiiderX effects and MMX Blade blades/prism/animation,
   should be encoded as reusable named presets before being applied to songs.
3. **Renderer support should expand by vocabulary, not raw channels.** Add
   semantic support for `prism`, `iris`, `frost`, `animation`, `blade`, and
   `flower_effect` only when a named authoring need exists.
4. **Mode choice matters.** The current iSpiiderX basic mode is efficient, but
   richer pixel/pattern looks would require a mode change and repatch.
5. **Haze is assumed for the target look.** The inspiration images rely on
   visible atmosphere. A no-haze variant would need more surface projection,
   front/side wash, and less beam-heavy cue language.

## Sources

- Local GDTF profiles: `data/fixtures/samples/BlenderDMX_LED_PAR_64_RGBW.gdtf`,
  `data/fixtures/samples/Robe_Robin_iSpiiderX.gdtf`,
  `data/fixtures/samples/Robe_Robin_MMX_Blade.gdtf`
- Rig source: `data/rigs/Rig 1.yaml`
- Official Robe reference: [Robin iSpiiderX product documentation](https://www.robeuk.com/ispiiderx)
- Official Robe reference: [Robin MMX Blade product documentation](https://www.robe.cz/mmx-blade)
- Official Robe reference: [Robin MMX Blade leaflet](https://www.robe.cz/res/downloads/catalogues/ROBE_ROBIN_MMX_Blade_leaflet_01.pdf)
- User-provided inspiration photos in the 2026-05-27 session
