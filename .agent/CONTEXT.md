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
│   ├── bridge/          # Art-Net / sACN protocol bridge
│   ├── fixtures/        # GDTF fixture handling
│   ├── visualizer/      # Web 3D stage visualizer
│   └── cli.py           # CLI entry point
├── data/
│   ├── fixtures/        # GDTF fixture library
│   └── shows/           # Show configurations
├── tests/               # Pytest suite
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

**Phase:** 9 — Productized Show Workflow (NEXT)

**Completed:**
- Phase 1 foundation cleanup and RayFlow package structure
- Phase 2 Art-Net / sACN bridge implementation
- Bridge CLI commands for send, receive, and status
- Bridge validation, error handling, and tests
- grandMA3 onPC Art-Net verification against installed version 2.3.2.0
- Phase 3 GDTF parser and fixture library
- Checked-in real GDTF sample pack with manifest validation
- GDTF channel mapping with attribute family classification
- Phase 3 in-memory GDTF fixture patching with CLI inspection command
- Phase 4 fixture comparison reports with real MA3 observation capture (14 modes)
- Phase 4 dry-run-safe OSC command sender and feedback listener
- Phase 4 cue stack command helpers with JSON batch input and nested CLI
- Phase 4 MVR export with embedded GDTF files and mode info
- Phase 4 integration tests (14 tests, requires running MA3)
- Phase 5 architecture document and AI interaction contract
- Phase 5 data models (11 dataclasses with validation, presets, rig templates, show overrides)
- Phase 5 YAML serialization with round-trip support
- Phase 5 CLI commands (rig create/list/info/copy/add-fixture/add-preset/export-mvr, show create/list/info/add-section/add-cue/add-preset-override/context/export-mvr)
- Phase 5 AI context bundle command (`show context --json`)
- Phase 5 prompt template for AI sessions
- Phase 5 full test suite (296 tests, 84% coverage)
- Phase 6 audio section import (`show import-sections`, `section_import.py`, JSON schema)
- Phase 6 vibe generation (`show set-vibe`, `Vibe.from_dict()`, enhanced prompt template)
- Phase 6 cue generation helpers (`cue_generator.py`, `show generate-cues/update-cue/delete-cue/renumber`)
- Phase 6 interactive direction (`show set-song-meta/update-section/delete-section/batch-update-cues`)
- Phase 6 MA3 push integration (`show push-to-ma3/push-section`, `push.py`)
- Phase 6 80 new tests (section import, cue generator, push, CLI)
- Phase 7 Slice 2: Sequence build hardening (`store_sequence`, `label_sequence`, `delete_sequence`, `clear_all`; `--sequence` on push commands)
- Phase 7 MA3 show export bundle (`show export` with MVR, OSC command list, README, metadata)
- Phase 7 show library (`show save/versions/restore/diff` with versioned YAML snapshots)
- Phase 7 MA3 Timecode XML generation from captured `CmdEvent` / `RealtimeCmd` export shape
- Phase 7 clean MA3 Timecode XML import/re-export validation against grandMA3 onPC 2.3.2.0
- Phase 7 internal Timecode playback clock validation via `Top Timecode 1` / `Go Timecode 1` and re-exported `Cursor`
- 2026-05-23 direction reset: MA3 remains a compatibility/export target, while the mainline moves to backend-neutral show intent, fixture-aware DMX rendering, Art-Net/sACN execution, and QLC+ WebSocket research
- CLI organization: `cli_show.py` split into focused show, cue, edit, export, and library modules
- Phase 8 backend-neutral MVP: adapter contract, fixture-aware DMX renderer, Art-Net/sACN evidence backends, experimental QLC+ WebSocket spike, backend CLI commands, docs, and tests
- Phase 9 productized practice workflow: checked-in practice rig/show, deterministic cue planning, workflow reports, and local Art-Net loopback receiver proof

**Current Focus:**
- Phase 9 closure checkpoint is ready after final health checks and commit
- Next product direction should build beyond the practice-show loop: live QLC+ proof, broader authoring ergonomics, or richer fixture-aware renderer capabilities
- Keep QLC+ experimental until live local command/query proof is captured
- MA3 export/playback remains a compatibility track; fixture import, fixture-aware presets, executor state, and runtime readback still need proof before mutating MCP tools
- LLM-agnostic design: AI coding tools (opencode, Claude Code, etc.) are the LLM

**Active Branch:** `codex/continue-development-session`

**grandMA3 Context:**
- Local installed version verified: grandMA3 onPC 2.3.2.0 (`/Applications/grandMA3.app`)
- Use version 2.3 manual pages for compatibility-track UI/protocol guidance unless the installed app changes
- Before giving manual grandMA3 UI instructions, verify they apply to 2.3.2.0 and prefer RayFlow automation or network verification where possible
- Do not treat MA3 as the core agent execution loop until mutation and readback are repeatably proven

**Project Direction:**
- RayFlow's unique value: AI-assisted show design, not a console or visualizer
- RayFlow show/rig/cue data is the source of truth
- Mainline workflow: build rig → pick song → AI suggests vibe → user directs AI → cues generated → fixture-aware renderer → Art-Net/sACN or QLC+ backend evidence
- Compatibility workflow: export MA3 bundles, Timecode XML, and gated OSC only for verified MA3 operations
- Next milestone: choose the post-Phase 9 track after committing the practice workflow checkpoint

## 🔄 Post-Session Protocol

**MANDATORY BEFORE EXIT:**
Before concluding any session, the AI agent MUST perform a self-critique and execute the following Reflection Protocol:

1. **Review Actions**: What code was changed? What new patterns emerged?
2. **Update PLAYBOOK**: If a new Success Pattern, Strategy, or Rule was identified during this session, you MUST append or modify `.agent/PLAYBOOK.md` to persist this learning.
3. **Log the Session**: Ensure a complete session log is written to `session_logs/`.
