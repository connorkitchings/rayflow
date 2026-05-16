# Two-Layer Design

This document describes RayFlow's two-layer architecture in detail.

## The Two Layers

### Layer 1: grandMA3 onPC (Console Layer)

grandMA3 onPC is the industry-standard lighting control software, available free for macOS. It provides:

- **Console Engine:** Cue lists, sequences, effects, executors, programmer
- **Built-in 3D Visualizer:** Preview your show with 3D rendered fixtures
- **Video Recording:** Capture visualizer output for export
- **GDTF/MVR Support:** Native support for open fixture and stage formats
- **OSC API:** Remote control via Open Sound Control protocol

This layer is the "source of truth" for lighting state. It handles all DMX processing, cue playback, and visual rendering.

### Layer 2: RayFlow (Tooling Layer)

RayFlow sits on top of grandMA3 onPC and provides tooling that makes programming faster, learning easier, and automation possible:

- **GDTF Fixture Library:** Download, parse, and manage fixture profiles
- **Stage Builder:** Create virtual rigs programmatically, export as MVR
- **Art-Net/sACN Bridge:** Send and receive DMX from Python
- **OSC Controller:** Automate console operations (store cues, trigger sequences)
- **AI Cue Generator:** Generate lighting cues from natural language descriptions

## How the Layers Communicate

```
┌─────────────────────────────────────────────────────┐
│                   RayFlow Layer                      │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ GDTF     │  │ AI Cue   │  │ Stage Builder    │   │
│  │ Library  │  │ Generator│  │ (MVR export)     │   │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘   │
│       │              │                 │             │
│       ▼              ▼                 ▼             │
│  ┌──────────────────────────────────────────────┐   │
│  │         Protocol Bridge                       │   │
│  │  Art-Net  │  sACN  │  OSC  │  MVR/GDTF       │   │
│  └────────────────────┬─────────────────────────┘   │
└───────────────────────┼─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│                grandMA3 onPC Layer                   │
│                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Console  │  │ 3D       │  │ Video            │   │
│  │ Engine   │  │ Visualizer│ │ Recording        │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Communication Channels

| Channel | Protocol | Direction | Purpose |
|---------|----------|-----------|---------|
| DMX | Art-Net (UDP 6454) | Bidirectional | Send/receive fixture values |
| DMX | sACN (multicast UDP) | Bidirectional | Alternative DMX transport |
| Commands | OSC (port 8000) | RayFlow → MA3 | Console automation |
| Stage | MVR file | RayFlow → MA3 | Import virtual rig |
| Fixtures | GDTF file | External → RayFlow | Fixture definitions |

## Where RayFlow Adds Value

RayFlow is not a replacement for grandMA3. It enhances the console experience:

1. **Faster Learning:** AI-generated cues give you a starting point to learn from, not just a blank console
2. **Automation:** Batch operations (patch 20 fixtures, store 10 cues) that would be tedious on the console
3. **Fixture Management:** Organize, search, and manage GDTF fixtures outside the console
4. **Stage Building:** Create rigs programmatically, export to MA3 for visualization
5. **Future Live Support:** Art-Net output to real DMX hardware for live shows

## Why Not Build a Custom Visualizer?

grandMA3 onPC already includes a capable 3D visualizer. Building a custom visualizer would:

- Duplicate existing functionality
- Require significant Three.js/WebGL development
- Need to parse GDTF geometry independently
- Not match MA3's rendering quality

The web visualizer (Phase 5) is optional and would serve as an independent testing target, not a replacement for MA3's built-in viz.

## Future: Live Show Support

The architecture naturally extends to live shows:

- Art-Net/sACN output can drive real DMX hardware
- RayFlow's cue generation can prepare shows for live programming
- The fixture library works the same for virtual and physical rigs
- OSC control works with physical grandMA3 consoles

The primary difference is the output layer: instead of MA3's visualizer, DMX goes to physical fixtures via a DMX interface.
