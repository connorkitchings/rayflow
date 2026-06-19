# Capture Visual Review Workflow

RayFlow's primary visual-review path is Capture. QLC+ is no longer used for the
product loop because it did not provide a usable stage visualization for the
`Climb to Safety Studio` pilot.

## Install Capture

Use the current Capture download and documentation pages as the source of truth
for supported platforms, licensing, and Student Edition limits:

- Download page: `https://www.capture.se/Downloads/Download-Capture`
- Documentation page: `https://www.capture.se/Support/Documentation`

The documentation page links to the web reference manual, an offline EPUB
download path through the manual toolbar, and short getting-started tutorials.

For the deeper research basis behind this workflow, see
`docs/research/capture-integration/README.md`.

## Export the RayFlow Handoff

```bash
uv run rayflow show export-capture 'Climb to Safety Studio' \
  --dir data/shows \
  --rig-dir data/rigs \
  --fixture-dir data/fixtures/samples \
  --output-dir exports/capture/climb-to-safety \
  --dmx-protocol sacn
```

The bundle contains:

- `rig.mvr` — import this into Capture.
- `cue_sheet.md` — review cue timing and labels while watching the song.
- `metadata.json` — machine-readable handoff metadata.
- `README.md` — import and DMX review instructions.

## Import Into Capture

1. Open Capture 2026 or Capture 2026 Student Edition.
2. Use Capture's model import workflow to import
   `exports/capture/climb-to-safety/rig.mvr`. Do not rely on double-clicking or
   opening the MVR as a project file.
3. If prompted, map the imported GDTF fixture types to Capture library fixtures.
4. Confirm fixture positions and patch against `data/rigs/Rig 1.yaml`.
5. Set Capture universe input to sACN or Art-Net, matching the handoff.

Record every fixture matching prompt during the first import. Those mappings
should become part of the RayFlow handoff so the next import is repeatable.

## Review Loop

1. Render or play RayFlow cues over the selected DMX protocol.
2. Watch Capture with the studio track.
3. Take notes by cue or section.
4. Apply feedback with `show refine-cues` or targeted cue edits.
5. Re-export the Capture handoff and repeat.

## Current Boundary

RayFlow does not yet generate a native Capture project file. The first proof is
MVR import plus DMX-driven visual review. Once that works, the next engineering
step is to automate more Capture-specific setup, such as camera/stage defaults
or fixture matching notes.

## Local App Caveat

On 2026-06-06, `/Applications/Capture.app` was verified as an iOS-on-Mac wrapper
with bundle identifier `se.capture.capturemobile`. It registered only native
Capture project document types (`.c2p` and `.c2s`), accepted an `open -a` handoff
for `rig.mvr`, but showed a blank scene and no MVR fixture-matching prompt. For
the first product proof, use the desktop Capture workflow that exposes explicit
MVR/model import.

The same app was observed listening on UDP `6454` and `5568`. RayFlow Art-Net
send to `127.0.0.1:6454` succeeded, while same-host sACN send failed because
Capture already held UDP `5568`.

On the same date, desktop Capture 2026 Student Edition `2026.0.37` successfully
opened `File > Import Model...` and detected the three fixture types in
`rig.mvr`, but could not read the embedded GDTF fixture files. Capture reported
each fixture file as missing or broken, loaded `0 polygons and 0 lines`, and the
project Fixtures tab remained empty. Treat the current MVR/GDTF payload as not
yet Capture-compatible.

The first Capture-specific MVR probe changed `GDTFSpec` to reference the exact
embedded `.gdtf` filename. Capture then detected `LED PAR 64 RGBW, Default`
without the missing/broken GDTF error.

The next blocker was Capture Student's fixture library. On 2026-06-06, the
desktop app initially reported `No library installed` in the Library tab and the
log contained `Library::LibraryManager::Load : No library loaded`. Installing
the library through the Library tab's `Download` button loaded library version
`6/5/26`, enabled fixture search results, and allowed a repeatable mapping from
`LED PAR 64 RGBW, Default` to `Generic Par 64, Control (1 ch)`. Capture saved
that association in its local custom fixture mappings file.

That mapping still did not complete the proof. The probe imported as
`0 polygons and 0 lines`, opened Capture's import navigator, and required a
drag/drop into the project design. After closing the navigator, the project
Fixtures tab remained empty. The next proof needs either a known
Capture-friendly fixture/MVR shape that creates placeable project content or a
manual navigator placement check that proves whether placement alone creates a
fixture row.

## Manual Fixture Visual Proof

On 2026-06-19, the visual-output path was proven independently of MVR fixture
placement:

- App: Capture 2026 Student Edition `2026.0.37`.
- Library date: `6/5/26`.
- Fixture: Capture library `Generic Par 64`, mode `Control (1 ch)`.
- Capture patch: internal universe `1`, address `1`.
- RayFlow output: Art-Net universe `0`, channel `1`, sent to
  `127.0.0.1:6454`.
- Result: Capture's universe preview visibly changed to `100%` for the patched
  Generic fixture after `rayflow bridge send` set channel 1 to `255`.

Proof artifacts:

- `exports/capture/proofs/rayflow-visual-proof.c2s`
- `exports/visualizations/capture-proof/rayflow-artnet-universe-0-channel-1-100pct.png`

This unblocks timed playout and recording work. It does not close the MVR
fixture-placement blocker: `one_fixture.mvr` still requires a Capture library
mapping and has not created a project fixture row through the import navigator.

## Sample Project Findings

The attached Capture samples are useful as reference projects, but they should
not become generated RayFlow artifacts yet:

- `Student Edition Club.c2s` is a binary Student Edition project file.
- `Chateau.zip`, `Teatro.zip`, and `Electric Opera.zip` contain native `.c2p`
  Capture projects plus media/assets such as `.jpg`, `.mp4`, `.mov`, `.ies`,
  and `.ILD` files.
- The `.c2s` and `.c2p` files are proprietary binary project formats, not
  simple text formats suitable for direct generation.

Decision: keep RayFlow's first Capture integration at the supported handoff
boundary: export MVR for the rig, send DMX via sACN or Art-Net, and use Capture
itself to save any native `.c2p` or `.c2s` project after import and fixture
matching.

## Next Research Tasks

1. Import `exports/capture/climb-to-safety/rig.mvr` into Capture and document
   fixture matching results.
2. Build a timed Art-Net playout and recording artifact using the saved manual
   proof project.
3. Continue the MVR fixture-placement investigation separately from recording.
4. Repeat over sACN only after resolving the local UDP `5568` bind conflict or
   using a separate host/interface.
5. Decide whether timed Capture playout should extend `show record` or become a
   new backend-neutral command.
6. Defer CITP/CAEX until MVR import plus sACN/Art-Net playout produces a
   reviewable recording.
