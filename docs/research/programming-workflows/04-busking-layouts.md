# Busking Layouts and Live Execution

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## The Ten-Playback Constraint

For live events where performances are unplanned or improvised (music festivals, DJ sets), designers rely on "busking" or "punting" layouts. The operator builds a modular layout to construct looks live to match the performance.

Under a strict "playbacks-only" constraint, programmers limit control to a single page of ten physical playback faders, disabling the virtual programmer during live playback.

### Grum Leesmith's Standard Festival Layout

| Fader | Function |
|---|---|
| 1 | Spots Intensity: dimmer on, random shutter, dimmer chase |
| 2 | Washes Intensity: dimmer on, random shutter, dimmer chase |
| 3 | Position Stack: preset looks with fixtures fanned in cohesive positions |
| 4 | Colour and Beam Stack: complementary colors and beam shapes/textures |
| 5 | Spot Movements: movement generator with fader mapped to control size |
| 6 | Wash Movements: movement generator with fader mapped to control size |
| 7 | Blinders Stack: All On, Chases, Odd/Even patterns |
| 8 | Strobe Stack: slow, medium, fast random strobes, blind mode |
| 9 | Dim Speed Master: scale speed of all active dimmer chases |
| 10 | Key Light: dedicated control for band/speaker key illumination |

### The Robe Demo Show "Multi-Fixture" Layout

| Fader | Function |
|---|---|
| 1 | Strobes: dedicated strobe control for spots, washes, LED array |
| 2 | PARs Wash (Base Looks): Left/Right split or solid color washes |
| 3 | PARs Wash (Base Looks): Left/Right split or solid color washes |
| 4 | Media & LED: pixel-mapped array intensities and chases |
| 5 | Moving Light Colors / Intensities: CMY color picker and wash dimmer |
| 6 | Moving Light Positions / Intensities: focus presets and wash dimmer |
| 7 | Moving Light Beams: GOBO selection and beam width |
| 8 | Moving Light Moves: pan/tilt movement sweeps and speed |
| 9 | Unallocated / Blinders: configurable master or audience blinder |
| 10 | Unallocated / Blinders: configurable master or audience blinder |

## Global Masters

Programmers configure global masters such as a **Speed Master** (or Rate Master). If a performer alters song tempo, pulling the Speed Master fader down physically compresses the cycle times of all active movements, color chases, and strobes simultaneously, aligning the entire rig with the new musical tempo in real time.
