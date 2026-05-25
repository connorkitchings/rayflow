# Project Charter

This document is the single source of truth for RayFlow's goals, scope, and technical context.

## Project Overview

**Project Name:** RayFlow

**Project Vision:** A tool that lets anyone design concert lighting for songs they love. The user provides taste and musical judgment; an AI assistant handles all technical execution — fixture selection, DMX addressing, console programming, and palette design. The user describes what they want in plain language and sees the result as they build, without ever needing to touch a lighting console.

**Terminal Goal:** Pick a song → collaborate with AI to develop a rig and lighting design → iteratively see and refine the result → record the finished show. Everything after design completion (live playback, console operation, performance use) is out of scope for the product.

## The Core Insight

Andrew Goedde (Goose's LD) spends 20–35 hours pre-building palettes, effects, and sequences in MA3 onPC + pre-viz software before tour. Then he loads that show file onto a physical console and calibrates focus to the real rig. RayFlow is this exact workflow — but with an AI doing the 20–35 hours of tedious infrastructure building, guided by a user who may have no console programming knowledge.

## Users & User Stories

### Primary Persona

**Target User:** Anyone who loves music and wants to create lighting for songs — no console programming experience required.

- **What they bring:** Taste. Knowledge of the music they love. An opinion about what looks good.
- **What the AI handles:** Fixture selection, DMX addressing, channel mapping, palette creation, cue programming, effect design, console syntax. Every technical detail.
- **What they do together:** The user says "I want warm amber front light that builds to a blue backlight peak on the chorus." The AI builds it. The user sees the result and says "the blue is too cold — try lavender." The AI adjusts. They iterate until the user likes it.

### Core User Story

**As a music lover, I want to describe how I want a song lit in plain language, see what the AI builds, and refine it until it looks right — without ever learning console programming.**

### How the User Works

1. Pick a song they like
2. Describe the vibe: "psychedelic, warm, big peaks on the choruses"
3. AI suggests a rig (fixture types, truss positions, count)
4. User approves or adjusts: "add more beam fixtures for aerial effects"
5. AI generates palettes, effects, and cue sequences
6. User sees the result (via pre-viz or DMX evidence)
7. User gives feedback: "the movement is too fast," "add strobes on the kick drum"
8. AI refines
9. Loop steps 6–8 until the user is satisfied
10. Record the show

## Features & Scope

### What We're Building (The Design Loop)

The product is the conversation between user and AI that produces a completed lighting show:

- **Rig generation:** User describes the show → AI selects fixtures, positions them, assigns addresses
- **Palette generation:** AI creates 100+ presets (position, color, beam, dimmer) from a vibe description
- **Cue generation:** AI builds song-specific cue stacks from the song's structure and the user's direction
- **Effect generation:** AI creates BPM-linked chases, movements, and color sweeps
- **Visualization:** User sees the result via pre-viz integration or DMX evidence
- **Iteration:** User provides taste feedback, AI refines, repeat until satisfied
- **Recording:** Capture the finished show

### Role of Existing Research

The 55+ documents in `docs/research/` serve as the AI's knowledge base. When the user says "I want a slow amber-to-lavender sweep on the backlight," the AI knows:
- What a backlight is and which fixtures serve that role
- What amber and lavender gel references translate to in RGB/CMY
- What "slow sweep" means in BPM-aware timing
- How to build a color chase effect with the right waveform and phase distribution
- How to render that intent to per-fixture DMX values

### Enabling Infrastructure (Already Built)

These are implementation details that make the design loop possible — they are not user-facing features:

- GDTF fixture parser and library (Phase 3) — so the AI knows what each fixture can do
- Show/Rig/Vibe/Cue data models (Phase 5) — the design's source of truth
- Fixture-aware DMX renderer (Phase 8, expanded Phase 11) — translates intent to concrete values
- Art-Net/sACN bridge (Phase 2) — one path to visualization and recording
- MVR export (Phase 4) — feeds pre-viz software for visual feedback
- Authoring system (Phases 6, 9, 10) — the AI's cue generation engine
- CLI (all phases) — the AI's interface to the codebase

### What's Next (Priority Order)

1. **Rig building tooling** — Auto-generate rigs from descriptions (venue type, show scale, vibe)
2. **Palette generation** — Auto-generate position, color, and beam preset libraries from a vibe and fixture list
3. **Integrated visualization** — Tighten the feedback loop between authoring and seeing
4. **Console show file export** — Produce files that import into MA3 onPC or other offline editors
5. **Record/export** — Capture the finished show in a standard format

### Out of Scope

- Live performance / busking during shows
- Hardware DMX output (USB-DMX interfaces)
- Full grandMA3 console replacement
- Multi-user collaborative programming
- Custom 3D visualizer
- Audio-reactive lighting (can be achieved through programming)

## Architecture

### High-Level Summary

RayFlow has three layers:

1. **Knowledge base** (55+ research docs) — What the AI knows about lighting design
2. **Design engine** (source code) — Data models, fixture library, renderer, authoring system
3. **AI interface** (CLI + context bundles) — How the AI coding tool interacts with the design engine

The user talks to the AI. The AI reads the knowledge base and uses the design engine. The design engine produces output artifacts (DMV frames, MVR files, show YAML) that feed pre-viz for visualization.

### System Diagram

```
 User (plain language)
        │
        ▼
 AI Coding Tool (opencode, Claude Code, etc.)
        │
        ├── reads ──→ Research Knowledge Base (55+ docs)
        │
        └── uses ──→ RayFlow Code
                        │
                        ├── Rig/Song/Vibe/Cue data models
                        ├── GDTF fixture library
                        ├── Fixture-aware DMX renderer
                        ├── Authoring system (plan-cues, etc.)
                        └── Context bundle builder
                                │
                                ▼
                        Output Artifacts
                        ├── Show YAML (source of truth)
                        ├── DMX frames (Art-Net/sACN → pre-viz)
                        ├── MVR files → pre-viz import
                        └── Console show files (future)

 Visualization Loop:
   AI authors → Output artifact → Pre-viz rendering → User sees → User gives feedback → AI refines
```

## Decision Log

| Date | Decision | Context |
|------|----------|---------|
| 2026-05-15 | grandMA3 onPC as console standard | Free, macOS native, industry standard |
| 2026-05-15 | GDTF as fixture standard | Open, supported by grandMA3, manufacturer-backed |
| 2026-05-17 | AI-as-primary interface | User works through AI coding tool; plain language → technical output |
| 2026-05-17 | Drop built-in web visualizer | Existing pre-viz tools (Capture, MA3 3D) serve visualization |
| 2026-05-23 | Backend-neutral control loop | MA3 OSC probes exposed fragility; show data is source of truth |
| 2026-05-26 | Terminal goal: design, not performance | Product ends when user is satisfied with the design. No live use. |
| 2026-05-26 | User is amateur, AI handles all console programming | User provides taste. AI does technical execution. The goal is to remove the need for console knowledge. |
| 2026-05-26 | Research serves AI knowledge base | 55+ research docs exist so the AI can translate amateur descriptions into correct technical output |
| 2026-05-26 | Priority: rig building → palette generation → visualization → console export → recording | Backend work (Art-Net, sACN, QLC+) is enabling infrastructure, not product features |
