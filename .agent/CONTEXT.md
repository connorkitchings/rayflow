# Context Router (ACE Framework)

> **Welcome.** This repository utilizes the Agentic Context Engineering (ACE) framework. This document is your routing hub. Do not look for deep project details here—follow the pointers below.

## 🗺️ Map of the Repo

```text
rayflow/
├── .agent/              # 🧠 AI Agent Brain (You are here)
│   ├── CONTEXT.md       # Context Router (This file)
│   ├── PLAYBOOK.md      # Dynamic memory: Rules, Strategies, and Patterns
│   ├── PRINCIPLES.md    # 11 operating principles
│   ├── skills/          # Executable workflows and procedures
│   └── workflows/       # Health checks and CI automation
├── src/rayflow/         # Application source code
│   ├── cli/             # Typer CLI application subcommands
│   ├── design/          # Creative lighting design models, presets, plans
│   ├── engine/          # Drivers, bridges, parsers, renderers, console adapters
│   ├── config.py        # Global settings
│   └── cli.py           # CLI entry point (routes cli.main)
├── data/
│   ├── fixtures/        # GDTF fixture library
│   └── shows/           # Show configurations
├── tests/               # Pytest suite (organized into cli/, design/, engine/)
├── docs/                # Architecture, guides, and manuals
├── scripts/             # Internal utilities and CLI tools
└── session_logs/        # Historical logs of AI sessions
```

## 🧭 Navigation Instructions

- **For Execution & Workflows:** Proceed to `.agent/skills/CATALOG.md` and load the appropriate skill for your task (e.g., `start-session`, `art-net-bridge`, `gdtf-fixture`).
- **For Project State & Rules:** Read `.agent/PLAYBOOK.md` to understand current strategies, rules, and success patterns.
- **For Fast Commands:** Review `.codex/QUICKSTART.md`.
- **For Immediate Context:** Check the latest log in `session_logs/`.
- **For AI-Operable MA3 Docs:** Read `docs/ai/MASTER_CONTEXT.md` — comprehensive references for AI agents to drive grandMA3 onPC.
- **For Project Goals:** Read `docs/project_charter.md` and `docs/implementation_schedule.md`.

## 📋 Current Status

**Phase:** Post-Phase 11 — Product direction clarified

**Terminal Goal:** Pick a song → collaborate with AI to design lighting → see the result → iterate until satisfied → record the show. No live use. The AI handles all console programming; the user provides taste and musical judgment.

**Completed:**
- Phase 1: Package structure and foundation
- Phase 2: Art-Net/sACN bridge (DMX send/receive)
- Phase 3: GDTF fixture parser and library
- Phase 4: grandMA3 compatibility research (OSC, MVR, probes)
- Phase 5: Show & Rig data models, CLI, YAML serialization (296 tests)
- Phase 6: AI show builder — section import, vibe generation, cue generation, MA3 push
- Phase 7: Export compatibility — MA3 bundles, Timecode XML, show library
- Phase 8: Backend-neutral MVP — adapter contract, fixture-aware renderer, DMX evidence
- Phase 9: Productized practice workflow — practice rig/show, workflow reports, loopback proof
- Phase 10: General authoring ergonomics — plan-cues, vibe-palette style
- Phase 11: Renderer expansion — pan/tilt, zoom, focus, shutter, gobo through GDTF maps
- 2026-05-25: Research expansion — 55+ docs covering lighting design concepts, programming workflows, concert LD profiles, protocol infrastructure
- 2026-05-25: Project charter rewritten to reflect true goal: AI-assisted design for amateurs, not a toolkit for professionals
- Phase 15 Option A (2026-05-25): QLC+ workspace exporter — `rayflow rig export-qxw` generates a `.qxw` file directly from a RayFlow rig; 583 tests at 81.98% coverage
- Product V1 setup loop (2026-05-25): `rayflow rig plan-build` and `rayflow show plan-palettes` add proposal/apply flows for generated rigs and show-specific `rf_` palette overrides; 597 tests at 82.84% coverage
- Preview/Critique V1 (2026-05-25): `rayflow show preview` and MCP `preview_show` build dry-run critique packets with rendered DMX evidence, fixture capabilities, warnings, and property-specific prompts; 605 tests at 83.07% coverage

**Current Focus:**
- All Phases 1–11 and the full post-Phase 11 candidate track are complete.
- Phase 15 Option A (QLC+ workspace exporter) shipped: `rayflow rig export-qxw` writes a loadable `.qxw` file.
- Rig Builder V1 and Palette Generator V1 shipped: AI can now propose/apply a deterministic generated rig from plain language and propose/apply a minimal generated palette library as show overrides.
- Preview/Critique V1 shipped: AI can now package show state, fixture capabilities, effective presets, rendered DMX frames, and critique prompts into one dry-run review artifact.
- Phase 15 Options B/C: QLC+ fixture definitions and function/scene triggers shipped; QLC+ depth now covers QXW workspace export, QXF fixture definitions, channel evidence, and function status/trigger commands.
- Next product priority: console show file export or recording/export workflow, with preview packet feedback available for iteration.

**Active Branch:** `codex/continue-development-session`

**grandMA3 Context:**
- Local installed version verified: grandMA3 onPC 2.3.2.0 (`/Applications/grandMA3.app`)
- MA3 onPC + pre-viz (Capture, MA3 3D) is the user's visualization path — RayFlow feeds this pipeline, it doesn't replace it
- Console show file export (.show.gz) is a future priority to directly feed the MA3 offline editor

**Project Direction:**
- RayFlow's unique value: AI handles all console programming so anyone can design concert lighting
- The user works through an AI coding tool (opencode) and never touches console syntax
- The research knowledge base (55+ docs) gives the AI deep lighting design knowledge to translate amateur descriptions into correct technical output
- Main design loop: user describes intent → AI generates rig/palettes/cues → user sees result via pre-viz or DMX evidence → user gives taste feedback → AI refines → repeat
- The product ends when the user is satisfied with the design. Live playback, busking, and performance use are out of scope.

## 🔄 Post-Session Protocol

**MANDATORY BEFORE EXIT:**
Before concluding any session, the AI agent MUST perform a self-critique and execute the following Reflection Protocol:

1. **Review Actions**: What code was changed? What new patterns emerged?
2. **Update PLAYBOOK**: If a new Success Pattern, Strategy, or Rule was identified during this session, you MUST append or modify `.agent/PLAYBOOK.md` to persist this learning.
3. **Log the Session**: Ensure a complete session log is written to `session_logs/`.
