# Fixture Types and DMX Channel Capabilities

**Source:** `docs/research/manual_research2.txt`, `docs/research/manual_research1.txt`  
**Parsed:** 2026-05-25

## Fixture Categories

### Conventional Dimmers

- **Channels:** 1 (intensity)
- **Description:** Standard incandescent or LED fixtures controlled via a dimmer pack. Each fixture maps to a single DMX address with values 0–255.
- **Use case:** Front light washes, practicals, static area lighting.

### LED PARs

- **Channels:** 4–8 (dimmer, red, green, blue, white, amber, UV, shutter/strobe)
- **Description:** Fixed-position LED fixtures with additive RGB or RGBW color mixing. No moving parts.
- **Use case:** Color washes, static background lighting, audience blinders.

### Moving Heads — Spot

- **Channels:** 15–30+ (pan, pan fine, tilt, tilt fine, dimmer, shutter, color wheel, gobo wheel, gobo rotation, prism, prism rotation, zoom, focus, frost, iris)
- **Description:** Motorized fixtures with precise pan/tilt control and complex optical paths. Spots produce sharp, defined beams with gobo projection capability.
- **Use case:** Key lighting, aerial beams, pattern projection.

### Moving Heads — Wash

- **Channels:** 12–20+ (pan, pan fine, tilt, tilt fine, dimmer, CMY or RGB color mixing, zoom, shutter, frost)
- **Description:** Similar to spots but with softer optical paths designed for wide, even color coverage rather than sharp beam definition.
- **Use case:** Stage washes, color transitions, area coverage.

### Moving Heads — Beam

- **Channels:** 10–16+ (pan, pan fine, tilt, tilt fine, dimmer, color wheel, prism, shutter/strobe, zoom)
- **Description:** Narrow-beam, high-intensity fixtures optimized for visible light shafts through atmospheric haze. Limited gobo/color complexity compared to spots.
- **Use case:** Aerial effects, ballyhoos, high-energy sweeps.

### Multi-Cell Pixel Bars

- **Channels:** 3–6 per cell × N cells (e.g., 8 cells × 4 channels = 32 channels)
- **Description:** Linear fixtures with individually addressable LED segments. Each cell typically has RGBW or RGBAW control.
- **Use case:** Pixel mapping, color chases, linear wipes, architectural shapes.

### Fog / Haze Machines

- **Channels:** 1–2 (output/intensity, fan speed)
- **Description:** Atmospheric effect machines that suspend microscopic particulate in the air to make light beams visible.
- **Use case:** Essential for beam effects, ballyhoos, and any aerial lighting design.

### Laser Systems

- **Channels:** 5–15+ (safety interlock, blanking, X scanner, Y scanner, red, green, blue, pattern selection, pattern rotation, speed)
- **Description:** High-intensity coherent light sources with galvanometer scanners for precise beam positioning.
- **Use case:** Geometric aerial patterns, audience scanning (with safety compliance), high-impact visual moments.

## DMX Channel Families

Professional consoles group fixture channels into **feature families** for efficient programming. These families map directly to palette types:

| Feature Family | Parameters | Palette Type |
|---|---|---|
| **Intensity** | Dimmer, shutter, strobe | Intensity Palette |
| **Position** | Pan, tilt, pan fine, tilt fine | Position Palette |
| **Color** | Color wheel, CMY, RGB, CTO, gel | Color Palette |
| **Beam** | Gobo, gobo rotation, prism, iris, zoom, focus | Beam Palette |
| **Effect** | Frost, animation wheel, macro parameters | Effect Palette |

## Channel Count Implications

A single physical DMX universe contains 512 addresses. Channel allocation per fixture type determines how many fixtures fit per universe:

- **Dimmers only:** Up to 512 fixtures per universe
- **LED PARs (4-channel):** ~128 fixtures per universe
- **Moving head spots (20-channel):** ~25 fixtures per universe
- **Pixel bars (32-channel):** ~16 fixtures per universe

Large rigs with hundreds of moving lights require multiple DMX universes, typically transported over Ethernet via Art-Net or sACN.

## Implications for RayFlow

RayFlow's fixture model must:

1. **Parse GDTF profiles** to determine exact channel count and mapping per fixture.
2. **Group channels by feature family** for palette-aware programming.
3. **Calculate universe allocation** based on fixture channel widths.
4. **Support multiple color models** (RGB additive, CMY subtractive, hybrid) within the same show.
5. **Handle fine-resolution channels** (16-bit pan/tilt) for smooth movement.
