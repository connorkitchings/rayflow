# MA3 Lua Patch and 3D Position Spike

**Target:** grandMA3 onPC 2.5.1
**Status:** run 2026-11-19, partial: imports and mover patch worked; wash patch, rotation and readback failed
**Plugin:** `ma3/plugins/spike_patch_3d/` (see its `README.md` for install and run steps)

## Questions this spike answers

1. What are the exact library names (and resulting show fixture type names) for a moving head and for the `LED - IRGBW` wash?
2. What are the available mode names and DMX channel counts for the wash type (and the mover), so the rig-as-code layer can pick a mode?
3. In onPC 3D, which direction do +X, +Y and +Z point (mover set to X=-3 Y=2 Z=6, wash to X=3 Y=-2 Z=6)?
4. Is the readback machine-readable: does the hand-built JSON parse, and does `ExportJson` produce valid JSON?
5. Do beams render in the onPC 3D window after the final `Fixture 1 + 101 At 100` step? Record which beams appeared (mover only, wash only, both).

Caveat for question 5: the library LED wash may default its colour emitters to 0, so it can stay dark even when it is patched and dimmed. Only the mover may light. One visible beam still proves 3D rendering. The spike sends no colour attribute commands.

Secondary: the real names of the fixture rotation properties (the readback dumps every property of each fixture).

## Command sequence

Modeled on `~/MALightingTechnology/gma3_2.5.1/shared/resource/lib_plugins/hw_test/libraryPlugin/hardwaretest/model/show/ShowPatch.lua:22-68`:

```text
cd Root
cd 'ShowData'.'Patch'
set 'FixtureTypes' 'Source'='library'
cd 'FixtureTypes'
import lib '<name>'              (retry; try candidate names, detect new child of FixtureTypes)
cd ..
cd 'Stages' / cd 1 / cd 'Fixtures'
store 2 thru 3
Assign FixtureType '<type>' at <idx>
Set <idx> Property 'FID' <fid>
Set <idx> 'PosX' | 'PosY' | 'PosZ' <value>
Set <idx> property 'Mode' '<HandleToStr(mode)>'     (mode found via ft.DMXModes children)
Set <idx> 'Patch' <universe.address>
```

Differences from ShowPatch.lua:

- The retry loop stops when a new fixture type actually appears under `FixtureTypes`, not only on a `Cmd` result of `OK`, because a bad library name may still return `OK`.
- Candidate library names tried in order. Mover: `Moving Head`, `Moving Head 1`, `Generic Moving Head`, `Moving Light`. Wash: `LED - IRGBW`, `LED - RGBW`, `LED - RGB`.
- Mode is the first enumerated mode for each type, not a hardcoded name.
- `Mode` object lookup uses `ft.DMXModes` / `DMXChannels` (seen in `systemtests/system_test_framework.lua:2240,2331`) instead of `FindRecursive(modeName)`.

Patched fixtures: mover FID 1 at 1.1, wash FID 101 at 1.101. Rotation values (mover 15/30/45, wash 10/20/35) are set only if a matching `RotX/RotY/RotZ` style property exists on the fixture.

## Assumptions

- ShowPatch.lua stores from index 2, implying index 1 already exists in `Stages.1.Fixtures` in a fresh show. The spike copies that: mover = index 2, wash = index 3. The readback reports `stageFixtureCount` and every fixture found, so this is checked, not trusted. If index 1 did not exist, expect an extra or missing fixture row and adjust.
- `Children()` order matches pool index (used only for the rotation step).
- Property reads use `obj:Get(name)`; property listing uses 0-based `PropertyCount()` / `PropertyName(i)` as in the MA system tests.
- Readback directory is `GetPath(Enums.PathType.Library)` joined with `/`.

## APIs not verified against the help pages

Marked `-- UNVERIFIED` in the Lua where they appear:

- `coroutine.yield(seconds)` argument semantics (ShowPatch.lua writes `coroutine:yield(1)`).
- `CurrentProfile().FixtureLibShowMA/User/Share` (copied from ShowPatch.lua, not in help pages).
- `PropertyCount`, `PropertyName`, `Find`, `FindRecursive`-style navigation, `DMXModes`, `DMXChannels`, `FixtureType` and `Mode` as object fields: seen only in MA's shipped Lua (system tests, hw_test), not in the 2.5.1 help HTML.
- Rotation property names (`RotX/RotY/RotZ` and variants) are guesses.
- `/` as path separator on Windows.
- `BuildDetails()` (help example for `ExportJson` uses it).

Verified in help HTML: `Cmd` (returns `OK`, `Syntax Error`, `Illegal Command`), `ExportJson(filename, table)` (docs warn output may not be valid JSON), `Export`, `GetPath(Enums.PathType.Library)`, `Echo`, `HandleToStr`, object `Children`, `Count`, `Get`, `Dump`. `Export` (XML) is not used.

## Outputs

Written to `gma3_library/`: `spike_patch_3d_log.txt`, `spike_patch_3d_readback.json` (hand-built via `io.open`), `spike_patch_3d_readback_exportjson.json` (via `ExportJson`). Readback values are read from the show objects after the commands run, not the values the script set. Each fixture row includes a full `properties` dump.

## Results

Run 2026-11-19 in a new scratch show on grandMA3 onPC 2.5.1.1 (build `6dd1a8dc`, compiled 2026-10-06), macOS. The plugin ended with `done. errors=2`. Evidence: `ma3_patch_3d_spike_log.txt`, `ma3_patch_3d_spike_result.json`, `ma3_patch_3d_spike_exportjson_result.json` (copies of the three output files).

"Verified" means backed by a line in the log or readback file. "Unverified" means not observed.

| Question | Answer | Status |
|---|---|---|
| Plugin import into the Plugins pool | Imported `spike_patch_3d.xml` from the `spike_patch_3d/` subfolder of the library via the Edit dialog's Import button in the Plugins pool. The result was plugin `Spike Patch 3D` with component file `spike_patch_3d.lua` (16kB, Source: Showfile). The import browser first listed only MA's sample plugins, so how the file was located is not recorded | Verified (observed on screen) |
| Mover library name and type | `import lib 'Moving Head'` returned OK; new type `Moving Head` (first candidate name worked) | Verified (log) |
| Wash library name and type | `import lib 'LED - IRGBW'` returned OK; new type `LED - IRGBW` (first candidate name worked) | Verified (log) |
| Modes and channel counts | `Moving Head`: `Default`, 9 channels. `LED - IRGBW`: `16 bit` (5 ch) and `8 bit` (5 ch). Chosen: mover `Default`, wash `16 bit` | Verified (readback) |
| `store 2 thru 3` | Returned OK, but afterwards only slot 2 accepted commands. See the wash failure below | Verified (log) |
| Mover patch and position | At slot 2: `Assign FixtureType`, `Set Property 'FID' 1`, `PosX -3`, `PosY 2`, `PosZ 6`, `Set property 'Mode'` and `Set 'Patch' 1.1` all returned OK | Command acceptance verified. Stored values not read back (see readback failure) |
| Wash patch and position | Every `Set` at slot 3 returned `Illegal object`: FID 101, PosX/Y/Z, Mode, Patch 1.101. `Assign FixtureType ... at 3` returned OK | Verified (log). Cause unknown |
| Index 1 pre-exists in `Stages.1.Fixtures` | Unknown. `cd 'Stages'`, `cd 1`, `cd 'Fixtures'` all returned OK, but the readback that counts fixtures crashed | Unverified |
| Rotation property names and effect | Rotation step crashed before it ran | Unverified |
| Axis directions in 3D (+X, +Y, +Z) | Not observed | Unverified |
| Beams in 3D | No fixture or beam visible in the 3D Viewer (Display 2) with the Front and Auto cameras; only an empty grey room. Intensity was never set: `Fixture 1 + 101 At 100` returned `Object not found`. The Top camera was not checked | Unverified. This run does not show whether 3D beams render |
| Hand-built readback JSON parses | Yes, `ma3_patch_3d_spike_result.json` parses with Python `json`, but it contains no data beyond imports, modes, build and the errors, with `"fixtures": []` | Verified |
| `ExportJson` output valid JSON | No. It returned `true`, but the file is unquoted-key, tab-indented JS-object style and fails `json.load`. Treat it as non-JSON and use the hand-built writer | Verified |
| Build info | `BigVersion` 2.5.1.1, `HostType` onPC, `CodeType` Release | Verified (readback) |

### Errors in the log

1. `Set 3 ...` x6 returned `Illegal object` (all commands on the wash at slot 3).
2. `ERROR in rotation` and `ERROR in readback`, both at `spike_patch_3d.lua:151`: `attempt to index a nil value (field 'Stages')`. Line 151 is `Root().ShowData.Patch.Stages[1].Fixtures` in `stageFixtures()`. The command-line `cd 'Stages'` worked, so the Lua object path to `Stages` differs from the dot-index used.
3. `Fixture 1 + 101 At 100` returned `Object not found`. This is expected because the wash never got FID 101, but it also means the mover was not given intensity.

### Findings

- Library imports work and the names `Moving Head` and `LED - IRGBW` are correct for 2.5.1.1, as are the modes above.
- The Lua path `Root().ShowData.Patch.Stages` is `nil` in this build. The `stageFixtures()` helper needs a different lookup. Not yet determined which.
- `store 2 thru 3` reporting OK is not proof that both fixtures exist. Slot 3 was an illegal object for `Set`.
- The plugin has no step that verifies the stage fixtures after `store`, so a bad run looks successful until the readback.

### Follow-ups (separate scoped change, not in this pass)

1. Find the correct Lua path to the stage fixtures, for example by dumping `Root().ShowData.Patch` children in a small probe or using `Patch.Stages` via `Children()`.
2. Re-check whether `store 2 thru 3` creates both slots, or whether the wash needs its own `store 3` or a different index.
3. After the readback works, re-run to capture rotation property names, then check axis directions and beam rendering in 3D. Include the Top camera and set intensity on the mover only if the wash patch stays broken.
