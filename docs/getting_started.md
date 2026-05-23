# Getting Started

> **Purpose:** Get RayFlow running and send your first DMX values through the
> protocol bridge.

---

## Prerequisites

- **Python 3.10+** — RayFlow's runtime
- **Git** — For version control
- **Optional: grandMA3 onPC 2.3.2.0** — Compatibility target for MA3 export/playback work
- **Optional: QLC+** — Planned API-first controller target

---

## 1. Install Optional External Targets

RayFlow can run its CLI and tests without a lighting console. Install external
targets only when you want live protocol testing:

- grandMA3 onPC for MA3 compatibility export/playback work.
- QLC+ for the planned WebSocket controller adapter spike.
- An Art-Net/sACN receiver, visualizer, or lighting node for direct DMX tests.

See the [grandMA3 Setup Guide](./guides/grandma3-setup.md) for MA3-specific
instructions.

---

## 2. Install RayFlow

```bash
# Clone the repository
git clone <repo-url>
cd rayflow

# Install dependencies
uv sync

# Install lighting extras (Art-Net, GDTF)
uv sync --extra lighting
```

---

## 3. Verify Setup

```bash
# Run tests
uv run pytest

# Check the CLI
uv run rayflow --help
```

---

## 4. Send Your First DMX

Once RayFlow is installed and you have a receiver/controller ready:

```bash
# Send DMX values to universe 0
uv run rayflow bridge send --universe 0 --channel 1 --value 255
```

You should see the receiver report a DMX value, or a fixture/visualizer respond
if it is patched to the matching universe and address.

See the [First DMX Guide](./guides/first-dmx.md) for a complete tutorial.

---

## 5. Next Steps

- **[Build a Rig](./guides/building-a-rig.md)** — Load GDTF fixtures and create a reusable rig
- **[Current Workflow](./guides/current-workflow.md)** — Author, version, export, and dry-run a show
- **[Control Backend Direction](./architecture/control-backend-direction.md)** — Understand the current backend adapter plan
- **[Implementation Schedule](./implementation_schedule.md)** — See what's being built next

---

## Project Structure

```
rayflow/
├── src/rayflow/
│   ├── bridge/          # Art-Net / sACN protocol bridge
│   ├── fixtures/        # GDTF fixture handling
│   ├── console/         # grandMA3 compatibility tools
│   ├── shows/           # Show/rig models and exports
│   ├── visualizer/      # Optional/future visualization work
│   └── cli.py           # CLI entry point
├── data/
│   ├── fixtures/        # GDTF fixture files
│   └── shows/           # Show configurations
├── docs/                # This documentation
├── tests/               # Test suite
└── .agent/              # AI agent guidance
```

---

## Development Workflow

```bash
# Format and lint
uv run ruff format . && uv run ruff check .

# Run tests
uv run pytest

# Serve docs
mkdocs serve  # http://127.0.0.1:8000
```

Always work on a feature branch, never `main`. See CONTRIBUTING.md for details.
