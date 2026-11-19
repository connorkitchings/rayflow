# Dimmer Curve Physics and Perceptual Response

**Source:** Web research, industry standards, perceptual psychology literature
**Parsed:** 2026-05-25

## Why Dimmer Curves Exist

DMX transmits linear 8-bit values (0–255), but neither the human eye, camera sensors, nor light sources respond linearly. A "50% DMX value" (128) does not look like "half as bright" to a human observer. Dimmer curves remap linear DMX input to perceptual brightness, ensuring smooth, natural-looking fades.

## The Perception Problem: Stevens' Power Law

Human brightness perception follows Stevens' power law:

```
Perceived Brightness ∝ (Physical Luminance)^n
```

Where n ≈ 0.33–0.5 for point sources under typical viewing conditions. This means:
- A light at 50% physical luminance appears ~70–80% as bright as full
- A light at 10% physical luminance appears ~30–40% as bright
- DMX value 128 driving a linear LED appears much brighter than "half"

## Common Dimmer Curve Types

### Linear (1:1)
```
DMX_out = DMX_in
```
- **Effect:** Raw DMX value maps directly to light output.
- **Result:** Perceived as "jumpy" at low intensities. Most intensity change happens visually between 0–50 DMX.
- **Use:** Never for theatrical dimming; sometimes for non-intensity parameters (pan/tilt, zoom).

### Square Law (x²)
```
DMX_out = (DMX_in²) / 255
```
- **Effect:** Compresses low values, expands high values.
- **Result:** More steps at the bottom end where the eye is most sensitive. Standard for tungsten emulation.
- **Use:** Concert lighting, front light, any situation needing smooth fades to black.

### Inverse Square Law (√x)
```
DMX_out = √(DMX_in / 255) * 255
```
- **Effect:** Expands low values, compresses high values.
- **Result:** Quick jump to visible brightness, then gradual taper at top. Feels "punchy."
- **Use:** LED fixtures that are too bright at low levels, strobes, effects lights.

### S-Curve / Television
- **Effect:** Gentle rise at bottom and top, steeper in middle.
- **Result:** Mimics broadcast camera gamma curves. Prevents LED flicker on camera.
- **Use:** Broadcast, IMAG (Image Magnification), any venue with cameras.

### Custom / Breakpoint
- **Effect:** User-defined table of input→output mappings with linear interpolation.
- **Result:** Precise control for fixture-specific behavior.
- **Use:** Correcting individual fixture anomalies, matching disparate fixture types in the same rig.

## Physics of Different Light Sources

### Tungsten / Halogen
- **Response:** Thermal. Filament heats and cools with hysteresis (lag).
- **Color shift:** As voltage drops, filament cools and color shifts from white → amber → orange → red → off (~3200K to ~1800K).
- **Benefits:** Natural, organic fade-to-black. The amber shift is aesthetically pleasing and masks the visual jump at low levels.
- **Curve:** Typically square law to match eye response, with the thermal lag providing additional smoothing.
- **DMX Reality:** At DMX 1 (0.4%), a tungsten lamp glows visibly amber. This "pre-heat" region is musically useful.

### LED
- **Response:** Electronic. Instant on/off with no thermal lag.
- **Color shift:** Typically none — LED color temperature stays constant across the dimming range, unless the fixture actively emulates tungsten shift.
- **Problems:**
  - **Stepping:** At low DMX values (1–5), the discrete 255-step resolution becomes visible as abrupt jumps, especially in dark scenes.
  - **Flicker:** Low-frequency PWM (pulse-width modulation) interacts with camera shutter speeds, producing visible banding.
  - **Abrupt cutoff:** Many LEDs snap off entirely below DMX 3–5 rather than fading smoothly.
- **Curve:** Inverse square law or custom curve to compensate for excess low-end brightness. High PWM frequency (≥1200 Hz) for camera safety.
- **DMX Reality:** A DMX value of 1 on an LED may already be uncomfortably bright. Some fixtures require DMX ≥ 8 before any visible output, then jump abruptly.

### Arc / Discharge (HMI, Xenon)
- **Response:** Not continuously dimmable. Mechanical dimming via dowser/shutter.
- **Curve:** N/A for electrical dimming. Mechanical dowsers have their own response characteristics.

## Dimming Curve Implementation in Consoles

### grandMA3
- Provides per-fixture or per-channel curve selection: Linear, Square, Inverse Square, S-Curve, and slot for custom curves.
- Curves are applied in the patch, so every cue using that fixture inherits the curve.
- Custom curves are edited graphically in the Curve Editor with draggable control points.

### ETC Eos
- Offers a library of standard curves plus a Curve Editor.
- Curves can be applied at the dimmer level (in patch) or at the cue level via intensity master curves.
- "Curve" is a discrete data object that can be copied between show files.

## Implications for RayFlow

1. **Curve-aware rendering:** The renderer should accept a curve specification per fixture channel and apply it when resolving cue intent to DMX frames.
2. **Per-fixture curve storage:** The rig model should store curve assignments at the fixture-slot level, referencing a library of named curves.
3. **Perceptual fade generation:** When generating fade times for cues, the authoring system should account for the fact that a 2-second fade on a square-law curve looks very different from a 2-second fade on linear.
4. **Cross-fixture consistency:** When multiple fixture types (tungsten, LED, arc) share the rig, dimmer values should be authored in perceptual units (0–100%) and converted to DMX values through each fixture's curve.
5. **Camera-safe output:** For broadcast-oriented shows, the renderer should warn if PWM-sensitive fixtures are driven at values likely to cause camera flicker (low intensity + low PWM frequency).
