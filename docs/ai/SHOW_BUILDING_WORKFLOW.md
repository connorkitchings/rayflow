# Show Building Workflow — Song to Finished Show

> **FOR AI AGENTS.** Complete end-to-end process for building a lighting show. Each phase includes exact MA3 operations and RayFlow commands. Use this alongside [MA3_OPERATIONS.md](./MA3_OPERATIONS.md).

---

## Workflow Overview

```
PHASE 1     PHASE 2       PHASE 3        PHASE 4          PHASE 5      PHASE 6
ANALYZE →  DESIGN RIG →  SETUP MA3 →   PROGRAM CUES →   ADD EFFECTS → REHEARSE & EXPORT
Song      Choose         Patch         Store looks       Chases,      Playback sync,
structure fixtures       fixtures      per section       phasers,     timing adjust,
                          Groups                         movements     record video
                          Presets
```

---

## Phase 1: Song Analysis

### Goal
Map the song's structure, identify lighting moments, and plan cue count.

### Steps

1. **Load the song.** Obtain the audio file.

2. **Listen and note the structure.** Identify sections:
   - Intro (bars)
   - Verse 1, 2, 3 (bars)
   - Pre-Chorus (if any)
   - Chorus 1, 2, 3 (bars)
   - Bridge / Middle 8
   - Instrumental / Solo
   - Outro

3. **Mark the time signatures.** That way:
   - 4/4 = 1 bar = ~2 seconds (at 120 BPM)
   - Cues often happen on bar boundaries or half-bar

4. **Assign lighting mood per section:**

| Section | Typical Mood | Lighting Approach |
|---------|-------------|-------------------|
| Intro | Ambient, mysterious | Cool colors, haze, slow fade in |
| Verse | Intimate, controlled | Warm wash, moderate intensity |
| Pre-Chorus | Building anticipation | Add movement, increase intensity |
| Chorus | High energy, full | All fixtures, bright colors, movement |
| Bridge | Atmospheric, breakdown | Hazer, slow color transitions |
| Solo | Spotlight, focused | Single fixture highlight, others dim |
| Outro | Resolution, fade out | Slow dim, single color, haze increase |

5. **Determine cue count.** Minimum 1 cue per song section. Typical: 6-12 cues for a 3-minute song.

### Template: Song Analysis Sheet

```
Song: [Title]                    BPM: [___]    Length: [___]

| # | Section | Time  | Mood        | Lighting Idea            |
|---|---------|-------|-------------|--------------------------|
| 1 | Intro   | 0:00  | Ambient     | Cool blue wash, 20%, 5s fade |
| 2 | Verse 1 | 0:20  | Intimate    | Warm amber, 50%, 3s fade |
| 3 | Chorus  | 0:50  | Energy      | Full stage, bright, 0.5s snap |
| 4 | Verse 2 | 1:20  | Building    | Add moving head positions |
| 5 | Chorus 2| 1:50  | Peak        | All + strobe effect |
| 6 | Bridge  | 2:20  | Atmospheric | Haze, slow color shift, 8s fade |
| 7 | Chorus 3| 2:50  | Climax      | Everything, fast movement |
| 8 | Outro   | 3:10  | Fade out    | Single blue, slow dim, 10s fade |
```

---

## Phase 2: Design the Rig

### Goal
Choose fixtures, plan DMX addressing, define stage positions.

### Steps

### 1. Choose Fixtures

Based on the song's needs. Start simple.

**Beginner Rig (4 PARs, 2 Moving Heads, 1 Hazer):**

| # | Fixture | Type | Channels | DMX Range |
|---|---------|------|----------|-----------|
| 1 | LED PAR 1 | Chauvet SlimPAR Pro H USB | 7 | 1-7 |
| 2 | LED PAR 2 | Chauvet SlimPAR Pro H USB | 7 | 8-14 |
| 3 | LED PAR 3 | Chauvet SlimPAR Pro H USB | 7 | 15-21 |
| 4 | LED PAR 4 | Chauvet SlimPAR Pro H USB | 7 | 22-28 |
| 5 | Moving Head 1 | MAC Aura XB | 19 | 29-47 |
| 6 | Moving Head 2 | MAC Aura XB | 19 | 48-66 |
| 7 | Hazer | Generic Hazer | 1 | 67 |

**Total: 67 channels in Universe 1.** Well within 512-channel limit.

**Channel guide by fixture type:**
- LED PAR (7 ch): Dimmer, R, G, B, strobe, color macro, auto program
- Moving Head (19 ch): Pan, Pan Fine, Tilt, Tilt Fine, Dimmer, R, G, B, A, strobe, color temp, color wheel, gobo, gobo rotate, prism, focus, zoom, control, reset

### 2. Source Fixture Files (GDTF)

**From RayFlow:**
```bash
# List fixtures if already downloaded to data/fixtures/
uv run rayflow fixture list

# Inspect a specific fixture
uv run rayflow fixture info "LED PAR"

# OR from Python:
from rayflow.fixtures.parser import GdtfParser
parser = GdtfParser("data/fixtures/fixture.gdtf.zip")
fixture = parser.parse()
print(f"{fixture.name}: {fixture.channel_count} channels in {len(fixture.modes)} modes")
```

**From gdtf-share.com:**
1. Search for fixture at https://gdtf-share.com/
2. Download `.gdtf` file
3. Place in `data/fixtures/`
4. OR import directly to MA3 via World Server

### 3. Design Stage Layout

**Coordinates (meters):**
- X: Left (-) to Right (+), center = 0
- Y: Height from floor (0 at stage floor)
- Z: Front (+) to Back (-)

**Beginner Stage Layout:**
```
                    BACK
                 Z = -4m
    PAR1 (X:-3,Z:-4,Y:3)      PAR4 (X:3,Z:-4,Y:3)
                   
    PAR2 (X:-1,Z:-4,Y:3)      PAR3 (X:1,Z:-4,Y:3)
                   
        MH1 (X:-2,Z:0,Y:2)   MH2 (X:2,Z:0,Y:2)
                   
    HAZER (X:0,Y:0,Z:4)
                    FRONT
```

**Setup in MA3:**
1. Patch fixtures (see Phase 3)
2. Position them in the 3D visualizer:
   - Select fixture → right-click in 3D → Position
   - Or: use Stage view → drag fixture to position
   - Or: encoder bar Position layer → adjust X/Y/Z

---

## Phase 3: Setup MA3 (Patching, Groups, Presets)

### Goal
Load the show, patch all fixtures, create groups and presets.

### 3a. Start and Configure

1. **Launch grandMA3 onPC.**
2. **Create new show:** `NewShow` or `Menu → New Show`
3. **Enable Art-Net input:** `Menu → DMX Protocols → Art-Net → Enable Input` → On → Add Input row for universe 1
4. **Enable OSC:** `Menu → In & Out → OSC → Enable Input` → On → Port 8000 → Receive Command: Yes
5. **Verify Art-Net:**
   ```bash
   sudo lsof -iUDP:6454 | grep app_gma3
   ```

### 3b. Patch Fixtures

**Method A: MA3 Command Line (fastest)**
```
Fixture 4 "LED PAR" At Address 1       ← Patches 4 LED PARs starting at addr 1
Fixture 2 "Moving Head" At Address 29   ← Patches 2 Moving Heads starting at addr 29
Fixture 1 "Hazer" At Address 67         ← Patches hazer at addr 67
```

**Method B: MA3 GUI (step-by-step)**
1. `Menu → Patch`
2. If empty: Wizard → select fixture type → set Quantity: 4 → Address: 1.1 → Create
3. If adding: Insert New Fixture → Library tab → browse → select mode → set quantity → address → Create

**Method C: OSC from RayFlow**
```python
from rayflow.console.osc import Ma3OscClient
client = Ma3OscClient("127.0.0.1", 8000)
client.send('Fixture 4 "LED PAR" At Address 1')
client.send('Fixture 2 "Moving Head" At Address 29')
client.send('Fixture 1 "Hazer" At Address 67')
```

**Verify:** Patch Menu shows all fixtures with expected addresses. 3D Visualizer shows fixtures at default positions.

### 3c. Position Fixtures in 3D

In 3D visualizer: Select fixture → drag to position, OR:
```
Select fixture → Position encoder layer → adjust X/Y/Z
```
Position according to your stage layout from Phase 2.

### 3d. Create Groups

```
# Select PARs
Fixture 1 Thru 4 Please
Store Group 1
Label Group 1 "Front PARs"

# Select Moving Heads
Fixture 5 + 6 Please
Store Group 2
Label Group 2 "Moving Heads"

# Select ALL
Fixture Thru Please
Store Group 3
Label Group 3 "All Fixtures"

# Select hazer
Fixture 7 Please
Store Group 4
Label Group 4 "Hazer"
```

### 3e. Create Color Presets

```
# Select PARs
Group 1 Please

# Red
At Preset 4.1    ← Apply color (or use encoder bar Color layer)
Store Preset 4.1
Label Preset 4.1 "Red"

# Blue
At Preset 4.2
Store Preset 4.2
Label Preset 4.2 "Blue"

# Warm Amber
At Preset 4.3
Store Preset 4.3
Label Preset 4.3 "Warm Amber"

# White
At Preset 4.4
Store Preset 4.4
Label Preset 4.4 "White"
```

### 3f. Create Position Presets

```
Group 2 Please   ← Select Moving Heads

# Center
At Preset 2.1    ← Set pan/tilt encoders to center
Store Preset 2.1
Label Preset 2.1 "Center"

# Wide
At Preset 2.2    ← Set wide pan positions
Store Preset 2.2
Label Preset 2.2 "Wide"

# Cross
At Preset 2.3    ← Set crossed positions (MH1 right, MH2 left)
Store Preset 2.3
Label Preset 2.3 "Cross"
```

### 3g. Create Intensity Presets

```
Group 1 Please
At 50
Store Preset 1.1
Label Preset 1.1 "Half"

At Full
Store Preset 1.2
Label Preset 1.2 "Full"

At 20
Store Preset 1.3
Label Preset 1.3 "Low"

At 0
Store Preset 1.4
Label Preset 1.4 "Off"
```

---

## Phase 4: Program Cues

### Goal
Store a cue for each song section identified in Phase 1.

### Programming Approach

For each cue:
1. Clear programmer: `Clear` × 3
2. Select fixtures for this look
3. Set intensity, color, position using presets
4. Store cue with timing
5. Verify by loading and playing

### Cue-by-Cue Programming

#### Cue 1 — Intro (Cool Blue Wash, Slow Fade)
```
Clear Clear Clear
Group "Front PARs"
At Preset 4.2            ← Blue
At Preset 1.3            ← 20%
At Preset 2.1            ← (Moving Heads to center, 0%)
Store Cue 1 Time 5 Please
Label Cue 1 "Intro - Blue Wash"
```

#### Cue 2 — Verse 1 (Warm Amber, Moderate)
```
Clear Clear Clear
Group "Front PARs"
At Preset 4.3            ← Warm Amber
At Preset 1.1            ← 50%
Store Cue 2 Time 3 Please
Label Cue 2 "Verse 1 - Warm Amber"
```

#### Cue 3 — Chorus 1 (Full Energy, Quick Snap)
```
Clear Clear Clear
Group "All Fixtures"
At Preset 4.4            ← White
At Preset 1.2            ← Full
Group "Moving Heads"
At Preset 2.2            ← Wide positions
Store Cue 3 Time 0.5 Please
Label Cue 3 "Chorus 1 - Full White Wide"
```

#### Cue 4 — Verse 2 (Building)
```
Clear Clear Clear
Group "Front PARs"
At Preset 4.3            ← Warm Amber
At Preset 1.2            ← Full
Group "Moving Heads"
At Preset 2.1            ← Center
Group "Hazer"
At 50
Store Cue 4 Time 3 Please
Label Cue 4 "Verse 2 - Building"
```

#### Cue 5 — Chorus 2 (Peak)
```
Clear Clear Clear
Group "All Fixtures"
At Preset 4.4            ← White
At Preset 1.2            ← Full
Group "Moving Heads"
At Preset 2.2            ← Wide
Group "Hazer"
At Full
Store Cue 5 Time 0.5 Please
Label Cue 5 "Chorus 2 - Peak"
```

#### Cue 6 — Bridge (Atmospheric)
```
Clear Clear Clear
Group "Front PARs"
At Preset 4.2            ← Blue
At Preset 1.1            ← 50%
Group "Moving Heads"
At Preset 2.3            ← Cross positions (slow movement)
Group "Hazer"
At Full
Store Cue 6 Time 8 Please
Label Cue 6 "Bridge - Cool Cross"
```

#### Cue 7 — Chorus 3 (Climax)
```
Clear Clear Clear
Group "All Fixtures"
At Preset 4.4            ← White
At Preset 1.2            ← Full
Group "Moving Heads"
At Preset 2.2            ← Wide
Group "Hazer"
At Full
Store Cue 7 Time 0.3 Please
Label Cue 7 "Chorus 3 - Climax"
```

#### Cue 8 — Outro (Fade to Black)
```
Clear Clear Clear
Group "Front PARs"
At Preset 4.2            ← Blue
At Preset 1.3            ← 20%
Store Cue 8 Time 10 Please
Label Cue 8 "Outro - Fade to Blue"
```

### Assign Sequence to Executor

```
Assign Sequence 1 At Executor 201
```

If sequence was auto-created by `Store` + executor, it's already assigned.

### Verify Cues

```
Go+             ← Trigger cue 1 (should fade in)
Goto Cue 3 Fade 2   ← Jump to cue 3
Pause           ← Pause at any point
Go+             ← Resume
Top             ← Go to first cue
```

---

## Phase 5: Add Effects

### Goal
Add dynamic movement, chases, and phaser effects for energy sections.

### 5a. Create a Color Chase (Phaser with Width=0%)
For choruses — fixtures cycle through colors.

```
# Select PARs
Group "Front PARs" Please

# Create 4-step color chase:
# Step 1: Red
At Preset 4.1                ← Red

# Step 2: White (MA + Next)
MA + Next
At Preset 4.4                ← White

# Step 3: Blue (MA + Next)
MA + Next
At Preset 4.2                ← Blue

# Step 4: Green (MA + Next)
MA + Next
At Preset 4.5                ← Green (if defined)

# Set chase properties
MA + Set                      ← Select all steps
Set Width to 0%              ← Instant snap between steps (Phaser Editor)
Set Phase 0 Thru 360         ← Spread fixtures across the chase

# Set speed
At Speed BPM 120

# Store as a new cue for a chorus
Store Cue 5.5
```

Or store as a phaser preset for reuse:
```
Store Preset 4.10 "Color Chase"
```

### 5b. Create Movement Effect (Position Circle)

```
Group "Moving Heads"
At Preset 2.1                ← Start at center

# Create circular movement using Phaser Editor:
# Open: Add Window → Tools → Phaser Editor

# Select A+ (Add Absolute) tool
# Tap points in 2D grid to form rough circle
# Use Move Handles to curve into circle
# Use Edit Phase → 360 to spread fixtures

# Set speed
At Speed Hz 1

Store Cue 5.1 "Movement Circle"
```

### 5c. Create Dimmer Chase (Intensity Pulse)

```
Group "Front PARs"
At 0

MA + Next                    ← Step 2
At 100

MA + Next                    ← Step 3
At 50

MA + Set                     ← Select all steps
Set Phase 0 Thru 360
At Speed Hz 2

Store Preset 1.10 "Intensity Chase"
```

### 5d. Create a Strobe Effect

```
Group "All Fixtures"
At 100                       ← Full intensity

# Create 2-step phaser (on/off):
MA + Next                    ← Step 2
At 0

# Set snap transition
MA + Set                     ← Select all steps
Set Width to 50%             ← 50% on, 50% off

At Speed Hz 4               ← Fast strobe

Store Preset 1.11 "Strobe"
```

### 5e. Apply Effects in Cues

Effects can be stored directly in cues:
```
Group "Moving Heads"
At Preset 4.10               ← Apply color chase
At Preset 2.10               ← Apply position circle
Store Cue 3.5 /Merge          ← Merge into chorus cue 3
```

Or create dedicated effect cues:
```
Group "Front PARs"
At Preset 1.10               ← Intensity chase
Store Cue 5.6 "Chorus - Intensity Chase"
```

---

## Phase 6: Rehearse & Export

### Goal
Play back with audio, adjust timing, record final video.

### 6a. Audio Sync Setup (optional)

**Load audio to MA3:**
1. `Menu → Setup → Audio → Import Audio`
2. Select song file
3. Set to play from beginning

**OR sync manually:**
- Play song separately (iTunes/Spotify)
- Watch visualizer as you trigger cues
- Note timing mismatches

### 6b. Rehearsal Run

```
Top Executor 201            ← Start from cue 1

# Play through. For each cue, note:
# - Is the fade time right?
# - Does the look match the song section?
# - Are transitions smooth?
# - Do effects start/stop at right times?

# Common adjustments:
Cue 3 CueFade 1.5           ← Extend fade time
Cue 5 CueDelay 0.2          ← Add pre-delay for snap
Cue 6 CueFade 8/8           ← Set in/out fade to 8s
```

### 6c. Timing Adjustments

| Issue | Fix |
|-------|-----|
| Cue too early | Increase CueDelay, or move earlier in timeline |
| Cue too late | Decrease CueDelay or cue number order |
| Fade too slow | Reduce CueFade |
| Snap too harsh | Increase CueFade to 0.5-1.0s |
| Color change jerky | Add fade: `Cue [n] CueFade 2` |
| Effects out of sync | Use Speed Master to sync: `Assign Master "Speed"."Speed1" At Exec 202` |

### 6d. Record Visualizer to Video

1. Open 3D visualizer (`3D` button)
2. `Menu → Recording → Screen Capture`
3. Set format: MP4
4. Set resolution: 1920×1080
5. Start recording
6. `Top Executor 201` to start sequence
7. Trigger cues manually or let them auto-play:
   - Manual: Press Go+ for each cue at song moments
   - Auto: Set Trig = Time or Follow in Sequence Sheet
8. Stop recording when song ends

### 6e. Save and Export

```
SaveShow                       ← Save show file
SaveShow As "data/shows/my_first_show"  ← Save to RayFlow show directory
```

**Export the video file** from the recording destination.

---

## Quick Reference: Full Command Sequence

Copy and run these commands to set up a complete beginner show:

```python
# === MA3 Commands (run in MA3 command line or via OSC) ===

# 1. Patch fixtures
Fixture 4 "LED PAR" At Address 1
Fixture 2 "Moving Head" At Address 29
Fixture 1 "Hazer" At Address 67

# 2. Create groups
Fixture 1 Thru 4 Please
Store Group 1
Label Group 1 "Front PARs"
Fixture 5 + 6 Please
Store Group 2
Label Group 2 "Moving Heads"
Fixture 7 Please
Store Group 3
Label Group 3 "Hazer"

# 3. Position fixtures in 3D (set via visualizer drag or encoder)

# 4. Store cue 1 - Intro blue wash
Group "Front PARs" Please
At 20 Please
Store Cue 1 Time 5 Please

# 5. Store cue 2 - Verse warm amber
Group "Front PARs" Please
At 50 Please
Store Cue 2 Time 3 Please

# 6. Store cue 3 - Chorus full
Group "All Fixtures" Please
Full
Store Cue 3 Time 0.5 Please

# 7. Assign to executor
Assign Sequence 1 At Executor 201

# 8. Play
Go+ Executor 201
```

---

## Show Templates by Genre

### Template: Rock Song (4 PARs, 4 Moving Heads)

| Cue | Section | Look | Timing |
|-----|---------|------|--------|
| 1 | Intro | Cool blue wash, 20%, MH center dim | Fade 5s |
| 2 | Verse 1 | Warm amber, 50%, MH subtle positions | Fade 3s |
| 3 | Chorus 1 | Full white, MH wide, fast movements | Snap 0.5s |
| 4 | Verse 2 | Warm amber, 70%, MH building positions | Fade 2s |
| 5 | Chorus 2 | Full + strobe MH, color chase PARs | Snap 0.3s |
| 6 | Bridge | Deep blue, haze full, MH slow cross | Fade 8s |
| 7 | Solo | Single MH spotlight, others dim | Fade 1s |
| 8 | Chorus 3 | Everything full, all effects | Snap |
| 9 | Outro | Single blue, slow dim to black | Fade 12s |

### Template: Electronic Song (LED bars, 4 Moving Heads, Strobes)

| Cue | Section | Look | Timing |
|-----|---------|------|--------|
| 1 | Intro | Strobe build, increasing speed | Rate increases |
| 2 | Build | Color sweep across fixtures | Fade 2s |
| 3 | Verse | Minimal, single color wash, 30% | Fade 2s |
| 4 | Build 2 | Add movement, intensity climb | Fade 1s |
| 5 | Drop 1 | Full strobe, all fixtures, color chase | Snap |
| 6 | Breakdown | Minimal, haze, slow position circle | Fade 4s |
| 7 | Build 3 | Intensity chase, building speed | Fade 1s |
| 8 | Drop 2 | Everything, fast chase, full strobe | Snap |
| 9 | Outro | Filter sweep, dim to black | Fade 6s |

### Template: Acoustic Song (4 PARs, 1 Hazer)

| Cue | Section | Look | Timing |
|-----|---------|------|--------|
| 1 | Intro | Warm amber, 20%, haze 30% | Fade 5s |
| 2 | Verse 1 | Warm, 50% | Fade 3s |
| 3 | Verse 2 | Slightly brighter, 60% | Fade 3s |
| 4 | Chorus | Full intensity, warm white | Fade 2s |
| 5 | Verse 3 | Back to 50% | Fade 3s |
| 6 | Chorus 2 | Full + slightly cool color shift | Fade 2s |
| 7 | Outro | Slow fade to dim blue, haze increase | Fade 10s |
