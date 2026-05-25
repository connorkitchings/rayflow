# Cue Timing Philosophy: Beat-Based, Perceptual, and Musical Timing

**Source:** Web research, professional programming guides, musical theory crossover
**Parsed:** 2026-05-25

## Timing as a Musical Act

Cue timing is not a technical detail — it is the primary way a lighting design expresses musicality. A cue that snaps on the downbeat feels different from one that blooms over a bar. The choice of fade time, delay, and follow timing communicates energy, tension, and release.

## Beat-Based Timing

In music-driven shows, all cue timing should reference the song's tempo. This ensures lighting changes land on musical grid points rather than arbitrary seconds.

### Converting Beats to Seconds

```
beat_duration = 60 / BPM
cue_time = beat_duration * beats
```

| BPM | 1 beat | 1 bar (4/4) | 2 bars | 4 bars | 8 bars |
|-----|--------|-------------|--------|--------|--------|
| 60 | 1.0s | 4.0s | 8.0s | 16.0s | 32.0s |
| 80 | 0.75s | 3.0s | 6.0s | 12.0s | 24.0s |
| 100 | 0.6s | 2.4s | 4.8s | 9.6s | 19.2s |
| 120 | 0.5s | 2.0s | 4.0s | 8.0s | 16.0s |
| 140 | 0.43s | 1.7s | 3.4s | 6.9s | 13.7s |
| 160 | 0.375s | 1.5s | 3.0s | 6.0s | 12.0s |

### Practical Timing Units

| Musical Duration | When to Use |
|-----------------|-------------|
| 0s (snap) | Strobe hits, blinders, drum fills, instantaneous punctuation |
| 1 beat | Quick accent (cymbal hit color flash) |
| 1 bar (4 beats) | Verse-to-chorus transitions, wash color changes |
| 2 bars | Section transitions, position moves, vibe shifts |
| 4 bars | Mood transitions, full rig color sweeps |
| 8+ bars | Slow builds, intro/outro fades, theatrical scene changes |

## Fade Time Psychology

### 0-Second Fade (Snap)
- **Musical meaning:** Accent, punctuation, hit, surprise.
- **Visual effect:** Instant change. Fixture mechanically snaps to new position/value.
- **Risk:** Fast pan/tilt moves are noisy and visually abrupt. Strobe snaps can startle.
- **Best for:** Blinder flashes, strobe accents, drum hits, sudden blackouts.

### 0.5–1 Second Fade
- **Musical meaning:** Rhythmic, tight, dancing on the beat.
- **Visual effect:** Quick but perceptible transition. The eye can follow the move.
- **Best for:** Color changes within a verse, small position adjustments, intensity bumps on chord changes.

### 2–4 Seconds Fade
- **Musical meaning:** Expressive, emotional, breathing with the phrase.
- **Visual effect:** Smooth transition. Moving heads trace visible arcs. Colors blend gracefully.
- **Best for:** Verse-to-chorus washes, mood shifts, backlight intensity arcs.

### 5–8 Seconds Fade
- **Musical meaning:** Atmospheric, cinematic, slow build.
- **Visual effect:** Almost imperceptible in the moment. Viewers notice the change when looking back, not while it's happening.
- **Best for:** Intro builds, ambient sections, slow sunset-to-night transitions.

### 10+ Seconds Fade
- **Musical meaning:** Environmental, tectonic, barely-there.
- **Visual effect:** Change so slow it's felt rather than seen. Often used for cyclorama color shifts over entire scenes.
- **Best for:** Long theatrical scenes, art installations, background evolution.

## Delay Timing

Delay creates offset between the cue's trigger and its visible start. This is most often used when a cue contains multiple attributes that need staggered execution.

### Common Delay Patterns

| Pattern | Example | Effect |
|---------|---------|--------|
| **Dimmer first, then color** | Dimmer @ 0s delay, Color @ 0.5s delay | Light appears at base color, then shifts to target color |
| **Color first, then dimmer** | Color @ 0s delay, Dimmer @ 0.5s delay | Fixture moves to target color in dark, then fades in |
| **Position first, then dimmer** | Position @ 0s delay, Dimmer @ 1.5s delay | Classic "mark in dark" — fixture repositions silently, then reveals |
| **Left-to-right stagger** | Fixtures get Delay 0→N Thru N seconds | Wave/wipe effect across fixtures without needing an effect engine |

## Follow vs. Wait Timing

Cues can be triggered manually (GO button) or automatically after a set time:

| Trigger Type | Console Term | Use Case |
|-------------|-------------|----------|
| **Manual GO** | Halt / Wait | Operator-triggered. Busking, live events where timing is flexible. |
| **Auto-Follow** | Follow time | Timecode shows, pre-programmed sequences. Cue 2 fires automatically N seconds after Cue 1 completes. |
| **Timecode** | SMPTE / MTC | Frame-accurate sync to audio/video playback. Broadcast, theater, high-budget tours. |

## Energy Curve Mapping

Cue timing should follow the song's energy arc:

| Section Energy | Fade Behavior | Timing Feel |
|---------------|--------------|-------------|
| Low (0.0–0.35) | Long fades (4–8s), gentle transitions | Breathing, atmospheric |
| Medium (0.35–0.7) | Moderate fades (1–4s), some snaps | Rhythmic, building |
| High (0.7–1.0) | Fast snaps (0–0.5s), rapid chases | Aggressive, explosive |

## Cue Density

The number of cues per time period also communicates energy:

| Section | Cues Per Minute | Effect |
|---------|----------------|--------|
| Intro / Outro | 1–4 | Sparse, atmospheric, patient |
| Verse | 4–8 | Moderate pacing, catching key musical moments |
| Chorus | 8–16 | Busy, high-energy, every beat or every other beat |
| Bridge / Breakdown | 2–6 | Sparse, creating contrast with surrounding density |
| Climax / Drop | 12–24 | Maximum density, rapid-fire hits and chases |

## Implications for RayFlow

1. **BPM-aware authoring:** The cue generator should use `song.bpm` to calculate all timing in musical units (beats, bars), not arbitrary seconds. If BPM is unknown, fall back to reasonable defaults based on section energy.
2. **Energy-to-fade mapping:** The `_energy_to_dimmer` pattern in `authoring.py` should extend to timing — low energy sections get longer fades, high energy gets snaps.
3. **Section-appropriate cue density:** Cue count per section should vary by section type (intro = sparse, chorus = dense) rather than a uniform `cues_per_section`.
4. **Delay as a cue attribute:** The `Cue` model should support per-attribute delay offsets to enable staggered attribute execution within a single cue.
5. **Follow time generation:** The authoring system should generate follow times between adjacent cues so the entire show can play back as a timed sequence without manual GO presses.
