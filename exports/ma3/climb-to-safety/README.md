# RayFlow MA3 Show Export: Climb to Safety Studio

Generated for grandMA3 onPC 2.3.2.0.

## Contents

- `rig.mvr` — MVR rig export for MA3 patch and 3D import.
- `ma3_push_commands.txt` — dry-run OSC command list for Sequence 1.
- `timecode.xml` — MA3 Timecode XML based on captured MA3 2.3.2.0
  event exports; validate import/playback before use.
- `metadata.json` — bundle metadata for automation and review.

## Verified Boundaries

RayFlow does not generate a native `.show.gz` file in this bundle. The MA3
native show format is treated as opaque until a writable format is verified.
This bundle uses inspectable artifacts instead: MVR, OSC command text, and
captured-export-shaped Timecode XML.

## Import Workflow

1. Import `rig.mvr` into grandMA3 to create the rig/patch for `Rig 1`.
2. Review `ma3_push_commands.txt` before sending anything to MA3.
3. Dry-run the same command path with:

   `rayflow show push-to-ma3 "Climb to Safety Studio" --sequence 1`

4. When the rig and command list look correct, send the cues with:

   `rayflow show push-to-ma3 "Climb to Safety Studio" --sequence 1 --execute`

5. Import `timecode.xml` into grandMA3 via *Import → Timecode Pool*
   and validate the events against the Timecode Viewer.

> **Note:** The Timecode XML follows captured MA3 2.3.2.0 event exports. Verify
> import/playback in MA3 before relying on it for show playback.
