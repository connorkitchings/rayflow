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

## Phase 5: Web 3D Visualizer

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Flask server | Backend for visualizer | ☐ Not Started | Serve frontend, receive DMX |
| Three.js scene | 3D stage environment | ☐ Not Started | Stage, truss, floor |
| Fixture rendering | 3D models for fixtures | ☐ Not Started | Basic geometry from GDTF |
| DMX → light mapping | Update visuals from DMX | ☐ Not Started | WebSocket real-time |
| Camera controls | Orbit, pan, zoom | ☐ Not Started | Three.js OrbitControls |
| Beam visualization | Light beams and cones | ☐ Not Started | Volumetric effect |
| Visualizer tests | Frontend + backend tests | ☐ Not Started | |

---

## Phase 6: AI-Assisted Lighting

| Task | Deliverable | Status | Notes |
|------|-------------|--------|-------|
| Natural language cues | "Warm wash on stage left" → DMX | ☐ Not Started | LLM prompt engineering |
| Look generation | AI suggests lighting looks | ☐ Not Started | Based on genre, mood, venue |
| Cue stack automation | Auto-generate show structure | ☐ Not Started | Verse, chorus, bridge patterns |
| Fixture recommendation | Suggest fixtures for a look | ☐ Not Started | From GDTF library |

---

## Milestones

- **M1: Foundation Complete** — Phase 1 done, package structure ready
- **M2: First Light** — Phase 2 done, DMX flowing from Python to visualizer
- **M3: Real Fixtures** — Phase 3 done, GDTF fixtures loaded and patched
- **M4: Console Connected** — Phase 4 done, grandMA3 onPC controlled from Python
- **M5: Visual Stage** — Phase 5 done, full 3D visualization working
- **M6: AI Designer** — Phase 6 done, AI-assisted look generation

---

## Risks

| Risk | Impact | Mitigation | Status |
|------|--------|------------|--------|
| grandMA3 OSC API undocumented | High | Reverse-engineer, use MA3 online manual | ☐ Open |
| GDTF spec complexity | Medium | Start with subset of features | ☐ Open |
| Three.js learning curve | Medium | Use examples, start simple | ☐ Open |
| Scope creep on visualizer | High | Phase 5 is MVP: basic geometry first | ☐ Open |

---

*Last updated: 2026-05-17*
