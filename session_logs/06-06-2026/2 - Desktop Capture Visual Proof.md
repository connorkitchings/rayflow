# Session Log — 2026-06-06 (Session 02)

## TL;DR

- **Goal**: Use desktop Capture 2026 Student Edition to import `exports/capture/climb-to-safety/rig.mvr`, verify the rig, send one RayFlow cue over Art-Net, and record whether Capture visibly responds.
- **Result**: Desktop Capture proof reached the correct MVR import workflow, but visual proof still failed because Capture could not read the embedded fixture profiles and imported zero fixtures.
- **Evidence**: Capture Student Edition `2026.0.37` opened `File > Import Model...`, identified three MVR fixture types, then reported all three fixture files as missing or broken and loaded `0 polygons and 0 lines`.
- **DMX**: Desktop Capture Student owned UDP `6454`; RayFlow Art-Net cue 1 sent successfully to `127.0.0.1:6454`, but there were no imported fixtures to respond.
- **Next**: Fix or replace the Capture MVR/GDTF payload before timed playout or recording work.
- **Branch**: `codex/climb-to-safety-product-loop`

## Desktop App Verification

Mounted local installer:

```bash
hdiutil attach '/Users/connorkitchings/Downloads/Capture 2026.0.37 Student.dmg' -nobrowse
```

Mounted path:

```text
/Volumes/Capture 2026 Student
```

Desktop app bundle:

```text
/Volumes/Capture 2026 Student/Capture 2026 Student Edition.app
```

Bundle metadata:

- `CFBundleIdentifier`: `se.capture.capturestudent`
- `CFBundleShortVersionString`: `2026.0.37`
- `CFBundleSupportedPlatforms`: `MacOSX`
- `CFBundleExecutable`: `Capture Student Edition`

This is the desktop Student Edition app, not the iOS-on-Mac wrapper from the earlier attempt.

## MVR Import Attempt

Workflow used:

1. Started a new Capture project.
2. Opened `File > Import Model...`.
3. Selected `rig.mvr`.
4. Capture opened the `Identify Fixtures` dialog.

Fixture types detected by Capture:

| Imported fixture type | Capture library fixture | Result |
|---|---|---|
| `BlenderDMX LED PAR 64 RGBW, Default` | none | Student library search returned no selectable match for `BlenderDMX LED PAR 64 RGBW`, `PAR RGBW`, or `LED` |
| `Robe Lighting Robin iSpiiderX, Mode 2 - Basic` | none | left unmapped |
| `Robe Lighting Robin MMX Blade, Mode 1 - Standard` | none | left unmapped |

After continuing without fixture mappings, Capture reported:

```text
Loading file '/Users/connorkitchings/Documents/rig.mvr'..
ERROR: Failed to read 'BlenderDMX@LED PAR 64 RGBW' - file is missing or broken.
ERROR: Failed to read 'Robe Lighting@Robin iSpiiderX' - file is missing or broken.
ERROR: Failed to read 'Robe Lighting@Robin MMX Blade' - file is missing or broken.
Done loading 0 polygons and 0 lines.
There were errors during import - please review them before continuing.
```

Project verification after import:

- Design views were empty.
- Fixtures tab showed no project fixture rows.
- No fixture count, stage positions, universe assignments, or visible fixture output could be verified inside Capture.

## MVR Package Checks

The file imported from Documents was byte-identical to the repository artifact:

```bash
shasum -a 256 '/Users/connorkitchings/Documents/rig.mvr' \
  'exports/capture/climb-to-safety/rig.mvr'
```

Result:

```text
8bf01d8747a479961d951b7366c612daa7d7dfb4268afc47d00990781db64233  /Users/connorkitchings/Documents/rig.mvr
8bf01d8747a479961d951b7366c612daa7d7dfb4268afc47d00990781db64233  exports/capture/climb-to-safety/rig.mvr
```

Archive integrity passed:

```bash
unzip -t 'exports/capture/climb-to-safety/rig.mvr'
```

Entries:

```text
GeneralSceneDescription.xml
BlenderDMX@LED PAR 64 RGBW.gdtf
Robe Lighting@Robin iSpiiderX.gdtf
Robe Lighting@Robin MMX Blade.gdtf
```

Each source `.gdtf` sample also passed `unzip -t`. This narrows the problem to Capture compatibility with the embedded GDTF payload or MVR packaging details, not ZIP corruption.

## Art-Net Proof

Desktop Capture Student listener check:

```bash
lsof -nP -iUDP:6454 -iUDP:5568
```

Relevant result:

```text
Capture 22043 ... UDP *:6454
Capture 22043 ... UDP *:5568
```

Dry run:

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend artnet \
  --target 127.0.0.1 \
  --json
```

Result:

- Passed.
- Target: `127.0.0.1:6454`.
- Rendered universe `0`, channels `1-30`, with nonzero dimmer/color values.

Live send:

```bash
uv run rayflow show output-cue 'Climb to Safety Studio' 1 \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --rig 'Rig 1' \
  --backend artnet \
  --target 127.0.0.1 \
  --execute \
  --json
```

Result:

- Passed.
- RayFlow reported `status: sent`, universe `0`, evidence quality `send-call-only`.
- Visual response failed because Capture had no imported fixtures.

## Decision

The next blocker is no longer app selection. The desktop Capture app and Art-Net listener path work. The blocker is the MVR/GDTF import payload:

- Capture recognizes the MVR fixture types.
- Capture cannot read the embedded GDTF files as usable fixture definitions.
- Capture imports no geometry or fixtures.

Do not proceed to timed Capture playout until RayFlow can produce a Capture-accepted MVR or a Capture-friendly fixture substitute workflow.

## Recommended Next Step

Create a Capture-compatible MVR export spike:

1. Build a minimal one-fixture MVR using a known Capture-friendly fixture profile or fixture type.
2. Verify Capture imports at least one fixture row and places it on the stage.
3. Compare the working MVR/GDTF package shape against RayFlow's current export.
4. Update RayFlow's Capture handoff export only after the one-fixture import succeeds.
