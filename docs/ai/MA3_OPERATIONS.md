# grandMA3 2.3 Operations Reference

> **FOR AI AGENTS.** Every MA3 operation documented with three approaches: GUI menu path, command-line syntax, and RayFlow/OSC equivalent. Sourced from the grandMA3 2.3 online manual, verified against 2.3.2.0.

---

## 1. Show Management

### New Show
**GUI:** Launch MA3 → Select "New Show" when prompted → Name show → OK
**CLI:** `NewShow`
**OSC:** `client.send("NewShow")`
**Verify:** Console initializes with blank show. Patch menu shows no fixtures.

### Open Existing Show
**GUI:** Launch MA3 → Select show file from list → Open
**CLI:** `LoadShow "Path/ShowName.show"`
**OSC:** Not available (requires file selection dialog)
**Verify:** Fixtures, cues, and settings from the show file appear.

### Save Show
**GUI:** Menu → Save Show (or `Ctrl+S` / `Cmd+S`)
**CLI:** `SaveShow`
**OSC:** `client.send("SaveShow")`
**Verify:** No confirmation dialog; show file timestamp updates.

### Save Show As
**GUI:** Menu → Save Show As → Enter name → OK
**CLI:** `SaveShow As "NewName"`
**Verify:** New `.show` file appears at chosen path.

### Close Show
**GUI:** Menu → Close Show
**CLI:** Not directly available via CLI
**Verify:** Console returns to launch screen.

---

## 2. Fixtures & Patching

### Open Patch Menu
**GUI:** `Menu` → `[Tap] Patch`
**CLI:** `Menu 'Patch'.'Edit'`
**OSC:** `client.send("Menu 'Patch'.'Edit'")`
**Verify:** Patch & Fixture Schedule window opens showing fixture rows.

### Add Fixture to Show (First Fixtures — Wizard)
**GUI (first fixtures in empty show):**
1. Menu → Patch
2. Wizard opens: Select fixture type (browse Manufacturer → Fixture → Mode)
3. Enter custom name (optional)
4. Enter Quantity
5. Enter First FID number
6. (Full mode) Select Layer and Class
7. Enter Patch address: `Universe.Address` (e.g., `1.1`)
8. Tap **Create !**

**GUI (add more fixtures):**
1. Open Patch Menu
2. Select a row (new fixtures inserted **above**)
3. Tap **Insert New Fixture** (or **Insert** at bottom)
4. Select DMX Mode to use pop-up:
   - **Show** tab: already-imported fixture types
   - **Library** tab: browse Internal drive, USB, or Shares (GDTF Share via World Server)
     - Sources: **MA** (grandMA3 + converted grandMA2), **User**, **Shares**
5. Select Manufacturer → Fixture → Mode → **Select**
6. Insert New Fixtures Wizard: Name, Quantity, FID, Universe.Address
7. Tap **Create !**

**CLI:** `Fixture 4 "LED PAR" At Address 1` — Patches 4 LED PARs starting at address 1
**OSC:** `client.send('Fixture 4 "LED PAR" At Address 1')`
**Verify:** Fixtures appear in Patch Menu rows. Check visualizer: fixtures appear in 3D stage.

### Assign DMX Address to Existing Fixture
**GUI:**
1. Patch Menu → Select Patch cell(s)
2. Type `Universe.Address` → `Please`
3. Or tap **Patch** button → Edit Patch pop-up → use encoders or **PatchTo**
4. **Patch To Next Free Address** / **Patch To Next Free Universe** available
5. **PatchOffset**: DMX channel gap between consecutive fixtures
6. **AddressMode**: `Univ.addr` (universe.address) or `Absolute` (continuous numbering)

**CLI:** `Patch Fixture 2 3.123` — Patch fixture 2 to universe 3, address 123
**OSC:** `client.send("Patch Fixture 2 3.123")`
**Verify:** Patch column updates. Visualizer: fixture responds at new address.

### Open Edit Patch for Range
**GUI:** Select multiple Patch cells → tap **Patch** button → Edit Patch pop-up
**CLI:** `Patch Fixture 1 Thru 10` — Opens Edit Patch GUI for fixtures 1-10
**Verify:** Edit Patch pop-up appears with address controls.

### Delete Fixture
**GUI:** Patch Menu → Select fixture rows → Tap **Delete** → Save and Exit
**WARNING:** Deletes ALL programmed data for those fixtures. Cannot undo with Oops.
**CLI:** `Delete Fixture 2` (from patch context or main command line)
**OSC:** `client.send("Delete Fixture 2")`
**Verify:** Fixture rows disappear from Patch Menu and visualizer.

### Unpatch (Remove DMX Address, Keep Fixture)
**GUI:** Edit Patch pop-up → **Unpatch**
**Verify:** Patch column becomes empty. Fixture remains in show but produces no output.

### Import Fixture Type (GDTF)
**GUI:**
1. Menu → Patch → [left sidebar] Fixture Types
2. Tap **Import**
3. Select drive (Internal, USB)
4. Enable source toggles: **MA**, **User**, **Shares**
5. Browse Manufacturer → Fixture → Mode
6. Tap **Import**

**From USB:** Download `.gdtf` file from gdtf-share.com → Place at `grandMA3/gma3_library/fixturetypes/` on USB → Insert USB → Fixture Types → Import → USB drive → select `.gdtf` file → Import

**From GDTF Share:** Requires World Server connection → Enable Share toggle (![Share]) → Browse library → Import

**CLI:** `Import Library "FixtureTypeName"` (from FixtureTypes destination context)
**OSC:** Not directly available (requires UI interaction)
**Verify:** Fixture type appears in Fixture Types list. Available for patching.

### Select Fixtures by Type / DMX Address / Channel
**CLI:**
```
SelectFixtures FixtureType 3                  — Select all fixtures of type 3
SelectFixtures DMXAddress 513                 — Select by absolute DMX address
SelectFixtures DMXUniverse 2.001              — Select by universe.address
Channel 10                                    — Select fixture by Channel ID
Channel 1 Thru 8 At Full                      — Set channels 1-8 to full
```
**Verify:** Selected fixtures highlight yellow in fixture sheet.

### Move Universe
**CLI:** `Move DMXUniverse 1 At DMXUniverse 11` — Move all fixtures from universe 1 to 11
**Verify:** Fixture patch addresses update accordingly.

### Patch Menu Navigation
- **Columns** button: Toggle Condensed / Full mode
- **Split View**: Filter by Fixture Types, DMX Universes, Filters, Hierarchy, ID Types, Layers, Classes
- **Show 3D Positions**: Mini 3D viewer in patch menu
- **Filter dropdown**: Column-based filtering

### Sub-Fixtures and Multi-Instance
**CLI:**
```
Fixture 10.5                                 — Select sub-fixture 5 of fixture 10
Fixture 301.                                  — Select fixture 301 + all sub-fixtures
Fixture 301.1. Thru                          — Select all pixels of fixture 301
```
**Verify:** Sub-fixtures appear when clicking right-arrow in Name column.

### Multipatch Fixtures
Virtual fixtures that mirror a primary fixture's parameters with their own DMX address.

**Create (GUI):** Patch Menu → Select primary → **Create Multipatch** → Enter amount → `Please`
**CLI:**
```
Fixture 4 Multipatch 2                       — Select multipatch 2 of fixture 4
Patch Fixture 2 Multipatch 3 42.6            — Patch multipatch 3 of fixture 2 to 42.6
```
**Verify:** Multipatch fixtures appear in red text.

---

## 3. Groups & Presets

### Create Group
**GUI:**
1. Select fixtures (`Fixture 1 Thru 4 Please`)
2. Press `Store`
3. Tap empty Group Pool object, OR press `Group` key + enter group number + `Please`

**CLI:** `Store Group 1` — Store current selection as Group 1
**OSC:** `client.send("Store Group 1")`
**Verify:** Group pool object appears with selection count. Tap it → fixtures highlight.

### Select Group
**GUI:** Tap group in Group Pool
**CLI:** `Group 1`
**OSC:** `client.send("Group 1")`
**Verify:** Fixtures in group highlight yellow.

### Create Preset
**GUI:**
1. Select fixtures, set values (position, color, etc.)
2. Press `Store`
3. Tap empty Preset Pool object in the appropriate feature group pool (e.g., Color Pool)

**CLI:** `Store Preset 4.1` — Store as color preset 4.1
**OSC:** `client.send("Store Preset 4.1")`
**Verify:** Preset pool object appears. Tap it → fixtures take preset values.

### Apply Preset
**GUI:** Select fixtures → tap preset in pool
**CLI:** `At Preset 4.1` — Apply color preset 4.1 to selected fixtures
**OSC:** `client.send("At Preset 4.1")`
**Verify:** Selected fixtures take preset values.

### Update Preset
**GUI:** Modify fixture values → tap preset icon → Update option
**CLI:** `PresetUpdate 4.1` — Update preset with current values
**OSC:** `client.send("PresetUpdate 4.1")`
**Verify:** Preset reflects new values.

### Delete / Name Preset
**CLI:**
```
Delete Preset 4.1                            — Delete color preset 4.1
Label Preset 4.1 "Steel Blue"                — Name preset
```

### Preset Pools Reference
| # | Pool | Feature Group |
|---|------|---------------|
| 1 | Dimmer | Dimmer |
| 2 | Position | Pan/Tilt |
| 3 | Gobo | Gobo |
| 4 | Color | Color |
| 5 | Beam | Beam |
| 6 | Focus | Focus |
| 7 | Control | Control |
| 8 | Shaper | Shaper |
| 9 | Video | Video |
| 11-15 | All 1-5 | Any feature group |
| 16 | Dynamic | Auto-switches to selected feature group |

### Preset Modes
- **Selective (S)**: Only applies to fixtures stored in preset
- **Global (G)**: Applies to any fixture with matching attributes
- **Universal (U)**: Applies to any fixture, stores attribute relative to defaults
- **Force Global**: Forces Global behavior even if originally Selective

---

## 4. Programming (Selecting Fixtures + Setting Values + Storing Cues)

### Select Fixtures

**GUI:**
- Tap fixtures in Fixture Sheet
- Draw lasso in 3D Viewer
- Tap a Group Pool object
- Tap a Preset Pool object

**CLI:**
```
Fixture 1 Thru 5 Please                      → Select fixtures 1-5
Fixture 1 Thru 10 - 6 Thru 8                → 1-5 + 9-10 (exclude 6-8)
Fixture 1 + 5 + 9                           → Add specific fixtures
Fixture Thru                                 → Select all parent fixtures
Fixture Thru .                               → Select all + all sub-fixtures
-Group + Fixture 5                          → Add fixture 5 to group selection
```

### Clear Selection / Programmer
The programmer stores temporary values before they are committed to cues. Three levels:
1. **Selected fixture** (yellow name/ID)
2. **Active values** (will be stored)
3. **Deactivated values** (affect output but won't be stored)

**CLI:**
```
Clear                                       — 1st: Deselect fixtures (values still active)
Clear (2nd press)                           — 2nd: Deactivate values
Clear (3rd press)                           — 3rd: Full programmer clear
Hold Clear (≥1 sec)                         — Full clear immediately
```

### Set Dimmer / Intensity
**GUI:** Select fixtures → Level wheel, or encoder bar Dimmer layer
**CLI:**
```
Fixture 1 At 50                              — Set fixture 1 intensity to 50%
Fixture 1 Thru 4 At Full                     — Set 1-4 to 100%
Full                                         — Selected fixtures to 100%
Zero                                         — Selected fixtures to 0%
At 3 0 Please                                — 30% (two digits)
```

### Set Color
**GUI:** Encoder bar → Color layer → adjust RGB/CMY/RGBW encoders, OR tap color in Color Picker
**CLI:** Fixture selected → encoder bar Color layer OR Apply color preset: `At Preset 4.1`
**OSC:** `client.send("At Preset 4.1")`
**Verify:** Visualizer shows color change.

### Set Position (Pan/Tilt)
**GUI:** Encoder bar → Position layer → dual encoders for pan and tilt
**CLI:** Adjust via encoders after selecting Position feature group, or apply position preset: `At Preset 2.3`
**OSC:** `client.send("At Preset 2.3")`
**Verify:** Visualizer shows fixture beam movement.

### Set Gobo / Beam
**GUI:** Encoder bar → Gobo or Beam layer → adjust respective encoders
**CLI:** Via encoders or presets
**Verify:** Visualizer shows gobo/beam change.

### Store Cue

**GUI — Store on empty executor (creates sequence + cue 1):**
1. Set fixture values in programmer
2. Press `Store`
3. Press empty executor button/key
→ Auto-creates new sequence + cue 1 + assigns executor

**GUI — Store with specific cue number:**
1. Set values in programmer
2. Press `Store` → `Cue` → enter number → `Please`

**GUI — Store to existing sequence via pool:**
1. Have Sequence Pool visible
2. Set values → `Store` → tap-swipe pool object → Assign → release

**CLI:**
```
Store Cue 1                                 — Store as cue 1
Store Cue 2 Sequence 5                      — Store as cue 2 in sequence 5
Store Cue 42 "Chorus Look"                  — Store named cue
Store Cue 4 Time 6 Time 1                   — Store with CueFade 6, CueDelay 1
Store Cue 1 /Merge                          — Merge into existing cue 1
Store Cue 1 /Overwrite                      — Overwrite cue 1
Store Cue 1 /CueOnly                        — Store as Cue Only (blocks tracking)
Store Cue 1 /Remove                         — Remove values from cue 1
Store Cue Next                              — Store to next existing cue
```

**OSC:** `client.send("Store Cue 1")` or `client.store_cue(1)`
**Verify:** Cue appears in Sequence Sheet. `Go+` plays it back. Visualizer shows the look.

### Store Options Pop-up Context
When `Store` + executor on **existing** sequence:
- **Create Second Cue** — Next whole number
- **Overwrite** — Replaces all existing cue data
- **Merge** — Adds new values (new values take priority)
- **Remove** — Removes stored values for attributes active in programmer
- **Release** — Stores special release value

When `Store` into **existing cue**:
- **Tracking** — Normal tracking behavior
- **Cue Only** — Blocks tracked values in next cue
- **Overwrite / Merge / Remove / Release**
- **Dimmer Cue Only** — Only dimmer uses Cue Only rules
- **Tracking Shield**: Off / ↑0 / >0

### Hold Store Key (Temporary Store Settings)
Hold `Store` key ~1 second:
- **Data Source**: Programmer / Output / DMX
- **Use Selection**: ActiveForSelected / AllForSelected / Active / All
- **If Not Empty**: Ask / Overwrite / Merge / Remove / Release
- **Cue**: Tracking / Cue Only / Dimmer Cue Only / Shield
- **Look**: Stores all attributes of fixtures with dimmer > 0

### Update Cue
**CLI:** `Update Cue 3` — Opens Update Menu or updates directly
**GUI:** Press `Update` key (flashes when programmer has values) → right side shows possible update targets → tap cue part to update

**Update Menu Settings (right-side dark yellow area):**
- **Tracking**: Cue Only / Tracking / Dimmer Cue Only / Shield
- **Sequence Update Mode**: Original Content Only / Add New Content
- **Sequence Mode**: All / Selected / Last Go

### Copy / Move / Delete Cues
**CLI:**
```
Copy Cue 2 At Cue 6                          — Copy cue 2 to cue 6
Copy Cue 1 Thru 4 At Cue 11                 — Copy range
Move Cue 2 At Cue 6                          — Move cue 2 to cue 6
Delete Cue 2                                 — Delete cue 2
Delete Cue 1 Thru 5                          — Delete range
Delete Sequence 1                            — Delete entire sequence
```

### Renumber Cues
**GUI only:** Sequence Sheet → Select cue numbers in **No** column → `Edit` → Edit Cue Number pop-up → type new number

### Block / Unblock (Tracking Control)
```
Block Cue 3                                 — Block tracked values in cue 3
Unblock Sequence 2                          — Remove redundant blocks
```

---

## 5. Sequences & Executors

### Create Sequence
**GUI:**
1. Press `Store` + empty executor button
→ Auto-creates sequence + cue 1 + assigns executor
2. OR: Sequence Pool → empty slot → `Store` → tap pool object

**CLI:** Assign sequence to executor (see below)
**Verify:** Sequence appears in Sequence Pool. Sequence Sheet opens.

### Open Sequence Sheet
**GUI:** Tap sequence in Sequence Pool, OR `Select Sequence [n]`
**CLI:** `Select Sequence 1`
**OSC:** `client.send("Select Sequence 1")`
**Verify:** Sequence Sheet opens showing cue list.

### Assign Sequence to Executor
**GUI:**
1. Press `Assign`
2. Tap sequence pool object or type sequence number
3. Press executor key

**CLI:**
```
Assign Sequence 3 At Executor 105           — Assign seq 3 to button executor 105
Assign Sequ 3 At Executor 201               — Short form
Assign Sequence 4 At Page 2.301             — Assign to page 2, executor 301
```

### Executor Numbering
| Row | Numbers | Type |
|-----|---------|------|
| Bottom | 101-190 | Keys only |
| Fader | 201-290 | Fader + key |
| Encoder | 301-390 | Encoder + key |
| Top encoder | 401-490 | Encoder + key |
| Xkeys | 191-198, 291-298 | Extra keys |

### Executor Functions
**Key functions:** Go+, Go-, Goto, Load, Pause, Top, Flash, Temp, Toggle, On, Off, Select, Black, Kill, Swap, Rate1, Speed1, DoubleSpeed, HalfSpeed, Learn, LearnSpeed, FastSync, ReSync, Time, At, Call, SelectFixtures, Empty, Custom Command

**Fader functions:** Master, CrossFade (X), CrossFadeA (XA), CrossFadeB (XB), Temp, Rate, Speed, Time

**Trigger options per key (up to 4):** Press, Release, MA+Press, MA+Release

### Sequence Settings
Access: Sequence Sheet title bar → **Settings**, or Assign Menu → **Edit Settings**

**Key settings:**
- **Tracking**: On/Off (Off = all tracked values become released)
- **Wrap Around**: Last cue → Go+ returns to first cue
- **Restart Mode**: First Cue / Current Cue / Next Cue
- **Auto Start/Auto Stop**: Master fader controls On/Off
- **Cue Zero Mode**: Off / All Used Attributes / Only Used Dimmers
- **Priority**: Super → Swap → HTP → Highest → High → LTP → Low → Lowest
- **Soft LTP**: On = fades between sequences; Off = jumps to fader position
- **Playback Master**: Shared sub-master across sequences
- **Rate Master**: Individual or global speed master link
- **Speed from Rate**: Link speed to follow rate
- **Swap Protect / Kill Protect**
- **Use Executor Time**: Affected by Exec Time master
- **MIB**: Enabled / Never / Force Early / Force UponGo / Force Late

### Sequence Sheet Columns
- **No**: Cue number
- **Name**: Cue label
- **CueIn Fade**: Fade time for intensity ↑ and non-snap attributes
- **CueIn Delay**: Delay before In Fade
- **CueOut Fade**: Fade time for intensity ↓ (defaults to CueIn Fade)
- **CueOut Delay**: Delay before Out Fade (defaults to CueIn Delay)
- **Snap Delay**: Delay for snap attributes
- **Command Delay**: Delay for cue commands
- **Trig Type**: Go / Time / Follow / Sound / BPM
- **Trig Time**: Time for Time/Follow trigger types
- **Trig Sound**: Frequency filter for Sound trigger

### Track Sheet Mode
Toggle in Sequence Sheet. Shows attribute values with colors:
- **Magenta**: Tracked value
- **White**: Blocked (stored, same as tracked)
- **Cyan**: Higher intensity than previous cue
- **Green**: Lower intensity than previous cue
- **Deep-sea green bg**: MIB active
- Edit values → Calculator opens (with Specials: Block, Unblock, Extract Presets)

---

## 6. Timing

### Set Cue Fade / Delay Times
**GUI:** Sequence Sheet → Edit CueIn Fade / CueIn Delay / CueOut Fade / CueOut Delay columns directly

**CLI:**
```
Cue 3 CueFade 5                               → Both in and out fade = 5s
Cue 4 CueFade 5/8                             → In-fade 5s, Out-fade 8s
Cue 4 CueFade /3                              → Set OutFade only to 3s
Cue 3 CueDelay 1                              → Set both in/out delay to 1s
CueDelay 1/                                   → Set InDelay only to 1s
Cue 3 SnapDelay 0.5                           → Set snap delay to 0.5s
Store Cue 4 Time 6 Time 1                     → Store with CueFade 6, CueDelay 1
```

### Timing Priority (lowest → highest)
1. General cue times (CueFade, CueDelay)
2. Feature Type Timing (preset-type specific Fade/Delay)
3. Individual Attribute times (Indiv Fade, Indiv Delay)
4. Executor Time (at moment of cue execution)
5. Dynamic Rate

### Feature Group Timings
Each preset type has its own Fade and Delay column in Sequence Sheet. Overrides general cue timing for that feature group. Example: Position has 3s fade while Dimmer has 0.5s.

### Individual Attribute Timing
Set via programmer + stored in cue. Columns: **Indiv Fade**, **Indiv Delay**, **Indiv Duration** (read-only). Individual timing takes priority over general cue timing.

### Executor Time
**GUI:** Toggle `Time On/Off` on executor. When On, **Exec Time** master fader replaces stored fade/delay.
**CLI:** Not directly (fader movement)
**Notes:** Fader position sampled at cue trigger. Moving fader after won't affect running fade. Sequences can be protected via **Use Executor Time** setting (Off = protected).

### Rate (Dynamic Speed Scaling)
**GUI:** Rate fader on executor. Display: `1:1` (normal), `1:∞` (max), `Stopped` (min).
**CLI:**
```
Rate 1                                      → Reset to normal speed
Rate 0.5                                    → Half speed
Rate 2                                      → Double speed
```
**Notes:** Rate dynamically scales ALL timing. `*` prefix on time display.

### Speed Masters
15 available + BPM master. Assignable to executors.
```
Assign Master "Speed"."Speed1" At Page 1.201
Cue 3 CueFade "Speed1"                     — Use speed master as fade value
```
**Notes:** Or use `At Speed Sec [n]` / `At Speed Hz [n]` / `At Speed BPM [n]` for phaser/effect speed.

### Trigger Types (per cue)
Set in `Trig Type` column of Sequence Sheet:

| Type | Behavior |
|------|----------|
| **Go** | Needs manual command (Go+, Goto, etc.) |
| **Time** | Triggers after **Trig Time** seconds from previous trigger |
| **Follow** | Triggers when previous cue fade completes + optional **Trig Time** |
| **Sound** | Triggers on sound input (22 frequency areas, set in **Trig Sound** column) |
| **BPM** | Triggers on beat detection from sound input |

### Cue Transition Types (9 types)
Set per cue part. Affects value interpolation path:
```
Cue 3 Transition "Linear"                   — Even speed throughout
Cue 3 Transition "Slow"                     — Slow start, fast end
Cue 3 Transition "Fast"                     — Fast start, slow end
Cue 3 Transition "SCurve"                   — Slow start and end
Cue 3 Transition "Swing-"                   — Fast start/end, slight reverse
```
**Types:** Linear (default), Slow, Slow+, Fast, Fast+, SCurve, Swing-, Swing, Swing+

### Default Cue Timings
Menu → Preference and Timings → **Cues** tab:
- Cue Timings (fade/delay defaults)
- Preset Timings (feature group defaults)
- MIB Preferences

Menu → Preference and Timings → **Timings** tab:
- Playback Timings (Goto, Go-, >>>, <<< defaults)
- MIB Timings (Fade, Delay, Transition)

---

## 7. Effects Engine (Phasers)

**In MA3, "Phasers" replace the MA2 Effects engine.** Any cue/preset with 2+ steps IS a phaser.

### Create Simple Phaser (Dimmer Sinus)
**GUI:**
1. Select fixtures → `At 0 Please` (set all to 0)
2. Hold `MA` + press `Next` (creates step 2)
3. `Full` (step 2 = 100%)
4. Press `MA` + `Set` (selects all steps)
5. Encoder Toolbar: tap Accel layer → Calculator → `+/-100`
6. Encoder Toolbar: tap Decel layer → Calculator → `+/-100`
7. Encoder Toolbar: tap Phase layer → Calculator → `0 Thru 360`
8. `Store Cue 1`

**CLI:**
```
At Speed Hz 70                              — Set speed
At Phase 0 Thru 360                         — Spread fixtures across phase
Store Cue 1                                 — Store phaser as cue
```

### Create Phaser from Presets (Step Key Method)
**GUI:**
1. Select fixtures
2. Press and HOLD the Step key (X5 on console, or MA+X5)
3. Tap desired presets for each step while holding Step
4. Release Step key

**Notes:** You can tap multiple preset types per step (e.g., color + position for step 1).

### Modify an Existing Step
**GUI:** Press Step → type step number → tap new preset
**CLI:** `Delete Step 3` — Delete step 3 from phaser

### Phaser Editor (Visual)
**Open:** Add Window → Tools → Phaser Editor

**GUI — Circular position movement:**
1. Select fixtures, set dimmers to full
2. Tap A+ (Add Absolute) tool on left toolbar
3. Tap in the blue 2D grid — each tap = one step
4. Use Move Handles tool to curve the path into a circle
5. Use Edit Phase tool → tap "360" to spread fixtures across form
6. Store to cue or preset

### Phaser Layers

**Value Layers (per step):** Absolute values (e.g., dimmer 50%) and/or Relative values (e.g., dimmer -20%)

**Step Layers (per step, editable in Phaser Editor):**
- **Width** — Time from step start to next step start (% of beat). 100% = 1 beat, 0% = instant, 200% = 2 beats
- **Transition** — % of step width used for actual value change. 100% = fade whole step, 10% = snap then hold
- **Accel** — Acceleration at step start. -100% = smooth start, 0% = linear, 200% = abrupt
- **Decel** — Deceleration at step end. -100% = smooth arrival, 0% = linear, 200% = abrupt
- **Tip:** For linear, keep Accel/Decel at 0%. For sine-like, use -100%.

**Phaser Layers (global, per attribute per fixture):**
- **Speed** — BPM, Hz, or Seconds
- **SpeedMaster** — Links to one of 15 speed masters or BPM master
- **Phase** — Timing offset per fixture, 0-360°
- **Measure** — Number of beats in repeating loop (e.g., Measure=4 at 120BPM = repeats every 2s)

### Effect Forms (Select Form tool in Phaser Editor)
| Form | Description |
|------|-------------|
| Sine | Smooth sinusoidal (Accel/Decel = -100%) |
| Sawtooth | Ramp up, snap down |
| Rectangle | Square wave — snap between values |
| Circle | Circular 2D position movement |

### Create a Chase

**Approach A — Phaser with Width=0% (instant snap):**
1. Create phaser steps as above
2. Phaser Editor: select all steps → Change Width tool → set to 0%
→ Fixtures snap between values instantly

**Approach B — Sequence with Auto-Follow:**
```
1. Store each chase step as separate cue with CueFade 0
2. Set Trig = "Follow" for each cue in Sequence Sheet
3. Go+ triggers first cue → subsequent cues auto-trigger
```

### MAtricks (Pattern Sub-Selection)
Sub-divides fixture selection across X, Y, Z grid axes.

**MAtricks Window:** Add Window → Data Pools → MAtricks

**Properties (per axis X/Y/Z):**
- **Grid:** Axis, Block, Group, Wings, Width
- **Layers:** Fade From/To, Delay From/To, Speed From/To, Phase From/To
- **Shuffle:** Shuffle value, Shift value

**CLI:**
```
Set Selection MAtricks 'X' 6                — Set MAtricks X group size
Set Selection MAtricks "SpeedFromX" 10      — Set speed gradient on X
Next / Prev                                  — Step through sub-selection
Set                                          — Select all, deactivate MAtricks; press again to reactivate
Shuffle                                      — Randomize selection order
```

**Invert (at MAtricks window bottom):** InvertStyle (Pan/Tilt/PanTilt/All) + InvertX/Y/Z

### Store Phaser as Preset
```
Store Preset 4.5                            — Store as color phaser preset
At Preset 4.5                               — Recall phaser preset
Store Preset 4.5 /Merge                     — Merge into existing preset
```
**Note:** Phaser presets show a three-dot icon (multistep marker).

### Controlling Phaser Playback
| Action | CLI |
|--------|-----|
| Pause all | `Pause` |
| Stop sequence | `Off Sequence 1` |
| Rate control | `Rate 0.5` (half), `Rate 1` (normal) |
| Speed Master | `Assign Master "Speed"."Speed1" At Exec 201` |

### Stomp (Stop Running Phaser)
Calling a static preset on attributes currently in a phaser auto-stomps (stops) the phaser and outputs the static look.
**CLI:** `At Preset 4.1` (static color preset) — stops running color phaser

---

## 8. Playback

### Trigger Cues (Go+/Go-)
**GUI:** Press executor key (set to Go+ function)

**CLI:**
```
Go+                                         — Trigger next cue on active executor
Go+ Executor 201                            — Trigger next cue on executor 201
Go+ Cue 5 Executor 201                      — Trigger cue 5 (and subsequent timed/follow cues)
Go-                                         — Go to previous cue (no subsequent triggers)
Go- Executor 201                            — Go to previous on executor 201
Go- Cue 3 Executor 201                      — Go to specific cue (no subsequent triggers)
```

### GoFastForward / GoFastBackward (Skip Timing)
```
>>>                                        — Skip to next cue with 0s timing
>>> Cue 5                                  — Skip to cue 5 (no timing)
<<<                                        — Skip back (no timing)
<<< Cue 3                                  — Skip back to cue 3
```
**Notes:** Does NOT trigger follow/timed cues. Uses Playback Timings defaults.

### Go+ vs Go- vs Goto vs >>> vs <<<
- **Go+**: Triggers subsequent timed/follow cues
- **Go-**: Does NOT trigger subsequent cues
- **Goto**: Asserts tracked values. Mode: None/Assert/X-Assert
- **>>> / <<<**: Skip timing, no subsequent triggers

### Goto (Jump to Cue)
**GUI:** Press executor key set to Goto function → enter cue number → Please

**CLI:**
```
Goto Cue 4 Sequence 6                        — Jump to cue 4 in sequence 6
Goto Cue 10 Executor 201 Fade 2              — Goto with explicit 2s fade
Goto Cue Next                                — Goto next cue
Goto Sequence 42 Cue Previous                — Goto previous cue
Goto Cue 5 Fade 3 Executor 105               — Goto cue 5 with 3s fade on exec 105
```

### Goto Assert Modes
- **None**: Tracked values not asserted
- **Assert**: Tracked values take precedence, use timing from original storage cue
- **X-Assert**: Tracked values take precedence, use timing from the Goto cue

### Load (Preload Cue)
**CLI:**
```
Load Cue 3                                  — Preload cue 3 (execute with next Go+)
Load Executor 114 Cue 5                     — Load cue 5 on executor 114
Load /Loaded /NoConfirmation                — Clear all loaded cues
Go+ Loaded                                  — Trigger all loaded cues
```
**GUI:** Press `Goto` `Goto` to enter Load mode
**Verify:** Executor label toggles between cue number and name. Multiple sequences can have loaded cues.

### Pause / Top
**CLI:**
```
Pause                                       — Pause/resume all fades, delays, phasers
Pause Executor 201                         — Pause specific executor
Top                                         — Trigger first cue
Top Executor 201                           — Trigger first cue on executor 201
```

### Flash / Temp / Toggle
**CLI:**
```
Flash Executor 201                          — Flash executor (momentary)
Temp Executor 201                           — Temporary enable (while held)
Toggle Executor 201                         — Toggle on/off
```

### Off / Kill
**CLI:**
```
Off Sequence 1                              — Release output from sequence 1
Off Executor 201                            — Turn off executor
Kill Executor 201                           — Kill executor (force off)
```

### Speed Controls
**CLI:**
```
DoubleSpeed                                  — Double speed on active executor
HalfSpeed                                    — Half speed on active executor
LearnSpeed                                   — Tap-learn speed
Rate 1                                       — Reset rate
```

### Timecode Playback
**GUI:**
1. Open Timecode Pool: Add Window → Timecode
2. Store/edit on empty Timecode pool object
3. Set **TC Slot**: Internal or a Timecode Slot (SMPTE, MIDI, Art-Net timecode)
4. Use Timecode Viewer with **Setup** active
5. Record mode: Press Record button → with time source running → executor actions auto-recorded

**Manual event creation:**
1. Timecode Viewer with Setup active
2. Create Track Group (tap+hold New Track Group)
3. Create Track (unfold group → tap+hold New Track)
4. Set Track Target (edit Target cell → Assignment Editor)
5. Add events: Move green cursor → tap Add Event, OR activate Add Tool → tap track

**Event Columns:** Time, AbsTime, Token (Go+, Pause, Flash, etc.), Cue Destination, Fade Override, Execute Command

**RayFlow Timecode XML:**
```bash
rayflow show export-timecode "<show>" --output /tmp/timecode.xml --sequence 1
```

RayFlow's generated Timecode XML is based on local grandMA3 onPC 2.3.2.0
event-bearing exports. It writes UTF-8 with BOM and maps each cue to a
sequence-targeted `Goto` event using decimal-second timestamps. Import the XML
into the Timecode Pool, then verify event positions and playback in the
Timecode Viewer before using it for a finished show.

---

## 9. Network Protocols

### Enable/Disable Network
**GUI:** Menu → Network → Enable button (lower-right). Red = Off, Green = On.
**Note:** Network must be enabled for ANY Ethernet DMX or OSC communication.

### Art-Net Configuration
**Menu path:** `Menu` → `DMX Protocols` → Tap Art-Net tab

**Top-Level Buttons:**
| Button | Description |
|--------|-------------|
| **Preferred IP** | CIDR notation (e.g., `10.0.0.0/8`). For auto interface selection |
| **Interface** | Select Ethernet interface (Con1, Con2, Con3, or Auto). Per-station |
| **Enable Output** | On/Off. Master must enable to transmit |
| **Enable Input** | On/Off. Must be On to receive Art-Net |
| **Broadcast Threshold** | Switch from Unicast to Broadcast above this receiver count |
| **ArtPollRate** | Interval between ArtPollRequest packets |
| **Setup Mode** | On = config only; Off = DMX + config |
| **Send Art-Net If IdleMaster** | Must be On for standalone (non-session) output |
| **Output Delay** | 0-30ms delay for entire output |

**Data Tab — Row Columns:**
| Column | Description |
|--------|-------------|
| **Enabled** | Yes/No |
| **Mode** | Broadcast, Unicast, Auto, or Input |
| **Destination IP** | For Unicast mode |
| **Local Universe** | grandMA3 universe (1-1024). Starting if Amount > 1 |
| **Amount** | Number of MA3 universes in this row |
| **Net** | 0-127. Use 0 for Art-Net I/II compatibility |
| **Art-Net Sub-Net** | 0-15 (0-F hex) |
| **Universe** (Art-Net) | 0-15 (0-F hex). 16 per sub-net |
| **Art-Net Absolute** | Calculated: (Net × 256) + (Sub-Net × 16) + Universe |
| **Packet Delay** | Delay between transmitted universes |
| **Merge Mode** | Off, Prio, HTP, LowTP (Input only) |
| **Input Priority** | Super ... Lowest (Input only) |
| **Timecode Slot** | 1-8. Routes ArtTimeCode to timecode slot |

**Enable Art-Net Input (step-by-step):**
1. `Menu` → `DMX Protocols` → Art-Net
2. Toggle **Enable Input** to On
3. In Data tab: set a row to Mode = `Input`
4. Set **Local Universe** to match what RayFlow sends (typically 1)
5. Verify: `sudo lsof -iUDP:6454` → MA3 process (`app_gma3`) bound to `*:6454`

**Art-Net Universe Mapping:** MA3 "Local Universe 1" maps 1:1 to the first Art-Net universe in the row's range. If Amount > 1, consecutive MA3 universes map to consecutive Art-Net universes within the same Net/Sub-Net. Test both Art-Net universe 0 and 1 if uncertain.

### sACN (E1.31) Configuration
**Menu path:** `Menu` → `DMX Protocols` → Tap sACN tab

**Top-Level Buttons:** Same as Art-Net (Preferred IP, Interface, Enable Output, Enable Input, Setup Mode, Send If IdleMaster, Output Delay)

**Data Tab — Row Columns:**
| Column | Description |
|--------|-------------|
| **Enabled** | Yes/No |
| **Mode** | Output Multicast, Output Unicast, Input Multicast, Input Unicast |
| **Destination IP** | For Output Unicast |
| **Local Universe** | grandMA3 universe (1-1024) |
| **Amount** | Number of universes |
| **sACN Universe** | E1.31 universe number (1-63999) |
| **Priority** | 0-200 (default 100) |
| **Preview Only** | Send as preview data |
| **TTL** | Time to Live (default 8) |
| **Merge Mode** | Off, Prio, HTP, LowTP (Input) |
| **Input Priority** | Super ... Lowest (Input) |

**Limits:** sACN multicast input = max 20 universes. Combined Art-Net + sACN input = max 128 universes.

### OSC Configuration
**Menu path:** `Menu` → `In & Out` → OSC tab

**Top Buttons:**
| Button | Description |
|--------|-------------|
| **Preferred IP** | IP range filter |
| **Interface** | Ethernet interface selector |
| **Enable Output** | On = transmit OSC. Title bar highlights yellow when sending |
| **Enable Input** | On = receive OSC. Title bar highlights yellow when receiving |

**Row Configuration Columns:**
| Column | Description |
|--------|-------------|
| **Name** | Row name |
| **Destination IP** | Where to send OSC |
| **Mode** | UDP or TCP |
| **Port** | Same port for send and receive |
| **Prefix** | Optional filter (e.g., `/lighting`) |
| **Receive** | Yes/No — Receive OSC data |
| **Send** | Yes/No — Send OSC data |
| **Receive Command** | Yes/No — Receive command-line commands via OSC |
| **Send Command** | Yes/No — Send command-line commands via OSC |
| **EchoInput / EchoOutput** | Show in System Monitor |

**Enable OSC Input (step-by-step):**
1. `Menu` → `In & Out` → OSC
2. Toggle **Enable Input** to On
3. In row: set **Receive Command** to Yes
4. Set **Port** to 8000 (default)
5. Verify: `sudo lsof -iUDP:8000` → MA3 listening on `*:8000`

**Key OSC Addresses:**
| Address | Type | Purpose |
|---------|------|---------|
| `/cmd` | `s` (string) | Command line control. e.g., `/cmd,s,Store Cue 1` |
| `/Page1/Fader201` | `i` or `f` | Direct fader control |
| Enumerated addresses | `si` or `sif` | Pool object control (retrieve via Lua) |

**RayFlow OSC usage:**
```python
from rayflow.engine.console.osc import Ma3OscClient
client = Ma3OscClient("127.0.0.1", 8000)
client.send("Store Cue 1")
client.about()  # Connection test
```

### Station Control (Master Toggle Panel)
**Menu path:** `Menu` → `Network` → `Station Control`
Master panel to toggle ALL protocol inputs/outputs in one place:
- OSC Input/Output, Art-Net Input/Output/Setup, sACN Input/Output/Setup, Send If IdleMaster for both.

### Network Interfaces
**Menu path:** `Menu` → `Network` → `My Interfaces`
- onPC: IPs set in OS (not editable in MA3)
- DHCP: Yes/No per interface. No = static IP, Mask, Gateway
- CIDR accepted: `192.168.101.11/24`
- **Blocked range:** `192.168.33.x` on Con1/Con2/Con3
- Auto interface selection priority: Class C (192.168.x.y) > Class B (172.16.x.y) > Class A (10.x.y.z) > Loopback (127.0.0.1)

---

## 10. Recording & Export

### Screen Capture (Record Visualizer to Video)
**GUI:**
1. Open the 3D visualizer (press `3D` button)
2. Menu → Recording → Screen Capture
3. Set output format (MP4 recommended)
4. Set resolution (1920×1080 for standard video)
5. Start recording
6. Play the sequence from beginning
7. Stop recording when done

**CLI:** Not directly available via command line
**OSC:** Not available (requires UI setup)
**Verify:** Video file saved to output destination.

### MVR Export (Visualizer Rig)
**GUI:** Menu → Export → MVR → select components → Export
**CLI:** `rayflow fixture export-mvr -d data/fixtures/samples -o rig.mvr`
**RayFlow:** `MvrExporter` in `src/rayflow/fixtures/mvr_export.py` — embeds GDTF files, scene hierarchy, fixture addressing, and 3D positions.

### Show File Backup
**GUI:** Menu → Save Show As → choose location
**CLI:** `SaveShow As "BackupPath"`
**Notes:** `.show` files are binary format. Do not attempt to generate them externally.

### DMX Output Recording (into Timecode)
(See Timecode Playback in §8 above)

---

## 11. Macros & Automation

### Create Macro
**GUI:**
1. Open Macro Pool: Add Window → Macro
2. Tap empty macro slot → Edit → Enter macro commands
3. Each line = one MA3 command line entry

**CLI:**
```
Store Macro 1                                — Store new macro
Edit Macro 1                                 — Edit macro 1
```

### Run Macro
**GUI:** Tap macro in Macro Pool → Play
**CLI:** `Macro 1`
**OSC:** `client.send("Macro 1")`
**Verify:** Macro commands execute sequentially.

### Delete / Rename Macro
**CLI:**
```
Delete Macro 1                               — Delete macro
Label Macro 1 "Fixture Setup"                — Name macro
```

### Lua Scripting
**CLI:** `Lua "[Lua code]"`
**Example:** `Lua "Printf(ObjectList('Master 1')[1]:Addr())"` — Get OSC address of Master 1

### Variables
**CLI:**
```
SetGlobalVariable "MyVar" "SomeValue"        — Set global variable
SetUserVariable "VarName" "Value"            — Set user variable
```

### Conditional Execution (Macros)
```
If [condition]
    ... commands ...
EndIf

IfActive Executor 201
IfOutput Attribute "Dimmer"
IfProgrammer
```

---

## 12. Multi-User & Sessions

### Create Session
**GUI:** Menu → Network → Create Session → set Session ID → OK
**CLI:** `Session 1` — Create session with ID 1
**Verify:** Other stations can see session in session list.

### Join Session
**GUI:** Menu → Network → Join Session → select session from list → OK
**CLI:** `JoinSession [IP] [SessionID]`
**Verify:** Station connects to session.

### Leave Session
**GUI:** Menu → Network → Leave Session
**CLI:** `LeaveSession`
**Verify:** Station disconnects from session.

### Login / Logout
**CLI:**
```
Login "UserName" "Password"                  — Login to console
Logout                                       — Logout
User [n]                                     — Select user profile
```

### Station Management
**CLI:**
```
Station "Name"                               — Select station
Invite [station]                             — Invite station to session
Disconnect [station]                         — Disconnect station
Reconnect [station]                          — Reconnect station
```

### Session Limits
- 1 fully-loaded session per network domain (262,144 parameters)
- Maximum 32 sessions per network domain
- Art-Net + sACN combined input: 128 universes max
- sACN multicast input: 20 universes max

### World Server
Required for GDTF Share access. Provides fixture library via network. Managed in Network menu.

### FastSync / Reboot / Shutdown
**CLI:**
```
FastSync                                     — Force session sync
Reboot                                       — Reboot console/onPC
Shutdown                                     — Shutdown console/onPC
```

---

## Common Operation Cheat Sheet

| Task | Shortest Path |
|------|--------------|
| Create show | `Menu → New Show` |
| Add 4 PARs at address 1 | `Fixture 4 "LED PAR" At Address 1` |
| Set intensity | `Fixture 1 At 50` or `Full` |
| Store cue on empty executor | `Store` + press executor key |
| Store cue 5 with fade | `Store Cue 5 Time 3 Please` |
| Update active cue | `Update` → tap cue in list |
| Go to next cue | `Go+` |
| Jump to cue 10 | `Goto Cue 10 Fade 2` |
| Preload cue | `Load Cue 3` then `Go+` |
| Create group | Select fixtures → `Store Group 1` |
| Select group | `Group 1` |
| Create color preset | Set color → `Store Preset 4.1` |
| Apply preset | `Fixture 1 At Preset 4.1` |
| Set 5s fade on cue 3 | `Cue 3 CueFade 5` |
| Create phaser (sinus) | `MA`+`Next` → `Full` → `MA`+`Set` → set Accel/Decel to -100 → set Phase `0 Thru 360` → `Store` |
| Pause everything | `Pause` |
| Clear programmer | `Clear` × 3 or hold `Clear` ≥1s |
| Save show | `SaveShow` |
| Enable Art-Net input | `Menu → DMX Protocols → Art-Net → Enable Input` |
| Enable OSC | `Menu → In & Out → OSC → Enable Input → Receive Command: Yes → Port: 8000` |
| DMX test output | `DMXUniverse 1.3 At 50` |
| Delete cue | `Delete Cue 5` |
| Copy cue | `Copy Cue 2 At Cue 6` |
| Assign sequence to executor | `Assign Sequ 3 At Executor 201` |
| Record visualizer | `Menu → Recording → Screen Capture` |
