# MA3 Probe Evidence Index

**grandMA3 onPC version:** 2.3.2.0  
**OSC endpoint:** `127.0.0.1:8000`

## Overview

This folder contains all evidence from RayFlow's live grandMA3 onPC control probes. Each probe tests a specific capability boundary between RayFlow and MA3. The control matrix (`ma3_control_matrix_2_3_2.md`) synthesizes all findings into a capability status table.

## Probe Status Summary

| File | Type | Status | Key Finding |
|---|---|---|---|
| `ma3_control_matrix_2_3_2.md` | Synthesis | Master reference | Full capability matrix for all MA3 operations; defines evidence standards |
| `ma3_basic_looks_probe_2_3_2.md` | Probe report | Partial pass | OSC command send works; sequence/group/preset shells created; fixture-aware programming unproven |
| `ma3_disposable_show_and_fixture_probe_2_3_2.md` | Probe report | Blocked | Show isolation via OSC commands unreliable; MVR import blocked; fallback to manual patching |
| `ma3_timecode_command_automation_2026-05-19.md` | Research | Partial | Timecode pool objects automatable via command line; track/event creation is UI-only |
| `ma3_timecode_xml_2_3_2.md` | Research | Pass | XML schema captured from real MA3 export; round-trip import/export validated; playback cursor movement confirmed |
| `ma3_command_acceptance_probe_result.json` | Evidence JSON | Pass | `ChangeDestination Root` + `Export Sequence 1` wrote XML successfully |
| `ma3_dimmer_proof_probe_result.json` | Evidence JSON | Fail | Export did not write after show isolation issues; Sequence 1 not found |
| `ma3_fixture_import_probe_result.json` | Evidence JSON | Pass (MVR gen) | MVR generation with MA3-compatible XML shape works; live import inconclusive |
| `ma3_show_isolation_probe_result.json` | Evidence JSON | Pass (assumed) | User-confirmed disposable show; `SaveShow` executed but file mtime unchanged |

## Evidence Chain

```
1. Command Acceptance (PASS)
   └── OSC /cmd works with ChangeDestination Root
   └── Export writes XML to datapools

2. Show Isolation (BLOCKED → ASSUMED)
   └── NewShow/SaveShow via OSC does not create target .show file
   └── Workaround: user creates/loads disposable show via UI
   └── --assume-disposable flag records manual confirmation

3. Fixture Import (BLOCKED → FALLBACK)
   └── MVR generation works but MA3 merge screen shows no fixtures
   └── Workaround: manual Generic/Dimmer patch via UI

4. Basic Looks (PARTIAL)
   └── Sequence/cue structure created and exported
   └── Preset shells created but empty (no fixture values captured)
   └── Dimmer/color/position programming unproven for real fixtures

5. Timecode (PASS)
   └── XML schema captured and validated
   └── Round-trip import preserves targets and events
   └── Playback advances cursor; cue-fire needs visual confirmation
```

## Gated Capabilities

The following capabilities are **not yet safe to automate** and require additional evidence before MCP exposure:

- `create_color_preset` — needs MA3-native color value syntax proof
- `create_position_preset` — needs pan/tilt fixture patch proof
- `program_basic_look` — needs fixture-aware preset content proof
- `verify_current_cue` — needs reliable runtime readback method

## Direction

As of 2026-05-23, MA3 control research is scoped to the **MA3 compatibility track**. It should not block Phase 8 backend-neutral work on DMX rendering, Art-Net/sACN output, or QLC+ WebSocket control. See `docs/research/agentic_show_control_architectures/04-rayflow-direction-review.md`.
