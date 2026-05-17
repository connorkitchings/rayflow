# Project Charter

This document is the single source of truth for RayFlow's goals, scope, and technical context.

## Project Overview

**Project Name:** RayFlow

**Project Vision:** An AI-assisted lighting design toolkit for creating timecoded light shows for recorded music. grandMA3 onPC serves as the console and visualizer; RayFlow provides the design intelligence layer — managing rigs, generating creative direction, and translating natural language into concrete lighting cues.

**Technical Goal:** Build a framework where a lighting designer can pick a song, work with an AI to develop a rig and show, direct the AI through iterative refinement, and export the result as an MA3-native timecoded show.

## Users & User Stories

### Primary Persona

**Target User:** Lighting designers and students learning concert lighting programming.

- **Name:** Connor (designer/learner)
- **Role:** Lighting designer creating shows for recorded music
- **Pain Points:** Building a show from scratch is slow; expensive visualizers; no easy way to iterate on creative ideas; repetitive console programming
- **Goals:** Create professional-quality timecoded light shows using AI assistance, practice lighting design on a computer, automate repetitive console tasks

### Core User Stories

**Story 1:** As a lighting designer, I want to define a rig with fixtures and presets so that I have a reusable foundation for show design.

- Priority: Must-have

**Story 2:** As a learner, I want to load GDTF fixture profiles so that I can work with real-world fixture data.

- Priority: Must-have

**Story 3:** As a programmer, I want to control grandMA3 onPC via OSC so that I can push AI-generated cues to the console for review.

- Priority: Must-have

**Story 4:** As a designer, I want to direct an AI in natural language to build and refine a lighting show so that I can focus on creative decisions.

- Priority: Must-have

**Story 5:** As a designer, I want to export my completed show as an MA3-native timecoded show for playback.

- Priority: Should-have

## Features & Scope

### Must-Have (MVP)

**Feature A:** Art-Net/sACN bridge — send and receive DMX universes from Python

- User Story: Story 3
- Implementation: Phase 2

**Feature B:** GDTF fixture parser — load and manage fixture definitions

- User Story: Story 2
- Implementation: Phase 3

**Feature C:** grandMA3 onPC OSC integration — remote control and automation

- User Story: Story 3
- Implementation: Phase 4

**Feature D:** Show & Rig Framework — data model for rigs, shows, presets, and vibes

- User Story: Story 1
- Implementation: Phase 5

**Feature E:** AI Show Builder — natural-language-driven cue generation and refinement

- User Story: Story 4
- Implementation: Phase 6

### Should-Have (Post-MVP)

**Feature F:** Export & Playback — MA3-native show export with timecode

- User Story: Story 5
- Implementation: Phase 7

### Out of Scope

- Hardware DMX output (USB-DMX interfaces)
- Full grandMA3 console replacement
- Production show playback
- Multi-user collaborative programming
- Built-in 3D visualizer (grandMA3 onPC provides this)

## Architecture

### High-Level Summary

RayFlow has four main components: a Python protocol bridge (Art-Net/sACN/OSC), a GDTF fixture library, a show/rig data model, and an AI interaction layer. grandMA3 onPC runs alongside as the console and visualizer, communicating via network protocols.

### System Diagram

```mermaid
graph TD
    User[Lighting Designer] --> AI[AI Coding Tool]
    AI --> Show[Show & Rig Data]
    Show --> CLI[RayFlow CLI]
    CLI --> Bridge[Art-Net / sACN Bridge]
    CLI --> OSC[OSC Controller]
    OSC --> MA3[grandMA3 onPC]
    MA3 -->|Art-Net/sACN| Bridge
    MA3 -->|OSC| OSC
    CLI --> GDTF[GDTF Fixture Library]
    GDTF --> MA3
    CLI --> MVR[MVR Export]
    MVR --> MA3
```

## Technology Stack

| Category | Technology | Version | Notes |
|----------|------------|---------|-------|
| Package Management | uv | latest | Python package manager |
| Core Language | Python | 3.10+ | Primary programming language |
| Console | grandMA3 onPC | 2.3.2.0 baseline | macOS native, locally verified |
| Art-Net | artnet / custom | — | DMX over UDP |
| sACN | sacn | 1.0+ | E1.31 streaming |
| OSC | python-osc | 1.8+ | Remote console control |
| Fixtures | GDTF | — | Open fixture format |
| Data Format | YAML + JSON | — | Show/rig serialization |
| AI Interface | LLM API | Any | Claude, GPT, etc. via coding tools |
| Linting | Ruff | 0.5+ | Format and lint |
| Testing | Pytest | 8.x | Test framework |
| Documentation | MkDocs + Material | — | Project docs |

## Risks & Assumptions

### Key Assumptions

- grandMA3 onPC remains free and available for macOS
- Art-Net and sACN protocols are stable and well-documented
- GDTF fixture library is available from gdtf-share.com
- AI coding tools can effectively work with structured YAML data and existing Python modules

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| grandMA3 onPC macOS compatibility breaks | Low | High | Test on each new release |
| Art-Net library unmaintained | Medium | Medium | Build minimal custom implementation as fallback |
| GDTF parsing complexity | Medium | Medium | Start with common fixture types, expand iteratively |
| AI prompt quality | High | High | Iterate on prompt templates, provide rich context bundles |
| MA3 OSC API undocumented | High | Medium | Reverse-engineer, use MA3 online manual |
| MA3 timecode integration | Medium | Medium | Research MA3 timecode API, start with manual cue triggering |

## Decision Log

| Date       | Decision                                    | Context / Drivers                                           | Impact / Follow-up                                    |
|------------|---------------------------------------------|-------------------------------------------------------------|-------------------------------------------------------|
| 2026-05-15 | grandMA3 onPC as console emulator           | Free, macOS native, industry standard                       | Primary console for all development                   |
| 2026-05-15 | Python for protocol bridge                  | Rich ecosystem (sacn, python-osc), AI-friendly              | Core of all lighting communication                    |
| 2026-05-15 | GDTF as fixture standard                    | Open, supported by grandMA3, manufacturer-backed            | All fixtures use GDTF format                          |
| 2026-05-17 | AI-as-primary interface                     | Designer directs AI in natural language; AI handles translation to MA3 | RayFlow's primary user is a human working through an AI coding tool |
| 2026-05-17 | Drop built-in web visualizer                | grandMA3 onPC has built-in 3D visualizer; redundant         | Focus on show/rig data model and AI interaction layer |
| 2026-05-17 | MA3-native export as target format          | Industry standard; leverages existing MA3 investment        | MVR for rig + OSC cues + timecode for playback        |
