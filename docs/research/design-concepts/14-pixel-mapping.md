# Pixel Mapping Fundamentals

**Source:** Web research, Art-Net specification, LED fixture documentation
**Parsed:** 2026-05-25

## What Is Pixel Mapping?

Pixel mapping assigns individual DMX channels to specific physical positions on a two-dimensional array (grid, bar, panel), then drives those positions with video-like content — color patterns, gradients, chases, or full video playback. Where a moving head creates one beam, a pixel-mapped LED bar creates dozens of independently colored segments.

## Pixel Fixture Types

| Fixture Type | Pixels | Typical DMX Footprint | Example |
|-------------|--------|----------------------|---------|
| **LED Pixel Bar** | 4–40 cells per bar | 3–6 channels per cell (RGB, RGBW, RGBAW) | GLP Impression X4 Bar (20 cells) |
| **LED Panel / Tile** | 64–2,304 pixels per panel | 3 channels per pixel (RGB) | ROE Visual LED panels |
| **Pixel Strip** | 30–144 LEDs per meter | 3 channels per pixel | Addressable LED tape |
| **Multi-Cell Wash** | 4–37 cells per fixture | 3–6 channels per cell | Ayrton MagicPanel 602 (36 cells) |
| **Hybrid Moving Head + Pixel** | 1–19 cells + pan/tilt | Combines moving light + pixel channels | Martin MAC Aura PXL |

## DMX Channel Explosion

A single pixel bar with 20 cells at 4 channels (RGBW) consumes 80 DMX addresses — nearly 1/6 of a universe. A 2m × 2m LED panel at a modest 32×32 pixel resolution consumes 3,072 channels (6 full universes). Pixel mapping is the primary driver of large universe counts in modern shows.

### Scaling Heuristics

| Content Type | Minimum Pixels | Universes Needed |
|-------------|---------------|-----------------|
| Single color chase across bars | 4–8 per bar | 1–2 |
| Gradient washes across panels | 16×16 (256 pixels) | 2 |
| Low-res video content | 64×64 (4,096 pixels) | 24 |
| HD video on LED wall | 1920×1080 (2M pixels) | ~12,000 |

## Layout View and Virtual Grids

Modern consoles use a Layout View to map physical pixel positions to a logical grid:

1. **Patch fixtures** with real DMX addresses.
2. **Place fixtures in Layout View** — drag and drop fixtures onto a virtual grid representing their physical positions.
3. **Assign content** to the layout. The console routes content pixels to DMX addresses based on the layout mapping.

Without a layout, pixel mapping is nearly impossible — the programmer would need to know the DMX address of every individual pixel and manually write values. The layout abstracts physical addressing.

## Content Types for Pixel-Mapped Fixtures

### Color Chases
Sequential color running across cells. A red flash sweeps left-to-right across a bar. Simplest and most common pixel effect.

### Color Waves / Gradients
Smooth color transitions across the array. A rainbow gradient spans from cell 1 (red) to cell 20 (violet). Can be static or animated.

### Pattern Generators
Geometric patterns (circles, lines, checkerboards) rendered across the pixel grid. Often built into console effect engines.

### Video Playback
External video content mapped to the pixel array. Requires a media server (Resolume, madMapper, Green Hippo, MA3 VPU) or Art-Net feed from a video source.

### Audio-Reactive
Pixel intensity/color driven by audio analysis (kick drum triggers flash, bass frequencies drive color intensity). Typically routed through a media server or custom software.

## Art-Net and sACN for Pixel Data

Pixel mapping almost always uses Ethernet protocols (Art-Net or sACN) rather than physical DMX cable because:

- **Bandwidth:** A single DMX universe refreshes at ~44 Hz maximum. Driving 20 universes of pixel data requires parallel network transport.
- **Cable count:** 20 universes = 20 DMX cables vs. 1 Ethernet cable.
- **Multicast (sACN):** Video content can be sent once and received by multiple pixel decoders simultaneously.

### Art-Net Universe Layout for Pixels
A common convention maps pixel columns to consecutive Art-Net universes:
- Column 1, rows 1–170 → Universe 0, addresses 1–510 (170 pixels × 3 RGB channels)
- Column 2, rows 1–170 → Universe 1, addresses 1–510
- Column 3, rows 1–170 → Universe 2

## Content Generation Pipeline

```
Media Server / Video Source
    → Art-Net / sACN over Ethernet
        → Network Switch
            → Pixel Decoder Node (Ethernet → DMX)
                → Pixel Fixture (DMX input)
```

Each pixel decoder node converts one Ethernet stream into 1–8 physical DMX outputs. Multiple nodes are chained on the network for larger installations.

## Console-Specific Pixel Mapping

| Console | Pixel Mapping Approach |
|---------|----------------------|
| **grandMA3** | Layout View with pixel mapping layer. Integrated media server (VPU). Built-in pattern generators. |
| **Chamsys MagicQ** | Strong pixel mapping engine. Grid-based layout. Competitive for club/small venue. |
| **ETC Eos** | Virtual Media Server for pixel mapping. Augment3d integration for layout. |
| **Avolites Titan** | Pixel Mapper effect. Key Frame Shapes for custom content. |

## Practical Considerations

### Refresh Rate and PWM
- LED fixtures with low PWM frequency (< 600 Hz) flicker on camera. This is amplified in pixel-mapped setups where hundreds of LEDs are visible simultaneously.
- **Fix:** Use fixtures with PWM ≥ 1200 Hz for broadcast. Test with venue cameras at the intended frame rate.

### Network Topology
- Segregate pixel data on a dedicated VLAN. Art-Net/sACN traffic can saturate a 100 Mbps link with 20+ universes.
- Use managed switches with IGMP snooping for sACN multicast.
- Avoid daisy-chaining network switches — use a star topology with a central core switch.

### Heat Management
- Dense pixel arrays (panels, tiles) generate significant heat. Leave air gaps between panels. Monitor temperature in enclosed installations.

## Implications for RayFlow

1. **Pixel-aware fixture channels:** The GDTF parser already handles multi-cell fixture modes. The renderer should support per-cell DMX output for pixel fixtures.
2. **Layout data in the rig model:** The rig model should capture fixture layout positions (grid coordinates) to enable the renderer to map content to pixel positions.
3. **Pixel content primitives:** The authoring system should generate simple pixel effects (color chases, gradients, waves) as cue attributes, not just static colors.
4. **Universe budgeting:** When patching pixel fixtures, the rig builder should warn if the pixel channel count exceeds available universe capacity.
5. **Content generation boundary:** Full video playback through RayFlow is out of scope, but exporting pixel cue data in formats readable by media servers (Art-Net frames, CSV channel maps) bridges the gap.
