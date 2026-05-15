# [RayFlow]

An agentic AI engine built to accelerate concert lighting programming and automate grandMA3 console workflows.

## Overview
This tool bridges the gap between show design logic and console execution. By utilizing agentic workflows, it automates tedious grandMA3 data tasks—including XML macro generation, sequence cue-stack construction, and fixture patching—allowing lighting designers to focus on the art of the look.

## Tech Stack
* Environment: Python (`uv`)
* AI Core: Built with Claude Code, Codex, and Gemini CLI
* Target: grandMA3 software / OSC / Art-Net / sACN workflows

# Vibe Coding Template

> **A lean, practical template for AI-assisted development supporting multiple AI coding tools.**

**Version 2.0** — Multi-Tool Template (Claude Code, Gemini CLI, Codex CLI, Antigravity)

---

## 🎯 What This Template Provides

This is a **Vibe Coding template** designed for "medium sophistication" AI-assisted development. It provides:

- ✅ **Multi-tool AI guidance** — Works with Claude Code, Gemini CLI, Codex CLI, and Antigravity
- ✅ **Session management** — Structured workflows for starting, working, and closing sessions
- ✅ **Cross-tool handoff** — Optional cli-continues integration for seamless context transfer
- ✅ **Quality gates** — Pre-commit checks, linting, testing, and health checks
- ✅ **Development standards** — Coding guidelines, checklists, and best practices
- ✅ **Documentation structure** — MkDocs-ready documentation with templates
- ✅ **Markdown fetcher** — Convert web URLs to clean Markdown (80% token reduction)
- ✅ **Working defaults** — Everything works out of the box

**Philosophy**: Practical patterns proven in real-world projects (cfb_model, PanicStats, JamBandNerd).

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **uv** ([Install](https://github.com/astral-sh/uv))
- **Git** for version control

### Quick Start

1. **Use this template:**
   ```bash
   # Clone or use as GitHub template
   git clone https://github.com/your-username/Vibe-Coding.git
   cd Vibe-Coding
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Read the agent guidance:**
   ```bash
   # Start here for AI-assisted development
   cat AGENTS.md

   # Or for your specific tool:
   cat CLAUDE.md    # Claude Code
   cat GEMINI.md    # Gemini CLI
   ```

4. **Start a session:**
   - Check branch: `git branch` (never work on `main`)
   - Create feature branch: `git checkout -b feat/your-feature`
   - Read: `.agent/CONTEXT.md`
   - Follow: `.agent/skills/start-session/SKILL.md`

### For AI Coding Tools

**All tools read the same files:**
- `AGENTS.md` — Multi-tool AI guidance (start here)
- `.agent/CONTEXT.md` — Current project state
- `.agent/skills/` — Task workflows (start-session, end-session)
- `.codex/QUICKSTART.md` — Essential commands

**Tool-specific entry points:**
- **Claude Code**: Reads `CLAUDE.md` → redirects to `AGENTS.md`
- **Gemini CLI**: Reads `GEMINI.md` → redirects to `AGENTS.md`
- **Codex/Antigravity**: Reads `AGENTS.md` directly

---

## 📂 Project Structure

```
Vibe-Coding/
├── AGENTS.md                   # Multi-tool AI guidance (READ FIRST)
├── CLAUDE.md                   # Redirect for Claude Code
├── GEMINI.md                   # Redirect for Gemini CLI
├── README.md                   # This file
│
├── .agent/                     # Active session management
│   ├── CONTEXT.md              # Entry point (project snapshot)
│   ├── skills/                 # Reusable task workflows
│   │   ├── CATALOG.md          # Skills index
│   │   ├── start-session/      # Session initialization
│   │   └── end-session/        # Session closing
│   └── workflows/              # Automation scripts
│       └── health-check.md     # Pre-commit validation
│
├── .codex/                     # Read-only context cache
│   ├── README.md               # Purpose explanation
│   ├── MAP.md                  # Project tree
│   └── QUICKSTART.md           # Essential commands
│
├── src/                        # Source code
│   └── vibe_coding/
│       └── utils/
│
├── tests/                      # Test suite
│   ├── api/
│   ├── core/
│   ├── data/
│   └── models/
│
├── docs/                       # Documentation (MkDocs)
│   ├── index.md
│   ├── project_charter.md
│   ├── implementation_schedule.md
│   ├── development_standards.md
│   ├── checklists.md
│   └── architecture/
│
├── session_logs/               # Session history
│   ├── README.md
│   ├── TEMPLATE.md
│   └── YYYY-MM-DD/
│
├── scripts/                    # Utility scripts
├── config/                     # Configuration files
├── pyproject.toml              # Dependencies and tooling
└── mkdocs.yml                  # Documentation config
```

---

## 🔧 Essential Commands

### Development Loop

```bash
# Format and lint
uv run ruff format . && uv run ruff check .

# Run tests
uv run pytest

# Run tests quietly
uv run pytest -q

# Health check (before commits)
# Follow steps in .agent/workflows/health-check.md
```

### Documentation

```bash
# Serve docs locally
mkdocs serve  # http://127.0.0.1:8000

# Build docs
mkdocs build
```

### Git Workflow

```bash
# CRITICAL: Never work on main
git branch

# Create feature branch
git checkout -b feat/<feature-name>

# Commit with conventional format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
git commit -m "docs: update documentation"
```

---

## 🤖 Multi-Tool AI Support

This template works with all major AI coding tools:

### Claude Code (claude.ai/code)
- Entry: `CLAUDE.md` → `AGENTS.md`
- Skills: `.agent/skills/`
- Context: `.agent/CONTEXT.md`

### Gemini CLI
- Entry: `GEMINI.md` → `AGENTS.md`
- Quick ref: `.codex/QUICKSTART.md`

### Codex CLI / Antigravity (VS Code fork)
- Entry: `AGENTS.md`
- Map: `.codex/MAP.md`

### Session Handoff (cli-continues)
- Docs: `docs/tools/cli-continues.md`
- Workflow: `.agent/workflows/session-handoff.md`
- Optional Node.js 22+ tool for cross-tool session transfer

**All tools share:**
- Same session logging format
- Same quality gates
- Same essential commands
- Same guardrails
- Optional cli-continues for context handoff

---

## 📖 Key Documentation

### For Getting Started
- `AGENTS.md` — Multi-tool AI guidance (read first)
- `.agent/CONTEXT.md` — Current project state
- `.codex/QUICKSTART.md` — Essential commands
- `docs/template_starting_guide.md` — Adapt template for your project

### For Development
- `.agent/skills/CATALOG.md` — Available workflows
- `docs/development_standards.md` — Coding standards
- `docs/checklists.md` — Quality gates
- `docs/implementation_schedule.md` — Current priorities

### For Reference
- `.codex/MAP.md` — Full project tree
- `docs/architecture/` — Architecture decisions
- `session_logs/` — Development history
- `docs/knowledge_base.md` — Solutions and patterns

---

## ✅ Quality Gates

### Pre-Commit Checklist
- [ ] Code formatted: `uv run ruff format .`
- [ ] Linting passes: `uv run ruff check .`
- [ ] Tests pass: `uv run pytest`
- [ ] No secrets in code
- [ ] Branch is not `main`

### Pre-Merge Checklist
- [ ] All pre-commit checks pass
- [ ] Session log created
- [ ] Documentation updated
- [ ] Implementation schedule updated
- [ ] Tests cover new code

---

## 🎓 Adapting This Template

When starting a new project:

1. **Read the Template Starting Guide**: `docs/template_starting_guide.md`
2. **Update project metadata**: Edit `pyproject.toml` and `README.md`
3. **Customize AGENTS.md**: Add project-specific critical rules
4. **Update .agent/CONTEXT.md**: Replace template notes with your project details
5. **Configure docs**: Update `mkdocs.yml` navigation
6. **Create initial tasks**: Populate `docs/implementation_schedule.md`

See `docs/template_starting_guide.md` for detailed instructions.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Create a feature branch: `git checkout -b feat/<name>`
2. Follow development standards: See `docs/development_standards.md`
3. Run health checks: Follow `.agent/workflows/health-check.md`
4. Create session log: See `session_logs/TEMPLATE.md`
5. Open pull request with clear description

---

## 📋 Session Workflow

Every development session should:

**Start:**
1. Check branch: `git branch` (create feature branch if on `main`)
2. Read: `.agent/CONTEXT.md`
3. Load: `.agent/skills/start-session/SKILL.md`
4. Plan before implementing

**During:**
- Follow: `.agent/skills/CATALOG.md` for common tasks
- Track: `docs/implementation_schedule.md` for priorities
- Document: Decisions and issues as you go

**End:**
1. Run: `.agent/workflows/health-check.md`
2. Create: Session log in `session_logs/YYYY-MM-DD/NN.md`
3. Update: `docs/implementation_schedule.md` if tasks completed
4. Load: `.agent/skills/end-session/SKILL.md`

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🌟 Credits

Template patterns derived from successful projects:
- **cfb_model** — Comprehensive session management and context loading
- **PanicStats** — Skill-based workflows and entry points
- **JamBandNerd** — Boot order, context budget, triage matrix

**Vibe Coding System** — Philosophy and methodology by Connor Kitchings

---

**Version**: 2.0 (Multi-Tool Template)
**Last Updated**: 2026-02-11
**Status**: Ready for use
