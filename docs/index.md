# RayFlow Documentation

For project overview and setup instructions, see the project README.

RayFlow's current usable workflow is show/rig authoring, show versioning,
MA3 compatibility bundle export, MA3 Timecode XML generation from captured
2.3.2.0 schemas, and dry-run-safe OSC cue pushing. The project direction has
pivoted: RayFlow's core should be backend-neutral show intent plus a
fixture-aware DMX renderer, with Art-Net/sACN, QLC+ WebSockets, and grandMA3
handled as adapters.

## Navigation

- **[Getting Started](./getting_started.md)** — Install grandMA3 onPC, set up RayFlow, send your first DMX
- **[Project Brief](./project_brief.md)** — Project goals, scope, and timeline
- **[Project Charter](./project_charter.md)** — Detailed technical context and architecture
- **[Implementation Schedule](./implementation_schedule.md)** — Current project timeline and milestones
- **[System Overview](./architecture/system_overview.md)** — How the backend-neutral components fit together
- **[Control Backend Direction](./architecture/control-backend-direction.md)** — Current architecture pivot and adapter strategy
- **[Two-Layer Design](./architecture/two-layer-design.md)** — Architecture deep dive
- **[Current Workflow](./guides/current-workflow.md)** — Build, version, export, and dry-run show outputs
- **[Development Standards](./development_standards.md)** — Coding standards and workflow
- **[Checklists](./checklists.md)** — Quality gates and review checklists
- **[Knowledge Base](./knowledge_base.md)** — Protocol specs, patterns, and accumulated knowledge
- **[Troubleshooting](./troubleshooting.md)** — Common issues and solutions
- **[Glossary](./glossary.md)** — Lighting industry terms and project acronyms

## Guides

- **[grandMA3 onPC Setup](./guides/grandma3-setup.md)** — Install and configure grandMA3 on macOS
- **[grandMA3 Learning Resources](./guides/grandma3-learning-resources.md)** — Version-specific MA3 reference sources and tutorial links
- **[Current Workflow](./guides/current-workflow.md)** — Practical RayFlow workflow available today
- **[First DMX](./guides/first-dmx.md)** — Send your first DMX values from Python
- **[Building a Rig](./guides/building-a-rig.md)** — Create a virtual stage with GDTF fixtures
- **[Recording a Show](./guides/recording-a-show.md)** — Program cues for a song and export video
