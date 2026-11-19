# Console Comparison: Terminology, Philosophy, and Feature Mapping

**Source:** Console manuals, web research, cross-training guides
**Parsed:** 2026-05-25

## Why Console Differences Matter

RayFlow aspires to be console-agnostic, but every console represents lighting concepts differently. A "cue" on ETC Eos behaves differently than a "cue" on grandMA3. An "effect" on Chamsys has a different parameter model than an "effect" on Avolites. Understanding these differences enables RayFlow to author in abstract terms while generating correct exports for each target console.

## The Big Four

| Console | Market | Primary Users | Programming Philosophy |
|---------|--------|--------------|----------------------|
| **grandMA3** | Concerts, tours, festivals, TV | Professional LDs, touring programmers | Object-oriented: fixtures, sequences, executors, recipes. Highly customizable. Network-native. |
| **ETC Eos** | Theater, opera, dance, education | Theatrical LDs, resident designers | Cue-list-centric with tracking. Precise numeric control. Magic sheets for custom layouts. |
| **Chamsys MagicQ** | Clubs, small-medium tours, budget productions | Club LDs, rental houses, students | Cost-effective. Strong pixel mapping. Execute window for busking. Free software with cheap hardware. |
| **Avolites Titan** | Clubs, festivals, busking-heavy shows | Busking specialists, festival LDs | Playback-focused. Palettes as foundational objects. Key frame shapes for movement. Visual, hands-on. |

## Terminology Translation Table

RayFlow uses its own attribute family model. Here's how each console names the same things:

| RayFlow Term | grandMA3 | ETC Eos | Chamsys MagicQ | Avolites Titan |
|-------------|----------|---------|----------------|----------------|
| Cue | Cue | Cue | Cue | Cue |
| Cue List | Sequence | Cue List | Cue Stack | Cuelist |
| Fixture | Fixture | Channel | Fixture (or Head) | Fixture |
| Preset | Preset | Palette | Palette | Palette |
| Rig | Patch & Stage View | Patch & Augment3d | Patch & Visualiser | Patch & Visualiser |
| Universe | Universe | Universe | Universe | Universe (or Line) |
| Executor Fader | Executor (Fader) | Submaster / Fader | Playback | Playback |
| Attribute Family | Feature / Preset Type | Category / Attribute | Attribute Group | Attribute Group / Palette Type |

## Tracking Philosophy

| Console | Tracking | Notes |
|---------|----------|-------|
| **ETC Eos** | Default (tracking mode) | Tracking-forward through the cue list. Cue-Only mode available per recording. Deepest tracking model. |
| **grandMA3** | Default (tracking mode) | Tracking with recipe system. Recipes replace absolute cues with abstract rules (which groups, which presets). |
| **Chamsys MagicQ** | Tracking mode available | Tracking with "Block" cues. Simpler model than Eos. |
| **Avolites Titan** | No tracking | Each cue is independent. No values carry forward. File sizes are larger, but cues are self-contained and simple to edit. |

## Cue Construction

| Capability | grandMA3 | ETC Eos | Chamsys | Avolites Titan |
|-----------|----------|---------|---------|---------------|
| Part Cues | Yes (per-attribute part timing) | Yes (Parts) | Limited | Via Key Frame Shapes |
| Mark Cues / MIB | Auto-Mark, selective MIB per fixture | Mark flags, Auto-Mark | Basic mark | Manual only |
| Multi-part fade | Yes (individual fade per attribute) | Yes (discrete timing per part) | Limited | Via Shapes + timing |
| Crossfade types | HTP/LTP/Off/On override | X-fade (HTP), Y-fade (LTP) | HTP/LTP priority | HTP/LTP |
| Delay per attribute | Yes | Yes (per part) | Limited | Via Shapes |
| Follow/Wait/Halt | Yes | Yes | Yes | Yes |
| Macros in cues | Yes (Command field) | Yes (Macro field) | Yes | Via Legend/Action |

## Effect Engines

| Capability | grandMA3 | ETC Eos | Chamsys | Avolites Titan |
|-----------|----------|---------|---------|---------------|
| Effect types | Form-based (sine, PWM, random, chase, etc.) | Step-based + Linear (absolute or relative) | Shape-based (sine, sawtooth, square, random) | Key Frame Shapes + Pixel Mapper |
| Phase control | Spread, Wing, Groups, Blocks | Offset, Mirror In/Out, Grouping | Phase, Spread, Fan | Phase (via Shape) + Waveform |
| Effect engine scope | Global (can affect any attribute) | Per-attribute effect categories | Per-attribute shapes | Per-attribute key frames |
| BPM sync | Yes (global speed masters) | Yes (global rate) | Yes (tap tempo) | Yes (BPM master) |
| Bounce / reverse | Direction control on forms | Bounce softkey (step effects) | Reverse flag | Via key frame ordering |
| Randomization | Random rate, random group | Random group, random rate | Random phase | Via key frame randomization |

## Palette / Preset Systems

| Capability | grandMA3 | ETC Eos | Chamsys | Avolites Titan |
|-----------|----------|---------|---------|---------------|
| Global presets | Yes (Universal preset) | Yes (Global palette) | Yes (Global palette) | Yes (Shared palette) |
| Selective presets | Yes (Selective preset) | Yes (By Type palette) | Yes (by fixture type) | Yes (per-fixture palette) |
| Preset update propagation | Automatic (all referencing cues update) | Automatic | Automatic | Not automatic (re-record referencing cues manually) |
| Nested presets | Yes (preset referencing another preset) | Yes (palette referencing palette) | No | No |
| Preset scoping | Universal, Global, Selective | Global, By Type, Single-Fixture type palette hierarchy | Global, Per-type | Shared, Normal |

## Show File Architecture

| Capability | grandMA3 | ETC Eos | Chamsys | Avolites Titan |
|-----------|----------|---------|---------|---------------|
| Show file format | Compressed XML (.show.gz) | Proprietary (.esf) | Compressed XML (.shw) | Proprietary |
| Partial show import | Yes (patch, groups, presets, sequences individually) | Yes (partial show merge) | Partial import | Partial import |
| Multi-user | Yes (network sessions, user tracking) | Yes (multi-console, partitioned) | Limited (network session) | Limited |
| User profiles | Yes (user roles, views, permissions) | Yes (user profiles, partitioned) | Basic user levels | Basic user levels |

## Implications for RayFlow

1. **Console-agnostic authoring with console-specific export:** RayFlow's `Cue`, `Preset`, and `Rig` models should remain console-agnostic. Export adapters (similar to the existing MA3 OSC adapter) translate RayFlow's model into each console's vocabulary.
2. **Tracking vs. cue-only as a show setting:** The `Show` model should support a `tracking_mode: bool` flag. For Eos/MA3 export, use tracking. For Avolites export, auto-expand all cues to be self-contained (flatten tracking).
3. **Effect export is the hardest problem:** Every console has a fundamentally different effect engine. Exporting a RayFlow-described chase may require different representations for each target: MA3 forms, Eos effects, Avolites key frame shapes, Chamsys shapes.
4. **Palette translation:** RayFlow's attribute-family model (dimmer, position, color, beam, focus, gobo) maps cleanly to all four consoles' preset/palette systems. The mapping should be one-to-one.
5. **Prioritize MA3 for concert, Eos for theater:** If the `performance_type` is "concert," generate MA3-optimized exports. If "theater," generate Eos-optimized exports. Don't try to be equally good at all formats simultaneously.
6. **Part cues as the universal multi-timing primitive:** All four consoles support part cues (or equivalents). This is the cleanest abstraction for multi-attribute timing.
