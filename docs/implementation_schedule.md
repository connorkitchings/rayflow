# RayFlow — Implementation Schedule

**Status Legend:** ☐ Not Started · ▶ In Progress · ✅ Done · ⚠ Risk/Blocked

---

## Phase 1: Project Foundation

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Update pyproject.toml | rayflow package, lighting deps | ✅ Done | sacn, python-osc, artnet, gdtf-parser |
| Rewrite README.md | Project overview | ✅ Done | Architecture diagram, quick start |
| Rewrite project charter | Goals, scope, architecture | ✅ Done | Lighting domain focus |
| Update agent guidance | CONTEXT, AGENTS, CATALOG | ✅ Done | Lighting-specific roles and skills |
| Create src/rayflow/ structure | Package skeleton | ✅ Done | bridge/, fixtures/, visualizer/, cli.py |
| Create data/ structure | Fixture and show directories | ✅ Done | data/fixtures/, data/shows/ |

---

## Phase 2: Art-Net / sACN Bridge

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| DMX universe model | Universe data structure | ✅ Done | 512 channels, universe addressing, conflict detection |
| Art-Net sender | Send DMX via Art-Net | ✅ Done | ArtDMX packets, universe targeting, input validation |
| Art-Net receiver | Receive DMX from console | ✅ Done | Listen on port 6454 |
| sACN sender | Send DMX via sACN | ✅ Done | Using sacn library, fixed channel indexing |
| sACN receiver | Receive DMX via sACN | ✅ Done | Multicast or unicast |
| Bridge CLI | `rayflow bridge send/recv/status` commands | ✅ Done | Wired to real bridge classes, rich output |
| Bridge tests | Unit + integration tests | ✅ Done | 75 tests, 83% coverage |

---

## Phase 3: GDTF Fixture Support

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| GDTF parser | Load .gdtf.zip files | ✅ Done | Validates ZIP, parses description.xml, extracts modes/channels |
| Fixture library | Manage loaded fixtures | ✅ Done | Catalog, search, by manufacturer, fixture summaries |
| Channel mapping | Map DMX addresses to channels | ✅ Done | Concrete address maps with family classification and bounds checks |
| Fixture patching | Assign fixtures to universes | ✅ Done | In-memory GDTF-aware patches with channel maps and CLI smoke command |
| Sample fixtures | Checked-in real fixture samples | ✅ Done | 3 public GDTF samples with manifest and hashes |
| Fixture tests | Parser, library, and sample tests | ✅ Done | Real samples validated offline |

---

## Phase 4: grandMA3 onPC Integration

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| OSC connection | Connect to MA3 onPC | ✅ Done | Dry-run-safe About command plus optional feedback listener |
| Command sender | Send MA3 commands via OSC | ✅ Done | `/cmd` sender, `--execute` gate, feedback capture |
| Cue stack builder | Build cue sequences from Python | ✅ Done | Typed command builders, JSON cue stacks, dry-run-safe nested CLI |
| Import/export helpers | Generate only verified MA3 import/export formats | ✅ Done | MVR export with embedded GDTF files and mode info; observation capture script |
| MVR export | Export rig to MVR format | ✅ Done | Embedded GDTF files, scene/layer hierarchy, fixture addressing, 3D positions |
| Integration tests | Test against MA3 onPC | ✅ Done | 14 integration tests (OSC, fixture comparison, MVR export, Art-Net send) |

---

## Phase 5: Show & Rig Framework

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Architecture document | Phase 5 data model and design decisions | ✅ Done | `docs/phase5_architecture.md` |
| AI interaction contract | Framework for AI tooling | ✅ Done | `docs/ai_interaction_contract.md` |
| Rig data model | `Rig`, `Venue`, `FixtureSlot`, `Preset` dataclasses | ✅ Done | 11 dataclasses with validation, presets, rig templates, show overrides |
| Show data model | `Show`, `Song`, `Section`, `Cue`, `Vibe` dataclasses | ✅ Done | Links rig to audio, preset overrides |
| Rig CLI | `rayflow rig create/list/info/copy/add-fixture/add-preset/export-mvr` | ✅ Done | Manage rigs, export to MVR |
| Show CLI | `rayflow show create/list/info/add-section/add-cue/add-preset-override/context/export-mvr` | ✅ Done | Manage shows, load context bundle |
| Preset system | Named presets with attribute families | ✅ Done | Dimmer, position, color, beam, focus, gobo |
| Tests | Full test suite for models and CLI | ✅ Done | 296 tests (259 unit + 37 CLI/context), 84% coverage |
| Docs | Rig/show data model documentation | ✅ Done | `docs/phase5_architecture.md`, `docs/ai_interaction_contract.md`, `docs/prompts/show_builder.md` |

---

## Phase 6: AI Show Builder

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Audio section import | Import section markers from external tool | ✅ Done | `show import-sections`, JSON schema, sample file |
| Vibe generation | AI suggests color palettes and organizing principles | ✅ Done | `show set-vibe`, `Vibe.from_dict()`, enhanced prompt template |
| Cue generation | AI generates cues per section based on vibe | ✅ Done | `cue_generator.py`, `show generate-cues`, `show update-cue`, `show delete-cue`, `show renumber` |
| Interactive direction | User directs AI: "more energy here", "change to cool colors" | ✅ Done | `show set-song-meta`, `show update-section`, `show delete-section`, `show batch-update-cues` |
| MA3 push | Push generated cues to MA3 via existing OSC | ✅ Done | `show push-to-ma3`, `show push-section` |
| Tests | Unit + integration tests | ✅ Done | 80 new tests (section import, cue generator, push, CLI) |
| Docs | Updated prompts and Phase 6 completion docs | ✅ Done | `docs/prompts/show_builder.md`, `docs/implementation_schedule.md` |

---

## Phase 7: Export & Playback

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Sequence build hardening | `--sequence` option on push commands, sequence labeling | ✅ Done | `store_sequence`, `label_sequence`, `delete_sequence`, `clear_all` builders; CLI `--sequence` default 1 |
| MA3 show export | Export cues/rig to MA3-importable format | ✅ Done | `show export` writes MVR, dry-run OSC command list, README, and metadata bundle |
| Timecode integration | MA3 timecode triggers for cue playback | ▶ In Progress | `timecode_export.py` generates GMA3 XML from event-bearing MA3 2.3.2.0 XML capture; requires MA3 import/playback validation |
| Show library | Versioned show storage | ✅ Done | `show save/versions/restore/diff`; local YAML snapshots with metadata |
| Tests | Export/playback regression coverage | ▶ In Progress | Sequence, MA3 show export, show library, and timecode tests added; MA3 import/playback validation pending |

---

## Milestones

- **M1: Foundation Complete** — Phase 1 done, package structure ready
- **M2: First Light** — Phase 2 done, DMX flowing from Python to MA3
- **M3: Real Fixtures** — Phase 3 done, GDTF fixtures loaded and patched
- **M4: Console Connected** — Phase 4 done, grandMA3 onPC controlled from Python
- **M5: Show Framework** — Phase 5 done, rig and show data model with CLI
- **M6: AI Designer** — Phase 6 done, AI-assisted show building working
- **M7: Timecoded Playback** — Phase 7 done, MA3-native show export with timecode

---

## Risks

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| GDTF spec complexity | Medium | Start with subset of features | ☐ Open |
| AI prompt quality | High | Iterate on prompt templates, provide rich context bundles | ☐ Open |
| MA3 OSC API undocumented | High | Reverse-engineer, use MA3 online manual | ☐ Open |
| MA3 timecode integration | Medium | Research MA3 timecode API, start with manual cue triggering | ⚠ Validation pending — event XML schema captured locally; import/playback still needs MA3 verification |
| Scope creep on AI features | High | Phase 6 is MVP: cue generation from vibe first | ☐ Open |

---

*Last updated: 2026-05-21 (event-bearing MA3 timecode XML captured; import/playback validation pending)*
