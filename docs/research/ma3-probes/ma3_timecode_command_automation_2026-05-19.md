# MA3 Timecode Command Automation Research

**Date:** 2026-05-19
**Target:** grandMA3 onPC 2.3.2.0
**Goal:** Determine whether RayFlow can create MA3 Timecode tracks/events entirely through command-line or OSC commands before generating MA3-native Timecode XML.

## Result

Partial automation is documented, but full Timecode event creation is not command-line verified yet.

RayFlow can rely on documented command-line syntax for Timecode pool object creation, property setting, playback control, and export/import. MA's 2.3 manual does not expose command-line syntax for creating Timecode track groups, tracks, assigning track targets, or adding/editing events. Those operations are documented through the Timecode Viewer with Setup mode.

The next practical step is to capture a real MA3 2.3.2.0 Timecode XML export from a minimal manually-created Timecode object, then decide whether the XML schema is stable enough for `rayflow show export-timecode`.

## Verified Environment

Local installed version:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
# 2.3.2.0
```

Local export folders inspected:

```text
~/MALightingTechnology/gma3_library/datapools/timecodes
~/MALightingTechnology/gma3_library/datapools/sequences
```

Both were empty during this research pass, so there were no existing Timecode or Sequence XML files to reverse-engineer locally.

## Documented Command-Line Surface

### Timecode Pool Objects

MA documents `Timecode` as an object keyword. It supports storing, playing, recording, editing, labeling, setting properties, and rewinding Timecode shows.

Documented examples:

```text
Store Timecode "Napalm Skies"
Set Timecode "Intro" "Duration" "55"
Set Timecode "Intro" "Name" "Prelude"
Go Timecode "Prelude"
Top Timecode "Prelude"
Label Timecode 3
```

Useful documented properties:

| Property | Notes |
| --- | --- |
| `Name` | Timecode show label |
| `Time` | Time cursor |
| `Duration` | Full Timecode show length |
| `Offset` | Move the entire Timecode show forward |
| `Loop Mode` | Loop, Pause, or Off behavior |
| `Loop Count` | Internal clock repeat count |
| `TCSlot` | Internal, Link Selected, Slot1, Slot2, etc. |
| `AutoStart` | External-source only |
| `AutoStop` | External-source only |

### Export / Import

MA documents generic XML export/import for show objects:

```text
Export [Object] ["Object_Name" or Object_Number] (If Drive [Drive_Number]) (/Option) ("Option_Value")
Import [Object] Library "File Name.xml" (If Drive [Drive_Number]) (At ["Object_Name" or Object_Number]) (/Option) ("Option_Value")
```

For Timecode, the plausible commands are:

```text
Export Timecode 1 "rayflow_minimal_timecode"
Import Timecode Library "rayflow_minimal_timecode.xml" At Timecode 1
```

These should be verified against a real MA3 Timecode export before RayFlow generates XML.

## Track And Event Creation Gap

MA documents the Timecode object model as:

```text
Timecode Show
  -> Track Group
      -> Track
          -> Time Range
              -> Events
```

Track targets can be:

```text
Sequence, Sound, Timecode, Timecode Slot, Preset, Group, Master
```

However, the documented creation workflow for tracks and events is UI-driven:

- Open the Timecode Viewer.
- Enable Setup mode.
- Tap-and-hold New Track Group.
- Tap-and-hold New Track.
- Edit the Target cell through the Assignment Editor.
- Move the cursor and use Add Event or Add Multiple Events.

No official 2.3 command-line syntax was found for:

- Creating a Timecode track group.
- Creating a Timecode track.
- Assigning a track target to a Sequence.
- Adding Timecode events at a timestamp.
- Setting event token, cue destination, fade override, or execute-command flags.

## Live OSC Probes

The following non-destructive commands were sent through RayFlow OSC `/cmd` probes:

```text
About
List Timecode
Help Timecode
ChangeDestination Timecodes
List
Help TimecodeSlot
Help RunningTimecode
Help Export
```

Each command was sent successfully to `127.0.0.1:8000`, but no OSC feedback was received. `lsof -nP -iUDP:8000` also showed no visible listener before the probes. This means the live-probe portion is inconclusive: it does not disprove command support, but it did not provide MA3 command parser feedback in the current environment.

Earlier attempted mutating probes such as `Store Timecode "RayFlow Probe"` were blocked by the local sandbox before any OSC packet was sent, and were intentionally not re-run outside the sandbox because the plan called for a throwaway show before mutating MA3 state.

## Automation Recommendation

Use this automation boundary for Phase 7:

1. **Automate now via OSC/command line:**
   - Timecode pool object creation.
   - Timecode properties that MA documents through `Set Timecode`.
   - Timecode playback control.
   - Timecode XML export/import commands.

2. **Do not automate yet:**
   - Track group creation.
   - Track creation.
   - Track target assignment.
   - Event insertion/editing.

3. **Next required verification:**
   - Create a minimal Timecode object in MA3 2.3.2.0 using the Timecode Viewer.
   - Export it with `Export Timecode 1 "rayflow_minimal_timecode"`.
   - Capture and inspect the XML from `~/MALightingTechnology/gma3_library/datapools/timecodes`.
   - Document the XML shape before implementing `rayflow show export-timecode`.

## Minimal Capture Procedure

Use the smallest unavoidable UI step:

1. Use RayFlow/OSC or MA command line to create the Timecode object:

   ```text
   Store Timecode "RayFlow Minimal"
   Set Timecode "RayFlow Minimal" "Duration" "10"
   Set Timecode "RayFlow Minimal" "TCSlot" "Internal"
   ```

2. In MA3, open Timecode Viewer for `RayFlow Minimal` with Setup active.
3. Create one Track Group and one Track.
4. Assign the Track target to Sequence 1.
5. Add two events at known timestamps, for example 00:00:01:00 and 00:00:05:00, with `Go+` cue actions.
6. Export:

   ```text
   Export Timecode "RayFlow Minimal" "rayflow_minimal_timecode"
   ```

7. Copy the exported XML into a sanitized research fixture if licensing permits.

## Sources

- MA Lighting grandMA3 2.3 Manual: Timecode Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_timecode.html
- MA Lighting grandMA3 2.3 Manual: Create a Timecode Show — https://help.malighting.com/grandMA3/2.3/HTML/timecode_create.html
- MA Lighting grandMA3 2.3 Manual: Tracks — https://help.malighting.com/grandMA3/2.3/HTML/timecode_tracks.html
- MA Lighting grandMA3 2.3 Manual: Export Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_export.html
- MA Lighting grandMA3 2.3 Manual: Import Keyword — https://help.malighting.com/grandMA3/2.3/HTML/keyword_import.html
