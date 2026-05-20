# RayFlow

AI-assisted lighting design toolkit for recorded music and grandMA3 onPC.

## Overview

RayFlow bridges the gap between creative intent and console execution. It
provides Python tooling for concert lighting programming, automating grandMA3
workflows, and an AI interaction layer that lets you direct show design in
natural language. grandMA3 onPC serves as the console and 3D visualizer;
RayFlow manages rigs, generates creative direction, and translates your ideas
into concrete lighting cues.

RayFlow can currently build and version show YAML, generate cue programming
commands, export an MA3-ready bundle with MVR plus OSC command text, and push
cues to grandMA3 over OSC. Native MA3 Timecode XML generation is intentionally
blocked until an event-bearing grandMA3 2.3.2.0 Timecode export is captured and
verified.

## Architecture

```
┌─────────────────┐     Natural Language      ┌──────────────────┐
│  Designer       │◄─────────────────────────►│  AI Coding Tool  │
│  (You)          │                            │  (Claude/Codex)  │
└─────────────────┘                            └────────┬─────────┘
                                                        │
                                                        ▼
┌─────────────────┐     Art-Net / sACN / OSC     ┌──────────────────┐
│  grandMA3 onPC  │◄────────────────────────────►│  RayFlow CLI     │
│  (Console+Viz)  │                               │  (Python)        │
└─────────────────┘                               └────────┬─────────┘
          ▲                                                  │
          │  GDTF / MVR                                      │
          │                                                  ▼
          │                                         ┌──────────────────┐
          │                                         │  GDTF Library    │
          │                                         │  Show/Rig Data   │
          └─────────────────────────────────────────└──────────────────┘
```

## Tech Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Console | grandMA3 onPC 2.3.2.0 | Verified local baseline, macOS native |
| Bridge | Python | Art-Net, sACN (E1.31), OSC protocols |
| Fixtures | GDTF | Open fixture definition standard |
| Data | YAML + JSON | Show/rig serialization, AI-readable |
| AI Interface | LLM API | Any LLM via AI coding tools |
| Package mgmt | uv | High-performance Python package manager |

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

RayFlow's usable workflow today does not require Timecode XML:

```bash
# Inspect existing rigs and shows
uv run rayflow rig list
uv run rayflow show list

# Create a versioned snapshot before changing a show
uv run rayflow show save "My Show" --message "before cue polish"

# Export an MA3 review bundle: MVR rig, OSC command list, README, metadata
uv run rayflow show export "My Show" --output-dir exports/my-show --sequence 1

# Review the same MA3 programming path without sending OSC
uv run rayflow show push-to-ma3 "My Show" --sequence 1

# Send cues to grandMA3 only when the dry-run looks correct
uv run rayflow show push-to-ma3 "My Show" --sequence 1 --execute
```

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
│   ├── console/         # grandMA3 onPC OSC control and cue builders
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
- **OSC** — Open Sound Control, used by grandMA3 for remote control
- **GDTF** — General Device Type Format, open fixture definition standard
- **MVR** — My Virtual Rig, scene sharing between consoles and visualizers

## grandMA3 onPC Setup

1. Download from [MA Lighting](https://www.malighting.com/downloads/products/grandma3/)
2. Install the macOS version. RayFlow currently targets grandMA3 onPC 2.3.2.0.
3. Run in standalone mode or connect to RayFlow via Art-Net/OSC.
4. Enable Art-Net input or OSC input in the show before expecting RayFlow traffic to affect MA3.
5. Use the built-in 3D visualizer to preview your shows.

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
