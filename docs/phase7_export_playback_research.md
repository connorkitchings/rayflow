# Phase 7 Export & Playback Research

**Date:** 2026-05-19
**Target:** grandMA3 onPC 2.3.2.0
**Status:** Research spike complete; implementation should begin with MA3 export capture. Follow-up command automation research is captured in `docs/research/ma3_timecode_command_automation_2026-05-19.md`.

## Goal

Phase 7 should turn a RayFlow show into a MA3-native playback package:

1. MVR rig export for MA3 patch and 3D visualization.
2. Sequence/cue programming in MA3.
3. Timecode pool object that triggers the sequence from RayFlow cue timestamps.

The preferred direction is MA3-native playback, not RayFlow acting as the runtime scheduler.

## Verified Local Baseline

The installed local application reports:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
# 2.3.2.0
```

Use MA's 2.3 manual for all command syntax and UI behavior unless this version changes.

## Official MA3 Findings

### Timecode Shows

MA3 timecode shows are pool objects controlled with the `Timecode` keyword. The keyword supports storing, playing, recording, editing, labeling, rewinding, and setting properties on timecode shows.

Useful documented properties include:

| Property | Use |
| --- | --- |
| `Name` | Label the timecode show |
| `Time` | Set the time cursor |
| `Duration` | Set full show length |
| `TCSlot` | Set source to Internal, Link Selected, Slot1, Slot2, etc. |
| `AutoStart` | Start when external timecode is received |
| `AutoStop` | Stop when external timecode is received |

Source: MA Lighting, grandMA3 2.3 manual, Timecode Keyword.

### Time Sources

A timecode show can use an internal source or a timecode slot. Timecode slots can listen to SMPTE/LTC, MIDI timecode, or ArtTimeCode. MA3 can receive up to eight external timecode signals.

Important constraint: timecode slot settings are not stored in the show file. RayFlow cannot rely on exported show data to carry all slot setup. Slot configuration should be documented and verified separately.

ArtTimeCode is receive-only in MA3: MA3 can receive ArtTimeCode into a configured slot, but cannot generate ArtTimeCode.

Sources: MA Lighting, grandMA3 2.3 manual, Timecode Slots and External Connections.

### Tracks And Events

A timecode show contains track groups, tracks, time ranges, and events. A track target can be a Sequence, Sound, Timecode, Timecode Slot, Preset, Group, or Master.

For RayFlow Phase 7, the most direct mapping is:

```text
RayFlow Show
  -> MA3 Sequence containing cues
  -> MA3 Timecode Show
      -> Track targeting that Sequence
      -> Events at cue timestamps
      -> Event token: Go+ / cue destination
```

MA's manual also warns that manually created cue events only trigger follow cues, timed cues, or cue commands when the relevant Playback and Record setting is set for manual events. This needs MA3 verification before implementation is called done.

Sources: MA Lighting, grandMA3 2.3 manual, Create a Timecode Show and Tracks.

### Import / Export

MA3 Import/Export is the supported way to move smaller portions of show data between shows. The Import/Export menu includes `Timecodes` as an object type, and the command line exposes `Import` and `Export` keywords for XML-based show objects.

Command syntax:

```text
Export [Object] ["Object_Name" or Object_Number] (If Drive [Drive_Number]) (/Option) ("Option_Value")
Import [Object] Library "File Name.xml" (If Drive [Drive_Number]) (At ["Object_Name" or Object_Number]) (/Option) ("Option_Value")
```

This means a Timecode XML import/export path is plausible, but RayFlow must not synthesize Timecode XML from assumptions. First capture a real MA3 2.3.2.0 Timecode export and build from that schema.

Sources: MA Lighting, grandMA3 2.3 manual, Import Keyword and Export Keyword; Import/Export manual page.

## Recommended Phase 7 Architecture

### Slice 1: Capture And Document MA3 Timecode XML

Create a minimal timecode show inside MA3 with:

- One sequence target.
- Two cue events at distinct timestamps.
- Internal time source.
- Manual Events playback behavior configured so events fire as expected.

Then export:

```text
Export Timecode 1 "rayflow_minimal_timecode"
```

Expected deliverables:

- `docs/research/ma3_timecode_xml_2_3_2.md`
- Sanitized fixture XML sample under `data/ma3_exports/samples/` if license-safe.
- A schema map from XML fields to RayFlow `Show` and `Cue`.
- A test fixture based on the captured XML.

Capture update: A real MA3 2.3.2.0 Timecode track skeleton export is now captured in `data/ma3_exports/samples/rayflow_minimal_timecode_track_skeleton_2_3_2.xml` and documented in `docs/research/ma3_timecode_xml_2_3_2.md`. It proves Timecode, TrackGroup, Track, and TimeRange XML shape, but it does not include a Sequence target or cue events. Keep `show export-timecode` blocked until an event-bearing export is captured.

Follow-up research found that MA3 2.3 documents command-line support for Timecode pool object creation, properties, playback, and export/import, but not for track group, track, target, or event creation. Treat Timecode Viewer event creation as the smallest currently verified manual capture step until an exported XML schema or MA command probe proves otherwise.

### Slice 2: Sequence Build Hardening

RayFlow already generates OSC commands that store cues in MA3. Phase 7 should formalize that into an explicit sequence export/push plan:

- Choose a default target sequence number or accept `--sequence`.
- Label the sequence from show/song metadata.
- Store cues in timestamp order.
- Set cue fade times from `Cue.fade_time`.
- Keep dry-run as default and require `--execute` for OSC.

This can build on `src/rayflow/shows/push.py` and `src/rayflow/console/cue.py`.

### Slice 3: Timecode XML Generator

After Slice 1 captures the real schema, implement:

```text
rayflow show export-timecode <show> --output <path.xml> --sequence <n> --fps <rate>
```

Suggested behavior:

- Convert `Cue.timestamp` seconds into MA3 timecode values.
- Generate one event per cue, targeting the selected sequence.
- Include show duration from `Show.song.duration`.
- Default source to internal timecode unless an external slot is explicitly requested.
- Validate monotonically increasing timestamps.
- Reject duplicate cue numbers or duplicate timestamps unless explicitly allowed.

### Slice 4: MA3 Import Helper

Add a dry-run-safe command helper:

```text
rayflow show import-timecode-to-ma3 <show> --xml <path.xml> [--execute]
```

This should print the MA3 command first:

```text
Import Timecode Library "filename.xml" At Timecode <n>
```

Only send it over OSC when `--execute` is passed.

### Slice 5: End-To-End Verification

Definition of done for Phase 7 should include:

- Export MVR from RayFlow and import into MA3.
- Push or import sequence cues.
- Import generated Timecode XML.
- Start internal timecode playback in MA3.
- Verify cue triggers occur at expected timestamps.
- Save a session log with MA3 version, commands, and any observed schema quirks.

## Risks And Open Questions

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Timecode XML schema is undocumented or unstable | High | Capture export from MA3 2.3.2.0 before code generation |
| Timecode slot settings are not show-file state | Medium | Keep slot setup as verified environment configuration |
| Manual event playback setting may block cue commands | Medium | Include this in the first MA3 verification script/checklist |
| Sequence object IDs may differ from user-visible numbers | Medium | Use exported XML to map object references before generating |
| Audio/sound pool integration may require additional imports | Low for MVP | Start with internal timecode, add sound track later |

## Sources

- MA Lighting grandMA3 2.3 Manual: Timecode Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_timecode.html
- MA Lighting grandMA3 2.3 Manual: Create a Timecode Show — https://help.malighting.com/grandMA3/2.3/HTML/timecode_create.html
- MA Lighting grandMA3 2.3 Manual: Tracks — https://help.malighting.com/grandMA3/2.3/HTML/timecode_tracks.html
- MA Lighting grandMA3 2.3 Manual: Timecode Slots — https://help.malighting.com/grandMA3/2.3/HTML/timecode_slots.html
- MA Lighting grandMA3 2.3 Manual: External Connections — https://help.malighting.com/grandMA3/2.3/HTML/timecode_external_connections.html
- MA Lighting grandMA3 2.3 Manual: Export Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_export.html
- MA Lighting grandMA3 2.3 Manual: Import Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_import.html
- MA Lighting grandMA3 Manual: Import / Export — https://help.malighting.com/grandMA3/2.0/HTML/import-export.html
