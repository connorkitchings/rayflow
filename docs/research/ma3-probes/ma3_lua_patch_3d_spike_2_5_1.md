# MA3 Lua Patch and 3D Position Spike

**Target:** grandMA3 onPC 2.5.1
**Status:** written, not yet run
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

Fill in after the run.

- Run date / onPC build:
- Exact library names that worked (mover):
- Exact library names that worked (wash):
- Resulting show fixture type names:
- Mover modes and channel counts:
- Wash modes and channel counts:
- Mode chosen for each:
- Index 1 pre-existed in `Stages.1.Fixtures`? (`stageFixtureCount`):
- Fixture rows read back (name, FID, type, mode, patch, PosX/Y/Z):
- Rotation property names:
- Axis directions in onPC 3D (+X, +Y, +Z):
- Hand-built JSON parses?:
- `ExportJson` output valid JSON?:
- Errors in log:
- Follow-ups:
