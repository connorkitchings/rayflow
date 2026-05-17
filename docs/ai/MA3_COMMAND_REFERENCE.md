# grandMA3 2.3 — Complete Command Reference

> **FOR AI AGENTS.** This is the exhaustive MA3 command-line syntax reference. Sourced from the grandMA3 2.3 online manual and verified against 2.3.2.0.
>
> **Conventions:**
> - `[brackets]` = optional argument
> - `(parens)` = additional optional arguments
> - Multiple forms separated by `/` = alternative keywords
> - Quotes needed for names with spaces or special characters
> - All keywords are case-insensitive
> - `Please` key executes the command (implied, may be shown)
> - Short form shown in parentheses after full keyword where applicable

---

## Fixture Commands

### Fixture / FixtureType / Channel

```
Fixture [number]                          — Select fixture by FID
Fixture [FID].[SubIndex]                  — Select sub-fixture (e.g., Fixture 301.2)
Fixture [FID].                            — Select fixture + all sub-fixtures
Fixture Thru                              — Select all fixtures
Fixture Thru .                            — Select all fixtures + all sub-fixtures
Fixture [n] Thru [m]                      — Select range
Fixture [n] Thru [m] - [x] Thru [y]      — Select range minus excluded range
Fixture [n] + [m] + [p]                   — Add fixtures to selection
Fixture [n] Thru [m] + [q] Thru [r]       — Add ranges
Channel [number]                          — Select fixture by Channel ID
Channel [n] Thru [m] At Full              — Set channel range to full
SelectFixtures FixtureType [num]           — Select all fixtures of a fixture type
SelectFixtures DMXAddress [absolute]       — Select by absolute DMX address
SelectFixtures DMXUniverse [u].[addr]      — Select by universe.address
```

### Select / SelFix

```
Select Fixture [n]                        — Select fixture
Select Sequence [n]                       — Select sequence (opens Seq Sheet)
Select Executor [n]                       — Select executor
Select DMXUniverse [n]                    — Select universe
Select Group [n]                          — Select fixtures in group
SelFix FixtureType [num]                  — Select all fixtures of type (alternate syntax)
```

### Highlight / Flip / Align

```
Highlight                                 — Toggle highlight mode
Flip [fixture]                            — Flip pan/tilt to alternate solution
Align Group [n]                           — Align fixtures to group's reference
```

---

## Value Commands

### At / Full / Zero / Percent

```
At [value]                                — Set intensity/value for selected fixtures
At [n] [m] Please                         — Two-digit value: 3 0 = 30
At 0                                       — Set to 0%
At At                                     — Set to "Normal Value" from user settings
At Preset [pool].[index]                  — Apply preset value
At Speed Hz [n]                           — Set phaser speed in Hz
At Speed BPM [n]                          — Set phaser speed in BPM
At Speed Sec [n]                          — Set phaser speed in seconds
At Phase 0 Thru 360                       — Spread fixtures across phase
Full                                      — Set to 100%
Zero                                      — Set to 0%
[n] Percent                               — Set to n% (alternate syntax)
```

### Delay / Fade / Speed / Phase / Width

```
At Delay [n]                              — Set delay time
At Fade [n]                               — Set fade time
At Speed [n]                              — Set speed
At Phase [n]                              — Set phase offset
At Width [n]                              — Set width (for phaser steps)
```

### Off / On / Park / Unpark

```
Off Fixture [n]                           — Turn off fixture (knock out programmer values)
Off Sequence [n]                          — Turn off sequence (release output)
Off Executor [n]                          — Turn off executor
Off DMXUniverse Thru                      — Disable DMX tester on all universes
On Fixture [n]                            — Turn on fixture
Park Fixture [n]                          — Park fixture (hold current value)
Unpark Fixture [n]                        — Unpark fixture
```

### Black

```
Black                                     — Blackout (override all output to 0)
Black Executor [n]                        — Black specific executor
```

---

## Store Commands

### Store

```
Store                                     — Store current programmer (auto-numbers on selected sequence)
Store Cue [n]                             — Store as cue n
Store Sequence [n] Cue [m]                — Store as cue m in sequence n
Store Cue [n] Time [fade] Time [delay]    — Store with CueFade fade, CueDelay delay
Store Cue [n] /Merge                      — Merge into existing cue
Store Cue [n] /Overwrite /O               — Overwrite existing cue
Store Cue [n] /CueOnly /CO                — Store as Cue Only
Store Cue [n] /Remove                     — Remove stored values from cue
Store Cue [n] /Release                    — Store release value in cue
Store Cue Next                            — Store to next existing cue
Store Cue Next [n]                        — Store to nth next existing cue
Store Cue Previous                        — Store to previous existing cue
Store Cue +                               — Create new cue after active (integer)
Store Cue + [n]                           — Create cue at active + n
Store Cue + 0.5                           — Create cue at active + 0.5
Store Cue - [n]                           — Create cue at active - n
Store Cue [n] Part [p]                    — Store in cue n, cue part p
Store Cue "Name"                          — Store named cue
Store Cue [n] Thru [m]                    — Store range of empty cues
Store MAtricks "Name"                     — Store MAtricks settings
Store Group [n]                           — Store current selection as group
Store Preset [pool].[index]               — Store values as preset
Store Preset [pool].[index] /Merge        — Merge into existing preset
```

### Store Option Keywords (used after `/`)

```
/Active, /ActiveForSelected, /All, /AllForSelected, /Ask, /Auto, /AutoFit
/CreateSecondCue, /CueOnly, /Embed, /ForceGlobal, /Global, /InputFilter
/KeepActivation, /Look, /MAtricks, /Merge, /NoConfirmation, /OddEven
/Overwrite, /PhaserData, /Remove, /Screen, /ScreenOnly, /Selective
/Universal, /Wait
```

### Update

```
Update                                    — Opens Update Menu
Update Cue [n]                            — Update specific cue
Update Cue [n] /Merge                     — Update with merge
Update /NoConfirmation                    — Update without pop-up
```

### Autostore / GridStore

```
Autostore                                 — Toggle Autostore mode
GridStore                                 — Store grid values
GridPosition                              — Store grid position
```

---

## Cue Commands

### Cue / CueFade / CueDelay / CueInFade / CueOutFade

```
Cue [n] CueFade [time]                    — Set cue n fade time (both in and out)
Cue [n] CueFade [in]/[out]                — Set in-fade and out-fade separately
Cue [n] CueDelay [time]                   — Set cue delay
Cue [n] CueInFade [time]                  — Set in-fade only
Cue [n] CueOutFade [time]                 — Set out-fade only
Cue [n] CueInDelay [time]                 — Set in-delay only
Cue [n] CueOutDelay [time]                — Set out-delay only
CueFade [in]/[out]                        — Set fade for active cue
CueDelay [time]                           — Set delay for active cue
Cue [n] Time [t1] / [t2] Please           — Using Time key (cycles keywords)
Cue [n] Time [t1] Time [t2] Please        — Store with CueFade t1, CueDelay t2
```

### Cue Timing Shorthand

```
Cue [n] Time [fade] Please                — Set CueFade (in and out)
Cue [n] Time [fade] Time [delay]          — Set CueFade + CueDelay
Cue [n] Time / [out]                      — Set CueOutFade only
```

### SnapDelay / Load / Loaded / Goto

```
Cue [n] SnapDelay [time]                  — Set snap delay for cue
Load Cue [n]                              — Preload cue n (execute with Go+)
Load Executor [n] Cue [m]                 — Load cue m on executor n
Load /Loaded /NoConfirmation              — Clear all loaded cues
Loaded                                    — List loaded cues
Goto Cue [n]                              — Jump to cue n (asserts tracked values)
Goto Cue [n] Sequence [m]                 — Jump to cue n in sequence m
Goto Cue [n] Executor [e] Fade [t]        — Goto with explicit fade time
Goto Cue Next                             — Goto next cue
Goto Cue Previous                         — Goto previous cue
Goto Sequence [m] Cue Previous            — Goto previous cue in sequence m
Goto Loaded                               — Execute all loaded cues
```

### Block / Unblock

```
Block Cue [n]                             — Block tracked values in cue n
Block Sequence [n]                        — Block entire sequence
Unblock Sequence [n]                      — Unblock (remove redundant blocks)
Unblock Cue [n]                           — Unblock specific cue
```

### KnockIn / KnockOut / CleanUp

```
KnockIn Cue [n]                           — Knock in values to cue
KnockOut Cue [n]                          — Knock out values from cue
CleanUp Sequence [n]                      — Remove empty cues and parts
```

### Copy / Move Cues

```
Copy Cue [n] At Cue [m]                   — Copy cue n to cue m
Copy Cue [n] Thru [m] At Cue [p]          — Copy range (preserves gaps)
Copy Cue [n] + [m] At Cue [p]             — Copy discrete cues
Move Cue [n] At Cue [m]                   — Move cue n to cue m
```

### Delete / Renumber

```
Delete Cue [n]                            — Delete cue n
Delete Cue [n] Thru [m]                   — Delete range
Delete Sequence [n]                       — Delete entire sequence
Delete /NoConfirmation Cue [n]            — Delete without confirmation
```

### Part

```
Cue [n] Part [p]                          — Reference cue part
Store Cue [n] Part [p]                    — Store to specific part (up to 256 parts)
```

---

## Sequence Commands

### Sequence / Executor / Page

```
Sequence [n]                              — Reference sequence
Select Sequence [n]                       — Select sequence (opens Sequence Sheet)
Assign Sequence [n] At Executor [e]        — Assign sequence to executor
Assign Sequ [n] At Executor [e]            — Short form
Assign Sequence [n] At Page [p].[exec]     — Assign to specific page/executor
```

### Assign Object to Executor

```
Assign Sequence [n] At Executor [201]      — Assign sequence to fader row executor
Assign Sequence [n] At Page [2].[301]      — Assign to page 2, encoder row executor
Assign Master "Speed"."Speed1" At Page [1].[201]
Assign Group [n] At Executor [101]        — Assign group to button executor
```

### Executor Number Ranges

```
Executors 101-190  → Bottom button row
Executors 201-290  → Fader + button row
Executors 301-390  → Encoder + button row
Executors 401-490  → Top encoder + button row
Xkeys 191-198, 291-298
```

---

## Playback Commands

### Go / Pause / Top

```
Go+                                      — Trigger next cue on active executor
Go+ Executor [n]                         — Trigger next cue on executor n
Go+ Cue [n] Executor [e]                 — Trigger specific cue (and timed/follow ones)
Go-                                      — Go to previous cue (no subsequent triggers)
Go- Executor [n]                         — Go to previous on executor n
Go- Cue [n] Executor [e]                 — Go to specific cue (no subsequent triggers)
GoFastForward                            — Skip to next cue with 0s timing (>>>)
GoFastForward Cue [n]                    — Skip to specific cue (>>>)
GoFastBackward                           — Skip back with 0s timing (<<<)
GoFastBackward Cue [n]                   — Skip back to specific cue (<<<)
Pause                                    — Pause/resume fades, delays, phasers
Pause Executor [n]                      — Pause specific executor
Top                                      — Trigger first cue on active executor
Top Executor [n]                        — Trigger first cue on executor n
```

### Flash / Temp / Toggle / Solo / Kill

```
Flash Executor [n]                      — Flash executor n
Temp Executor [n]                       — Temporarily enable executor
Toggle Executor [n]                     — Toggle executor on/off
Solo Executor [n]                       — Solo executor (mute others)
Kill Executor [n]                       — Kill executor
```

### Speed / Rate

```
DoubleSpeed                             — Double speed on active executor
HalfSpeed                               — Half speed on active executor
LearnSpeed                              — Learn speed from tapping
Rate [n]                                — Set rate (1 = normal, 0.5 = half, 2 = double)
Rate 1                                  — Reset rate to normal
```

### Eject

```
Eject Executor [n]                      — Eject (remove assignment) from executor
```

---

## Effect (Phaser) Commands

### Step Commands

```
Next Step                               — Go to next step in phaser editor
Previous Step                           — Go to previous step
Delete Step [n]                         — Delete step n from phaser
Set                                     — Select all steps / deactivate MAtricks
```

### Generator / Bitmap / XYZ / Grid

```
Generator [n]                           — Apply generator effect
Bitmap "Name"                           — Apply bitmap effect
XYZ                                     — XYZ position effect
Grid                                    — Grid-based effect
```

### AlignTransition / Transition / Measure

```
AlignTransition                         — Align transitions across steps
Transition [value]                      — Set transition type
Measure [n]                             — Set measure length (beats per loop)
```

---

## Group & Preset Commands

### Group

```
Group [n]                               — Select fixtures in group n
Store Group [n]                         — Store current selection as group n
Delete Group [n]                        — Delete group n
Copy Group [n] At Group [m]             — Copy group n to group m
Move Group [n] At Group [m]             — Move group n to group m
Label Group [n] "Name"                  — Name group n
```

### Preset

```
Preset [pool].[index]                   — Reference preset (e.g., Preset 4.1 = color pool, index 1)
At Preset [pool].[index]                — Apply preset to selected fixtures
Store Preset [pool].[index]             — Store current values as preset
Store Preset [pool].[index] /Merge      — Merge into existing preset
Delete Preset [pool].[index]            — Delete preset
Label Preset [pool].[index] "Name"      — Name preset
PresetUpdate                            — Update preset from current values
```

### Preset Pools

| Pool | Number | Feature Group |
|------|--------|---------------|
| Dimmer | 1 | Dimmer |
| Position | 2 | Position (Pan/Tilt) |
| Gobo | 3 | Gobo |
| Color | 4 | Color |
| Beam | 5 | Beam |
| Focus | 6 | Focus |
| Control | 7 | Control |
| Shaper | 8 | Shaper |
| Video | 9 | Video |
| All 1-5 | 11-15 | Any feature group |
| Dynamic | 16 | Auto-switches to selected feature group |

### Preset Update

```
PresetUpdate [pool].[index]             — Update preset from current values
```

### Attribute / FeatureGroup

```
Attribute "Dimmer"                      — Select attribute for editing
FeatureGroup "Color"                    — Select feature group (for encoder bar)
```

### World / Filter / Collection

```
World [n]                               — Apply world n (limits selection/control scope)
Filter [n]                              — Apply filter n (limits what is stored/played)
Store World [n]                         — Store world settings
Collection [n]                          — Select collection n
```

---

## Network Commands

### Session / JoinSession / LeaveSession

```
Session [n]                             — Create session with ID n
JoinSession [IP]                        — Join session at IP
JoinSession [IP] [session_ID]           — Join specific session
LeaveSession                            — Leave current session
```

### Login / Logout / User

```
Login "UserName" "Password"             — Login to console
Logout                                  — Logout
User [n]                                — Select user profile
```

### Station / NetworkNode

```
Station [name]                          — Select station (in multi-user session)
NetworkNode [n]                         — Select network node
```

### Invite / Disconnect / Reconnect

```
Invite [station]                        — Invite station to session
Disconnect [station]                    — Disconnect station
Reconnect [station]                     — Reconnect station
```

### DMX Commands

```
DMXUniverse [n].[addr] At [value]        — DMX test: send value to universe/address
DMXUniverse [n] At [value]              — DMX test on universe n (all addresses)
Select DMXUniverse [n]                  — Select universe n
Move DMXUniverse [n] At DMXUniverse [m]  — Move universe n to universe m
Off DMXUniverse Thru                    — Disable DMX tester on all universes
```

### FastSync / Reboot / Shutdown

```
FastSync                                — Force session sync
Reboot                                  — Reboot console/onPC
Shutdown                                — Shutdown console/onPC
```

---

## Macro Commands

### Macro

```
Macro [n]                               — Run macro n
Macro [n] /NoConfirmation               — Run without confirmation
Delete Macro [n]                        — Delete macro n
Store Macro [n]                         — Store new macro
Edit Macro [n]                          — Edit macro n
Label Macro [n] "Name"                  — Name macro n
```

### Running / MyRunning

```
RunningMacro [n]                        — Reference running macro
MyRunningMacro [n]                      — Reference own running macro
```

### SetGlobalVariable / SetUserVariable

```
SetGlobalVariable "Name" "Value"        — Set global variable
SetUserVariable "Name" "Value"          — Set user variable
```

---

## Utility Commands

### Delete / Copy / Move / Clone / Insert / Exchange / Swap

```
Delete [object] [number]                — Delete any object
Copy [object] [n] At [object] [m]       — Copy any object
Move [object] [n] At [object] [m]       — Move any object
Clone [object] [n]                      — Clone (copy with auto-number)
Insert [object] [n]                     — Insert new object
Exchange [obj1] [n] At [obj2] [m]       — Exchange two objects
Swap                                     — Swap active with selected
```

### Edit / Assign / Set / Label / List

```
Edit [object] [n]                       — Open editor for object
Assign [object] [n] At [destination]    — Assign object to destination
Set Selection [property] [value]        — Set selection property
Label [object] [n] "Name"              — Name an object
List [object]                           — List objects of type
```

### Clear / Oops

```
Clear                                   — Clear programmer (1st press = deselect, 2nd = deactivate, 3rd = full clear)
Hold Clear                              — Full clear immediately (>1 sec hold)
Oops                                     — Undo last action
```

### Call / Select

```
Call [object] [n]                       — Call object into programmer
Select [object] [n]                     — Select object
```

### Lock / Unlock

```
Lock [object] [n]                       — Lock object (prevent editing)
Unlock [object] [n]                     — Unlock object
```

### Cut / Paste

```
Cut [object] [n]                        — Cut object to clipboard
Paste [object] [n]                      — Paste clipboard at object n
```

### Blind / Freeze

```
Blind                                   — Toggle blind mode (values hidden from output)
Freeze                                  — Toggle freeze (programmer values override executors)
```

### If / EndIf / Thru / + / -

```
If [condition]                          — Conditional execution (macro)
EndIf                                   — End conditional block
Thru                                    — Range operator (1 Thru 5 = 1,2,3,4,5)
+                                       — Add to selection/list
-                                       — Remove from selection/list
```

### IfActive / IfOutput / IfProgrammer

```
IfActive [executor]                     — Check if executor is active
IfOutput [attribute]                    — Check if attribute has output
IfProgrammer                            — Check if programmer has values
```

---

## Patch / Show Commands

### Patch / Multipatch

```
Patch Fixture [FID] [Universe].[Address]       — Patch fixture to DMX address
Patch Fixture [n] Thru [m]                      — Open Edit Patch for range
Patch Fixture [n] Multipatch [idx] [u].[addr]   — Patch multipatch fixture
```

### FixtureType

```
Import Library "FixtureName"                    — Import fixture type from library
Assign FixtureType [num] At [FID] Thru [FID]    — Assign fixture type in patch context
```

### AutoCreate

```
AutoCreate                                 — Auto-create objects
```

### Import / Export

```
Import [object] Library "filename" (If Drive [n]) (At [dest])
Export [object] "filename"                 — Export object to file
```

### Show Commands

```
NewShow                                     — Create new show
LoadShow "Path"                             — Load show file
SaveShow                                    — Save current show
SaveShow As "Path"                          — Save show to path
```

---

## Screen / View Commands

### View / ViewButton / Screen

```
View "Name"                                 — Open view/window
ViewButton [n]                              — Press view button
Screen [n]                                  — Select screen (1-N)
Screen "Name"                               — Select screen by name
ScreenContent [n]                           — Screen content
ScreenConfiguration [n]                     — Screen configuration
Layout [n] "Name"                           — Apply layout
```

### Appearance / Image / Camera

```
Appearance [n]                              — Assign appearance
Image "Name"                                — Load image
Camera [n]                                  — Select camera view
Camera [n] Fly                              — Fly camera to position
```

### Stage / Environment

```
Stage                                       — Stage settings
Environment                                 — Environment settings
```

---

## Masters / Lua / Plugin Commands

### Master / SpeedMaster

```
Master [n]                                  — Reference master
SpeedMaster [n]                             — Reference speed master (1-15)
Assign Master "Speed"."Speed1" At Exec [n]   — Assign speed master to executor
```

### Lua

```
Lua "code"                                  — Execute Lua code
Lua "Printf(ObjectList('Master 1')[1]:Addr())"  — Get object OSC address
```

### Plugin

```
Plugin [n]                                  — Run plugin n
Store Plugin [n]                            — Store plugin
Edit Plugin [n]                             — Edit plugin
```

---

## Keyboard / Menu / Help

### Key

```
Key "KeyName"                               — Simulate key press (e.g., Key "Please")
Key "PageUp"                                — Page up
Key "PageDown"                              — Page down
```

### Menu

```
Menu "MenuName"                             — Open menu (e.g., Menu "Patch", Menu "ArtNet")
Menu 'Patch'.'Edit'                          — Open submenu
```

### Help

```
Help                                        — Open help
Help "Topic"                                — Search help topic
```

---

## Option Keywords Reference (after `/`)

Complete list of option keywords that can be appended to commands:

| Option | Description |
|--------|-------------|
| `/Active` | Use active values |
| `/ActiveForSelected` | Active only for selected fixtures |
| `/All` | Use all values |
| `/AllForSelected` | All values for selected |
| `/Ask` | Ask behavior |
| `/Auto` | Auto mode |
| `/AutoFit` | Auto-fit |
| `/CreateSecondCue` | Create second cue on existing executor |
| `/CueOnly` `/CO` | Store as Cue Only |
| `/Embed` | Embed into parent |
| `/ForceGlobal` | Force global preset mode |
| `/Global` | Global preset mode |
| `/InputFilter` | Apply input filter |
| `/KeepActivation` | Keep activation state |
| `/Look` | Store attributes for fixtures with dimmer > 0 |
| `/MAtricks` | Apply MAtricks |
| `/Merge` | Merge values |
| `/NoConfirmation` | Skip confirmation pop-up |
| `/OddEven` | Odd/even selection pattern |
| `/Overwrite` `/O` | Overwrite existing |
| `/PhaserData` | Store phaser data |
| `/Remove` | Remove values |
| `/Screen` | Screen-relative |
| `/ScreenOnly` | Screen only |
| `/Selective` | Selective preset mode |
| `/Universal` | Universal preset mode |
| `/Wait` | Wait for completion |

---

## Priority Keywords (for DMX Merging)

| Priority | Behavior |
|----------|----------|
| `Super` | Above all playbacks AND programmer |
| `Swap` | Intensity = LTP above HTP |
| `HTP` | Highest intensity wins; other attributes LTP |
| `Highest` | Highest possible LTP priority |
| `High` | Higher than normal LTP |
| `LTP` | Normal: latest value takes precedence |
| `Low` | Lower LTP |
| `Lowest` | Lowest possible LTP |

---

## Transition Types (for Cue Transitions)

```
Cue [n] Transition [type]                — Set transition type for cue

Types: Linear, Slow, Slow+, Fast, Fast+, SCurve, Swing-, Swing, Swing+
```

---

## Trigger Types (for Cue Triggers)

Set in Sequence Sheet `Trig Type` column:

| Type | Description |
|------|-------------|
| `Go` | Manual trigger (Go+, Goto, etc.) |
| `Time` | Auto-trigger after Trig Time seconds from previous trigger |
| `Follow` | Auto-trigger when previous cue transition completes |
| `Sound` | Trigger on sound input |
| `BPM` | Trigger on beat detection |
