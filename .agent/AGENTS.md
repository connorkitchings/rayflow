# AGENTS.md — Project Agent Operating Manual

> **Purpose:** Define AI agent roles, handoff patterns, and operating rules for AI-assisted development.

> **Core Principles**: See `.agent/PRINCIPLES.md` for the 11 operating principles that guide every session.

---

## Agent Roster and Mandates

### Navigator (Front Door)

**Role**: Request triage and task routing

**Responsibilities**:
- Classify incoming requests and produce a 3-7 line plan
- Select appropriate Specialist(s) and attach minimal context bundle
- Confirm scope, definition of done, and constraints
- Open or update issue or schedule task if applicable
- **Context budget**: ≤2.5k tokens on cold start; fetch on-demand docs only as needed

**Key Files**:
- `.agent/CONTEXT.md` - Project snapshot (READ FIRST)
- `.agent/skills/CATALOG.md` - Available skills
- `docs/implementation_schedule.md` - Current priorities
- `.agent/skills/start-session/SKILL.md` - Session start workflow
- `.agent/skills/end-session/SKILL.md` - Session close workflow

---

### Researcher

**Role**: Information gathering and analysis

**Responsibilities**:
- Find up-to-date information on lighting protocols, grandMA3 features, GDTF spec
- Return concise brief with links and risks/gaps called out
- Verify data discrepancies across multiple sources
- **Context budget**: ≤1.5k tokens initial, then targeted fetches

**Key Files**:
- `docs/knowledge_base.md` - Protocol specs, rate limits, gotchas
- `data/fixtures/` - GDTF fixture library

---

### FixtureEngineer

**Role**: GDTF fixture parsing, channel mapping, and patching

**Responsibilities**:
- Parse GDTF fixture files and extract channel definitions
- Map DMX addresses to fixture channels (dimmer, pan, tilt, color, gobo)
- Build and manage fixture library
- Handle fixture patching to universes
- **Context budget**: ≤2k tokens initial, then targeted fetches

**Key Files**:
- `src/rayflow/fixtures/` - GDTF parsing and fixture management
- `data/fixtures/` - GDTF fixture files
- `.agent/skills/gdtf-fixture/SKILL.md` - GDTF workflow

---

### ProtocolBridge

**Role**: Art-Net, sACN, OSC, and backend adapter implementation

**Responsibilities**:
- Implement Art-Net send/receive (ArtDMX packets over UDP)
- Implement sACN/E1.31 send/receive (multicast/unicast)
- Implement fixture-aware DMX output and backend adapter contracts
- Implement OSC communication with grandMA3 onPC only as a gated compatibility adapter
- Ensure proper universe addressing and channel mapping
- **Context budget**: ≤2k tokens initial

**Key Files**:
- `src/rayflow/bridge/` - Protocol bridge implementation
- `docs/architecture/control-backend-direction.md` - Backend-neutral adapter strategy
- `.agent/skills/art-net-bridge/SKILL.md` - Art-Net/sACN workflow
- `.agent/skills/ma3-workflow/SKILL.md` - grandMA3 OSC workflow

---

### BackendRenderer

**Role**: Fixture-aware rendering and output evidence

**Responsibilities**:
- Resolve RayFlow cue intent against GDTF fixture capabilities
- Render cue states into universe/channel frames
- Produce dry-run artifacts and backend evidence packets
- Keep renderer logic independent of MA3, QLC+, or any single controller
- **Context budget:** ≤2k tokens initial

**Key Files**:
- `src/rayflow/fixtures/` - GDTF parsing and channel mapping
- `src/rayflow/bridge/` - Art-Net/sACN send and receive
- `src/rayflow/shows/` - Show and cue models
- `docs/architecture/control-backend-direction.md` - Adapter contract direction

### VisualizerDev

**Role**: Optional web-based visualizer development

**Responsibilities**:
- Build Flask backend for DMX-to-WebSocket bridge
- Implement Three.js 3D scene with stage, truss, fixtures
- Map DMX channel values to visual properties (intensity, color, beam)
- Implement camera controls and beam visualization
- **Context budget**: ≤2k tokens initial

**Key Files**:
- `src/rayflow/visualizer/` - Web visualizer implementation
- `.agent/skills/dmx-universe/SKILL.md` - DMX universe management

---

## Subagent Strategy

Use subagents to keep the main context window clean and focused.

**When to use subagents:**
- Research on lighting protocols, GDTF spec, grandMA3 OSC API
- Exploration of Three.js patterns and examples
- Parallel analysis of fixture channel mappings
- Complex problems that benefit from focused, dedicated attention

**Best practices:**
- One task per subagent for focused execution
- Give clear, specific instructions to the subagent
- Review subagent results carefully before incorporating
- For complex problems, throw more compute at it via subagents

**Key Files**:
- `.agent/workflows/workflow-orchestration.md` - Task management patterns

---

## Handoff Packet Template (Navigator → Specialist)

When routing a task, Navigator provides:

1. **Task goal and definition of done** - Clear success criteria
2. **Links to relevant files** - File paths and line anchors
3. **Constraints** - Timebox, scope, context budget
4. **Expected artifacts** - Code paths, tests, docs to update
5. **Rollback plan** - If applicable

**Example**:

```text
Task: Implement Art-Net sender for universe 1
DoD: Send DMX values to visualizer, packets verified with Wireshark
Files: src/rayflow/bridge/artnet.py:1-50
Constraints: ≤2hr, UDP only, no sACN
Artifacts: Sender class, tests, usage example
Rollback: Revert commit
```

---

## Handoff Packet Caps

Keep context minimal when routing tasks:

- **Navigator → Specialist**: Max 10 bullets + max 5 file pointers
- **Avoid**: Pasting large file excerpts; use file paths with line numbers
- **Fetch on-demand**: Load docs only when needed for current task
- **If noisy**: Summarize in session log and restart

---

## Operating Rules

1. **Every PR must include tests** when logic is added or changed
2. **Use ruff for format and lint**; pytest must pass locally before PR
3. **Update docs** when behavior or APIs change
4. **Never commit secrets**; respect robots.txt and ToS during ingestion
5. **Link to schedule tasks** in commit messages and PRs
6. **Session logs required** for all work (see start-session/end-session skills)
7. **Pre-commit hooks** must pass before pushing
8. **Test with real protocols** — verify Art-Net/sACN packets with network tools

---

## Core Principles

The full set of 11 operating principles are documented in `.agent/PRINCIPLES.md`, including:

- **Plan First** — Plan mode for non-trivial tasks
- **Ship Small, Stay Simple** — Minimal, focused changes
- **Test-Driven** — Every feature needs tests
- **Minimal & Reversible** — Touch only what's necessary
- **No Lazy Fixes** — Find root causes
- **Elegant When Non-Trivial** — Consider better solutions
- **Verify Before Done** — Prove it works
- **Self-Improve** — Capture lessons from corrections
- **Autonomous Bug Fixing** — Just fix it
- **Subagent Strategy** — Keep context clean
- **Audited Actions** — Log important operations

---

## Common Flows (Skills)

For detailed checklists, see `.agent/skills/CATALOG.md`:

### Lighting Protocols
- **Art-Net Bridge**: Send/receive DMX via Art-Net
- **DMX Universe**: Manage universes and channel mapping

### Fixture Management
- **GDTF Fixture**: Load and parse GDTF fixture profiles

### Console Integration
- **MA3 Workflow**: grandMA3 onPC OSC control

### Session Management
- **Start Session**: Initialize development session
- **End Session**: Close session with logging

**All skills**: See `.agent/skills/CATALOG.md`

---

## Definition Of Done (Per PR)

- [ ] Small, focused diff; linked to schedule task or issue
- [ ] Tests added/updated; pytest green locally
- [ ] Ruff format and lint clean (`uv run ruff format . && uv run ruff check .`)
- [ ] Docs updated where relevant
- [ ] Session log updated with outcomes
- [ ] No secrets or credentials in code
- [ ] Pre-commit hooks pass

---

## Escalation And Safety

### When Blocked By External Sites

- Reduce request rate; check configuration for limits
- Switch to backup sources (if available)
- Cache responses to minimize repeated requests
- Document rate limit issues in knowledge base

### For Security/Data Integrity Issues

- Never bypass authentication or validation
- Log security events appropriately

### When Information Is Uncertain

- Return assumptions and risks explicitly
- Ask for clarification via session log or issue
- Cite sources for all data verification

### CI Failures

- Open failed job in GitHub Actions
- Read failing step logs completely
- Reproduce locally with same command from CI
- Check recent commits for breaking changes

---

## Glossary (Agent Terms)

- **Context budget**: Estimated token allowance for startup or a handoff
- **Handoff packet**: Minimal set of links, goals, and constraints to start work
- **DoD**: Definition of Done - acceptance criteria for task completion
- **Session log**: Work log created using start-session and end-session skills
- **DMX**: Digital Multiplex — 512-channel lighting control protocol
- **Art-Net**: DMX over UDP protocol (port 6454)
- **sACN**: Streaming ACN / E1.31 — DMX over multicast UDP
- **GDTF**: General Device Type Format — open fixture definition
- **MVR**: My Virtual Rig — scene sharing format based on GDTF
- **OSC**: Open Sound Control — network protocol for console control

---

## Documentation Map

**Primary Guides**:

- `.agent/CONTEXT.md` - Entry point: project snapshot, current status, critical rules
- `.agent/PRINCIPLES.md` - Core operating principles (11 rules for every session)
- `.agent/tasks/lessons.md` - Self-improvement: capture lessons from corrections
- `CONTRIBUTING.md` - Start here for workflow
- `docs/project_charter.md` - Project goals and scope
- `docs/implementation_schedule.md` - Current priorities

**Technical Docs**:

- `docs/architecture/` - Architecture decisions
- `.agent/skills/start-session/SKILL.md` - Session kickoff workflow
- `.agent/skills/end-session/SKILL.md` - Session closing workflow
- `.agent/workflows/health-check.md` - Pre-commit validation
- `docs/development_standards.md` - Code quality standards

---

## Maintenance

- **Quarterly**: Review this file for alignment with schedule and system changes
- **Keep file ≤8,000 tokens**: Prefer links to long explanations
- **Update agent mandates**: As new patterns emerge or roles evolve
- **Sync with CONTRIBUTING.md**: Ensure consistency with primary guide
