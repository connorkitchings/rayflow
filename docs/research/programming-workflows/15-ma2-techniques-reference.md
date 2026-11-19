# MA2 Techniques — YouTube Reference Index

**Source:** YouTube — Christian Jackson / "Learn Stage Lighting .com" channel
**Total:** 14 videos (13 with captions, 1 without)
**Raw transcripts:** `docs/research/raw_sources/ma2-techniques/`
**Parsed:** 2026-05-26

---

## Episode Index

| # | Title | Captions | Topic |
|---|-------|----------|-------|
| — | MA2 onPC Quick Start Guide | ✅ | Complete MA2 onPC setup walkthrough |
| — | MA2 Effects Engine Basics | ✅ | Building effects from scratch — waveforms, parameters, phase |
| — | My Custom MA2 Lighting Setup | ✅ | Creator's personal MA2 configuration and workflow |
| — | Recording Movement Looks as Positions | ✅ | Capturing effect snapshots as static position presets |
| — | REAPER + MA2 — Timecode Made Easy | ✅ | DAW timecode integration for synchronized playback |
| — | MA2 Color Effect Generator Tutorial | ✅ | Building color chase effects |
| — | Connecting MA3D to MA2 onPC | ✅ | Visualizer connection and configuration |
| — | MA2 Layout View — Toggle Buttons | ✅ | Building toggle-button busking layouts |
| — | Top 5 MA2 Programming Tricks | ✅ | Workflow efficiency techniques |
| — | Art-Net Output from MA2 | ❌ No captions | Network DMX output configuration |
| — | Connect Capture to Any GrandMA2 | ✅ | Full Capture visualizer integration |
| — | Import Capture Fixtures into MA2 | ✅ | Fixture import workflow from pre-viz to console |
| — | Custom Tap-to-BPM Button | ✅ | Building a physical/soft button for live tempo sync |
| — | MA2 Startup Macros | ✅ | Automating show file initialization |

---

## Key Techniques by Category

### Setup & Configuration
- **MA2 onPC Quick Start:** Installation, network setup, first patch, basic programming
- **Custom Setup:** Personal view layouts, screen configurations, default pools, workspace optimization
- **Startup Macros:** Automated initialization — load groups, presets, views, set defaults on each session start

### Effects & Programming
- **Effects Engine Basics:** Waveform selection, speed/size/phase parameters, group/wing/blocks distribution, creating chases and movement effects from scratch
- **Color Effect Generator:** Building color chases — step-based color sequencing, absolute effects, rainbow chases
- **Recording Movement as Positions:** Taking a snapshot of an active movement effect and storing it as a static position preset — useful for freezing a specific moment of a chase
- **Top 5 Programming Tricks:** Efficiency techniques — shortcuts, workflow patterns, time-saving approaches

### Visualizer Integration
- **MA3D Connection:** Network setup for MA2 onPC → MA3D visualizer
- **Capture Connection (Full):** Complete Capture integration — network, universe mapping, session connection
- **Import Capture Fixtures:** Importing pre-viz fixture layouts into MA2 — saves hours of manual patching and positioning

### Show Control
- **Timecode with REAPER:** Using a DAW as timecode source for MA2 — SMPTE/MTC generation, cue linking, synchronized playback
- **Tap-to-BPM Button:** Building a custom executor button that calculates BPM from taps and applies it to speed masters
- **Layout View Toggle Buttons:** Creating playable busking interfaces with toggle-state executors

---

## Key Insights for RayFlow

### 1. The Capture → MA2 Pipeline Mirrors RayFlow's Goal
The "Import Capture Fixtures into MA2" and "Connect Capture to Any GrandMA2" videos show the exact workflow RayFlow should enable:
- Build rig in pre-viz (Capture) → export fixture layout → import to console → patch → program
- RayFlow replaces Capture in this pipeline for rig generation, then feeds MA3 onPC

### 2. Startup Macros Are the AI's "Boot Sequence"
The "MA2 Startup Macros" concept directly maps to RayFlow's output: a series of commands that initialize the show file — load the right views, set defaults, position windows. RayFlow should generate startup macros that set up the console for the generated show.

### 3. Tap-to-BPM Is a Critical Live Performance Feature
The "Custom Tap-to-BPM Button" video shows how LDs create a dedicated tempo-tapping mechanism. For RayFlow's busking infrastructure, every generated show should include a tap-to-BPM executor linked to all speed masters.

### 4. Recording Movement as Positions Is a Busking Power Move
Freezing an active movement effect into a static position preset lets the LD capture a "perfect moment" mid-chase. This is exactly the kind of technique the AI should suggest to users: "Want to freeze this look? Record it as a position preset."

### 5. Layout View Toggle Buttons Are the Busking UI
Toggle-state executors in Layout View create a playable interface that doesn't rely on remembering fader assignments. This is a more visual, intuitive approach to busking that amateur users would find easier than traditional fader-based layouts.

### 6. Timecode via DAW Opens a Simple Recording Path
Using REAPER (or any DAW) as a timecode source means the user doesn't need expensive timecode hardware. For RayFlow's "record the show" terminal goal, timecode export via a free/cheap DAW is a practical path.

---

## Comparison to Existing MA Knowledge

| Concept | Already Covered? | New Detail |
|---------|-----------------|------------|
| MA2 effects engine | Partially (MA3 phaser tutorials) | MA2-specific effect construction workflow |
| Capture/MA3D integration | Partially (pre-viz doc, MA3 tutorial E17) | MA2-specific connection and import workflow |
| Timecode | ✅ (03-timecode-automation) | DAW-based timecode using REAPER — practical, cheap |
| Speed masters | ✅ (04-busking-layouts, 10-concert-effect-techniques) | Tap-to-BPM button implementation |
| Busking layouts | ✅ (04-busking-layouts, 09-busking-architecture) | Layout View toggle button approach |
| Macros | ✅ (MA3 tutorial E12-E13) | Startup macro concept for session initialization |
| Movement → position recording | Not covered | New technique — freezing effects as presets |

---

## Implications for RayFlow

1. **Startup macros should be generated with every show.** The AI should output a sequence of MA3 commands that initialize the console for the generated show file — load views, set defaults, position pools.

2. **Tap-to-BPM executor is a required element of busking infrastructure.** Every generated busking layout should include a dedicated tap-tempo executor linked to all speed masters.

3. **Capture import workflow validates the "generate → pre-viz → console" pipeline.** RayFlow should generate MVR files that import cleanly into Capture, and MA3 show files that consume that import seamlessly.

4. **Layout View is a more accessible busking interface for amateurs.** Toggle buttons on a visual layout are more intuitive than fader-based executors. RayFlow should generate Layout View configurations alongside traditional executor assignments.

5. **DAW timecode is a practical recording path for amateur users.** RayFlow's "record the show" feature could output a timecode track playable alongside the song in a free DAW.
