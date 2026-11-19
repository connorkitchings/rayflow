# Glossary

Plain definitions for terms used in the learn guides. Examples are for grandMA3 onPC.

- **Attribute**: one controllable property of a fixture, such as `Dimmer`, `Pan`, `Tilt` or red, green, blue color. Each attribute maps to one or more DMX channels.
- **Cue**: one stored look inside a sequence. Playing (Go) a cue fades from the previous look to this one. Example: `Store Cue 2` while a new look is in the programmer.
- **Executor**: a fader or button on the console (or its on-screen version) that plays a sequence. Storing a cue onto an empty executor creates a sequence.
- **Feature group**: a family of attributes shown together, such as Dimmer, Position, Color, Beam. In onPC the encoder bar has layers named after them; the Generic Moving Head type defines groups named `Dimmer`, `Position`, `Color`, `Focus`, `Beam` and `Control`.
- **FID**: fixture ID, the number you use to select a fixture in commands. Example: `Fixture 1 Thru 4` selects FIDs 1 to 4. It is separate from the DMX address.
- **Fixture**: one light in the show, such as a moving head or an LED wash. Each fixture has a type, a FID and a DMX address.
- **Group**: a stored selection of fixtures. Example: select the washes, then `Store Group 1`, and later recall all eight by selecting Group 1.
- **Haze**: a fine, mostly invisible fog in the air that makes light beams visible. In the 3D viewer, beams may need haze enabled to be seen (see the first-hour guide).
- **Patch**: the list that tells the console which fixtures exist and where each listens on DMX. Example: four movers at addresses `1.001`, `1.019` and so on.
- **Preset**: a stored set of attribute values for reuse, such as an amber color or a stage position. Presets live in pools by type.
- **Programmer**: the live scratchpad where your current values sit before you store them. `ClearAll` empties it.
- **Sequence**: an ordered list of cues. A sequence is played by an executor.
- **Timecode**: a running clock (hours:minutes:seconds:frames) that triggers cues at exact times, so the lights follow a song without a human pressing Go.
