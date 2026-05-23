# Project Brief

## Project Name:
RayFlow

## Overview:
RayFlow is a personal toolkit for learning and building concert lighting design by programming song-based shows in AI-readable project files. It combines Python-based fixture management, cue generation, and DMX rendering with output adapters for direct Art-Net/sACN, API-first controllers such as QLC+, and professional console compatibility targets such as grandMA3 onPC.

## Key Objectives:
- Build a GDTF fixture library to work with real-world lighting fixtures
- Create tools for building virtual stages and programming lighting cues
- Enable AI-assisted cue generation to accelerate learning and creativity
- Support a workflow from song → rig/show intent → programmed cues → deterministic output artifacts
- Render show intent to direct DMX and controller adapters before relying on console-specific mutation
- Lay groundwork for future live show lighting capabilities

## Target Audience:
Connor Kitchings — lighting designer in training, using this as a practice and learning platform.

## Key Features/Deliverables:
- GDTF fixture parser and library management
- Art-Net/sACN bridge for direct DMX communication and verification
- Fixture-aware DMX renderer from RayFlow cues to universe/channel values
- Controller adapter track for QLC+ WebSocket execution
- grandMA3 compatibility export track for MVR, Timecode XML, and gated OSC
- Stage builder tools for creating virtual rigs
- AI-assisted cue generation from natural language descriptions
- Workflow documentation for recording shows as video

## Success Metrics:
- Can load a GDTF fixture, patch it to a universe, and render cue intent into inspectable DMX values
- Can build a virtual stage with 10+ fixtures and program a complete cue list for a song
- Can run a show through at least one deterministic backend without manual console mutation
- AI can generate reasonable starting cues from a natural language prompt

## Timeline (High-Level):
- **Start Date:** 2026-05-15
- **Phase 1 (Foundation):** Project setup, package structure — May 2026
- **Phase 2 (Bridge):** Art-Net/sACN send/receive — Jun 2026
- **Phase 3 (Fixtures):** GDTF parser and library — Jul 2026
- **Phase 4 (Console Compatibility):** grandMA3 onPC OSC/MVR research — Aug 2026
- **Phase 5 (Show Model):** AI-readable rig/show data — Sep 2026
- **Phase 6 (AI):** AI-assisted cue generation — Oct 2026
- **Phase 7 (Export/Playback):** MA3 export and Timecode compatibility — Nov 2026
- **Phase 8 (Backend Pivot):** DMX renderer, QLC+ adapter, and adapter boundary — Current focus

## Stakeholders:
- Connor Kitchings — Project Lead, primary user, lighting designer in training

## Contact:
Connor Kitchings (GitHub: `connorkitchings`)
