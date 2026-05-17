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

**Phase:** 4 — grandMA3 onPC Integration (COMPLETE)

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

**Current Focus:**
- Phase 4 is complete — ready for Phase 5 (Web 3D Visualizer) or Phase 6 (AI-Assisted Lighting)
- 203 total tests (189 unit + 14 integration), 84% coverage
- Branch cleanup and merge pending before starting new phase

**grandMA3 Context:**
- Local installed version verified: grandMA3 onPC 2.3.2.0 (`/Applications/grandMA3.app`)
- Use version 2.3 manual pages for UI/protocol guidance unless the installed app changes
- Before giving manual grandMA3 UI instructions, verify they apply to 2.3.2.0 and prefer RayFlow automation or network verification where possible

## 🔄 Post-Session Protocol

**MANDATORY BEFORE EXIT:**
Before concluding any session, the AI agent MUST perform a self-critique and execute the following Reflection Protocol:

1. **Review Actions**: What code was changed? What new patterns emerged?
2. **Update PLAYBOOK**: If a new Success Pattern, Strategy, or Rule was identified during this session, you MUST append or modify `.agent/PLAYBOOK.md` to persist this learning.
3. **Log the Session**: Ensure a complete session log is written to `session_logs/`.
