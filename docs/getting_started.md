# Getting Started

> **Purpose:** Get RayFlow running and send your first DMX values to grandMA3 onPC.

---

## Prerequisites

- **macOS** — grandMA3 onPC runs natively on macOS
- **Python 3.10+** — RayFlow's runtime
- **Git** — For version control
- **grandMA3 onPC 2.3.2.0** — Current RayFlow baseline and verified local version (see [grandMA3 Setup Guide](./guides/grandma3-setup.md))

---

## 1. Install grandMA3 onPC

Download from [MA Lighting Downloads](https://www.malighting.com/downloads/products/grandma3/):

1. Select "grandMA3 onPC Software for macOS"
2. Install the application (~630 MB)
3. Launch grandMA3 onPC and create a new show
4. Verify the built-in 3D visualizer works

See the full [grandMA3 Setup Guide](./guides/grandma3-setup.md) for detailed instructions.

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

Once grandMA3 onPC is running and RayFlow is installed:

```bash
# Send DMX values to universe 0
uv run rayflow bridge send --universe 0 --channel 1 --value 255
```

You should see a fixture respond in the grandMA3 visualizer after Art-Net input is enabled for the matching local universe in grandMA3.

See the [First DMX Guide](./guides/first-dmx.md) for a complete tutorial.

---

## 5. Next Steps

- **[Build a Rig](./guides/building-a-rig.md)** — Load GDTF fixtures and create a virtual stage
- **[Record a Show](./guides/recording-a-show.md)** — Program cues for a song and export video
- **[Implementation Schedule](./implementation_schedule.md)** — See what's being built next

---

## Project Structure

```
rayflow/
├── src/rayflow/
│   ├── bridge/          # Art-Net / sACN protocol bridge
│   ├── fixtures/        # GDTF fixture handling
│   ├── visualizer/      # Web 3D stage visualizer
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
