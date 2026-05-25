# RayFlow Documentation

> AI-assisted lighting show authoring — build rigs, program cues, render through fixture-aware DMX, and output via Art-Net/sACN or export to grandMA3.

## Architecture

| Document | Description |
|----------|-------------|
| [System Overview](./architecture/system_overview.md) | How RayFlow's backend-neutral components fit together |
| [Control Backend Direction](./architecture/control-backend-direction.md) | Adapter strategy and pivot rationale |
| [Backend Adapter Contract](./architecture/backend-adapter-contract.md) | Interface contract for output backends |
| [Renderer](./architecture/renderer.md) | Fixture-aware DMX rendering from cue intent |
| [Phase 5 Architecture](./phase5_architecture.md) | Show/rig data models and authoring design |
| [Two-Layer Design](./architecture/two-layer-design.md) | Historical architecture deep dive (merged into system overview) |
| [Phase 2 Bridge Design](./architecture/phase2-bridge-design.md) | Historical bridge design doc (archived) |

## Guides

| Document | Description |
|----------|-------------|
| [Getting Started](./getting_started.md) | Install, set up, and send your first DMX |
| [Current Workflow](./guides/current-workflow.md) | Build, version, export, and dry-run show outputs |
| [First DMX](./guides/first-dmx.md) | Send DMX values from Python |
| [Building a Rig](./guides/building-a-rig.md) | Create a virtual stage with GDTF fixtures |
| [QLC+ Setup](./guides/qlcplus-setup.md) | QLC+ WebSocket setup (experimental) |
| [grandMA3 onPC Setup](./guides/grandma3-setup.md) | Install and configure grandMA3 on macOS |
| [grandMA3 Learning Resources](./guides/grandma3-learning-resources.md) | MA3 reference sources and tutorial links |

## Project Management

| Document | Description |
|----------|-------------|
| [Project Brief](./project_brief.md) | Project goals, scope, and timeline |
| [Project Charter](./project_charter.md) | Detailed technical context |
| [Implementation Schedule](./implementation_schedule.md) | Phase timeline and milestones |
| [CHANGELOG](./CHANGELOG.md) | Release history |

## Standards & Reference

| Document | Description |
|----------|-------------|
| [Development Standards](./development_standards.md) | Coding standards and workflow |
| [AI Interaction Contract](./ai_interaction_contract.md) | How AI agents should interact with this project |
| [CLI Reference](./cli-reference.md) | Complete command-line interface reference |
| [Glossary](./glossary.md) | Lighting industry terms and project acronyms |
| [Checklists](./checklists.md) | Quality gates and review checklists |
| [Troubleshooting](./troubleshooting.md) | Common issues and solutions |
| [Knowledge Base](./knowledge_base.md) | Protocol specs, patterns, and accumulated knowledge |

## AI Agent Context

| Document | Description |
|----------|-------------|
| [MASTER_CONTEXT](./ai/MASTER_CONTEXT.md) | Comprehensive MA3 references for AI agents |
| [Agent AGENTS.md](../.agent/AGENTS.md) | AI agent guidance and skills |

## Research

See `docs/research/` for organized research materials:
- `agentic_show_control_architectures/` — AI-driven lighting system patterns
- `ai-lighting-patterns/` — AI-assisted lighting design approaches
- `design-concepts/` — Color theory, fixture types, GDTF/MVR formats
- `ma3-probes/` — grandMA3 protocol investigation results
- `programming-workflows/` — Console architecture, cue syntax, timecode, busking
- `protocols-and-systems/` — DMX, Art-Net, sACN, RDM, OSC references
- `raw_sources/` — Original research dumps
