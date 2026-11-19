# Movement Patterns, Phasing, and Fanning

**Source:** Web research, console programming guides, lighting design literature
**Parsed:** 2026-05-25

## Movement as a Compositional Layer

Movement is the most immediately visible layer of a lighting design. While color and intensity set mood, movement signals energy, directs attention, and creates the kinetic excitement that defines live concert lighting. Movement programming operates on two axes: the **path** a fixture traces, and the **relationship** between multiple fixtures executing that path.

## Basis Functions: How Consoles Generate Movement

All pan/tilt movement effects are built from sine and cosine oscillators driving the pan and tilt channels independently. The combination of two oscillators with specific phase relationships creates recognizable geometric paths:

### Fundamental Movement Patterns

| Pattern | Pan Function | Tilt Function | Phase Offset | Visual Result |
|---------|-------------|--------------|-------------|---------------|
| **Circle** | `sin(t)` | `cos(t)` | 90° | Perfect circle. Pan leads tilt by 90°. |
| **Ellipse** | `sin(t) * W` | `cos(t) * H` | 90° | Oval. Different amplitude on pan (W) vs tilt (H). |
| **Horizontal Line** | `sin(t)` | 0 (static) | N/A | Fixture sweeps left/right only |
| **Vertical Line** | 0 (static) | `sin(t)` | N/A | Fixture sweeps up/down only |
| **Diagonal Line** | `sin(t)` | `sin(t)` | 0° | 45° diagonal sweep |
| **Figure-8** | `sin(t)` | `sin(2t)` | N/A | Lissajous curve. Tilt cycles twice per pan cycle. |
| **Square/Rectangle** | Smoothed square wave | Smoothed square wave | 90° | Approximation of rectangular path |
| **Triangle** | `sin(t)` | `sin(t + 180°)` | 180° | Opposing diagonal sweep |
| **Random Walk** | Random steps | Random steps | Independent | Organic, unpredictable wandering |

### Lissajous Curves

Named patterns emerge from the frequency ratio of pan to tilt oscillators:

| Ratio (pan:tilt) | Shape |
|-----------------|-------|
| 1:1, 0° phase | Diagonal line |
| 1:1, 90° phase | Circle / Ellipse |
| 1:2 | Figure-8 |
| 1:3 | Three-looped figure |
| 2:3 | Complex looping pattern |
| 3:4 | Ornate trefoil-like pattern |

### Movement Size and Center Position

The amplitude of the oscillator determines the physical sweep range:

```
actual_pan = center_pan + (sin(t) * size * pan_range / 2)
actual_tilt = center_tilt + (cos(t) * size * tilt_range / 2)
```

- **Center:** The programmed position preset (e.g., "Lead Singer" focus position)
- **Size:** Scales the movement radius from 0 (static at center) to 100% (full sweep range)
- **Fader mapping:** On busking layouts, movement size is typically mapped to a fader for real-time control

## Phase Offset and Fixture Coordination

Phase offset distributes identical movement patterns across fixtures with staggered timing, creating coordinated visual effects.

### Phase Distribution Methods

| Method | Description | Visual Result |
|--------|-------------|---------------|
| **Sequential (Spread)** | Each fixture advances by 360°/N phase | "Wave" — fixtures trace the same path in sequence |
| **Synchronized** | All fixtures share the same phase | All fixtures move in unison |
| **Mirror** | Fixtures 1..N/2 mirror fixtures N/2+1..N | Symmetrical movement, left mirrors right |
| **Random** | Random phase per fixture | Organic, chaotic movement |
| **Grouped** | Groups of G fixtures share phases (e.g., pairs, triplets) | Sub-group choreography |

### Wings and Fanning

Wings determine how the phase distribution is ordered across the fixture selection:

| Wings Value | Description |
|-------------|-------------|
| **0 (No Wings / Spread)** | Sequential from first to last selected fixture |
| **2 (Mirror / Two Wings)** | Two mirrored halves: fixtures 1→N/2 spread left half, N/2+1→N mirror right half |
| **4 (Quad)** | Four quadrants mirrored. Even/odd selections produce complementary patterns |

## Fan / Spread Distributions (Non-Movement)

"Fan" or "Spread" also applies to non-movement attributes — distributing values across a fixture range rather than applying the same value to all:

| Fan Type | Behavior |
|----------|----------|
| **Pan/Tilt Fan** | First selected fixture pans left, last pans right. Middle fixtures interpolate. |
| **Even Fan** | Linear interpolation of values from first to last selected fixture |
| **Wing Fan** | Values spread from center outward symmetrically |
| **Block Fan** | Groups of adjacent fixtures receive the same value |

Fanning is distinct from phase-based movement: fan creates *static spread* (fixtures pointing different directions simultaneously), while phase creates *dynamic stagger* (fixtures tracing the same path at different times).

## Selection Order Significance

Fixture selection order is critical in professional programming. The order in which fixtures are selected determines:

1. **Chase/effect step order:** First selected = step 1, last selected = step N
2. **Phase distribution:** First selected = phase 0°, last selected = phase ~360°
3. **Fan direction:** First selected = left/cold end, last selected = right/hot end
4. **Layout grid mapping:** Row/column assignment for pixel effects

Modern consoles provide "Selection Order" editors (e.g., MA3's Layout view) to reorder fixtures logically without re-patching. Grid layouts decouple physical DMX addressing from visual sequencing.

## 16-Bit Resolution and Movement Smoothness

Pan and tilt are the attributes that most benefit from 16-bit resolution:

- **8-bit (coarse only):** 256 steps across 540° pan range = 2.1° per step. Visible stepping at slow speeds and long throws.
- **16-bit (coarse + fine):** 65,536 steps across 540° pan range = 0.008° per step. Smooth at all speeds.

The renderer must write both coarse (MSB) and fine (LSB) channels for 16-bit attributes when the fixture mode includes them. The combined value is:
```
16bit_value = (coarse << 8) | fine    # range 0–65535
dmx_coarse = (16bit_value >> 8) & 0xFF
dmx_fine = 16bit_value & 0xFF
```

## Implications for RayFlow

1. **Movement primitives as data:** Geometric patterns (circle, line, figure-8, etc.) can be authored as named movement styles and rendered to pan/tilt DMX values at cue time.
2. **Phase-aware fixture rendering:** The renderer needs awareness of fixture selection order and grouping to correctly map phase offsets to individual fixtures.
3. **Size as a fader parameter:** Movement size should be an animated parameter, distinct from position, that scales the oscillation amplitude. This enables busking-style control from RayFlow's authoring.
4. **Fan as a static distribution:** Fan/spread values for non-movement attributes (focus, zoom, color) should be supported as static distributions across fixture groups, not just uniform values.
5. **Selection order persistence:** The rig model should preserve selection order and logical grouping (grids, zones, subgroups) as metadata to inform phase distribution calculations.
