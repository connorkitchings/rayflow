# Your first hour in grandMA3 onPC

Goal: patch a small rig, see it in the built-in 3D viewer, set intensity, color and position, store a cue, and play it. No hardware needed.

This guide follows `docs/ai/MA3_OPERATIONS.md`, which was checked against onPC 2.3.2, plus what was seen on onPC 2.5.1.1. Menu labels can still move. If a label differs, tell your AI tutor what you see and it will adjust the guide.

## 0. Before you start

1. Launch grandMA3 onPC 2.5. It opens straight into the console, there is no start screen.
2. Click the command line at the bottom, type `NewShow "first-hour"` and press Enter. This creates a new empty show named `first-hour` (seen working on 2.5; not in the 2.3.2 probes).

Terms used below (full list in `glossary.md`):
- **Patch**: the list of fixtures in the show, each with a fixture ID (FID) and a DMX address.
- **Programmer**: the live scratchpad where you set values. Nothing is saved until you Store.
- **Pool**: a grid of saved things (groups, presets, sequences).
- **Command line**: the text line at the bottom of the screen. Commands in this guide can be typed there and run with Enter.

## 1. Patch the rig (4 movers, 8 washes)

Fixture choice, modes, FIDs and addresses are in `starter-rig.md`. Use that table, not guesses.

1. Type `Menu 'Patch'.'Edit'` on the command line and press Enter. The Insert New Fixtures dialog opens. (Seen working on 2.5.)
2. The dialog has a Show tab and a Library tab. Open the Library tab. The sources are MA, User and Share. Choose MA.
3. Type `moving head` in the search box, pick Manufacturer `Generic`, fixture `Moving Head`, mode `Default`. Set Quantity `4`, First FID `1`, address `1.001`, then confirm (the button was labelled **Create !** in 2.3.2; the 2.5 label is unverified).
4. Open the dialog again, search for the wash type listed in `starter-rig.md` (the wash row there is partly unverified; write down the mode you pick). Quantity `8`, First FID `101`, address `1.101`. Confirm.
5. Check: the Patch window shows 12 rows.

## 2. Open the 3D viewer

1. Press the **3D** key, or use **Menu** then add a **3D** window to a view.
2. Fixtures appear at the origin of the stage, probably stacked. That is expected until you position them.
3. Position each fixture: in Patch, open the fixture row's position settings (X, Y, Z in meters and rotation), or use the **Show 3D Positions** mini viewer in the Patch menu. Use the positions in the stage layout table in [`starter-rig.md`](starter-rig.md#stage-layout).
   - Aim downward: rotate fixtures so they face the stage. The table gives positions only.
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
