# Busking Architecture: The Console as an Instrument

**Source:** Industry knowledge, LD techniques, console programming philosophy
**Parsed:** 2026-05-25

## What Busking Actually Means

"Busking" (also called "punting") is the art of building a lighting show in real time from pre-built building blocks — palettes, effects, sequences, and chases — without knowing in advance what the band will play. The LD assembles the show moment by moment, like a musician improvising a solo from scales and patterns they've internalized.

## The Fader as Primary Interface

In a busking layout, every fader and executor button is a musical control. The LD's hands rarely leave the console surface. The layout is designed for one person operating at speed, with the most-used controls closest to the dominant hand.

### The Standard Festival Layout (Grum Leesmith Pattern)

Ten faders, one page, no programmer access during show:

| Fader | Layer | What It Controls |
|-------|-------|-----------------|
| 1 | Spots Intensity | Dimmer on/off, shutter random, dimmer chase intensity. Fader = master level. |
| 2 | Washes Intensity | Same for wash group. Independent from spots. |
| 3 | Position Stack | 10–30 position presets in a cue stack. Button = next position, fader = crossfade speed. |
| 4 | Color + Beam Stack | Complementary colors and beam textures. Button cycles through combinations. |
| 5 | Spot Movements | Movement generator. Fader = movement size. Button toggles circle/line/figure-8. |
| 6 | Wash Movements | Independent movement for washes. Same pattern, different fixtures. |
| 7 | Blinders | All on, odd/even chase, random flash. Purely intensity — no color. |
| 8 | Strobes | Slow/medium/fast/random flash rates. Separate from blinders for independent control. |
| 9 | Speed Master | Scaled master for all dimmer chases. Pull down = slower chases. Push up = faster. |
| 10 | Key Light | Dedicated front light for band/speaker. Always accessible. Never part of a chase. |

### Layered Approach in Practice

The LD might simultaneously:
- Fader 1 at 60% (spots dimmer low, building)
- Fader 2 at 0% (washes off)
- Fader 4 at position 3 (cyan + breakup gobo)
- Fader 5 at 30% size (small circle movement)
- Fader 9 at 50% (moderate chase speed)
- Fader 10 at 80% (key light consistent)

Then on the chorus:
- Fader 2 snap to 100% (washes on full)
- Fader 4 advance to position 7 (red + open gobo)
- Fader 5 push to 80% size (big sweeping movement)
- Fader 7 flash (blinders hit)
- Fader 9 push to 100% (chases accelerate)

All in the space of one beat. This is what "playing the console" means.

## Sequence Architecture for Busking

Each fader's sequence is designed differently from a theatrical cue list:

### Intensity Sequences

```
Cue 1:  Dimmer @ Full, shutter open          (basic on)
Cue 2:  Dimmer @ Full, random shutter         (flickering energy)
Cue 3:  Dimmer chase (sine, speed = master)   (pulsing with music)
Cue 4:  Dimmer chase (fast random)            (chaotic energy)
Cue 5:  All off (blackout)                    (reset)
```

The fader acts as a master level for whichever cue is active. Cue 3 at 50% fader = dimmer chase at half brightness. Cue 3 at 100% fader = full brightness chase.

### Position Stacks

```
Cue 1:  All spots DSC (downstage center) — basic front
Cue 2:  Spots fanned in a line across stage — full coverage
Cue 3:  Spots crossed (left fixtures → right, right → left) — dramatic
Cue 4:  All spots straight up — aerial emphasis
Cue 5:  Spots aimed at audience — engagement
...up to 30 presets
```

Each cue is a snapshot of all spots at specific positions. The LD advances through these with a button press, crossfading smoothly.

### Movement Generators

A movement fader doesn't store positions — it applies a movement *effect* to whatever position the fixtures are currently at:

- **Fader position = movement size.** 0% = fixtures hold current position. 50% = medium circles. 100% = full-range sweeps.
- **Button = movement pattern.** Circle, horizontal line, vertical line, figure-8, random.
- **Speed = linked to speed master.** Movement tempo follows the chase master.

This separation of "where they point" (Position stack) from "how they move" (Movement fader) is the key busking insight. The LD can point fixtures at the drummer (cue 4 on position stack) AND have them circle (fader 5 at 40%) simultaneously.

## Speed Masters: The Global Tempo Knob

A speed master is a single fader that controls the cycle time of every tempo-linked effect in the show:

```
Speed Master at 100% = effects run at programmed speed
Speed Master at 200% = effects run at double speed
Speed Master at 50% = effects run at half speed
Speed Master at 0% = all effects frozen (static look)
```

### What Gets Linked to Speed Master

- All dimmer chases (intensity pulsing)
- All movement generators (pan/tilt effects)
- All color chases (rainbow sweeps)
- Strobe patterns (not individual flashes — the pattern tempo)
- Gobo rotation speeds

### What Does NOT Get Linked

- Fixed cue fades (these are absolute time, not musical time)
- Key light intensity (always consistent)
- Blinder flashes (punctuation, not tempo)
- Manual GO cues (operator-timed)

### BPM Tap

Most busking consoles allow the LD to tap a BPM button in time with the drummer. The console calculates current BPM and adjusts all speed-master-linked effects accordingly. If the band speeds up mid-jam, the LD taps faster and the lights follow.

## HTP/LTP Doubling

On grandMA, each executor has a fader (HTP for intensity) and a button (LTP for attributes). Clever programming doubles each fader's functionality:

| Executor | Fader (HTP) | Button (LTP) |
|----------|-----------|------------|
| 1 | Spots dimmer level | Spots color select |
| 2 | Washes dimmer level | Washes color select |
| 3 | — (position can't HTP) | Position select |
| 4 | — | Beam/gobo select |
| 5 | Movement size | Movement pattern select |

Ten physical faders → 20 independent controls.

## Color Selection in Busking

Color is handled two ways:

### Cue Stack Approach
A sequence contains complementary color pairs or triads. The LD presses a button to advance through: Warm Front/Cool Back → Cool Front/Warm Back → Monochrome Blue → Full Spectrum → White → Blackout.

### Direct Select Approach
Color presets are assigned to executor buttons in a grid. The LD presses a button to assign that color to the selected fixture group. This is faster but requires more physical buttons.

Most buskers use a hybrid: a base color stack for the overall show arc, and direct color selects for special moments (brand colors, song-specific palettes).

## The Pre-Programming Paradox

A busking show requires *less timecoded pre-programming* but *more pre-built infrastructure* than a timecoded show. The LD spends days building:

- 40+ position presets
- 50+ color presets (including multi-fixture color combinations)
- 20+ beam presets (gobo + zoom + focus combinations)
- 10+ effect templates (chases, movements, color sweeps)
- 10 faders × 5–30 cues each = 50–300 cues organized as playable sequences

This infrastructure is the LD's instrument. Once built, any song can be lit without touching the programmer.

## Implications for RayFlow

1. **Author for busking, export for timecode:** RayFlow should generate busking-ready infrastructure (palettes, effects, layered sequences) as its primary output. Timecode exports are a secondary flattening of that infrastructure.
2. **Speed master as a first-class concept:** The cue model should support `speed_master_link: bool` to indicate which effects respond to global tempo. The renderer should generate BPM-dependent timing tables.
3. **Sequence type metadata:** Sequences should carry a `sequence_purpose` field (intensity, position, color, beam, movement, strobe, key, master) to guide busking layout generation.
4. **Fader mapping export:** The show export should include a recommended busking layout — which RayFlow-generated sequences go on which faders — based on the fixture rig and show vibe.
5. **Layered rendering:** The renderer should support rendering multiple active sequences simultaneously to simulate busking blends. This enables the LD to pre-visualize how sequences will combine.
