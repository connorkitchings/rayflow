# MA3 Timecode XML Capture Notes

**Date:** 2026-05-19  
**grandMA3 onPC version:** 2.3.2.0  
**Fixture:** `data/ma3_exports/samples/rayflow_minimal_timecode_track_skeleton_2_3_2.xml`

## Result

A real MA3 2.3.2.0 Timecode export was captured, but it is a track skeleton, not the final event-bearing fixture required for `rayflow show export-timecode`.

The captured object proves the top-level Timecode, TrackGroup, MarkerTrack, Track, and TimeRange XML shape. It does not yet prove the event XML schema, cue target reference format, or Go+ cue action encoding.

Keep `show export-timecode` blocked until a Timecode export containing at least two cue events is captured and documented.

## Capture Commands

The installed MA3 version was verified with:

```bash
/usr/libexec/PlistBuddy -c 'Print :CFBundleVersion' /Applications/grandMA3.app/Contents/Info.plist
```

Output:

```text
2.3.2.0
```

The initial Timecode pool object was created through the MA3 web remote command line:

```text
Store Timecode "RayFlow Minimal"
Set Timecode "RayFlow Minimal" "Duration" "10"
Export Timecode "RayFlow Minimal" "rayflow_minimal_timecode"
```

That export produced only the Timecode header:

```xml
<Timecode Name="RayFlow Minimal" Duration="10.00" TCSlot="-1" .../>
```

A Lua probe appended structural Timecode children:

```text
Lua "local tc=ObjectList('Timecode 1')[1]; local tg=tc:Append('TrackGroup'); local tr=tg:Append('Track'); Echo('rayflow appended timecode track')"
Export Timecode 1 "rayflow_minimal_timecode_lua_track"
```

MA3 exported the resulting XML at:

```text
~/MALightingTechnology/gma3_library/datapools/timecodes/rayflow_minimal_timecode_lua_track.xml
```

## Captured Structure

The export root records the MA3 data version:

```xml
<GMA3 DataVersion="2.3.2.0">
```

The Timecode object stores show-level settings as attributes:

| XML field | Captured value | RayFlow relevance |
| --- | --- | --- |
| `Name` | `RayFlow Minimal` | Use from `Show.title` or export label. |
| `Duration` | `10.00` | Use max cue timestamp plus tail padding. |
| `TCSlot` | `-1` | Represents the captured internal/default source state. Needs confirmation before generation. |
| `LoopCount` | `0` | MVP should leave non-looping. |
| `AutoStop` | `No` | Playback behavior; do not synthesize until validated with events. |
| `SwitchOff` | `Keep Playbacks` | Playback cleanup behavior. |
| `TimeDisplayFormat` | `Default` | Display-only unless generation requires frame formatting. |
| `FrameReadout` | `Default` | Display-only unless generation requires frame formatting. |

The captured hierarchy is:

```text
GMA3
└── Timecode
    └── TrackGroup
        ├── MarkerTrack
        ├── Track
        │   └── TimeRange
        └── Track
            └── TimeRange
```

Captured child objects:

| XML element | Notes |
| --- | --- |
| `TrackGroup` | Contains `Play=""` and `Rec=""`; likely default per-group playback/record flags. |
| `MarkerTrack` | MA3 created a marker lane with `Name="Marker"`. |
| `Track` | Contains `Guid`, `Play=""`, and `Rec=""`; target assignment was not captured. |
| `TimeRange` | Contains `Guid`, `Duration="To End"`, `Play=""`, and `Rec=""`; events are expected to be children of this element per MA3 docs. |

## Event Schema Gap

MA's Timecode docs state that events are children of `TimeRange`, and that manually created cue events only trigger correctly when the Timecode show's Playback and Record setting is `Manual Events`.

The captured XML does not contain:

- Track target reference to `Sequence 1`.
- Event timestamp attributes.
- Event token/action encoding for `Go+`.
- Cue destination/reference encoding.
- Playback and Record setting serialization.

Without those fields, RayFlow cannot safely generate importable Timecode XML.

## Automation Findings

- MA3 command-line export works for Timecode pool objects.
- MA3 Lua `Append("TrackGroup")` and `Append("Track")` created exportable TrackGroup/Track/TimeRange XML.
- The MA3 2.3 manual still documents event creation through Timecode Viewer UI, not a command-line event creation syntax.
- A direct WebSocket command injection helper was tested against MA3 Web Remote after Playwright stalled, but it did not produce additional exports; it is not a reliable path yet.

## Next Required Capture

Use the MA3 Timecode Viewer with Setup active to create the missing event-bearing fixture:

1. Open or create `RayFlow Minimal`.
2. Set duration to `10s`.
3. Keep source/internal timecode as the MVP target.
4. Create one Track Group.
5. Create one Track targeting `Sequence 1`.
6. Ensure Playback and Record is `Manual Events`.
7. Add two `Go+` cue events at `00:00:01:00` and `00:00:05:00`.
8. Export:

```text
Export Timecode "RayFlow Minimal" "rayflow_minimal_timecode_events"
```

Then copy the export into `data/ma3_exports/samples/` and update this note with the event element mapping.
