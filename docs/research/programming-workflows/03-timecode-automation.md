# Timecode Integration and Automation

**Source:** `docs/research/manual_research2.txt`  
**Parsed:** 2026-05-25

## Timecode Format

A continuous digital clock signal transmitted via MIDI Timecode (MTC) or SMPTE audio signals. Format: hours:minutes:seconds:frames (e.g., 01:14:32:12).

## Integration Workflow

1. **System Lock:** Lighting console is networked to the playback computer or master show controller ("Master Clock").
2. **Cue Linking:** Programmer constructs standard cue lists.
3. **Timecode Mapping:** Each cue is assigned an absolute, frame-accurate timecode trigger instead of relying on a physical "GO" button.
4. **Synchronized Playback:** As the master audio/video timeline plays, it broadcasts timecode. The console listens; when incoming clock matches a cue's trigger, the cue executes.
5. **Redundancy Protocols:** Manual fallback options are configured. If timecode stream drops, the console transitions to manual tracking so the operator can execute cues on the beats without dropping output.
