# Common Techniques Across Improvisational Concert LDs

**Source:** Analysis of shared patterns across the LDs profiled in this directory
**Parsed:** 2026-05-26

## The Universal Principles

Every LD in this tradition shares these principles:

### 1. Listen Like a Musician
The console is an instrument. The LD is not a technician executing a plan — they're a performer co-creating the show in real time. This requires deep musical listening, not just cue-list monitoring.

### 2. Anticipate, Don't React
The great LDs are slightly ahead of the band. They know the repertoire well enough to predict where an improvisation is heading. Body language, harmonic signals, and energy arcs all inform anticipation.

### 3. Layer, Don't Sequence
Timecoded shows run one cue list. Improvisational shows run 10–20 sequences simultaneously. The LD blends layers — intensity, color, position, movement, beam texture — creating unique combinations moment by moment.

### 4. Contrast Creates Emotion
Darkness defines light. Stillness defines movement. Warm defines cool. The most powerful moments come from contrast, not from everything being big all the time.

### 5. Infrastructure Enables, Technique Executes
A great LD can make magic with 12 PAR cans. But well-built infrastructure — palettes, presets, effect templates, busking layouts — gives the LD vocabulary. The best LDs invest heavily in building infrastructure before they need it.

## The Speed Master Pattern

Every LD in this tradition uses speed masters:

```
Global Speed Master → Controls tempo of ALL time-based effects
  ├── Dimmer chase speed (all fixture groups)
  ├── Movement generator speed
  ├── Color chase / sweep speed
  ├── Strobe pattern speed
  └── Gobo rotation speed
```

Tap tempo keeps everything locked to the band. One fader pulls the entire show into a new tempo.

## The Executive Layout Pattern

The ten-fader busking layout (Grum Leesmith pattern) provides the template:

| Position | Primary Function | Secondary (LTP Button) |
|----------|-----------------|----------------------|
| 1 | Spots dimmer | Spots color |
| 2 | Washes dimmer | Washes color |
| 3 | Position stack | Position advance |
| 4 | Color + beam stack | Color/beam advance |
| 5 | Spot movement size | Movement pattern |
| 6 | Wash movement size | Movement pattern |
| 7 | Blinders | Blinder pattern |
| 8 | Strobes | Strobe rate |
| 9 | Speed master | Tap tempo |
| 10 | Key light | — |

## The Palette Infrastructure Pattern

Every busking LD builds extensive palette libraries before programming a single cue:

| Palette Family | Minimum | Optimal | Purpose |
|---------------|---------|---------|---------|
| Position | 15 | 40+ | Stage positions, band positions, audience, aerial, specials |
| Color | 20 | 50+ | Warm family, cool family, saturated, pastels, band-specific |
| Beam | 10 | 25+ | Gobo + zoom + focus combinations, with and without prism |
| Dimmer | 5 | 10 | Full, 75%, 50%, 25%, chase base levels |

## The Hybrid Cue Stack Pattern (Waful / Factor)

Song-specific cue stacks that blend structured sections with busking handoff:

```
Cue 1–8:   Composed intro and verse   (timecoded, precise)
Cue 9:     BUSKING HANDOFF             (release to faders)
Cue 10–14: Jam section                 (LD improvises via busking)
Cue 15:    RETURN TO STRUCTURE         (timecoded, precise)
Cue 16–22: Composed outro              (timecoded, precise)
```

The handoff points are structural markers in the song's arrangement. They're known in advance even though the jam content is not.

## The "Big Sweep" Pattern (Hoffman)

Slow, 16–32 bar full-rig color transitions that transform the stage without the audience perceiving individual steps:

```
Bar 1–8:   Warm amber wash, cool lavender back
Bar 9–16:  Wash shifts amber → orange, back shifts lavender → medium blue
Bar 17–24: Wash shifts orange → deep red, back shifts medium blue → deep blue
Bar 25–32: Hold at deep red / deep blue peak, then reverse or cut
```

## The Blackout → Explosion Pattern (Kuroda / Brightman)

Sudden blackout held for 2–8 beats, then full-rig explosion on the downbeat:
- Used 1–3 times per show maximum (preserves impact)
- Most effective after a sustained dense section
- The explosion should introduce a new color palette, not return to the previous look
- The contrast creates the emotion; the explosion defines the new section

## The BPM Economy

As song tempo changes, the LD adjusts:

| Band Tempo Change | LD Response |
|------------------|-------------|
| Tempo increases | Push speed master forward, chase speed increases proportionally |
| Half-time feel | Pull speed master to 50%, chases breathe at half speed |
| Double-time feel | Push speed master to 200%, chases double |
| Free time / rubato | Freeze effects (speed master = 0%), static look |
| Tempo unknown | Tap tempo continuously, adjust on the fly |

## Implications for RayFlow

1. **Busking-first authoring model:** RayFlow's primary output should be layered, playable busking infrastructure (palettes, effects, sequences organized by function) rather than monolithic timecoded cue lists.
2. **Speed master as a data model primitive:** The cue and effect models must support BPM dependency declaration. The export system should generate speed master hierarchies.
3. **Palette library as show foundation:** Show generation should start with palette generation (40+ positions, 50+ colors, 25+ beams) before any cues are authored.
4. **Structural contrast planning:** The cue planner should explicitly schedule contrast moments — blackout/explosion pairs, warm/cool transitions, still/moving shifts — based on the song's structural markers.
5. **Genre-adaptive authoring:** Authoring defaults (palette, pace, density, contrast style) should change based on genre — jam band vs. electronic vs. roots rock vs. acoustic.
6. **Time-to-deploy awareness:** Generated busking infrastructure should include a complexity budget: can this be loaded and operational in the time an LD has before showtime?
