# Virtual Show Development — Andrew Goedde and the Offline-First Pipeline

**Source:** Industry knowledge, LD workflows, pre-viz and console offline editor practices
**Parsed:** 2026-05-26

## The Offline-First Approach

Andrew Goedde (Goose) represents the modern jam band LD who pre-builds substantial portions of the show virtually before stepping into a venue. His approach mirrors what RayFlow aims to enable: develop the show on a computer, iterate rapidly without real fixtures, and arrive at load-in with a mostly-finished product.

This is the same pattern used by many touring LDs today, adapted for the improvisational jam band context:

```
     OFFLINE DEVELOPMENT                    LIVE EXECUTION
─────────────────────────────────┬─────────────────────────────
                                 │
  Pre-Viz / Console Offline      │     Console + Real Rig
  ┌─────────────────────┐        │    ┌──────────────────┐
  │ Build rig in pre-viz │        │    │ Load show file   │
  │ Build palettes       │───────▶│    │ Tweak for room   │
  │ Program cue stacks   │        │    │ Busk the jams    │
  │ Build effects        │        │    │ Ride speed master│
  │ Render & critique    │        │    │ Live iteration   │
  └─────────────────────┘        │    └──────────────────┘
                                 │
  Time: Days to weeks            │    Time: Soundcheck + show
  Latency: Sub-second            │    Latency: Real-time
  Risk: None (just a file)       │    Risk: Real audience
```

## The Technical Stack

A modern LD's virtual development stack typically includes:

### Console Offline Editor (Primary Programming Tool)
The same software that runs on the physical console, but on a laptop:
- **grandMA3 onPC:** Full-featured. Runs on macOS/Windows. Connect to pre-viz, build entire show file. The exact same show file loads onto a physical MA3 console.
- **ETC Eos Nomad:** Eos console software on laptop. Connect to Augment3d for built-in pre-viz.
- **Chamsys MagicQ:** Free on PC/Mac. Connect to built-in visualizer or external pre-viz.

### Pre-Visualization Software (Visual Feedback)
Connected to the offline editor via Art-Net or session link:
- **Capture:** Industry standard for concert touring. Fast, excellent fixture library. One-click connection to MA3/MA2 onPC.
- **Depence²:** High-end, photorealistic. Used for large productions and broadcast pre-viz.
- **L8:** Strong MA3 integration. Fast workflow.
- **grandMA3 3D:** Free, built-in. Limited but functional. Good enough for palette and position programming.
- **Vectorworks Vision:** Theatrical focus. Integrates with Spotlight for plot drafting.

### Workflow: Console Offline + Pre-Viz

```
1. Launch MA3 onPC (or other console offline editor)
2. Launch Capture (or other pre-viz)
3. Connect: MA3 onPC → Art-Net → Capture (same machine, loopback IP)
4. Patch fixtures in MA3 onPC
5. Build pre-viz rig in Capture (match fixture types and positions)
6. Program on MA3 onPC → See result in Capture in real time
7. Save show file
8. Load show file onto physical MA3 console at venue
9. Connect console to real rig → tweak focus, color balance → showtime
```

The show file that leaves the laptop is the same file loaded into the console. The transition from virtual to real is seamless — same software, same show file, same programming. Only the DMX output destination changes (from pre-viz software to real fixtures).

## What Gets Built Offline vs. On-Site

### Built Offline (Days/Weeks Before)

| Component | Why Offline | Time Investment |
|-----------|------------|----------------|
| Fixture patch | Venue-independent. Can be adjusted later. | 1–2 hours |
| Position presets (40+) | Generic stage positions work in any venue. Adjust focus on-site. | 3–6 hours |
| Color presets (50+) | Fixture-dependent, not venue-dependent. | 2–4 hours |
| Beam/gobo presets (25+) | Fixture-dependent. | 1–2 hours |
| Dimmer presets | Universal. | 30 min |
| Effect templates (chases, movements, color sweeps) | Complex, time-consuming. Better built offline with pre-viz feedback. | 4–8 hours |
| Busking layout design | Fader assignments, sequence structures. Purely console programming. | 4–8 hours |
| Song-specific cue stacks (for known song structures) | Pre-programmed looks for composed sections. | 2–4 hours per song |
| Group definitions | Fixture grouping by function. Venue-independent. | 1 hour |
| Speed master hierarchy | Purely console programming. | 30 min |
| **Total offline investment** | | **20–35 hours** |

### Built On-Site (Soundcheck / Day of Show)

| Component | Why On-Site | Time Investment |
|-----------|------------|----------------|
| Focus position presets to actual stage | Real positions differ from virtual. | 1–2 hours |
| Color balance to real fixtures | Pre-viz color accuracy is ~80%. Fine-tune on real rig. | 30 min |
| Trim height adjustments | Real venue trim may differ from planned. | 15 min |
| Haze level calibration | Room-dependent. | 15 min |
| Camera/IMAG adjustments (if applicable) | Real camera response differs from pre-viz. | 30 min |
| **Total on-site investment** | | **2–3.5 hours** |

The ratio is striking: ~90% of programming time happens offline. The venue visit is calibration, not creation.

## Why This Matters for RayFlow

RayFlow's role in this pipeline is to accelerate the offline phase. Where an LD currently spends 20–35 hours manually building palettes, effects, and cue stacks in the console offline editor, RayFlow's AI authoring could:

1. **Auto-generate the palette library** — 100+ presets across position, color, beam, dimmer, and effects from a vibe description and fixture list.
2. **Auto-generate busking sequences** — Fader-ready cue stacks with appropriate structure for each fixture group.
3. **Auto-generate effects** — BPM-linked chases, movements, and color sweeps with rideable parameters.
4. **Export to console format** — The generated show file imports directly into the console offline editor, where the LD can validate in pre-viz and refine.

RayFlow doesn't replace the console or pre-viz — it *feeds* them. The LD starts from a RayFlow-generated foundation instead of a blank show file.

## The Jam Band Adaptation

For improvisational acts like Goose, the offline development has a different character than for timecoded pop shows:

| Component | Timecoded Pop Show | Improvisational Jam Show |
|-----------|-------------------|------------------------|
| Cue stacks | Fully programmed, frame-accurate to timecode | Partial — composed sections only. Jam sections are busking. |
| Palette library | Show-specific (150 songs = 150 unique palettes) | Universal (palettes serve all songs through combination) |
| Effects | Song-specific, timecode-locked | Generic, BPM-linked, rideable via faders |
| Pre-viz role | Verify every cue against timecode | Verify palette combinations and effect behavior. Actual show content is improvised. |

For Goose, Goedde's offline work likely focuses on:
- **Building a massive palette library** — enough position, color, and beam presets that any song can be lit through combination.
- **Building effect templates** — chases, movements, and color sweeps that can be triggered and modified in real time.
- **Building busking infrastructure** — the fader layout, sequence structures, and speed master hierarchy.
- **Song-specific cue stacks for known structural moments** — intros, composed sections, planned transitions.

The actual show is a live performance on top of this infrastructure. The infrastructure is built offline; the performance is real-time.

## The RayFlow Pipeline (Proposed)

```
RayFlow (authoring)

    │  User describes: "Goose-inspired club rig, warm psychedelic vibe,
    │  song has verse/chorus/bridge/jam structure"
    │
    ▼
RayFlow generates:
    ├── Rig YAML (fixture selection, placement, addressing)
    ├── MVR file (for pre-viz import)
    ├── Palette library (100+ presets)
    ├── Busking sequences (10 faders × 5–30 cues)
    ├── Effect templates (dimmer chases, movements, color sweeps)
    ├── Song-specific cue stacks (composed sections)
    └── Speed master hierarchy

       │
       ▼
Import into console offline editor (MA3 onPC, Eos Nomad)
    │
    ├── Validate in pre-viz (Capture, Depence², MA3 3D)
    ├── Iterate: tweak, refine, re-render from RayFlow
    │
    ▼
Load onto physical console at venue
    │
    ├── Calibrate focus and color to real rig
    └── Showtime: busk the jams on RayFlow-built infrastructure
```

## Implications for RayFlow

1. **Console show file export is the critical bridge.** RayFlow must produce files that import cleanly into console offline editors. For MA3, this means a `.show.gz` file (or OSC commands that build the show programmatically). For Eos, an `.esf` file. This is harder than MVR export but is the single most valuable integration point.

2. **The palette generator is the highest-value feature.** A good palette library is the foundation of both busking and timecoded shows. If RayFlow can auto-generate a solid, well-organized palette library from a vibe description and fixture list, it saves the LD 10–15 hours.

3. **Pre-viz integration is secondary to console integration.** The LD already has pre-viz. They don't need RayFlow to be a pre-viz tool. They need RayFlow to generate the show file that they can validate in their existing pre-viz.

4. **The round-trip workflow matters.** The LD should be able to: generate in RayFlow → validate in pre-viz → identify issues → refine in RayFlow → re-export → validate again. Fast round-trips make the tool useful.

5. **Offline-first design.** RayFlow should optimize for the offline phase because that's where the time is spent. On-site features (live busking assistance, real-time BPM tracking) are valuable but secondary to powerful offline authoring.
