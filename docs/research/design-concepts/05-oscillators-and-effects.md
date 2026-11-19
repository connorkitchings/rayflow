# Mathematical Oscillators and Effect Primitives

**Source:** Web research (ETC Eos effect engine documentation, console programming guides)
**Parsed:** 2026-05-25

## Effect Engine Architecture

Lighting console effect engines generate time-varying DMX values from mathematical oscillators. Every effect is defined by a waveform function, a set of parameters, and a fixture assignment list.

### Core Oscillator Types

| Type | Shape | Description | Use Case |
|------|-------|-------------|----------|
| **Sine** | Smooth wave, -1 to +1 | Continuous, organic oscillation. No sharp edges. | Fluid intensity chases, smooth pan/tilt movement, color fades |
| **Sawtooth** | Linear ramp up, instant drop (or reverse) | Directional motion with sharp reset. | Color wipes, linear sweeps, "runner" chases |
| **Triangle** | Linear ramp up and down | Symmetrical back-and-forth motion. | Bounce chases, symmetrical pan/tilt |
| **Square** | Binary high/low states | Abrupt on/off switching. | Strobe effects, step-based chases, hard cuts |
| **Random/Step** | Arbitrary values at irregular intervals | Unpredictable variation. | Flicker, twinkle, chaotic movement |
| **PWM** | Variable-width square wave | Duty-cycle control of on/off ratio. | Mechanical wipes, synchronized dimmer/movement |

## Effect Parameters

All effects share a common parameter model regardless of waveform type:

| Parameter | Description | Typical Range |
|-----------|-------------|---------------|
| **Rate / Speed** | Cycles per second (Hz) or beats per minute (BPM) | 0.01–50 Hz |
| **Size / Amplitude** | Magnitude of oscillation around center point | 0–100% of parameter range |
| **Offset / Phase** | Starting point within waveform cycle | 0–360° (degrees) |
| **Cycle Time** | Duration of one complete waveform cycle | 0.1–999 seconds |
| **Grouping** | Number of fixtures sharing the same phase offset | 1–N (fixture count) |
| **Wings** | Fan spread: 0 = sequential, 2 = mirror, 4 = quad | 0, 2, 4 |

## How Oscillators Map to DMX Values

An oscillator output of -1.0 to +1.0 is remapped to DMX 0–255 through the following transformation:

```
DMX_value = base_level + (oscillator_output * size * parameter_range)
```

- **Base level:** The fixture's current programmed value (e.g., dimmer at 50%)
- **Size:** Scales the oscillation amplitude (0–100%)
- **Parameter range:** Full DMX range if relative, absolute value range if absolute

For a sine wave dimmer chase with base=128, size=50%:
- Peak: 128 + (1.0 * 0.50 * 255) = 255 (100%)
- Trough: 128 + (-1.0 * 0.50 * 255) = 0 (0%)

## Step-Based vs. Continuous Effects

### Step-Based Effects
- Discrete steps applied sequentially across fixtures
- Each step has an On State and Off State
- Build: previously triggered steps stay on as sequence progresses
- Bounce: sequence runs forward then backward, repeating
- Stop and Hold: freezes at final step instead of looping

### Linear (Continuous) Effects
- Mathematical waveform applied continuously to all fixtures
- Smooth transitions between values
- Mirror In/Out: waveform origin starts at center or edges of fixture group
- Random Group/Rate: stochastic variation within defined bounds

## Effect Families by Attribute

| Attribute | Common Effect Types |
|-----------|-------------------|
| **Dimmer** | Chase (step-based), sine wave intensity pulse, random flicker, PWM mechanical wipe |
| **Color** | Absolute color chase (rainbow), color wipe (left→right, center→out), color pulse |
| **Position** | Circle (sine pan + cosine tilt), figure-8 (sine pan, 2× sine tilt), line sweep, random walk |
| **Beam** | Zoom pulse, iris open/close cycle, gobo rotation speed oscillation |
| **Strobe** | Rate oscillation, duty-cycle sweep, random flash pattern |

## Chase Distribution Patterns

How effects are distributed across a fixture selection determines the visual result:

| Pattern | Description |
|---------|-------------|
| **Sequential (1→N)** | Fixtures cycle in order: fixture 1 peaks, then 2, then 3... |
| **Center Out** | Fixtures at center of selection peak first, radiating outward |
| **Outside In** | Edges peak first, converging to center |
| **Mirror (Wings=2)** | Left half mirrors right half symmetrically |
| **Random** | Each fixture assigned a random phase offset |

## Phase Offset Mathematics

Phase offset distributes N fixtures evenly across a 360° cycle:

```
phase_per_fixture = 360° / (fixture_count / grouping)
fixture_phase(i) = (i / grouping) * phase_per_fixture + global_offset
```

With grouping=2 (pairs share phases), 8 fixtures produce 4 distinct phases: 0°, 90°, 180°, 270°.

## BPM Synchronization

Effects with Rate set to BPM mode convert musical tempo to cycle frequency:

```
cycles_per_second = BPM / (60 * beats_per_cycle)
```

A chase set to 120 BPM with 4 beats per cycle produces one full oscillation every 2 seconds (0.5 Hz). Tap-tempo and audio beat detection allow live synchronization.

## Implications for RayFlow

1. **Effect primitives as reusable data objects:** Each effect type can be modeled as a waveform + parameter set, then rendered to per-fixture DMX values.
2. **Fixture-aware phase distribution:** Phase offsets must respect fixture selection order and grouping, which requires integration with the rig model.
3. **Render-time resolution:** Effects must be sampled at render time (e.g., at cue start + elapsed time) to produce concrete DMX frames.
4. **BPM-to-frequency conversion:** Support for musical tempo mapping in the authoring pipeline enables tempo-synchronized cue effects.
5. **Attribute safety:** Not all fixtures support all effect families. The renderer must warn or degrade gracefully when a fixture lacks a channel for an effect attribute.
