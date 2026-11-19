# Concert Effect Techniques: Speed Masters, Effect Engines, and Real-Time Manipulation

**Source:** Industry knowledge, console programming guides, LD techniques
**Parsed:** 2026-05-26

## The Problem: Static Looks Drain Energy

In concert lighting, a static look — even a beautiful one — loses its impact within 8–16 bars. The human visual system adapts. What felt dramatic at the start of the verse feels flat by the end. Movement, intensity variation, and color cycling prevent visual adaptation and maintain the audience's engagement.

## Effect Manipulation as Performance

Concert LDs don't just trigger effects — they *play* them. A chase isn't turned on and left alone; it's continuously modulated. The LD rides faders, taps tempo, switches patterns, and adjusts size throughout the song. Each modulation is a musical decision.

### The Rideable Parameters

| Parameter | Control | Musical Effect |
|-----------|---------|---------------|
| **Rate / Speed** | Speed master fader or tap tempo | Faster = more energy. Slower = more relaxed. |
| **Size / Amplitude** | Dedicated fader (0–100%) | Larger sweeps = more dramatic. Smaller = more subtle. |
| **Intensity Base Level** | Group master fader | Brighter = more present. Darker = more atmospheric. |
| **Pattern / Waveform** | Button: cycle through shapes | Circle = floating. Line = directed. Random = chaotic. |
| **Phase / Grouping** | Button: cycle through groupings | Singles = sequential wave. Groups of 4 = block movement. |
| **Color** | Palette selector or color fader | Warm = intimate. Cool = distant. Saturated = aggressive. |

## Building Playable Chases

### The Single-Fader Dimmer Chase

A well-built dimmer chase sequence on one fader:

```
Cue 1: Dimmer @ Full, no chase              (basic on — verse)
Cue 2: Sine chase, size = 30%, groups = 1   (subtle pulse — pre-chorus)
Cue 3: Sine chase, size = 60%, groups = 2   (stronger pulse — chorus)
Cue 4: Sawtooth chase, size = 80%, groups = 1  (driving energy — peak)
Cue 5: Random chase, size = 50%             (chaotic — jam section)
Cue 6: All off, chase off                   (blackout — reset)
```

The fader position controls overall intensity. Advancing through cues changes the chase character. The speed master controls the chase tempo. Three dimensions of control from two physical inputs.

### The Movement Generator

A two-fader movement system (size + pattern):

```
Movement Fader 1 (Size): 0% = static → 100% = full range sweep
Movement Fader 2 (Speed via speed master): linked to global tempo
Movement Buttons:
  Button 1: Circle (sine pan, cosine tilt)
  Button 2: Horizontal line (sine pan, static tilt)
  Button 3: Vertical line (static pan, sine tilt)
  Button 4: Figure-8 (sine pan, 2× sine tilt)
  Button 5: Diagonal (sine pan, sine tilt, 0° phase)
  Button 6: Random (random pan, random tilt)
  Button 7: Freeze (all movement stops, fixtures hold current position)
```

The LD points fixtures somewhere (position stack), then adds movement (movement generator), then adjusts size (size fader), all while the speed master keeps everything in time with the band.

## Speed Master Architecture

### The Hierarchy

```
Global Speed Master (fader 9)
  ├── Dimmer Chase Speed (spots)
  ├── Dimmer Chase Speed (washes)
  ├── Movement Speed (spots)
  ├── Movement Speed (washes)
  ├── Color Chase Speed
  ├── Strobe Pattern Speed
  └── Gobo Rotation Speed
```

One fader controls the tempo of every time-based effect. When the band drops into half-time, the LD pulls the speed master to 50% and everything — chases, movements, color sweeps — slows together.

### Tap Tempo

The LD taps a button on each beat (or every 4 beats) during the song. The console calculates:

```
current_bpm = 60 / average_tap_interval
effect_rate = current_bpm / beats_per_cycle
```

A chase set to "4 beats per cycle" at 120 BPM completes one full cycle every 2 seconds. If the band speeds to 140 BPM and the LD taps along, the chase speeds to 1.71 seconds per cycle — automatically, without reprogramming.

### Speed Divide/Multiply

Effects can run at multiples of the master tempo:

```
Speed Master at 100% (base tempo)
  Effect A: ×1     (one cycle per N beats — standard chase)
  Effect B: ×2     (double speed — energetic, urgent)
  Effect C: ×0.5   (half speed — relaxed, breathing)
  Effect D: ×0.25  (quarter speed — slow evolution, almost static)
```

This allows one fader to drive effects running at four different perceived speeds, creating polyrhythmic visual complexity.

## Strobe and Blinder Technique

### Strobe as Musical Punctuation

Strobes are not continuous effects — they're punctuation. A concert LD uses strobes like a drummer uses crash cymbals: once or twice per chorus, on the biggest hits, and not again until the next section.

```
Typical strobe pattern through a song:
  Verse 1:   No strobe
  Chorus 1:  1–2 strobe hits (on the downbeat)
  Verse 2:   No strobe
  Chorus 2:  2–4 strobe hits
  Bridge:    No strobe
  Final Chorus: 4–8 strobe hits, culminating in continuous strobe for final 4 bars
  Outro:     No strobe
```

### Blinder as Audience Connection

Blinders flash the audience with intense white light, physically connecting the crowd to the stage. They work because they're rare — 2–4 uses per song, maximum. Overuse makes them annoying rather than exciting.

### The Strobe Fader

```
Cue 1: Slow strobe (4 Hz)      — atmospheric, pulsing
Cue 2: Medium strobe (8 Hz)    — building energy
Cue 3: Fast strobe (15 Hz)     — intense, disorienting
Cue 4: Random strobe           — chaotic, unpredictable
Cue 5: Blind mode (solid on)   — maximum intensity, brief flash
Cue 6: Off                     — silence
```

## Color Manipulation in Real Time

### The Color Bump

A "color bump" is a momentary flash of a different color — the wash snaps to red for one beat, then returns to blue. This creates rhythmic punctuation without changing the base look. Accomplished via a bump button (momentary executor) assigned to a color preset.

### The Color Sweep

A slow rotation through the color spectrum, typically linked to the speed master. The wash gradually shifts: Deep Blue → Lavender → Magenta → Red → Amber → Yellow → Green → Cyan → Deep Blue, completing one cycle every 32–64 beats.

### Rainbow Chase (Absolute Effect)

A grandMA absolute effect that steps fixtures through color presets sequentially. Fixture 1 = Red, Fixture 2 = Orange, Fixture 3 = Yellow, etc. The chase advances through the rainbow with each beat. Speed master controls the advance rate.

## The "Cue Stack as Song" Approach

Some LDs pre-build song-specific cue stacks that combine structured sections with improvisational sections:

```
Sequence 17: "Divided Sky" (Phish)
  Cue 1:    Intro — sparse blue wash, single spot on Trey
  Cue 2–8:  Composed section — precise looks for each phrase
  Cue 9:    "Pause" — full blackout (famous silent section in this song)
  Cue 10:   Re-entry — full rig explosion
  Cue 11–15: Composed outro
  Cue 16:   Jam section — release to busking faders
  Cue 17:   Return to head — structured looks resume
```

The composed sections are pre-programmed. The jam section hands control back to the busking faders. This hybrid approach gives the LD the best of both worlds: precision where the music is predictable, flexibility where it isn't.

## Implications for RayFlow

1. **Effect templates with rideable parameters:** RayFlow should generate effects that expose rate, size, pattern, phase, and group parameters — not just fixed-value chases. These parameters become the LD's performance controls.
2. **Speed master dependency graph:** The authoring system should track which effects depend on which speed masters and generate a dependency graph. Exporting this graph tells the console how to build the speed master hierarchy.
3. **Strobe/blinder economy:** The cue generator should enforce strobe restraint — no more than 2–4 strobe uses per chorus, with increasing density through the song but never continuous until the climax.
4. **Song-specific cue stack generation:** For songs with known structures (verse/chorus/bridge), RayFlow should generate a hybrid cue stack: structured cues for composed sections, busking handoff for jam sections.
5. **Tap tempo simulation:** The renderer should support variable BPM input, simulating how effects change as the LD taps tempo in response to the band. This enables pre-visualization of tempo-flexible shows.
6. **Color bump presets:** The preset library should include "bump" presets — momentary color flashes intended for rhythmic punctuation — alongside sustained color presets.
