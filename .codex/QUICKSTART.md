# Quick Start

> **Purpose**: Essential commands for common operations. Copy-paste ready.

---

## Setup

```bash
# First time setup
uv sync

# Install lighting extras (Art-Net, GDTF)
uv sync --extra lighting

# Install visualizer extras (Flask, WebSocket)
uv sync --extra visualizer
```

---

## Development

```bash
# Format and lint code
uv run ruff format . && uv run ruff check .

# Run all tests
uv run pytest

# Run tests quietly
uv run pytest -q

# Run tests with verbose output
uv run pytest -vv

# Run specific test file
uv run pytest tests/test_bridge.py

# Run tests matching pattern
uv run pytest -k "test_artnet"
```

---

## Health Check

```bash
# Run pre-commit checks (format, lint, test)
# See .agent/workflows/health-check.md for steps
```

---

## Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build

# Documentation available at: http://127.0.0.1:8000
```

---

## Git Workflow

```bash
# Check current branch (CRITICAL - never work on main)
git branch

# Create feature branch
git checkout -b feat/<feature-name>

# Check status
git status

# Stage changes
git add <files>

# Commit with conventional commit format
git commit -m "feat: add art-net sender"
git commit -m "fix: resolve universe addressing bug"
git commit -m "docs: update fixture guide"
git commit -m "test: add dmx channel tests"
git commit -m "refactor: simplify bridge module"
git commit -m "chore: update dependencies"

# Push to remote
git push origin <branch-name>
```

---

## Session Management

```bash
# Start a new session
# 1. Check branch: git branch
# 2. Read: .agent/CONTEXT.md
# 3. Load: .agent/skills/start-session/SKILL.md

# End a session
# 1. Create log: session_logs/YYYY-MM-DD/NN.md
# 2. Health check: See .agent/workflows/health-check.md
# 3. Load: .agent/skills/end-session/SKILL.md
```

---

## Common Tasks

```bash
# Add new dependency
uv add <package-name>

# Add dev dependency
uv add --dev <package-name>

# Remove dependency
uv remove <package-name>

# Update dependencies
uv sync

# Check outdated dependencies
uv pip list --outdated
```

---

## grandMA3 onPC

```bash
# grandMA3 onPC is a standalone macOS application
# Download from: https://www.malighting.com/downloads/products/grandma3/
# Default OSC port: 8000
# Default Art-Net port: 6454
```

---

## Troubleshooting

```bash
# Lint failures - auto-fix
uv run ruff check . --fix

# Import errors - sync dependencies
uv sync

# Test failures - verbose output
uv run pytest -vv

# Test failures - last failed only
uv run pytest --lf

# Clean Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Project Structure

```
rayflow/
├── src/rayflow/       # Source code (bridge, fixtures, visualizer)
├── data/              # GDTF fixtures and show configs
├── tests/             # Test suite
├── docs/              # Documentation
├── scripts/           # Utility scripts
├── .agent/            # AI session management
└── session_logs/      # Session history
```

---

## Essential Files

- `AGENTS.md` - AI agent guidance (read first)
- `README.md` - Project overview
- `.agent/CONTEXT.md` - Current project state
- `.agent/skills/CATALOG.md` - Available workflows
- `docs/implementation_schedule.md` - Current priorities
- `session_logs/` - Recent work history

---

**Keep this file updated when core commands or workflows change.**
