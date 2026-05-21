# MA3 Timecode XML Capture Notes

**Date:** 2026-05-19  
**grandMA3 onPC version:** 2.3.2.0  
**Initial fixture:** `data/ma3_exports/samples/rayflow_minimal_timecode_track_skeleton_2_3_2.xml`  
**Event-bearing local capture:** `~/MALightingTechnology/gma3_library/datapools/timecodes/findme2.xml`

## Result

A real MA3 2.3.2.0 Timecode export was initially captured as a track skeleton. A later local export, `findme2.xml`, captured event-bearing `CmdEvent` / `RealtimeCmd` records and is now the source of truth for RayFlow's first timecode XML generator.

The combined captures prove the top-level Timecode, TrackGroup, MarkerTrack, Track, TimeRange, `CmdSubTrack`, `CmdEvent`, and `RealtimeCmd` shape used by grandMA3 onPC 2.3.2.0. Import/playback validation is still required before the Phase 7 timecode milestone is considered complete.

`show export-timecode` may generate XML from the captured schema, but every generated file should still be validated in MA3 before relying on it for playback.

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

## Event Schema Capture

The local `findme2.xml` export captured both `Go+` command events and a sequence-targeted `Goto` event. RayFlow uses the `Goto` form because each cue timestamp maps to an explicit cue number.

Captured `Goto` structure:

```xml
<Track Target="ShowData.DataPools.Default.Sequences.Default" Play="" Rec="">
    <TimeRange Duration="To End" Play="" Rec="">
        <CmdSubTrack>
            <CmdEvent Name="Goto" Time="6.150" CueDestination="Cue 1">
                <RealtimeCmd Type="Key" Source="Original" UserProfile="0"
                    User="1" Status="On" IsRealtime="0" IsXFade="0"
                    IgnoreFollow="0" IgnoreCommand="0" Assert="0"
                    IgnoreNetwork="0" FromTriggerNode="0" IgnoreExecTime="0"
                    IssuedByTimecode="0" FromLocalHardwareFader="1"
                    IgnoreExecXFade="0" IsExecXFade="0"
                    Object="13.13.0.5.0" ExecToken="Goto"
                    ValCueDestination="0.5.0.1000"/>
            </CmdEvent>
        </CmdSubTrack>
    </TimeRange>
</Track>
```

RayFlow's generated XML intentionally keeps the captured command shape but omits the captured `Object` field because it appears to be a show-local object reference. Sequence targeting remains configurable through the `Track Target` attribute.

Captured details used by RayFlow:

- Time values are decimal seconds, such as `Time="6.150"`, not `HH:MM:SS.mmm`.
- Sequence tracks use `Target="ShowData.DataPools.Default.Sequences.<sequence>"`.
- Cue triggers are `CmdEvent Name="Goto"` with `CueDestination="Cue <number>"`.
- `RealtimeCmd` uses `ExecToken="Goto"` and `ValCueDestination="0.5.0.<cue_number * 1000>"`.
- MA3 exports Timecode XML as UTF-8 with BOM; RayFlow writes timecode XML with `utf-8-sig`.

## Live Round-Trip Validation

On 2026-05-21, RayFlow generated and imported a 15-event sample Timecode XML into grandMA3 onPC 2.3.2.0 after first creating the target Sequence 1 cues through OSC.

The first import attempt over an existing Timecode object accepted timestamps but stripped the target and cue destination fields on re-export. A clean import path worked:

```text
Delete Timecode 1 /NoConfirmation
Import Timecode Library "rayflow_sample_timecode.xml" At Timecode 1
Export Timecode 1 "rayflow_sample_timecode_roundtrip_3"
```

The successful re-export preserved:

- Track target rewritten by MA3 to the resolved sequence name:
  `ShowData.DataPools.Default.Sequences.All In Time`.
- All 15 `CmdEvent Name="Goto"` events.
- Cue destinations rewritten from `Cue <n>` to cue labels, such as `Intro Open`.
- `ExecToken="Goto"` and `ValCueDestination="0.5.0.<cue_number * 1000>"` for every cue.
- Times above 60 seconds rewritten to MA3's display format, such as `1m02.000`.

Validated automation requirements:

- OSC command input must be enabled with `Receive=Yes`, `ReceiveCommand=Yes`, UDP port `8000`.
- RayFlow must target the MA3 interface IP when loopback is not active, for example `10.0.0.241`.
- Target sequence cues must exist before importing the Timecode XML.
- Import Timecode into a clean Timecode slot; delete the old Timecode object first when replacing it.

During cue-stack setup, MA3 accepted explicit sequence-targeted cue commands:

```text
Store Sequence 1 Cue 1 /Overwrite /NoConfirmation
Label Sequence 1 Cue 1 "Intro Open"
Set Sequence 1 Cue 1 CueFade "4"
```

MA3 rejected direct RayFlow color values such as `Channel 2 At #FF9933` and rejects channels if the show has no patched channel/fixture objects. Until fixture-aware color mapping is implemented, RayFlow's MA3 push path should send safe dimmer/intensity values only.

## Live Playback Probe

On 2026-05-21, RayFlow drove the imported Timecode object through OSC:

```text
Top Timecode 1
Go Timecode 1
Export Timecode 1 "rayflow_timecode_after_playback"
```

The post-playback export added `Cursor="37.40"` to Timecode 1. This proves
MA3 accepted playback control for the imported Timecode object and advanced its
internal cursor past the first three event timestamps: `0.000`, `15.000`, and
`30.000`.

`Export Sequence 1` before and after playback was byte-identical, so MA3
sequence XML export does not expose runtime current-cue state. The remaining
acceptance check is a visual Timecode Viewer/current-cue observation that the
`Goto` events fire Sequence 1 cues during playback.

## Automation Findings

- MA3 command-line export works for Timecode pool objects.
- MA3 Lua `Append("TrackGroup")` and `Append("Track")` created exportable TrackGroup/Track/TimeRange XML.
- The MA3 2.3 manual still documents event creation through Timecode Viewer UI, not a command-line event creation syntax.
- A direct WebSocket command injection helper was tested against MA3 Web Remote after Playwright stalled, but it did not produce additional exports; it is not a reliable path yet.

## Next Required Validation

Use RayFlow to generate a timecode XML, import it into MA3, start Timecode playback, and confirm in the Timecode Viewer/current-cue UI that cue events fire correctly:

```text
rayflow show export-timecode <show> --output /tmp/timecode.xml --sequence 1
```

Then import `/tmp/timecode.xml` into a clean Timecode Pool object and validate event playback against the Timecode Viewer. A post-playback re-export should show `Cursor` movement after `Go Timecode 1`; final acceptance also needs visible cue advancement.
