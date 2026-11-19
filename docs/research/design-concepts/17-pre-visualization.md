# Pre-Visualization Tools and Workflows

**Source:** Web research, manufacturer documentation, professional design workflows
**Parsed:** 2026-05-25

## What Pre-Viz Is

Pre-visualization (pre-viz) software renders a 3D simulation of a lighting rig in a virtual venue, showing what the lights will look like before any physical fixture is hung. It allows designers and programmers to build, focus, and cue a show entirely offline, then transfer the programming to the real console and rig.

Pre-viz closes the gap between "I think this will look good" and "I can see it looks good" — without the time, labor, and cost of hanging real fixtures.

## The Major Pre-Viz Platforms

| Platform | Type | Price | Best For |
|----------|------|-------|----------|
| **Capture** | Standalone pre-viz + console visualizer | $500–$4,000 (editions) | All-around. Fastest workflow for concert/touring. Excellent fixture library. |
| **Vectorworks Spotlight + Vision** | CAD + pre-viz combo | $2,000+/year subscription | Theatrical design. Draw the plot in Spotlight, visualize in Vision. Industry standard for theater drafting. |
| **WYSIWYG** | All-in-one: CAD, pre-viz, paperwork | $1,000–$5,000+ | Full production package. Paperwork generation (channel hookups, schedules). |
| **Depence²** | High-end pre-viz | $3,000+ | Photorealistic rendering. Water, pyro, and environmental effects. Large-scale productions. |
| **L8** | Mid-range pre-viz | $1,000–$2,000 | Strong MA3 integration. Media server pre-viz. Compact and fast. |
| **Unreal Engine (custom)** | Game-engine pre-viz | Free (engine) + development | Photorealistic with custom effort. Used for broadcast pre-viz and virtual production. |
| **grandMA3 3D** | Console-integrated | Free with MA3 onPC | Basic pre-viz. Directly connected to MA3 session. Limited fixture library. |
| **ETC Augment3d** | Console-integrated | Free with Eos | Integrated into Eos software. Good for theater scale. |

## Pre-Viz Workflow

### 1. Venue Modeling
Import or build the venue: stage dimensions, truss positions, seating, obstacles, reflective surfaces. Many platforms include venue templates or import from CAD (DWG, SketchUp).

### 2. Rig Building
Place fixtures at their planned positions. Patch them to DMX addresses (matching the real-world patch). Assign fixture types from the platform's library (or import GDTF files for fixtures not in the library).

### 3. Console Connection
Connect the pre-viz software to the lighting console via Art-Net or sACN. The console sends DMX data; the pre-viz software renders what the console is outputting. Common connections:
- **Art-Net loopback:** Both running on the same machine. Console outputs to 127.0.0.1, pre-viz receives.
- **Network:** Console and pre-viz on the same VLAN. Separate from show-critical networks.
- **Session link (MA3):** MA3 onPC and Capture/L8/Depence² join the same MA-Net3 session.

### 4. Programming
Program cues on the console as if in the real venue. The pre-viz window shows the result in real time with reasonable accuracy for intensity, color, beam angle, and gobo projection.

### 5. Export to Production
- **MVR export:** Export the rig from pre-viz as MVR. Import to the console for the real show.
- **Show file transfer:** The console show file programmed in pre-viz is the same file loaded on the real console. Only the patch may need updating for venue-specific addressing.
- **Paperwork generation:** WYSIWYG and Vectorworks generate light plots, channel hookups, instrument schedules, and patch sheets.

## Fidelity Limitations

Pre-viz is an approximation, not a simulation. Key differences from reality:

| Attribute | Pre-Viz Accuracy | Real-World Factor |
|-----------|-----------------|-------------------|
| **Intensity** | ~70–80% accurate | Real brightness depends on fixture age, lamp hours, lens cleanliness, voltage |
| **Beam visibility** | Approximate | No haze model captures real atmospheric behavior. Beams look sharper in pre-viz than reality. |
| **Color** | ~80–90% accurate on calibrated monitor | Monitor calibration, fixture color engine variance, gel fading |
| **Gobos** | Good for geometry, poor for subtle breakup | Pre-viz renders gobo outlines. Real gobo projection has edge softness, chromatic aberration, and heat shimmer |
| **Strobes** | Approximate | Real strobe persistence and camera interaction not modeled |
| **Haze density** | Single scalar | Real haze is non-uniform, affected by HVAC, and changes over time |
| **Ambient light** | Poor | Pre-viz assumes perfect darkness. Real venues have exit signs, backstage work lights, architectural spill |

Designers using pre-viz learn the "pre-viz discount": what you see on screen is 10–20% more dramatic than what you'll see in the room. Program accordingly.

## Connection to RayFlow

RayFlow's fixture-aware DMX renderer is a form of pre-viz — it resolves cue intent to concrete DMX frames. The key differences and opportunities:

| Capability | RayFlow Renderer | Full Pre-Viz |
|-----------|-----------------|-------------|
| DMX frame output | Yes | No (renders visually, doesn't expose raw DMX) |
| 3D visual output | No | Yes |
| Beam rendering | No (DMX only) | Yes (volumetric cone rendering) |
| Fixture-aware | Yes (GDTF channel maps) | Yes (GDTF + proprietary models) |
| Cue intent to output | Yes (authoring → renderer → DMX) | No (requires console to generate DMV values) |
| Batch/programmatic | Yes (CLI-based rendering) | Limited (most platforms are GUI-driven) |

RayFlow's renderer produces *provable DMX evidence* — concrete values you can verify with an Art-Net receiver. Pre-viz produces *visual approximation*. These are complementary: RayFlow proves the DMX is correct, pre-viz shows what it might look like.

### Integration Possibilities
- **MVR export for pre-viz import:** RayFlow already exports MVR. Import that MVR into Capture/Vision/WYSIWYG for visual preview.
- **Art-Net feed to pre-viz:** RayFlow's Art-Net backend could feed a pre-viz platform for real-time visual feedback during authoring.
- **Pre-viz as verification:** After RayFlow renders a cue, feed the DMX to pre-viz. Does it look right? If not, iterate on the cue intent.

## Implications for RayFlow

1. **MVR as the bridge format:** RayFlow's MVR export is the primary handoff to pre-viz platforms. The MVR should include fixture positions, GDTF references, and universe/address assignments — all of which the current exporter supports.
2. **Renderer + pre-viz feedback loop:** A future workflow could: author cue in RayFlow → render DMX frame → send to pre-viz via Art-Net → verify visually → iterate.
3. **Pre-viz discount awareness:** The authoring system should bake in a "pre-viz discount" factor when selecting intensity values — target values should be 10–20% higher than what looks right on a simulated screen.
4. **Don't compete, complement:** RayFlow should not try to build a visual pre-viz. Capture, Vectorworks, and Unreal do this better. Instead, RayFlow should produce the data they need (MVR, DMX, cue lists) and let the visual tools handle the pretty pictures.
