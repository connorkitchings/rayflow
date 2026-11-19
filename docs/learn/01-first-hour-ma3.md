# Your first hour in grandMA3 onPC

Goal: patch a small rig, see it in the built-in 3D viewer, set intensity, color and position, store a cue, and play it. No hardware needed.

This guide follows `docs/ai/MA3_OPERATIONS.md`, which was checked against onPC 2.3.2. Menu labels can move slightly in 2.5. If a label differs, tell your AI tutor what you see and it will adjust the guide.

## 0. Before you start

1. Update grandMA3 onPC from 2.3.2 to 2.5 (free, from the MA Lighting download page). Install it over the existing app.
2. Launch onPC. On the start screen, create a **New Show** and name it `first-hour`.

Terms used below:
- **Patch**: the list of fixtures in the show, each with a fixture ID (FID) and a DMX address.
- **Programmer**: the live scratchpad where you set values. Nothing is saved until you Store.
- **Pool**: a grid of saved things (groups, presets, sequences).
- **Command line**: the text line at the bottom of the screen. Commands in this guide can be typed there and run with Enter.

## 1. Patch the rig (4 movers, 8 washes)

1. Open **Menu** and tap **Patch**. In an empty show a wizard opens.
2. Choose the fixture type: Library tab, source **MA**, then pick a Manufacturer, Fixture and Mode. Any moving head with pan, tilt, color and dimmer works for the movers. Any LED wash or PAR works for the washes.
   - Note the exact manufacturer, fixture and mode you chose. Phase 2 plugins need them.
3. Quantity `4`, First FID `1`, address `1.1`. Tap **Create !**.
4. Insert the washes: select a row, tap **Insert New Fixture**, choose the wash type, Quantity `8`, First FID `101`, address `1.101` (check it does not overlap the movers' channels; the mover rows show their address range). Tap **Create !**.
5. Check: the Patch window shows 12 rows.

## 2. Open the 3D viewer

1. Press the **3D** key, or use **Menu** then add a **3D** window to a view.
2. Fixtures appear at the origin of the stage, probably stacked. That is expected until you position them.
3. Position each fixture: in Patch, open the fixture row's position settings (X, Y, Z in meters and rotation), or use the **Show 3D Positions** mini viewer in the Patch menu. Suggested layout:
   - Movers on a back truss: Y = -3, Z = 5, X = -3, -1, 1, 3
   - Washes on a front truss: Y = 3, Z = 5, X spread from -4 to 4
   - Aim downward: rotate fixtures so they face the stage.
4. If you see no beams later, check the 3D window settings for beam rendering and haze, and make sure the fixtures have intensity.

## 3. Select and set values

Type these on the command line, press Enter after each:

1. `Fixture 101 Thru 108` selects the washes.
2. `At 50` sets intensity to 50%. You should see washes light up in 3D.
3. Open the encoder bar **Color** layer, or the Color Picker, and pick amber.
4. `Fixture 1 Thru 4` selects the movers, then `At Full`.
5. Open the encoder bar **Position** layer and turn pan and tilt until the beams point at the stage.

## 4. Store groups, a preset and a cue

1. Select the washes, then `Store Group 1`. Select the movers, then `Store Group 2`.
2. Select Group 1, set amber, then `Store Preset 4.1` (color pool).
3. Select Group 2, aim the beams, then `Store Preset 2.1` (position pool).
4. With a look in the programmer (washes amber at 50%, movers aimed at full), press **Store**, then tap an empty executor. This creates a sequence with cue 1.
5. Type `ClearAll` to empty the programmer. The lights go dark.

## 5. Play it

1. Press the executor's **Go** (or type `Go+ Sequence 1`). The look from cue 1 fades in on the 3D viewer.
2. Repeat steps 3 and 4 with a different color to store a second cue, using `Store Cue 2` while the new look is in the programmer.
3. Play cue 1 and cue 2 in turn with Go+. Try `Store Cue 2 Time 4` style fade times later.

## Gate: the 3D viewer check

Take a screenshot of the onPC 3D window with beams visible on stage, and send it to your AI tutor.

- If beams render: Phase 2 can start.
- If the 3D window is blank, black, or crashes on this Apple Silicon Mac: tell your AI tutor which of those happened. The fallback is buying a viz-key and using Capture Student, which is already installed.
