# Gobo Design, Construction, and Selection

**Source:** Web research, manufacturer documentation, lighting design guides
**Parsed:** 2026-05-25

## What Is a Gobo?

A GOBO ("Goes Before Optics") is a thin stencil placed at the focal plane of a profile (ellipsoidal) fixture's optical path. Light passing through the gobo projects the pattern onto a surface or through atmospheric haze. Gobos add texture, depth, and visual interest beyond what a uniform wash can achieve.

## Construction Types

### Metal / Stainless Steel Gobos

| Property | Description |
|----------|-------------|
| **Construction** | Laser-cut stainless steel or brass sheet, typically 0.2–0.5 mm thick |
| **Pattern types** | Breakup (leaves, branches), linear (slats, bars), geometric (circles, triangles), abstract |
| **Durability** | High heat tolerance. Suitable for high-wattage fixtures (575W–1200W+) |
| **Resolution** | Limited — cannot produce photographic detail. Fine details require support bridges |
| **Cost** | Low ($10–$50 each) |
| **Best for** | Breakup textures, aerial beam shaping, theatrical scenery |

### Glass Gobos

| Property | Description |
|----------|-------------|
| **Construction** | Multi-layer dichroic coating on high-temperature borosilicate or quartz glass |
| **Pattern types** | Full-color photographic imagery, multi-color abstract, corporate logos |
| **Durability** | Moderate. Coating can degrade under extreme heat over time |
| **Resolution** | Very high — photographic-quality detail with smooth gradients |
| **Cost** | High ($50–$300+ each) |
| **Best for** | Logo projection, scenic backdrops, photographic textures |

### Plastic / Transparency Gobos

| Property | Description |
|----------|-------------|
| **Construction** | Printed transparency film |
| **Durability** | Low. Only suitable for LED fixtures (no heat) |
| **Resolution** | Very high |
| **Cost** | Very low ($5–$15 each) |
| **Best for** | Short-term events, LED source fixtures |

## Gobo Mechanism Types

| Mechanism | Description | DMX Channels |
|-----------|-------------|-------------|
| **Fixed / Static** | Single gobo inserted into a holder. No DMX control. | 0 |
| **Gobo Wheel** | Rotating wheel with 6–12 fixed positions. DMX selects slot. | 1 (index/position) |
| **Rotating Gobo** | Single gobo on a motorized mount. Continuous rotation + indexed positioning. | 2 (rotation speed + index angle) |
| **Animation Wheel** | Secondary wheel with radial slots that rotates independently. Creates moving texture effects (fire, water, clouds) when combined with a static gobo. | 1–2 (rotation speed, sometimes direction) |
| **Gobo Morphing** | Two gobo wheels that crossfade between patterns. Found on high-end fixtures. | 2 (gobo A position, gobo B position) |

## The Optical Path: Focus, Zoom, and Iris Integration

A gobo projects best when the fixture is sharply focused at the projection plane. The relationship between optical elements determines gobo quality:

| Control | Effect on Gobo |
|---------|---------------|
| **Focus** | Sharpens or softens gobo edges. Soft focus creates atmospheric, dreamy texture. Hard focus is required for logos and lettering. |
| **Zoom** | Adjusts beam angle (e.g., 15° to 30°). Wider zoom = larger, dimmer projection. Narrow zoom = smaller, brighter, sharper projection. |
| **Iris** | Narrows the beam diameter without changing focus. Can crop gobo edges for a tighter projection. |
| **Prism** | Splits the beam into multiple copies of the gobo pattern (3-facet, 5-facet, etc.). Rotation creates kaleidoscopic effects. |
| **Frost** | Diffuses the beam, softening or completely washing out the gobo pattern. Useful for transitioning between gobo texture and smooth wash. |

## Common Gobo Categories

| Category | Examples | Visual Purpose |
|----------|----------|---------------|
| **Breakup** | Leaves, branches, organic shapes | Simulating dappled light through trees, breaking up flat surfaces |
| **Linear** | Slats, Venetian blinds, bars | Creating architectural texture, prison/office window effects |
| **Geometric** | Circles, squares, hexagons, grids | Clean, modern texture. Good for corporate events |
| **Abstract** | Swirls, splatters, irregular shapes | Adding energy and chaos. Popular for concert lighting |
| **Aerial** | Open-center rings, beam shapers | Shaping beam fixtures for visible air effects |
| **Custom / Logo** | Company logos, event branding, text | Corporate events, product launches |
| **Dot / Confetti** | Dense patterns of small apertures | Starfield effects, disco-style texture |

## Gobo Selection Heuristics

- **Large venues:** Choose high-contrast patterns with bold elements. Fine details are lost at distance.
- **Camera/IMAG:** Avoid dense line patterns (moiré artifacts on camera sensors). Choose organic breakup over tight grids.
- **Skin tones:** Avoid projecting gobos directly on performers' faces unless intentional. Dense breakup patterns create distracting shadow maps.
- **Atmospheric beam effects:** Use open-center or ring gobos. Solid-center gobos block the visible beam core.
- **Heat management:** Metal gobos in high-wattage fixtures expand and may warp. Glass gobos handle heat but are fragile to mechanical shock.

## GDTF Gobo Wheel Representation

GDTF defines gobo wheels as `Wheel` elements within the fixture's `PhysicalDescriptions`:

```xml
<Wheel Name="Gobo1">
  <Slot Name="Open" />
  <Slot Name="Gobo 1">
    <Facet Color="0.15" Image="wheel1.png" />
  </Slot>
</Wheel>
```

Each slot can reference a PNG image (the gobo pattern) stored in the GDTF ZIP archive. The `Color` attribute specifies the glass color coefficient (0–1 per RGB channel).

## Implications for RayFlow

1. **Gobo-aware authoring:** The cue authoring system should select gobos that match the show's vibe (e.g., "organic" for folk, "geometric" for electronic).
2. **Fixture capability check:** Before assigning a gobo to a cue, verify the fixture has a gobo wheel or rotating gobo channel. Fixtures without gobo support should fall back gracefully.
3. **Gobo image rendering:** For visual preview (if ever implemented), gobo wheel images from GDTF files could be composited into the beam render.
4. **Gobo + zoom interaction:** When a cue specifies both gobo and zoom values, the renderer should validate that the zoom range can project the gobo with acceptable sharpness.
5. **Animation wheel support:** The gobo family should also cover animation wheel rotation speed as a continuous DMX parameter.
