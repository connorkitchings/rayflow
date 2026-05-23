# Skills Catalog

> **Purpose**: Index of all available skills for common development tasks. Skills are reusable workflows with clear contracts.

---

## Core Session Skills

### start-session
**Path**: `.agent/skills/start-session/SKILL.md`
**Purpose**: Initialize a new development session safely
**Triggers**: "start", "kickoff", "begin", "new task", "hello"
**Outputs**: Planning document with roadmap options
**Use when**: Starting any new development session

### end-session
**Path**: `.agent/skills/end-session/SKILL.md`
**Purpose**: Close session properly with logging and handoff
**Triggers**: "end", "close", "finish", "wrap up", "done"
**Outputs**: Session log, health check results, handoff notes
**Use when**: Completing any development session

---

## Lighting Protocol Skills

### art-net-bridge
**Path**: `.agent/skills/art-net-bridge/SKILL.md`
**Purpose**: Send and receive DMX via Art-Net protocol
**Triggers**: "art-net", "send dmx", "receive dmx", "artdmx", "udp lighting"
**Outputs**: Art-Net sender/receiver implementation, packet verification
**Use when**: Implementing Art-Net communication, testing DMX output

### dmx-universe
**Path**: `.agent/skills/dmx-universe/SKILL.md`
**Purpose**: Manage DMX universes, channel addressing, and patching
**Triggers**: "universe", "dmx address", "channel map", "patch fixture"
**Outputs**: Universe data structures, channel mapping logic
**Use when**: Working with DMX addressing, fixture patching, channel allocation

### backend-adapter-design
**Path**: `docs/architecture/control-backend-direction.md`
**Purpose**: Design or update backend-neutral output adapters
**Triggers**: "backend", "adapter", "renderer", "qlc", "direct dmx", "output target"
**Outputs**: Adapter contract, dry-run/apply/evidence shape, backend capability notes
**Use when**: Implementing the Phase 8 control loop, fixture-aware DMX rendering, QLC+ WebSocket support, or backend selection

---

## Fixture Management Skills

### gdtf-fixture
**Path**: `.agent/skills/gdtf-fixture/SKILL.md`
**Purpose**: Load, parse, and manage GDTF fixture profiles
**Triggers**: "gdtf", "fixture", "load profile", "channel definition", "parse gdtf"
**Outputs**: Parsed fixture data, channel definitions, fixture library entries
**Use when**: Adding new fixtures, parsing GDTF files, building fixture library

---

## Console Compatibility Skills

### ma3-workflow
**Path**: `.agent/skills/ma3-workflow/SKILL.md`
**Purpose**: grandMA3 onPC compatibility via OSC and verified import/export workflows
**Triggers**: "grandma3", "ma3", "osc control", "macro", "cue stack"
**Outputs**: OSC commands, cue stack builders, verified import/export workflows
**Use when**: Working on the MA3 compatibility track, verifying MA3 workflows, building cue sequences, or exporting MA3 artifacts

---

## Utility Skills

### context-audit
**Path**: `.agent/skills/context-audit/`
**Purpose**: Audit and optimize context loading
**Triggers**: "audit context", "context size", "optimize loading"
**Outputs**: Context usage report, optimization recommendations
**Use when**: Context budget is exceeded or session is slow

### doc-writer
**Path**: `.agent/skills/doc-writer/SKILL.md`
**Purpose**: Create or update technical documentation
**Triggers**: "documentation", "docs", "readme", "write docs", "update docs"
**Outputs**: Documentation file following project standards
**Use when**: Writing README, ADRs, guides, or API docs

### test-writer
**Path**: `.agent/skills/test-writer/SKILL.md`
**Purpose**: Write effective tests following best practices
**Triggers**: "test", "testing", "pytest", "unit test", "integration test"
**Outputs**: Test file with fixtures and comprehensive coverage
**Use when**: Adding tests for features or bug fixes

---

## Workflow References

### health-check
**Path**: `.agent/workflows/health-check.md`
**Purpose**: Run pre-commit quality checks
**Triggers**: "health check", "validate", "pre-commit"
**Use when**: Before creating commits or PRs

### session-handoff
**Path**: `.agent/workflows/session-handoff.md`
**Purpose**: Transfer session context between AI coding tools
**Triggers**: "handoff", "switch tool", "continue session", "cross-tool"
**Use when**: Switching between Claude, Gemini, Codex, OpenCode

---

## How to Use Skills

### 1. Discover Available Skills
Browse this catalog to find skills matching your task.

### 2. Load Skill Documentation
Read the skill's SKILL.md file to understand:
- When to use it
- What inputs it needs
- What outputs it produces
- Step-by-step process

### 3. Execute Skill Contract
Follow the skill's documented steps exactly. Skills are designed to be:
- **Repeatable**: Same inputs → same outputs
- **Testable**: Clear success criteria
- **Composable**: Can be chained together

### 4. Document Skill Usage
In your session log, note which skills were used and any deviations from the standard process.

---

## Creating New Skills

When creating a new skill:

1. **Identify Repeated Pattern**: Is this task done frequently?
2. **Define Clear Contract**: Inputs, outputs, success criteria
3. **Create Skill Directory**: `.agent/skills/<skill-name>/`
4. **Write SKILL.md**: Use frontmatter and clear sections
5. **Add to Catalog**: Document triggers and purpose
6. **Test Skill**: Verify it works in multiple contexts

**Skill template:**
```markdown
---
name: skill-name
description: "Brief description"
metadata:
  trigger-keywords: "keyword1, keyword2"
  trigger-patterns: "^pattern1, ^pattern2"
---

# Skill Name

## When to Use
## Inputs
## Steps
## Validation
## Common Mistakes
## Links
```

---

## Skill Maintenance

Skills should be:
- **Updated** when workflows change
- **Deprecated** when no longer needed
- **Versioned** when major changes occur
- **Tested** regularly to ensure accuracy

**Ownership**: Skills are maintained by the project. Anyone can propose updates via PR.

---

## Links

- Context: `.agent/CONTEXT.md`
- Agent guidance: `AGENTS.md`
- Start session: `.agent/skills/start-session/SKILL.md`
- End session: `.agent/skills/end-session/SKILL.md`
- Health check: `.agent/workflows/health-check.md`

---

**Skills are tools. Use them to maintain consistency and quality.**
