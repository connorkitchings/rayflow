# MA3 Control Capability Matrix

**Date:** 2026-05-22  
**grandMA3 onPC version:** 2.3.2.0  
**Purpose:** Decide whether RayFlow has enough verified control over grandMA3 onPC
to program MA3-native looks, and define what must be proven before adding an MCP
server.

## Result

RayFlow has a useful command path into MA3, but it does not yet have a complete
lighting-programming control layer.

Verified today:

- RayFlow can send arbitrary MA3 command-line strings through OSC `/cmd` when
  MA3 OSC input is enabled.
- RayFlow can generate MVR rig exports, MA3 sequence/cue command lists, and
  MA3 Timecode XML from captured 2.3.2.0 exports.
- MA3 accepted RayFlow sequence/cue commands during the Phase 7 timecode probe.
- MA3 accepted imported RayFlow Timecode XML in a clean Timecode slot and
  preserved target/cue event fields on re-export.
- MA3 accepted Timecode playback commands and advanced the internal Timecode
  cursor.

Not verified enough for full programming:

- Fixture-aware color, position, beam, focus, gobo, and phaser programming.
- Creating MA3 presets from RayFlow's abstract preset attributes.
- Reliable readback of current programmer, selected fixtures, active cue, pool
  state, executor state, or current output state.
- Fully automated fixture type import/patch for the sample fixtures through
  MA3 command line alone.

Conclusion: **control research should continue before MCP implementation**. An
MCP server would be useful later, but it should expose verified MA3 operations,
not hide unresolved console-control gaps.

## Evidence Baseline

Installed local version:

```text
2.3.2.0
```

Repo sample fixtures for reproducible probes:

| Fixture | File | Control families to prove |
| --- | --- | --- |
| LED PAR 64 RGBW | `data/fixtures/samples/BlenderDMX_LED_PAR_64_RGBW.gdtf` | dimmer, RGB/RGBW color |
| Robe Robin MMX Blade | `data/fixtures/samples/Robe_Robin_MMX_Blade.gdtf` | dimmer, pan, tilt, color/gobo basics |

Existing local evidence:

- `docs/research/ma3_basic_looks_probe_2_3_2.md` documents a live OSC probe
  that created/exported sequence, group, and preset shells, but failed to prove
  disposable-show creation, fixture patching, or fixture-aware preset content.
- `docs/research/ma3_disposable_show_and_fixture_probe_2_3_2.md` documents the
  current safety blocker: MA3 `app_gma3` is bound to UDP 8000, but the latest
  `SaveShow`/`NewShow` `/cmd` attempts produced no observable title or show-file
  mutation. Row-level OSC command receive must be reconfirmed before any deeper
  live mutation probe.
- `docs/research/ma3_timecode_xml_2_3_2.md` documents captured Timecode XML,
  clean import/re-export, and cursor movement after playback.
- `docs/research/ma3_timecode_command_automation_2026-05-19.md` documents the
  command-line boundary for Timecode pool objects versus UI-only event editing.
- `src/rayflow/shows/push.py` intentionally drops non-dimmer preset attributes
  because direct MA3 color values such as `#FF9933` were rejected during the
  Phase 7 probe.
- `tests/test_push.py` verifies RayFlow's current MA3 push behavior: dimmer
  commands are emitted, color attributes are preserved in show data but skipped
  during MA3 push.

## Capability Matrix

Status values:

- **Verified automation**: safe to automate now with current evidence.
- **Needs proof**: plausible, but needs MA3 export/readback or live observation.
- **Manual/setup-only**: keep as documented setup for now.
- **Not viable yet**: no reliable current interface.

| Capability | MA3 object/model | Required setup | Write operation | Readback/verification | Known failure modes | Status | MCP exposure |
| --- | --- | --- | --- | --- | --- | --- | --- |
| OSC command send | Command line via OSC `/cmd` | OSC Input On, row `Receive=Yes`, `Receive Command=Yes`, UDP 8000 | `rayflow console cmd "<command>" --execute` | Command effect, MA3 monitor/exports; feedback is not reliable yet | Wrong IP/interface; OSC disabled; UDP has no delivery confirmation; latest session had UDP listener but no visible `/cmd` effect | Verified automation when configured; current session needs command-receive reconfirmation | Tool: `ma3.send_command`, but require dry-run/confirm for mutations |
| MA3 version pin | Application bundle metadata | `/Applications/grandMA3.app` installed | None | `CFBundleVersion` reads `2.3.2.0` | App upgraded without docs update | Verified automation | Resource: `ma3.environment` |
| Disposable show isolation | Show file / loaded show | A known throwaway show loaded in MA3 | `NewShow "rayflow_control_probe"`, `SaveShow`, or UI-created `rayflow_control_probe` followed by harness verification | New `.show` file exists and is the active show | `SaveShow As "..."` is wrong syntax and created `As.show`; latest `NewShow "rayflow_control_probe"` + `SaveShow` and `SaveShow "rayflow_control_probe"` attempts produced no file/title change while command receive was suspect | Needs proof | Required before mutating MCP tools |
| MVR rig export | MVR scene with embedded GDTF | RayFlow rig + fixture library | `rayflow rig export-mvr` / bundle export | Import into MA3 and inspect patch/3D | Import may require user workflow; command-line import not fully proven | Needs proof | Tool after import workflow is verified |
| Fixture type import | FixtureTypes / GDTF library | Fixture file accessible to MA3 | GUI import or MVR import | Fixture type appears in MA3 Fixture Types | MA3 command-line import syntax is context-sensitive; World Server/UI may be required | Manual/setup-only | Resource guidance only until automated import is proven |
| Fixture patching | Patch / Fixture Schedule | Fixture type exists in MA3 | `Fixture 4 "LED PAR" At Address 1` or MVR import | Patch menu, exported patch/show state, visualizer response | Fixture name/mode mismatch; insert behavior depends on patch context | Needs proof | Tool only after sample-fixture patch round trip |
| Fixture/channel selection | Programmer selection | Patched fixtures or channels | `Fixture 1 Thru 4`, `Channel 1 Thru 8` | Fixture sheet highlight; possible Lua/ObjectList probe | Selection can be blocked by worlds/filters; no RayFlow readback yet | Needs proof | Tool after selection readback exists |
| Programmer clear | Programmer | Active programmer values | `Clear`, `ClearAll` | Fixture sheet/programmer state; output returns to tracked/default values | Clear levels differ; `ClearAll` can reset more than expected | Needs proof | Tool with explicit safety notes |
| Dimmer values | Programmer values / Dimmer feature group | Patched fixtures/channels | `Channel <range> At <value>` | Visualizer/output; stored cue export after `Store` | No patched channel means no visible output; values must be MA3-compatible | Verified for basic sequence setup; needs fixture-output proof | Tool for basic look programming after output proof |
| Direct color values | Color feature group | Fixture color attributes patched | Current RayFlow hex/name push is skipped | Prior probe rejected `Channel 2 At #FF9933` | MA3 needs fixture-aware attribute/preset syntax, not RayFlow hex strings | Not viable yet | Do not expose until mapped through presets/attributes |
| Color presets | Preset pool 4 / Color | Fixtures selected; color attributes set in MA3-compatible form | Likely `Store Preset 4.x`, `Label Preset 4.x` | Preset pool export/UI; applying preset changes output | Need exact syntax for RGB/RGBW values or encoder attributes | Needs proof | Future tool: `ma3.create_color_preset` |
| Position presets | Preset pool 2 / Position | Moving head patched; pan/tilt attributes controllable | Likely set pan/tilt then `Store Preset 2.x` | Preset pool export/UI; moving head position changes | Pan/tilt syntax and 16-bit attributes need fixture-aware mapping | Needs proof | Future tool: `ma3.create_position_preset` |
| Groups | Group pool | Fixtures selected | `Store Group <n>`, `Label Group <n>`, `Group <n>` | Group pool object/export; selected fixtures after recall | Probe exported Group 1 with SelectionData ID 1, but fixture identity/patch is not proven | Partially verified | Future tool after fixture and selection verification |
| Sequence/cue creation | Sequence pool and Cue objects | Programmer values or empty cues | `Store Sequence <n> Cue <m> /Overwrite /NoConfirmation`, `Label`, `CueFade` | Sequence XML export, cue sheet, timecode import resolving labels | Probe exported Cue 1 and fade, but no stored fixture values | Verified automation for structure; look content needs proof | Tool: `ma3.create_sequence_cues` |
| Executor assignment/playback | Executor/Page + Sequence | Sequence exists | `Assign Sequence 1 At Executor 201`, `Go Sequence 1` | Executor UI, sequence sheet, output/current cue | Current-cue readback not solved | Needs proof | Future tool after playback state probe |
| Timecode XML import | Timecode pool | Target sequence cues exist; clean slot | `Delete Timecode 1`, `Import Timecode Library "<file>" At Timecode 1` | Re-export preserves target/events | Import over existing object stripped fields in one probe | Verified automation with clean-slot rule | Tool after cue-fire observation |
| Timecode playback | Timecode pool | Imported Timecode object | `Top Timecode 1`, `Go Timecode 1`, `Off Timecode 1` | Re-export showed `Cursor="37.40"` | Cursor movement does not prove cues visibly fire | Partially verified; cue-fire needs proof | Tool with verification warning |
| Current cue/state readback | Runtime sequence/playback state | Sequence running | Unknown; candidates include Lua/ObjectList, exports, OSC feedback | Need current cue or playback state probe | Sequence XML before/after was byte-identical | Not viable yet | Essential future MCP resource; do not fake it |
| Pool object readback | Groups/Presets/Sequences/Timecodes | Objects exist | `List`, `Export`, or Lua probes | Exported XML or captured text/OSC feedback | OSC command feedback was unreliable in prior probe | Needs proof | Resource after readback channel is proven |
| Phaser/effects programming | Phaser data, MAtricks, Speed Masters | Fixture attributes and forms understood | MA3 command grammar / Phaser Editor | Visual output and exported sequence/preset data | Too advanced before basic looks | Not viable for this milestone | Defer |

## Basic Looks Milestone

The next implementation target should be deliberately small:

1. Create a disposable MA3 show named `RayFlow Control Probe`.
2. Import or patch:
   - one LED PAR 64 RGBW fixture for dimmer/color proof;
   - one Robe Robin MMX Blade fixture for pan/tilt proof.
3. Prove selection and clear behavior:
   - select each fixture/channel;
   - set a dimmer value;
   - clear programmer state;
   - capture how to verify each state.
4. Prove one MA3-native color preset and one position preset:
   - create and label the preset;
   - apply it to the fixture;
   - store a cue using the preset;
   - export enough MA3 state to confirm the stored cue references real MA3 data.
5. Prove sequence playback:
   - store three cues in Sequence 1;
   - assign Sequence 1 to an executor;
   - play cues through command line;
   - identify a reliable current-cue or output-state readback method.

Acceptance for this milestone is not "the UI looked right once." It is a
repeatable evidence packet: commands sent, exported files or screenshots, known
readback channel, and a short conclusion for each capability.

## MCP Implications

Build MCP only after the basic look milestone produces verified operations.

Good first MCP resources:

- `rayflow://environment/ma3` — installed MA3 version, OSC endpoint, current
  verification status.
- `rayflow://shows/<name>/context` — existing show context bundle.
- `rayflow://ma3/capabilities` — this control matrix as machine-readable
  capability status.

Good first MCP tools after verification:

- `ma3_dry_run_commands(show, sequence)` — return command list only.
- `ma3_send_command(command, execute=false)` — command send with explicit
  mutation guard.
- `ma3_export_timecode(show, sequence)` — generate XML from verified schema.
- `ma3_probe_state(kind)` — only once a readback method is proven.

Do not expose these yet:

- `create_color_preset`
- `create_position_preset`
- `program_basic_look`
- `verify_current_cue`

Those names describe the right future interface, but they need MA3 proof first.

## Sources

- Local RayFlow evidence: `docs/research/ma3_timecode_xml_2_3_2.md`.
- Local RayFlow evidence:
  `docs/research/ma3_timecode_command_automation_2026-05-19.md`.
- Current push implementation: `src/rayflow/shows/push.py`.
- Current push tests: `tests/test_push.py`.
- MA3 operations reference: `docs/ai/MA3_OPERATIONS.md`.
- MA3 command reference: `docs/ai/MA3_COMMAND_REFERENCE.md`.
- MA Lighting grandMA3 2.3 Manual: Timecode Keyword —
  https://help.malighting.com/grandMA3/2.3/HTML/keyword_timecode.html
- MA Lighting grandMA3 2.3 Manual: Import Keyword —
  https://help.malighting.com/grandMA3/2.3/HTML/keyword_import.html
- MA Lighting grandMA3 2.3 Manual: Export Keyword —
  https://help.malighting.com/grandMA3/2.3/HTML/keyword_export.html
