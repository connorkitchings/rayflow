# RayFlow

AI-assisted concert lighting design toolkit with backend-neutral show data, DMX rendering, and console adapters.

## Overview

RayFlow bridges creative intent and lighting execution. It keeps the show,
rig, fixture, cue, and vibe data in AI-readable project files, then renders that
intent through deterministic backends: direct Art-Net/sACN DMX output,
structured controller adapters such as QLC+, and gated professional-console
adapters such as grandMA3.

The project started with grandMA3 onPC as the primary execution target. Live
probing showed that MA3 remains valuable for professional compatibility, but
raw MA3 mutation is too fragile to be the core agent loop until command
acceptance, fixture import, and readback are repeatably proven. The current
direction is backend-neutral: RayFlow owns the show model and evidence
contracts; output adapters translate that model into DMX frames, controller
commands, or MA3 export/playback artifacts.

RayFlow can currently build and version show YAML, generate cue programming
commands, export MA3 review bundles with MVR plus OSC command text, generate
MA3 Timecode XML from captured 2.3.2.0 exports, and send dry-run-gated OSC
commands to MA3. The next implementation focus is a fixture-aware DMX renderer
and API-first output adapters.

## Architecture

```
┌─────────────────┐     Natural Language      ┌──────────────────┐
│  Designer       │◄─────────────────────────►│  AI Coding Tool  │
│  (You)          │                            │  (Claude/Codex)  │
└─────────────────┘                            └────────┬─────────┘
                                                        │
                                                        ▼
┌─────────────────┐     show direction      ┌──────────────────┐
│  Designer       │◄───────────────────────►│  RayFlow Data    │
│  + AI Tool      │                         │  Show/Rig/Cues   │
└─────────────────┘                         └────────┬─────────┘
                                                     │
                                                     ▼
                                            ┌──────────────────┐
                                            │ Fixture-Aware    │
                                            │ DMX Renderer     │
                                            └────────┬─────────┘
                                                     │
        ┌──────────────────────┬─────────────────────┼─────────────────────┐
        ▼                      ▼                     ▼                     ▼
┌──────────────┐        ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│ Art-Net/sACN │        │ QLC+ WS      │      │ MA3 Export   │      │ Middleware   │
│ DMX Output   │        │ Adapter      │      │ + Gated OSC  │      │ Adapters     │
└──────────────┘        └──────────────┘      └──────────────┘      └──────────────┘
```

## Tech Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Core | Python | CLI, data models, renderers, adapters |
| Data | YAML + JSON | Show/rig serialization, AI-readable source of truth |
| Fixtures | GDTF | Open fixture definition standard |
| Direct DMX | Art-Net, sACN | Deterministic output and protocol-level verification |
| Controller adapter | QLC+ WebSockets | Planned API-first structured controller target |
| Console adapter | grandMA3 onPC 2.3.2.0 | Compatibility/export target with gated OSC probes |
| AI Interface | AI coding tools | Claude, Codex, Gemini CLI, OpenCode, etc. |
| Package mgmt | uv | Python package manager |

## Quick Start

```bash
# Install dependencies
uv sync

# Install lighting extras
uv sync --extra lighting

# Run the CLI
uv run rayflow --help
```

## Current Workflow

RayFlow's usable workflow today is file-first and dry-run-first:

```bash
# Inspect existing rigs and shows
uv run rayflow rig list
uv run rayflow show list

# Create a versioned snapshot before changing a show
uv run rayflow show save "My Show" --message "before cue polish"

# Export an MA3 compatibility bundle: MVR rig, OSC command list, README, metadata
uv run rayflow show export "My Show" --output-dir exports/my-show --sequence 1

# Review the MA3 command path without sending OSC
uv run rayflow show push-to-ma3 "My Show" --sequence 1

# Send cues to grandMA3 only when the dry-run and target show are confirmed
uv run rayflow show push-to-ma3 "My Show" --sequence 1 --execute
```

The mainline roadmap now prioritizes rendering the same show data to direct
DMX frames and API-first controller adapters. MA3 remains supported, but
fixture-aware MA3 mutation is no longer the blocker for RayFlow's next
milestone.

Show snapshots are local YAML versions:

```bash
uv run rayflow show versions "My Show"
uv run rayflow show diff "My Show" --version 20260520T120000Z
uv run rayflow show restore "My Show" --version 20260520T120000Z --force
```

## Project Structure

```
rayflow/
├── src/rayflow/
│   ├── bridge/          # Art-Net / sACN protocol bridge
│   ├── fixtures/        # GDTF fixture loading, parsing, MVR export
│   ├── console/         # grandMA3 OSC compatibility and cue builders
│   ├── shows/           # Show/rig models, exports, snapshots
│   └── cli.py           # CLI entry point
├── data/
│   ├── fixtures/        # GDTF fixture library
│   ├── rigs/            # Rig definitions (fixtures, presets, venue)
│   └── shows/           # Show definitions (song, cues, vibe)
├── tests/               # Test suite
├── docs/                # Project documentation
├── scripts/             # Session management utilities
└── .agent/              # AI agent guidance and skills
```

## Key Protocols

- **Art-Net** — DMX512 over UDP, the most widely used lighting network protocol
- **sACN (E1.31)** — Streaming ACN, modern alternative to Art-Net
- **OSC** — Open Sound Control, used for MA3 and middleware control
- **WebSocket** — Planned structured controller path for QLC+
- **GDTF** — General Device Type Format, open fixture definition standard
- **MVR** — My Virtual Rig, scene sharing between consoles and visualizers

## grandMA3 onPC Setup

1. Download from [MA Lighting](https://www.malighting.com/downloads/products/grandma3/)
2. Install the macOS version. RayFlow currently targets grandMA3 onPC 2.3.2.0.
3. Run in standalone mode or connect to RayFlow via Art-Net/OSC for compatibility testing.
4. Enable Art-Net input or OSC input in the show before expecting RayFlow traffic to affect MA3.
5. Use the built-in 3D visualizer as a compatibility preview target, not as RayFlow's only execution path.

## AI-Assisted Development

This project uses AI coding tools (Claude Code, Gemini CLI, Codex, OpenCode) as the primary interface for show design.

- **AI Interaction Contract**: `docs/ai_interaction_contract.md` — How AI tools work with RayFlow
- **Phase 5 Architecture**: `docs/phase5_architecture.md` — Show & rig data model design
- **Project state**: `.agent/CONTEXT.md`
- **Available skills**: `.agent/skills/CATALOG.md`
- **Never work on `main`** — always use feature branches

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and standards.

## License

MIT — See [LICENSE](LICENSE) for details.
