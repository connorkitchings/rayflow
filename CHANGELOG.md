# Changelog

All notable changes to RayFlow will be documented in this file.

## [0.1.0] — 2026-05-15

### Added
- Project foundation: package structure, CLI skeleton, docs, and agent guidance
- Art-Net bridge wrapper (`stupidArtnet` integration)
- sACN/E1.31 bridge wrapper (`sacn` library integration)
- grandMA3 onPC OSC client wrapper (`python-osc` integration)
- GDTF fixture parser wrapper (`pygdtf` integration)
- Fixture library with search, load, and catalog
- DMX universe model with fixture patching and conflict detection
- RayFlow CLI with bridge, fixture, and console subcommands
- Environment-variable-based configuration system
- Project charter, implementation schedule, and architecture docs
- AI agent guidance with lighting-specific roles and skills

## Phase 2 — Art-Net / sACN Bridge

- Art-Net send/receive with input validation and universe targeting
- sACN send/receive with unicast/multicast support
- Bridge CLI commands: `bridge send`, `bridge recv`, `bridge status`
- Bridge validation, error handling, and network failure modes
- grandMA3 onPC Art-Net verification against installed version 2.3.2.0

## Phase 3 — GDTF Fixture Support

- GDTF parser: ZIP validation, description.xml parsing, mode/channel extraction
- Fixture library: catalog, search, manufacturer grouping
- Channel mapping with attribute family classification and bounds checks
- In-memory GDTF fixture patching with CLI inspection command
- Checked-in real GDTF sample pack with manifest validation

## Phase 4 — grandMA3 Compatibility Research

- Fixture comparison reports with real MA3 observation capture (14 modes)
- Dry-run-safe OSC command sender and feedback listener
- Cue stack command helpers with JSON batch input and nested CLI
- MVR export with embedded GDTF files and mode info
- Integration tests (14 tests, requires running MA3)

## Phase 5 — Show & Rig Framework

- Architecture document and AI interaction contract
- Data models: `Rig`, `Venue`, `FixtureSlot`, `Preset`, `Show`, `Song`, `Section`, `Cue`, `Vibe` (11 dataclasses with validation)
- YAML serialization with round-trip support
- Rig CLI: `rig create/list/info/copy/add-fixture/add-preset/export-mvr`
- Show CLI: `show create/list/info/add-section/add-cue/add-preset-override/context/export-mvr`
- AI context bundle command (`show context --json`)
- Prompt template for AI sessions
- Full test suite (296 tests, 84% coverage)

## Phase 6 — AI Show Builder

- Audio section import (`show import-sections`, JSON schema)
- Vibe generation (`show set-vibe`, `Vibe.from_dict()`, enhanced prompt template)
- Cue generation helpers (`cue_generator.py`, `show generate-cues/update-cue/delete-cue/renumber`)
- Interactive direction (`show set-song-meta/update-section/delete-section/batch-update-cues`)
- MA3 push integration (`show push-to-ma3/push-section`)
- 80 new tests (section import, cue generator, push, CLI)

## Phase 7 — Export & Playback Compatibility

- Sequence build hardening (`store_sequence`, `label_sequence`, `delete_sequence`, `clear_all`; `--sequence` on push)
- MA3 show export bundle (`show export` with MVR, OSC command list, README, metadata)
- Show library (`show save/versions/restore/diff` with versioned YAML snapshots)
- MA3 Timecode XML generation and import/re-export validation against grandMA3 onPC 2.3.2.0
- Internal Timecode playback clock validation

## Phase 8 — Backend-Neutral Control Loop

- 2026-05-23 direction reset: MA3 as compatibility adapter, mainline moves to backend-neutral show intent
- Backend adapter contract (dry-run, apply, evidence, capabilities)
- Fixture-aware DMX renderer (dimmer, RGB/RGBW, named colors, 16-bit channels)
- Art-Net/sACN evidence backends (receiver buffer comparison)
- Experimental QLC+ WebSocket spike
- Backend CLI: `show render-cue`, `show output-cue`, `show output-section`, `show qlc-spike`
- Renderer tests with real GDTF samples

## Phase 9 — Productized Practice Workflow

- Checked-in practice rig and show using sample fixtures
- Deterministic cue planning with proposal/apply gate
- Workflow reports (`show workflow-report`) aggregating render + evidence
- Local Art-Net loopback receiver proof captured

## Phase 10 — General Show Authoring Ergonomics

- Reusable proposal/apply cue planning for any show
- `show plan-cues` command (proposal by default, `--apply` to write)
- Vibe-palette style during cue planning with fallback warnings
- Phase 9 practice command compatibility preserved

## Phase 11 — Fixture-Aware Renderer Expansion

- Position rendering: pan/tilt through GDTF channels with 16-bit fine channels
- Numeric family rendering: zoom, focus, shutter, gobo as percentage-style values
- Renderer warnings for unsupported fixture channels
- Regression tests with Robin iSpiiderX fixture covering position, shutter, zoom, aliases, and missing gobo fallback
