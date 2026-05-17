# RayFlow

Concert lighting design toolkit — grandMA3 onPC integration, Art-Net/sACN bridge, and 3D stage visualizer.

## Overview

RayFlow bridges the gap between show design logic and console execution. It provides Python tooling for concert lighting programming, automating grandMA3 workflows, and visualizing stage designs — allowing lighting designers to focus on the art of the look.

## Architecture

```
┌─────────────────┐     Art-Net / sACN / OSC     ┌──────────────────┐
│  grandMA3 onPC  │◄────────────────────────────►│  RayFlow Bridge  │
│  (macOS)        │                               │  (Python)        │
└─────────────────┘                               └────────┬─────────┘
         │                                                  │
         │  GDTF / MVR                                      │  WebSocket
         ▼                                                  ▼
┌─────────────────┐                               ┌──────────────────┐
│  Built-in 3D    │                               │  Web Visualizer  │
│  Visualizer     │                               │  (Three.js)      │
└─────────────────┘                               └──────────────────┘
```

## Tech Stack

| Component | Technology | Notes |
|-----------|------------|-------|
| Console | grandMA3 onPC 2.3.2.0 | Verified local baseline, macOS native |
| Bridge | Python | Art-Net, sACN (E1.31), OSC protocols |
| Fixtures | GDTF | Open fixture definition standard |
| Visualizer | Web (Three.js) | Browser-based 3D stage visualization |
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

## Project Structure

```
rayflow/
├── src/rayflow/
│   ├── bridge/          # Art-Net / sACN protocol bridge
│   ├── fixtures/        # GDTF fixture loading and parsing
│   ├── visualizer/      # Web-based 3D stage visualizer
│   └── cli.py           # CLI entry point
├── data/
│   ├── fixtures/        # GDTF fixture library
│   └── shows/           # Show configurations
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
5. Use the built-in 3D visualizer or connect to the RayFlow web visualizer.

## AI-Assisted Development

This project uses AI coding tools (Claude Code, Gemini CLI, Codex, OpenCode).

- Start here: `AGENTS.md`
- Project state: `.agent/CONTEXT.md`
- Available skills: `.agent/skills/CATALOG.md`
- Never work on `main` — always use feature branches

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow and standards.

## License

MIT — See [LICENSE](LICENSE) for details.
