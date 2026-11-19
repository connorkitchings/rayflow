# Learn grandMA3 for concert lighting

Learning path for a complete console beginner using grandMA3 onPC 2.5.1.1 on a Mac. No hardware needed.

Start here:
- [First hour in grandMA3 onPC](01-first-hour-ma3.md): patch, look, cue, play.
- [Starter rig](starter-rig.md): the 4 moving heads and 8 LED washes, with exact fixture types, FIDs and addresses.
- [Glossary](glossary.md): plain definitions of the terms used.

## Phases

- Phase 1a is pre-work: the first-hour guide and the reading.
- Phase 1b is hands-on: modules 1 to 7 below. Each module is a concept, reading, a 15-minute onPC exercise and an LD (lighting director) whose work shows it best. Each module's full guide is written when you reach it. This page is only the index.

Reading paths are under `docs/research/`. LD profiles are under `docs/research/concert-lds/`. Which LD fits which module is an editorial choice, not a claim that they are the only example.

## Modules

### Module 1: Light's jobs: front, back and side

- Concept: light from the front makes performers readable, light from behind separates them from the dark, and light from the side gives them shape. Most rigs are built by assigning fixtures to these jobs.
- Reading: [`design-concepts/02-illumination-methods.md`](../research/design-concepts/02-illumination-methods.md), [`design-concepts/13-rig-design-fixture-placement.md`](../research/design-concepts/13-rig-design-fixture-placement.md)
- 15-minute exercise:
  1. Select the 8 washes (`Fixture 101 Thru 108`) and light only the front-truss washes at 50%.
  2. In the 3D viewer, note what the stage looks like.
  3. Add the movers as back light and note the change.
  4. Remove front light and compare.
  5. Store the three looks as cues 1 to 3.
- LD: Candace Brightman, whose rigs had only fixed lights and so leaned on placement: [`concert-lds/01-candace-brightman.md`](../research/concert-lds/01-candace-brightman.md)

### Module 2: Fixtures and attributes

- Concept: every fixture is a set of attributes (dimmer, pan, tilt, color, zoom) that become DMX channels. Knowing what a fixture type can do tells you what a look can be.
- Reading: [`protocols-and-systems/02-fixture-types-and-capabilities.md`](../research/protocols-and-systems/02-fixture-types-and-capabilities.md), [`design-concepts/23-reading-a-rig.md`](../research/design-concepts/23-reading-a-rig.md)
- 15-minute exercise:
  1. Select one mover and open each encoder bar layer in turn.
  2. Change one attribute at a time and watch the 3D viewer.
  3. Compare against the 18-channel list in `starter-rig.md`.
  4. Do the same for one wash.
  5. Write down which attributes the washes lack.
- LD: Paul Hoffman, whose organic busking relies on knowing each fixture's strengths by feel: [`concert-lds/03-paul-hoffman.md`](../research/concert-lds/03-paul-hoffman.md)

### Module 3: Color

- Concept: color is mixed (red, green, blue) or chosen from a wheel, and colors read differently next to each other. A small palette used consistently looks more deliberate than many colors.
- Reading: [`design-concepts/04-color-theory.md`](../research/design-concepts/04-color-theory.md), [`design-concepts/09-color-harmony.md`](../research/design-concepts/09-color-harmony.md)
- 15-minute exercise:
  1. Pick a two-color pair, one for movers and one for washes.
  2. Set them on the programmer using the Color layer.
  3. Store each as a color preset.
  4. Recall both pairs in turn and compare in the 3D viewer.
  5. Try one clashing pair and one harmonious pair.
- LD: Andrew Goedde, known for saturated, dense color: [`concert-lds/06-andrew-goedde.md`](../research/concert-lds/06-andrew-goedde.md)

### Module 4: Intensity and contrast

- Concept: the difference between bright and dark is what the eye reads as a shape or an accent. Many looks work better with less light overall plus one bright element.
- Reading: [`design-concepts/06-dimmer-curve-physics.md`](../research/design-concepts/06-dimmer-curve-physics.md), [`design-concepts/10-haze-and-atmosphere.md`](../research/design-concepts/10-haze-and-atmosphere.md)
- 15-minute exercise:
  1. Set all washes to 100% and look at the 3D viewer.
  2. Lower them to 20% and raise only the movers to full.
  3. Compare the two.
  4. Store both as cues.
  5. Toggle haze in the 3D window settings and see how beams change (3D haze setting location: unverified).
- LD: Candace Brightman, who shaped mood largely with intensity alone: [`concert-lds/01-candace-brightman.md`](../research/concert-lds/01-candace-brightman.md)

### Module 5: Movement

- Concept: moving lights add pan, tilt and shape over time, and the speed and pattern of the movement should match the music's energy. Slow sweeps feel different from fast chases.
- Reading: [`design-concepts/08-movement-patterns.md`](../research/design-concepts/08-movement-patterns.md), [`design-concepts/05-oscillators-and-effects.md`](../research/design-concepts/05-oscillators-and-effects.md)
- 15-minute exercise:
  1. Store two position presets for the movers, for example aimed at the center and aimed at the back.
  2. Store a cue that uses each.
  3. Play them with a slow fade, then a fast one.
  4. Compare in the 3D viewer.
  5. Note which speed suits a slow song.
- LD: Chris Kuroda, whose large rig is described as vocabulary of motion: [`concert-lds/02-chris-kuroda.md`](../research/concert-lds/02-chris-kuroda.md)

### Module 6: Cues and timing

- Concept: a cue stores a look, and its fade time controls how the change feels. A snap hits like a drum; a long fade blooms like a pad.
- Reading: [`design-concepts/12-cue-timing-philosophy.md`](../research/design-concepts/12-cue-timing-philosophy.md), [`programming-workflows/02-cue-and-effect-syntax.md`](../research/programming-workflows/02-cue-and-effect-syntax.md)
- 15-minute exercise:
  1. Store 4 cues of different looks in one sequence.
  2. Give cue 2 a 1-second fade and cue 3 an 8-second fade.
  3. Play with Go and watch the 3D viewer.
  4. Adjust the times to match a song you know.
  5. Check the exact `Time` syntax against the MA 2.5 manual (unverified).
- LD: Paul Hoffman, for organic, ear-led timing: [`concert-lds/03-paul-hoffman.md`](../research/concert-lds/03-paul-hoffman.md)

### Module 7: The song: sections and timecode

- Concept: a song has sections (intro, verse, chorus, solo) and each can have its own look. Timecode lets the lights follow the song automatically instead of by hand.
- Reading: [`programming-workflows/03-timecode-automation.md`](../research/programming-workflows/03-timecode-automation.md), [`design-concepts/22-design-iteration-loop.md`](../research/design-concepts/22-design-iteration-loop.md)
- 15-minute exercise:
  1. Write the sections of one song with their start times.
  2. Assign one stored cue to each section.
  3. Create a timecode show and place the cues at those times (see `docs/research/ma3-probes/ma3_timecode_command_automation_2026-05-19.md` for what has been verified).
  4. Play it back.
  5. Fix any timing that feels late.
- LD: Jefferson Waful, who combines section-based programming with busking: [`concert-lds/04-jefferson-waful.md`](../research/concert-lds/04-jefferson-waful.md)
