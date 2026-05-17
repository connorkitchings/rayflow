# AI Interaction Contract

> **Purpose**: Define how AI coding tools (Claude Code, Codex, etc.) interact with RayFlow to build and modify lighting shows. This is the framework that makes natural-language direction effective.

## Overview

RayFlow's primary interface is through an AI coding tool running in this repository. The user directs the AI in natural language; the AI reads the show context, generates concrete modifications, and pushes results to grandMA3 onPC via OSC.

**The AI is the designer's assistant.** The human provides creative direction; the AI handles the mechanical translation into MA3 commands.

## Context Bundle

Before an AI tool can work on a show, it must load this context:

### Required Context
1. **Rig definition** — `data/rigs/<rig_name>.yaml`
   - All fixtures (names, modes, DMX addresses, positions)
   - All presets (names, attributes, channel targets)
   - Venue dimensions
2. **Show definition** — `data/shows/<show_name>.yaml`
   - Song metadata and sections
   - Current cues (number, label, timestamp, attributes)
   - Current vibe (if any)
3. **Fixture capabilities** — GDTF data from `data/fixtures/`
   - What attributes each fixture supports (dimmer, color, pan, tilt, gobo, etc.)
   - Available color wheels, gobo wheels, etc.
4. **Available commands** — Existing RayFlow modules
   - `console/cue.py` — Cue command builders
   - `console/osc.py` — OSC client for MA3
   - `fixtures/mvr_export.py` — MVR export
   - `bridge/artnet.py` — Direct DMX send

### Context Loading Command

```bash
# Load full context for a show
rayflow show context <show_name> --json
```

This outputs a JSON bundle containing the rig, show, fixture capabilities, and available actions — everything the AI needs to understand before making changes.

## Request Translation

Natural language requests map to concrete actions through these patterns:

### Intensity Changes
| User Says | AI Does |
|-----------|---------|
| "Make the chorus brighter" | Increase dimmer values for all cues in the chorus section |
| "Dim the intro to 30%" | Set dimmer attribute to 30 for intro cues |
| "Blackout at 2:30" | Add a cue at timestamp 150s with dimmer=0 for all channels |

### Color Changes
| User Says | AI Does |
|-----------|---------|
| "Change to cool colors" | Modify color attributes using cool palette (blues, cyans, whites) |
| "Make verse 2 warm amber" | Set color attribute to warm amber for verse 2 cues |
| "Use the vibe palette for the chorus" | Apply `show.vibe.palette.colors` to chorus cues |

### Position/Movement Changes
| User Says | AI Does |
|-----------|---------|
| "Add movement to verse 2" | Add pan/tilt attributes that sweep across verse 2 duration |
| "Point everything at center stage" | Set pan/tilt to center position for all moving fixtures |
| "Slow sweep on the moving heads" | Add slow pan sweep to fixtures with position capability |

### Beam Changes
| User Says | AI Does |
|-----------|---------|
| "Tighten the beams" | Reduce zoom values on fixtures that support beam control |
| "Add strobe to the chorus hit" | Add shutter/strobe attribute to chorus cues |
| "Widen the wash" | Increase zoom, add frost if available |

### Preset Operations
| User Says | AI Does |
|-----------|---------|
| "Apply warm_wash to the intro" | Set preset reference on intro cues to "warm_wash" |
| "Create a preset called verse_glow" | Add new Preset to rig with specified attributes |
| "What presets do we have?" | List rig.presets with descriptions |

### Structural Changes
| User Says | AI Does |
|-----------|---------|
| "Add a cue at 1:00" | Insert new Cue at timestamp 60s, renumber subsequent cues |
| "Make the fade from chorus to verse slower" | Increase fade_time on the transition cue |
| "Delete cue 5" | Remove cue, renumber subsequent cues |

## Available Actions

The AI can perform these actions on a show:

### Read Actions
- `read_rig(name)` — Load and return rig definition
- `read_show(name)` — Load and return show definition
- `list_presets(rig)` — Return all presets with descriptions
- `get_fixture_capabilities(fixture_name)` — Return supported attributes
- `get_cues_for_section(show, section)` — Return cues in a section
- `get_vibe(show)` — Return current vibe or None

### Write Actions
- `add_cue(show, cue)` — Insert a cue, auto-renumber
- `update_cue(show, cue_number, changes)` — Modify cue attributes
- `delete_cue(show, cue_number)` — Remove a cue, renumber
- `add_preset(rig, preset)` — Add a new preset to the rig
- `update_preset(rig, preset_name, changes)` — Modify preset attributes
- `set_vibe(show, vibe)` — Set or replace the show's vibe
- `save_show(show)` — Serialize show to YAML
- `save_rig(rig)` — Serialize rig to YAML

### Push Actions
- `push_to_ma3(show, execute=False)` — Generate OSC commands for all cues, dry-run by default
- `push_section_to_ma3(show, section, execute=False)` — Push cues for one section
- `export_mvr(rig, output_path)` — Export rig as MVR for MA3 import

### Analysis Actions
- `check_dmx_conflicts(rig)` — Validate no overlapping DMX addresses
- `suggest_cue_times(show)` — Suggest cue timestamps based on section boundaries
- `validate_preset_coverage(preset, rig)` — Check that preset attributes are supported by target fixtures

## Prompt Template

When starting a session with an AI coding tool, use this prompt structure:

```
I'm working on a lighting show in RayFlow. Here's the context:

## Rig
[Output of: rayflow show context <show_name> --json]

## Current Show State
[Show YAML contents]

## What I Want
[Natural language direction]

## Instructions
1. Read the rig and show context above
2. Determine what changes are needed
3. Show me the proposed changes before applying them
4. Wait for my confirmation
5. After confirmation, modify the show YAML
6. Optionally push to MA3 with --execute flag
```

## Safety Constraints

### Dry-Run by Default
All MA3 push operations default to dry-run. The AI generates and displays the OSC commands but does not send them unless the user explicitly confirms with `--execute`.

### Reversible Changes
All show modifications are serialized to YAML and tracked in git. Any change can be reverted with `git checkout`.

### Validation Before Push
Before pushing to MA3:
1. Validate DMX addressing has no conflicts
2. Validate all referenced fixtures exist in the GDTF library
3. Validate all preset attributes are supported by target fixtures
4. Display a summary of changes for user review

### No Destructive Operations Without Confirmation
Deleting cues, presets, or fixtures requires explicit user confirmation. The AI must show what will be deleted and ask before proceeding.

## Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  1. User: "Create a show for song X with rig Y"             │
│     → AI creates show YAML, loads rig context               │
├─────────────────────────────────────────────────────────────┤
│  2. User: "Suggest a vibe"                                  │
│     → AI analyzes song sections, proposes vibe              │
│     → User approves or modifies                             │
├─────────────────────────────────────────────────────────────┤
│  3. User: "Build cues for the intro"                        │
│     → AI generates cues based on vibe + section energy      │
│     → Shows proposed cues, waits for confirmation           │
│     → User: "Looks good" → AI saves to show YAML            │
├─────────────────────────────────────────────────────────────┤
│  4. User: "Make the chorus brighter, add movement"          │
│     → AI modifies chorus cues (dimmer up, add pan/tilt)     │
│     → Shows diff, waits for confirmation                    │
├─────────────────────────────────────────────────────────────┤
│  5. User: "Push to MA3"                                     │
│     → AI generates OSC commands, displays dry-run output    │
│     → User: "--execute" → AI sends to MA3                   │
├─────────────────────────────────────────────────────────────┤
│  6. User reviews in MA3 visualizer                          │
│     → "Tweak cue 3, slower fade"                            │
│     → AI modifies cue, pushes again                         │
├─────────────────────────────────────────────────────────────┤
│  7. User: "Export the show"                                 │
│     → MVR for rig + cue data for sequences + timecode map   │
└─────────────────────────────────────────────────────────────┘
```

## AI Tool Integration

### How This Works in Practice

The user runs an AI coding tool (Claude Code, Codex, etc.) in the RayFlow repository. The tool has access to:

1. **All source code** — Can read and modify any module
2. **All data files** — Can read and modify rig/show YAML files
3. **The CLI** — Can run `rayflow` commands to validate, export, or push
4. **The OSC client** — Can send commands to MA3 (with `--execute` gate)

The AI doesn't need a special interface — it uses the same tools a human developer would use. The contract defines **what data to read**, **what actions are valid**, and **what safety constraints apply**.

### What Makes This Effective

1. **Structured data** — YAML shows/rigs are readable and modifiable by both humans and AI
2. **Clear vocabulary** — Presets, attribute families, and sections give the AI a language to work with
3. **Existing infrastructure** — OSC client, cue builders, and MVR export are already implemented
4. **Safety gates** --execute flag prevents accidental MA3 changes
5. **Git tracking** — All changes are versioned and reversible

## Glossary

| Term | Definition |
|------|------------|
| **Rig** | A stage configuration: fixtures, positions, presets |
| **Show** | A rig + song + cues + optional vibe |
| **Preset** | A named, preprogrammed lighting look |
| **Vibe** | AI-generated creative direction (palette, intensity curve, movement style) |
| **Cue** | A lighting state at a specific timestamp in the song |
| **Section** | A part of the song (verse, chorus, bridge) with energy and mood metadata |
| **Attribute Family** | Category of fixture control: dimmer, position, color, beam, focus, gobo |
| **Context Bundle** | The full set of data an AI needs to work on a show |
| **Dry-Run** | Generating commands without sending them to MA3 |
| **--execute** | Flag that gates actual OSC command transmission to MA3 |
