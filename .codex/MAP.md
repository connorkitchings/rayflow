# Project Map

> **Purpose**: Visual project structure for quick orientation.

---

## Root Level

```
rayflow/
├── AGENTS.md                   # Multi-tool AI guidance (read first)
├── CLAUDE.md                   # Redirect to AGENTS.md
├── GEMINI.md                   # Redirect to AGENTS.md
├── README.md                   # Project overview
├── CHANGELOG.md                # Version history
├── pyproject.toml              # Dependencies and tooling
├── mkdocs.yml                  # Documentation config
└── .pre-commit-config.yaml     # Pre-commit hooks
```

---

## AI Agent Structure

```
.agent/                         # Active session management
├── CONTEXT.md                  # Entry point (project snapshot)
├── PLAYBOOK.md                 # Dynamic memory and patterns
├── PRINCIPLES.md               # 11 operating principles
├── skills/                     # Reusable task workflows
│   ├── CATALOG.md              # Skills index
│   ├── start-session/
│   │   └── SKILL.md            # Session initialization
│   ├── end-session/
│   │   └── SKILL.md            # Session closing
│   ├── art-net-bridge/
│   │   └── SKILL.md            # Art-Net send/receive
│   ├── dmx-universe/
│   │   └── SKILL.md            # DMX universe management
│   ├── gdtf-fixture/
│   │   └── SKILL.md            # GDTF fixture parsing
│   └── ma3-workflow/
│       └── SKILL.md            # grandMA3 onPC integration
└── workflows/                  # Automation scripts
    └── health-check.md         # Pre-commit validation
```

---

## Source Code

```
src/rayflow/
├── __init__.py
├── cli.py                      # CLI entry point (typer)
├── bridge/                     # Art-Net / sACN protocol bridge
│   ├── __init__.py
│   ├── artnet.py               # Art-Net sender/receiver
│   └── sacn.py                 # sACN/E1.31 sender/receiver
├── fixtures/                   # GDTF fixture handling
│   ├── __init__.py
│   ├── parser.py               # GDTF file parser
│   ├── library.py              # Fixture library management
│   └── patch.py                # Fixture patching to universes
└── visualizer/                 # Web 3D stage visualizer
    ├── __init__.py
    ├── server.py               # Flask backend
    └── static/                 # Three.js frontend
```

---

## Data

```
data/
├── fixtures/                   # GDTF fixture files (.gdtf.zip)
└── shows/                      # Show configurations
```

---

## Tests

```
tests/
├── __init__.py
├── test_bridge.py              # Art-Net/sACN bridge tests
├── test_fixtures.py            # GDTF parser tests
├── test_visualizer.py          # Visualizer tests
└── test_cli.py                 # CLI tests
```

---

## Documentation

```
docs/
├── index.md                    # Documentation hub
├── project_charter.md          # Project vision and goals
├── implementation_schedule.md  # Current priorities
├── development_standards.md    # Coding standards
├── checklists.md               # Quality gates
├── knowledge_base.md           # Solutions and patterns
├── runbook.md                  # Operations guide
├── security.md                 # Security guidelines
├── glossary.md                 # Project terminology
├── getting_started.md          # Onboarding guide
├── architecture/
│   ├── system_overview.md      # Architecture overview
│   └── adr/                    # Architecture decisions
└── archive/                    # Archived docs
```

---

## Scripts

```
scripts/
├── cli.py                      # CLI interface
└── init_session.py             # Session initialization
```

---

## Session Logs

```
session_logs/
├── README.md                   # Logging guidelines
├── TEMPLATE.md                 # Session log template
└── YYYY-MM-DD/                 # Daily session logs
```

---

## Key Paths for Common Tasks

### Starting a Session
1. `AGENTS.md` - Read first
2. `.agent/CONTEXT.md` - Current state
3. `.agent/skills/start-session/SKILL.md` - Session workflow
4. `session_logs/` - Review last 3-5 logs

### During Development
- `src/rayflow/` - Source code
- `tests/` - Test suite
- `docs/implementation_schedule.md` - Current priorities
- `.agent/skills/CATALOG.md` - Available workflows

### Closing a Session
1. `.agent/skills/end-session/SKILL.md` - Closing workflow
2. `session_logs/YYYY-MM-DD/NN.md` - Create log
3. `.agent/workflows/health-check.md` - Run checks
4. `docs/implementation_schedule.md` - Update if needed

### Documentation
- `docs/index.md` - Start here
- `mkdocs.yml` - Navigation structure
- Run: `mkdocs serve` for local preview

---

**Last Updated**: 2026-05-15
**Update Frequency**: When major structural changes occur
