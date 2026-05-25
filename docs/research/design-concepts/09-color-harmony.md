# Color Harmony Systems for Lighting Design

**Source:** Web research, color theory literature, lighting design guides
**Parsed:** 2026-05-25

## Why Color Harmony Matters for Stage Lighting

Color is the most emotionally immediate element of a lighting design. Unlike static visual art, stage lighting colors transition over time, creating emotional arcs that must feel intentional, not jarring. A color harmony system provides rules for selecting and sequencing colors that feel naturally pleasing or deliberately provocative.

## Traditional Harmony Frameworks Mapped to Lighting

### Complementary (Opposing Colors)

```
Red ↔ Cyan,    Green ↔ Magenta,    Blue ↔ Yellow
```

- **Visual impact:** Maximum contrast, maximum energy. A red wash with cyan backlight creates intense visual separation.
- **Mixing behavior:** Complementary colors mixed at equal intensity produce white (neutral) light. Unequal mixing produces desaturated tints.
- **When to use:** High-energy choruses, dramatic reveals, contrast between different stage zones.
- **Risk:** Can feel garish or "holiday-themed" if overused (red+green = Christmas).

### Analogous (Adjacent Colors)

```
Warm set:     Red → Orange → Amber → Yellow
Cool set:     Cyan → Light Blue → Deep Blue → Lavender
```

- **Visual impact:** Harmonious, serene, cohesive. Smooth transitions between hues.
- **When to use:** Ballads, ambient sections, lyrical passages, scene-setting.
- **Advantage:** Safe choice. Analogous palettes are almost impossible to make look bad.
- **Limitation:** Can become visually monotonous over long durations.

### Triadic (Evenly Spaced)

```
Red → Green → Blue    (120° spacing)
Cyan → Magenta → Yellow
```

- **Visual impact:** Balanced but vibrant. Three distinct color families that don't clash.
- **When to use:** Multi-zone stage designs where different areas need distinct identities, or three-song medleys with clear transitions.
- **Console mapping:** Assign each triadic color to a different fixture group (spots = red, washes = green, beams = blue).

### Split-Complementary

```
Blue + Amber + Orange    (Blue + the two colors adjacent to Blue's complement)
Red + Cyan + Sea Green
```

- **Visual impact:** High contrast like complementary, but softer and more nuanced. Less "obvious" than straight complementary.
- **When to use:** Theatrical productions where strong contrast is needed but not "concert" energy. Good for tension scenes.

### Tetradic (Double Complementary / Rectangle)

```
Red + Cyan + Green + Magenta    (two complementary pairs)
Amber + Blue + Lavender + Yellow-Green
```

- **Visual impact:** Complex, rich, full-spectrum. Requires careful balancing.
- **When to use:** Large-scale productions with many fixture groups. Each complementary pair can be assigned to different stage levels (front/back, floor/air).

### Monochromatic

```
Deep Blue → Medium Blue → Light Blue → White (single hue, varying saturation/brightness)
```

- **Visual impact:** Elegant, sophisticated, minimal. Creates depth through intensity variation rather than hue changes.
- **When to use:** Corporate events, dramatic theatrical monologues, intimate acoustic performances.
- **Advantage:** No color clash possible. Fixtures with different color engines (RGB vs. CMY vs. color wheel) can all achieve the same monochromatic look.

## Color Temperature and Emotional Response

| Temperature | Kelvin Range | Associated Mood | Fixture Examples |
|-------------|-------------|----------------|-----------------|
| **Warm** | 2000K–3500K | Intimacy, comfort, nostalgia, sunrise/sunset, romance | Tungsten (3200K), Warm LED, CTO-filtered arc |
| **Neutral** | 3500K–5000K | Clarity, focus, professionalism, daytime | LED at 4000K, arc with CTO correction |
| **Cool** | 5000K–7000K | Calm, melancholy, mystery, moonlight, technology | LED at 5600K, arc (native), CTB filter |
| **Cold** | 7000K+ | Alien, clinical, sterile, underwater, dream | Deep blue LED, heavily CTB'd arc |

### Color Temperature Transitions

Transitioning color temperature over time communicates narrative progression:
- **Warm fade → Cool:** Sunset to night, emotional cooling, resolution
- **Cool fade → Warm:** Dawn, emotional warming, hope
- **Warm/Cool oscillation:** Diurnal cycling (McCandless diurnal simulation), dramatic tension/release

## Practical Stage Palettes

Field-tested 2–4 color combinations that work on skin tones:

### Two-Color Palettes
| Palette | Colors | Vibe |
|---------|--------|------|
| "Golden Hour" | Warm Amber + Lavender | Romantic, cinematic |
| "Deep Sea" | Deep Blue + Teal | Mysterious, calm |
| "Industrial" | White + Cyan | Modern, clean, corporate |
| "Ember" | Deep Red + Amber | Intense, passionate |

### Three-Color Palettes
| Palette | Colors | Vibe |
|---------|--------|------|
| "Sunset Drive" | Amber + Magenta + Deep Blue | Nostalgic, energetic |
| "Forest Light" | Green + Amber + Lavender | Organic, earthy |
| "Neon City" | Cyan + Magenta + White | Electronic, futuristic |
| "Velvet Night" | Deep Blue + Deep Red + Warm White | Theatrical, dramatic |

### Four-Color Palettes
| Palette | Colors | Vibe |
|---------|--------|------|
| "Full Spectrum" | Red + Amber + Cyan + Deep Blue | Energetic, versatile |
| "Pastel Dream" | Light Pink + Light Blue + Lavender + Warm White | Soft, dreamy |
| "Vintage" | Amber + Teal + Warm White + Light Pink | Retro, warm |

## Color Transition Strategies

Switching colors mid-show is the most common source of visual jarring. Three strategies minimize this:

### 1. Fade-Through-Black
Silent-to-black (1–2 seconds), then new color fades in. Clean break. Works for major mood shifts.

### 2. Color Crossfade
Both colors active simultaneously during the fade. The midpoint is a mix of both (may produce unintended colors). Works best with analogous palettes where the midpoint is pleasant.

### 3. Chase/Wipe Transition
Rather than all fixtures changing simultaneously, a chase sweeps the new color across fixtures left to right, center out, or random. Smooths the perceptual impact.

## Gel Library References as Color Anchors

Named gel colors from Rosco, Lee, and GAM provide universal color references that transcend console-specific palettes:

| Name | Rosco # | Lee # | Approximate Hex |
|------|---------|-------|----------------|
| Bastard Amber | R02 | L162 | #F7B262 |
| No Color Blue | R60 | L063 | #A8C7E9 |
| Primary Red | R27 | L106 | #CC000D |
| Fern Green | R89 | L122 | #2C6C34 |
| Lavender | R52 | L136 | #C8A9D8 |
| Congo Blue | R382 | L181 | #181899 |
| Surprise Pink | R46 | L128 | #E0218A |
| Medium Amber | R17 | L135 | #E87D30 |

Using gel references rather than raw RGB values gives the authoring system access to thousands of designer-tested colors that work on skin tones and under common light sources.

## Implications for RayFlow

1. **Vibe-driven palette selection:** The `Vibe` model should select from named palette templates (warm-cool, analogous, complementary, etc.) based on song mood keywords.
2. **Color transition strategies in authoring:** The cue generator should choose transition strategies (fade-through-black, crossfade, or chase) appropriate to the color distance between adjacent cues.
3. **Gel reference library:** RayFlow should maintain a lookup of named gel references (Rosco, Lee) as canonical color anchors, with RGB/hex equivalents for fixture-appropriate mapping.
4. **Fixture color model awareness:** A "Warm Amber" gel translates differently to an RGB LED fixture (red+green channels) vs. a CMY moving head (magenta+yellow mix) vs. a color wheel spot (nearest slot). The renderer must handle this translation.
5. **Per-fixture color correction:** When mixed fixture types share a color palette, apply per-type color correction to achieve perceptual uniformity — what looks "warm amber" on LEDs should match "warm amber" on tungsten.
