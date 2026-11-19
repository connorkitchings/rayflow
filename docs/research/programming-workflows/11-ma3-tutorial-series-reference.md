# grandMA3 Tutorial Series — Extracted Reference

**Source:** YouTube playlist "GrandMA 3 Tutorials" — https://www.youtube.com/playlist?list=PLhh6ZoFPnUu1hMCDT2YhuYJxLgW_G0rTn
**Episodes:** 22 (E01–E22)
**Raw transcripts:** `docs/research/raw_sources/ma3-tutorial-series/`
**Parsed:** 2026-05-25

---

## Episode Index

| # | Title | Video ID | Key Topics |
|---|-------|----------|------------|
| E01 | OnPC Screens and System Views | z2LXO74Q9mA | Screen layout, system views, rear panel |
| E02 | Patching Fixtures | EjA2MX5v46c | Patch menu, fixture sources, DMX addressing |
| E03 | Setup Views | 8iZy1U9rWOk | View construction, groups pool, preset pools |
| E04 | Setup 3D View | psp-QbFTTzg | 3D fixture placement, X/Y/Z positioning |
| E05 | Swipeys and Presets | XC8q5cTWuuc | Preset workflow, color picker, gobo channel sets |
| E06 | Layout View | CLXiwL1B4Zs | Layout pool, assign, per-type filtered views |
| E07 | 3D Render Quality | P9uiTBWVe9Q | Beam/spot quality, rendering settings |
| E08 | Sequence and Cue | Ivcf1FRgvE4 | Sequences, cues, fade times, store modes |
| E09 | Executors Faders and Buttons | lsDUS4ez3Oc | Executor rows 101/201/301/401, button functions |
| E10 | Phaser Effects for Beginners | KMGH4YPruuc | Phaser engine, speed masters, phase spread |
| E11 | How To Create Flyout Effect | 5xy9hNsnkmc | Phaser editor, step-based effects, MAtricks shuffle |
| E12 | Predefined Macros | nRHw4Y3x06U | Macro pool, importing predefined macros |
| E13 | How To Write Macros Part 2 | Z0P4NZaOPcI | Custom macro writing, CLI command syntax |
| E14 | Selection Grid and MAtricks | tzU9Ad1T-UM | Selection grid, block/group/wings/width/shuffle |
| E15 | GrandMA3 RECAST | rRAohf4vbJI | Recast preset, All Preset pool 21 |
| E16 | Fade and Delay Effects | ZmjoNG3F0PM | Split fades, per-fixture delay, follow cues |
| E17 | Export MVR from WYSIWYG | btk-vMUnuI8 | MVR import/export, fixture replacement |
| E18 | Setup Large Layout View Fast | WAHgwghd4o8 | Camera-based arrangement, auto-layout |
| E19 | 3 Different Patch Techniques | BT5a9T2Ii_4 | Command-line patch, Plus/Thru syntax |
| E20 | Merge Overwrite and Remove | TV0NI1D9qqw | Store modes: Merge/Override/Remove |
| E21 | Why Tracking Is So Important | q49H5Bmz5Uw | Tracking, cue only, block/unblock cues |
| E22 | Customize Appearances | GOHDlkNHP0w | Appearance pool, color-coding objects |

---

## MA3 Command Syntax Reference (extracted from series)

### Fixture Selection
```
701 Thru 712 Please          Select fixtures by ID range
1 Thru 10000 Please          Select all fixtures (use high max ID)
```

### Patching
```
Patch Fixture 701 Thru 706 Plus 601 Thru 610 Plus 301 Thru 304 Please
Patch To 1.1 Please           Patch selected fixtures starting at universe.address
```

### Preset & Cue Storage
```
Store                          Store programmer to target (pool slot / cue)
Store Cue 2 /o                 Store with Override flag (no prompt)
Store Cue 2 /m                 Store with Merge flag
Store Cue 2 Thru 10            Create empty cues 2–10
```

### Preset Referencing
```
At Preset 21.1                 Apply preset 1 from All Preset pool (21)
At Preset 3.5                  Apply preset 5 from Gobo pool (3)
```

### Preset Pool Numbers
| Pool | Number |
|------|--------|
| Position | 1 |
| Gobo | 3 |
| Focus (Zoom) | 6 |
| All Preset | 21 |

### Cue Operations
```
Block Cue 7                    Record hard values for all active params
Unblock Cue 1 Thru 50          Remove redundant hard values
Recast Preset 21.37            Push preset changes to all referencing cues
Recast Preset 21.37 Thru 500   Batch recast a range
```

### Sequence & Executor Assignment
```
Assign Sequence 1 Fader 201    Assign sequence to executor fader
Go Sequence 2                  Trigger sequence 2 (embeddable in cue command field)
```

### Macro Commands
```
Selfix                         Select fixtures from current sequence
Blind                          Toggle blind mode (prevents visual output)
Clear All                      Clear programmer
Label Cue 2 "Sinus Effect"     Label a cue
```

### Layout
```
Assign Group 1                 Assign group to layout
```

---

## Key Workflows (Step-by-Step)

### 1. New Show Setup (E01–E07)

1. Install and launch MA3 OnPC from malighting.com
2. **Patch fixtures** (E02): Menu → Patch → Insert New Fixture → select source (MA3/MA2/GDTF) → set Name, Quantity, Fixture ID, DMX address → Apply → Save & Exit
3. **Position fixtures in 3D** (E04): 3D view → Setup → set Z (height), Y (depth), X (spread) in meters → use Align (dash mode) for symmetric fan
4. **Create groups** (E03): `701 Thru 712 Please` → Store → click group pool slot → label
5. **Build preset pools** (E05): Position, Color, Gobo, Focus, Beam presets using swipeys or command line
6. **Build views** (E03, E06): Programming view (groups + all preset pools + 3D) → Layout view (per fixture type)
7. **Configure 3D quality** (E07): Beam quality = High Shadow Fancy, Spot quality = Gobo + Bloom

### 2. Sequence & Cue Programming (E08–E09)

1. Set look in programmer → `Store` → click Sequence pool slot → label
2. Change look → `Store` → same sequence → Create (new cue)
3. Set fade times in Sequence Sheet (right-click fade cell → enter seconds)
4. `Assign Sequence 1 Fader 201` → gives fader + Go button
5. Extend to rows 101/301/401 for more buttons/knobs per sequence

### 3. Effect Programming (E10–E11)

1. Import predefined phasers: Macro Pool → New Macro Line → Import → "Import Predefined Phaser"
2. Select fixtures → click effect in All Preset pool
3. Set phase spread: Phaser menu → parameter → `0 Thru 360`
4. Create Speed Master: right-click executor → Special Master → Speed
5. Assign Speed Master to sequence in sequence settings
6. For custom effects: Phaser Editor → Step 1 values → Step 2 values → choose waveform → apply phase

### 4. Macro-Based Show Building (E12–E13)

```
Line 1:  Blind
Line 2:  Selfix
Line 3:  At Preset 21.1
Line 4:  Store Cue 2 /o
Line 5:  Label Cue 2 "Sinus Effect"
Line 6:  Selfix
Line 7:  At Preset 21.2
Line 8:  Store Cue 3 /o
Line 9:  Label Cue 3 "Snap On Effect"
...
Line N:  Clear All
Line N+1: Blind
```

### 5. Advanced Cue Timing (E16)

- **Split fades**: `5 / 1` = 5s fade-in, 1s fade-out
- **Per-fixture delay**: Edit cue → select fixtures → set delay `0 Thru 1` (spreads 0s→1s across fixtures)
- **Gobo-before-dimmer**: Delay dimmer ~0.5s so gobo positions before lamp comes up
- **Follow cues**: Set trigger to Follow → auto-advances when cue completes
- **Cross-sequence trigger**: Embed `Go Sequence 2` in a cue's command field

### 6. Tracking Management (E20–E21)

- **Tracking**: Cues only record values that change; unchanged values inherit from previous cues
- **Cue Only**: Check this box for one-off changes that auto-revert (strobe bumps, flash cues)
- **Block Cue**: `Block Cue 7` — prevents values from tracking through a section boundary
- **Unblock**: `Unblock Cue 1 Thru 50` — removes redundant hard values
- **Remove mode**: `Store Cue N` → Remove — deletes specific parameter values, restoring tracking

### 7. MVR Import (E17)

1. Export from WYSIWYG/Vectorworks: File → Export → MVR
2. Copy `.mvr` to `grandMA3/library/mvr/` on thumb drive
3. MA3: Settings → Patch → Import MVR → import everything
4. Replace incorrect fixture types from shares library
5. Sort by Fixture ID → patch DMX addresses

---

## Fixture ID Numbering Convention (from demo)

| Fixture Type | ID Range | Group |
|---|---|---|
| Dimmers / Blinders | 101–112 | 100 |
| Strobes (Atomics) | 301–306 | 300 |
| Wash (Auras) | 601–612 | 600 |
| Profile/Spot (Vipers) | 701–712 | 700 |

## Executor Row Architecture

| Row | Components | Notes |
|-----|-----------|-------|
| 101 | Bottom button only | Independent, standalone trigger |
| 201 | Button + fader | Tied together; main playback |
| 301 | Button + rotary encoder | Upper knob |
| 401 | Button + rotary encoder | Top knob |

## 3D Position Defaults (meters)

| Fixture Type | Z (height) | Y (depth) | X spread (±) |
|---|---|---|---|
| Profile spots | 6.0 | 6.0 | 6.0 |
| Wash lights | 6.5 | 5.5 | 6.0 |
| Strobes | 7.0 | 5.0 | 6.0 |
| Dimmers/Blinders | 7.5 | 4.5 | 6.0 |

---

## RayFlow Integration Notes

### Critical Path for AI-Generated Shows

The MA3 command-line syntax extracted from this series is what RayFlow must emit to generate valid show files. The minimum viable show requires:

1. **Patch** — `Patch Fixture <range> Patch To <universe.address>`
2. **3D positions** — X/Y/Z coordinates in meters
3. **Groups** — `FixtureID Thru FixtureID Please` → Store to group pool
4. **Presets** — Position, Color, Gobo, Focus, Beam stored to correct pool numbers
5. **Sequences** — Store cues with proper fade/delay/trigger settings
6. **Executor assignment** — `Assign Sequence N Fader 201`
7. **Effects** — Phaser effects with phase spread, speed masters

### Key Patterns RayFlow Must Implement

1. **Wrap macros in Blind mode** to prevent visual output during automated show construction
2. **Use `/o` flag** on Store commands to prevent interactive prompts
3. **Default to Merge** when adding to existing cues; use Override only for full replacement
4. **Apply phase spread** (`0 Thru 360`) to all phaser effects for spatial distribution
5. **Insert block cues** at section boundaries to prevent tracking contamination
6. **Run `Unblock`** after generation to clean redundant hard values
7. **Use `Recast Preset`** when modifying presets rather than rewriting cues individually
8. **Delay dimmer ~0.5s** when cues involve gobo changes (gobo-before-dimmer pattern)

### Command Generation Priority

| Priority | Commands | Purpose |
|---|---|---|
| P0 | Patch, Store, Assign | Show structure |
| P0 | Selfix, At Preset, Store Cue /o, Label Cue | Macro building |
| P1 | Blind, Clear All | Safe automated execution |
| P1 | Phase, Speed Master assignment | Effect quality |
| P2 | Block Cue, Unblock Cue, Recast Preset | Tracking hygiene |
| P2 | Follow, Go Sequence N | Auto-advancing playback |
| P3 | Appearances, Layout Views | Polish and usability |
