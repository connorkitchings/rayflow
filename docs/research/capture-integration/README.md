# Capture Integration Research

## Purpose

This dossier tracks how RayFlow should use Capture as the primary visual-review
and recording surface. It is written for future implementation work, not as an
end-user quickstart. The user-facing workflow remains in
`docs/guides/capture-workflow.md`.

## Decision Summary

RayFlow should not try to generate native Capture project files in the first
integration pass. The supported product loop is:

1. RayFlow remains the source of truth for show YAML, rig YAML, cues, presets,
   and fixture-aware rendered DMX frames.
2. RayFlow exports an MVR handoff bundle for Capture import.
3. Capture imports the rig, resolves fixture types through its own library, and
   saves any native `.c2p` or `.c2s` project file.
4. RayFlow drives Capture through sACN or Art-Net for visual review.
5. The user records the Capture visualizer and gives timestamped critique.
6. RayFlow applies targeted cue refinement and repeats the export/review loop.

Native Capture project generation remains out of scope until MVR import plus
DMX-driven review is proven on the `Climb to Safety Studio` pilot.

## Official Documentation Findings

### Product and Edition Constraints

The Capture 2026 download page states that the standard download is both the
demo and full version, with the full version activated once a licence is
installed. Demo mode disables saving and limits each session to 90 minutes.

Capture 2026 Student Edition is free to use for any purpose and differs from
Solo Edition in ways that matter to RayFlow:

- It has unlimited DMX universes.
- It has a reduced truss and fixture library.
- Motion objects and special effects are unavailable.
- It opens and saves Student Edition project files only.
- It does not export Capture Presentations.
- All console connectivity options except MA-Net3 are present and functional.

RayFlow implication: Student Edition is viable for the first local proof if the
sample fixture types can be mapped to the reduced library. If fixture mapping is
poor, the standard demo can still prove import and DMX visual behavior, but not
save a reusable project.

### MVR Import

Capture's 2026 manual lists MVR as a model import format. The manual describes
MVR as an interchange format containing geometry, textures, and patch
information. Capture supports MVR version 1.4 and higher and prompts the user to
identify Capture library fixture types corresponding to fixture types referenced
in the MVR.

RayFlow implication: MVR is the correct first handoff format, but the import
step may require human fixture matching. RayFlow should improve the handoff by
including fixture matching notes and fixture family fallbacks, rather than
pretending the native project can be generated automatically.

### DMX Connectivity

Capture's connectivity page says Capture supports many network protocols and
generally recommends Art-Net or sACN ethernet DMX protocols. It also warns
against using WiFi for console connectivity.

The Universes tab manual says Capture automatically connects external universes
discovered on the network to project universes. The External universe property
can override assignment and can show which external universes Capture sees.

RayFlow implication: the near-term test harness should send sACN and Art-Net
frames and require the user to verify that Capture sees the expected external
universes. sACN should be the default because its universe numbering is less
ambiguous for users, but Art-Net should remain available when local loopback or
network behavior makes it easier.

### Developer Surfaces

Capture's developer page documents CITP as an integration option. CITP can
transmit DMX to Capture without Art-Net or sACN, receive DMX feedback from
Capture, transmit streaming video, and use Capture-specific CAEX extensions for
live view imagery, cue recording UI, and bidirectional fixture patch/selection
communication.

Capture also exports glTF 2.0 with a `CAPTURE_model` extension.

RayFlow implication: CITP/CAEX is the likely future path if RayFlow needs
automated screenshots, live view acquisition, fixture patch feedback, or a more
Capture-native cue recording interface. It should not block the first proof
because RayFlow already has Art-Net/sACN output.

## Local Sample Project Findings

Attached files inspected on 2026-06-05:

| File | Finding | RayFlow implication |
|------|---------|---------------------|
| `/Users/connorkitchings/Downloads/Student Edition Club.c2s` | Binary Student Edition Capture project. Header strings include `StudentProject` and `SoftwareVersion`. | Treat `.c2s` as native Capture state owned by Capture. Do not generate directly. |
| `/Users/connorkitchings/Downloads/Chateau.zip` | Contains `Chateau.c2p`, `BLACK.jpg`, `kalido.mp4`, and `red loop.mp4`. | Native project plus media bundle. Useful as reference, not as a generation target. |
| `/Users/connorkitchings/Downloads/Teatro.zip` | Contains `Teatro.c2p`, image media, and multiple video files. | Native project plus media bundle. Shows Capture projects can depend on sidecar media. |
| `/Users/connorkitchings/Downloads/Electric Opera.zip` | Contains `Electric Opera.c2p`, `.ies`, `.ILD`, image, and video media. | Capture projects can include photometric and laser/media assets. RayFlow should not assume a single project-file artifact. |

The `.c2p` and `.c2s` files are proprietary binary project formats. They are not
simple XML or JSON. Direct generation would be brittle and unsupported.

## RayFlow Integration Architecture

```text
RayFlow show YAML
  + RayFlow rig YAML
  + GDTF fixture samples
        |
        v
show export-capture
        |
        +--> rig.mvr              -> Import into Capture
        +--> cue_sheet.md         -> Review notes by timestamp/section
        +--> metadata.json        -> Handoff provenance
        +--> README.md            -> Manual import and DMX steps
        |
        v
RayFlow DMX output
  sACN or Art-Net
        |
        v
Capture visualizer
        |
        v
screen recording + critique
        |
        v
show refine-cues / targeted edits
```

## Near-Term Implementation Plan

### 1. Capture Import Proof

Goal: prove `exports/capture/climb-to-safety/rig.mvr` imports into Capture and
produces a usable visible stage.

Actions:

1. Open Capture 2026 or Capture 2026 Student Edition.
2. Import `exports/capture/climb-to-safety/rig.mvr`.
3. Record every fixture matching prompt.
4. Save the resulting native Capture project if the edition allows it.
5. Add fixture matching notes to the Capture handoff bundle.

Success criteria:

- Fixture count matches RayFlow metadata.
- Fixture positions roughly match `data/rigs/Rig 1.yaml`.
- DMX addresses/universes match the RayFlow rig.
- The visual surface is understandable to a non-programmer.

### 2. DMX Link Proof

Goal: prove Capture responds to RayFlow-rendered frames.

Actions:

1. Configure Capture project universes to receive Art-Net first on localhost.
2. Run a RayFlow output command against a single cue with `--execute`.
3. Verify Capture's Universes tab sees external universe input.
4. Repeat with sACN only after resolving same-host UDP port binding behavior.
5. Document the exact working network/interface settings.

Success criteria:

- At least one fixture visibly changes in Capture from RayFlow output.
- The same cue can be repeated deterministically.
- The chosen protocol and universe numbering are documented.

2026-06-06 proof attempt:

- The installed `/Applications/Capture.app` was the iOS-on-Mac wrapper
  (`se.capture.capturemobile`, version `2026.0.34`), not the expected desktop
  import workflow.
- Opening `rig.mvr` with the wrapper produced a blank scene and no visible MVR
  fixture-matching prompt.
- The wrapper listened on UDP `6454` and `5568`.
- RayFlow Art-Net live send to `127.0.0.1:6454` succeeded with send-call-only
  evidence.
- RayFlow sACN live send failed locally because Capture already held UDP
  `5568`, and the Python sACN sender also tried to bind that port.
- The visual proof remains blocked until the desktop MVR import workflow is
  used.

2026-06-06 desktop Student Edition follow-up:

- Capture 2026 Student Edition `2026.0.37` (`se.capture.capturestudent`,
  `MacOSX`) exposed the expected `File > Import Model...` workflow.
- The importer detected three fixture types from `rig.mvr`: `BlenderDMX LED PAR
  64 RGBW`, `Robe Lighting Robin iSpiiderX`, and `Robe Lighting Robin MMX
  Blade`.
- Student Edition library search did not provide selectable replacements for
  the imported fixture types.
- Continuing without mappings failed with `Failed to read ... file is missing
  or broken` for all three embedded GDTF profiles.
- Capture loaded `0 polygons and 0 lines`, and the project Fixtures tab stayed
  empty.
- Desktop Capture owned UDP `6454`; RayFlow Art-Net send to `127.0.0.1:6454`
  succeeded, but no visual response was possible because no fixtures imported.
- The current blocker is RayFlow's Capture MVR/GDTF compatibility, not app
  selection or Art-Net output.

2026-06-06 Capture-compatible MVR spike:

- Added an opt-in Capture MVR profile where `GDTFSpec` references the exact
  embedded `.gdtf` filename.
- Generated `exports/capture/probes/one_fixture.mvr` with one `LED PAR 64 RGBW`
  fixture.
- Capture detected `LED PAR 64 RGBW, Default` and no longer reported the GDTF as
  missing or broken.
- Capture still loaded `0 polygons and 0 lines`, the import navigator was empty,
  and the project Fixtures tab stayed empty.
- The remaining proof needs a known Capture-friendly GDTF/MVR sample or a
  substitution workflow that maps RayFlow fixture intent to Capture library
  fixtures.

2026-06-06 Capture library mapping follow-up:

- Capture Student's Library tab initially reported `No library installed`.
- Installing through the Library tab `Download` button loaded library version
  `6/5/26` and created `Library.c2z` under Capture Student's application
  support directory.
- Re-importing `exports/capture/probes/one_fixture.mvr` showed real Capture
  library fixture options.
- The imported `LED PAR 64 RGBW, Default` fixture type was mapped to
  `Generic Par 64, Control (1 ch)`.
- Capture saved the mapping locally and reused it on the next import attempt.
- The probe still loaded `0 polygons and 0 lines`, opened the import navigator,
  and did not create a project fixture row after the navigator was closed.
- The current blocker is now project placement/import geometry, not missing
  library data or missing fixture identification.

### 3. Timed Playout Proof

Goal: trigger the full `Climb to Safety Studio` cue list in song time while
Capture is visible.

Actions:

1. Add or adapt a RayFlow command that outputs rendered cues at their timestamps
   through sACN or Art-Net.
2. Produce a dry-run report before live output.
3. Run live playout while the song is played locally.
4. Capture a screen recording.
5. Save a recording report that links the show YAML, rig YAML, Capture handoff,
   Capture project, protocol settings, and video path.

Success criteria:

- The user can watch a video, not just inspect DMX evidence.
- Timing is good enough for timestamped feedback.
- The loop can be reproduced from documented commands.

### 4. Feedback Refinement Proof

Goal: use the recording to refine the show without regenerating everything.

Actions:

1. Review the recording by section.
2. Convert notes into structured critique:
   `section`, `timestamp`, `issue`, `desired_change`.
3. Use `show refine-cues` when its critique categories fit.
4. Use targeted cue edits when the critique is more specific.
5. Re-export the Capture handoff and repeat the recording.

Success criteria:

- Unaffected sections stay stable.
- Changes are proposal-first until applied.
- The before/after videos show a visible improvement.

## Open Questions

- Does Capture Student Edition's reduced fixture library contain acceptable
  substitutes for RayFlow's current `Rig 1` fixtures?
- Does the desktop Capture 2026 workflow expose MVR import on this Mac, separate
  from the installed iOS-on-Mac wrapper? Answer from 2026-06-06: yes, desktop
  Capture Student exposes `File > Import Model...`.
- Which GDTF/MVR package shape does Capture accept for fixture import, and what
  differs from RayFlow's current embedded sample profiles?
- Does Capture 2026 on this Mac receive sACN from localhost reliably once the
  UDP `5568` bind conflict is resolved, or do we need Art-Net/unicast or a
  non-loopback interface?
- Does RayFlow's current MVR exporter emit enough geometry for an immediately
  useful stage, or do we need to add truss/stage objects to the handoff?
- Should the Capture handoff include a generated fixture-matching checklist per
  fixture type?
- Should RayFlow create a dedicated `show play-capture` command, or generalize
  `show record` away from QLC+ into backend-neutral timed playout?
- When should we explore CITP/CAEX for automated live-view capture?

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Student Edition cannot map RayFlow fixtures well | Visual review looks wrong | Use generic substitute fixtures; document mapping; consider standard demo for import proof |
| sACN loopback fails on macOS | No visible DMX response | Try Art-Net; try a non-loopback interface; document exact interface settings |
| MVR import lacks stage/truss context | Fixtures import but scene is hard to judge | Add simple stage/truss geometry to RayFlow MVR or provide Capture setup checklist |
| Native `.c2p` generation is tempting | High engineering risk | Keep native files owned by Capture until official automation path is identified |
| Recording remains manual | Product loop feels incomplete | Automate timed DMX playout first; later explore Capture live image capture through CITP/CAEX |

## Source Links

- Capture download page: `https://www.capture.se/Downloads/Download-Capture`
- Capture documentation page: `https://www.capture.se/Support/Documentation`
- Capture connectivity page: `https://www.capture.se/Support/Connectivity`
- Capture developer page: `https://www.capture.se/Support/Developers`
- Capture 2026 manual, Universes tab:
  `https://www.capture.se/Manual/en-UK/2026/UniversesTab.html`
- Capture 2026 manual, File menu / MVR import:
  `https://www.capture.se/Manual/en-UK/2026/FileMenu.html`
- Capture design page:
  `https://www.capture.se/Products/Capture/design`
