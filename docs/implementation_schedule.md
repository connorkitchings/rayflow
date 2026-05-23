# RayFlow — Implementation Schedule

**Status Legend:** ☐ Not Started · ▶ In Progress · ✅ Done · ⚠ Risk/Blocked

---

## Direction Reset

As of 2026-05-23, RayFlow's mainline direction is backend-neutral show intent
plus deterministic output adapters. grandMA3 remains an important compatibility
target, but it is no longer the critical path for the next milestone.

The next milestone is Phase 8: define the backend adapter boundary, render
fixture-aware cue intent to DMX frames, verify Art-Net/sACN output, and spike
QLC+ WebSocket control.

---

## Phase 1: Project Foundation

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Update pyproject.toml | rayflow package, lighting deps | ✅ Done | sacn, python-osc, artnet, gdtf-parser |
| Rewrite README.md | Project overview | ✅ Done | Updated for backend-neutral direction |
| Rewrite project charter | Goals, scope, architecture | ✅ Done | Updated with 2026-05-23 direction reset |
| Update agent guidance | CONTEXT, AGENTS, CATALOG | ✅ Done | Lighting-specific roles and skills |
| Create src/rayflow/ structure | Package skeleton | ✅ Done | bridge/, fixtures/, console/, shows/, visualizer/ |
| Create data/ structure | Fixture and show directories | ✅ Done | data/fixtures/, data/rigs/, data/shows/ |

---

## Phase 2: Art-Net / sACN Bridge

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| DMX universe model | Universe data structure | ✅ Done | 512 channels, universe addressing, conflict detection |
| Art-Net sender | Send DMX via Art-Net | ✅ Done | ArtDMX packets, universe targeting, input validation |
| Art-Net receiver | Receive DMX from console/tool | ✅ Done | Listen on port 6454 |
| sACN sender | Send DMX via sACN | ✅ Done | Using sacn library, fixed channel indexing |
| sACN receiver | Receive DMX via sACN | ✅ Done | Multicast or unicast |
| Bridge CLI | `rayflow bridge send/recv/status` commands | ✅ Done | Wired to real bridge classes, rich output |
| Bridge tests | Unit + integration tests | ✅ Done | Existing bridge coverage |

---

## Phase 3: GDTF Fixture Support

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| GDTF parser | Load `.gdtf` fixture files | ✅ Done | Validates ZIP, parses description.xml, extracts modes/channels |
| Fixture library | Manage loaded fixtures | ✅ Done | Catalog, search, by manufacturer, fixture summaries |
| Channel mapping | Map DMX addresses to channels | ✅ Done | Concrete address maps with family classification and bounds checks |
| Fixture patching | Assign fixtures to universes | ✅ Done | In-memory GDTF-aware patches with channel maps and CLI smoke command |
| Sample fixtures | Checked-in real fixture samples | ✅ Done | Public GDTF samples with manifest and hashes |
| Fixture tests | Parser, library, and sample tests | ✅ Done | Real samples validated offline |

---

## Phase 4: grandMA3 Compatibility Research

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| OSC connection | Connect to MA3 onPC | ✅ Done | Dry-run-safe About command plus optional feedback listener |
| Command sender | Send MA3 commands via OSC | ✅ Done | `/cmd` sender, `--execute` gate, feedback capture |
| Cue stack builder | Build cue sequences from Python | ✅ Done | Typed command builders, JSON cue stacks, dry-run-safe nested CLI |
| MVR export | Export rig to MVR format | ✅ Done | Embedded GDTF files, scene/layer hierarchy, fixture addressing, 3D positions |
| Probe harness | Command acceptance and disposable-show probes | ▶ In Progress | Useful for compatibility, no longer next milestone blocker |
| Fixture import/patch proof | MA3 import evidence packet | ⚠ Blocked | Live probes did not prove repeatable MVR fixture import; move off mainline |

---

## Phase 5: Show & Rig Framework

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Architecture document | Phase 5 data model and design decisions | ✅ Done | `docs/phase5_architecture.md` |
| AI interaction contract | Framework for AI tooling | ✅ Done | Needs ongoing updates for backend adapters |
| Rig data model | `Rig`, `Venue`, `FixtureSlot`, `Preset` dataclasses | ✅ Done | Validation, presets, rig templates, show overrides |
| Show data model | `Show`, `Song`, `Section`, `Cue`, `Vibe` dataclasses | ✅ Done | Links rig to audio, preset overrides |
| Rig CLI | `rayflow rig ...` commands | ✅ Done | Manage rigs, export to MVR |
| Show CLI | `rayflow show ...` commands | ✅ Done | Manage shows, load context bundle |
| Preset system | Named presets with attribute families | ✅ Done | Dimmer, position, color, beam, focus, gobo |
| Tests | Full test suite for models and CLI | ✅ Done | Existing regression coverage |

---

## Phase 6: AI Show Builder

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Audio section import | Import section markers from external tool | ✅ Done | `show import-sections`, JSON schema, sample file |
| Vibe generation | AI suggests color palettes and organizing principles | ✅ Done | `show set-vibe`, `Vibe.from_dict()`, prompt template |
| Cue generation | AI generates cues per section based on vibe | ✅ Done | `cue_generator.py`, `show generate-cues`, cue edit commands |
| Interactive direction | User directs AI refinement | ✅ Done | Song metadata, section editing, batch cue updates |
| MA3 push | Push generated dimmer cues to MA3 via OSC | ✅ Done | Compatibility path only; not renderer proof |
| Tests | Unit + integration tests | ✅ Done | Existing section import, cue generator, push, CLI coverage |

---

## Phase 7: Export & Playback Compatibility

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Sequence build hardening | `--sequence` option on push commands, sequence labeling | ✅ Done | `store_sequence`, `label_sequence`, `delete_sequence`, `clear_all` builders |
| MA3 show export | Export cues/rig to MA3-compatible bundle | ✅ Done | `show export` writes MVR, dry-run OSC command list, README, metadata |
| Timecode integration | MA3 Timecode XML for cue playback | ▶ In Progress | Clean import/re-export validated; final cue-fire observation pending |
| Show library | Versioned show storage | ✅ Done | `show save/versions/restore/diff`; local YAML snapshots with metadata |
| MA3 control matrix | Verified control boundary before MCP | ✅ Done | Documents capabilities, gaps, and why MCP should wait |

---

## Phase 8: Backend-Neutral Control Loop

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Backend adapter design | Interface for dry-run, apply, evidence, capabilities | ☐ Not Started | Should cover Art-Net, sACN, QLC+, MA3 export/OSC |
| Fixture-aware DMX renderer | Render cue intent to universe/channel frames | ☐ Not Started | Start with dimmer and RGB/RGBW sample fixtures |
| DMX evidence capture | Packet/receiver proof for rendered frames | ☐ Not Started | Use Art-Net/sACN receiver tests or network capture |
| QLC+ WebSocket spike | Command/query proof against local QLC+ | ☐ Not Started | Target plain text WebSocket API and state queries |
| Backend CLI | Select backend and render/apply/dry-run output | ☐ Not Started | Keep live output behind explicit execute flags |
| Renderer tests | Unit tests with real GDTF samples | ☐ Not Started | Validate channel maps and output frames |
| Docs | Update workflow guides for non-MA3 execution | ▶ In Progress | Direction reset started 2026-05-23 |

---

## Milestones

- **M1: Foundation Complete** — Phase 1 done, package structure ready
- **M2: Protocol Bridge** — Phase 2 done, Art-Net/sACN send/receive available
- **M3: Real Fixtures** — Phase 3 done, GDTF fixtures loaded and patched in RayFlow
- **M4: Console Compatibility** — Phase 4 done, MA3 OSC/MVR compatibility explored
- **M5: Show Framework** — Phase 5 done, rig and show data model with CLI
- **M6: AI Designer** — Phase 6 done, AI-assisted show building working
- **M7: MA3 Export Compatibility** — Phase 7 mostly done, MA3 export/playback path documented
- **M8: Backend-Neutral Execution** — Phase 8 target, fixture-aware rendering and API-first backends

---

## Risks

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| Fixture-aware renderer complexity | High | Start with dimmer and RGB/RGBW, then expand family by family | ☐ Open |
| GDTF spec complexity | Medium | Use existing parser and real sample fixtures; test channel maps | ☐ Open |
| QLC+ WebSocket behavior differs from docs | Medium | Build a small command/query spike before designing around it | ☐ Open |
| MA3 OSC/API readback incomplete | Medium | Keep MA3 as gated compatibility adapter, not the mainline blocker | ⚠ Open |
| AI prompt quality | High | Provide rich context bundles and backend capability declarations | ☐ Open |
| Scope creep on visualizer work | Medium | Make renderer/evidence the milestone, not a full custom visualizer | ☐ Open |

---

*Last updated: 2026-05-23 (backend-neutral control loop adopted as next mainline direction).*
