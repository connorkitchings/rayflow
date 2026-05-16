# Glossary

This glossary defines lighting industry terms and project-specific acronyms used throughout RayFlow.

## Art-Net

**Definition:** A royalty-free protocol for transmitting DMX512 data over UDP/IP networks.

**Context:** Used to send DMX values from RayFlow to grandMA3 onPC or visualizers. Runs on port 6454.

## Beam

**Definition:** The cone of light emitted by a fixture. In visualizers, beams are rendered as volumetric cones showing direction, color, and intensity.

**Context:** Beam visualization is a key feature of any lighting visualizer.

## Channel

**Definition:** A single controllable parameter of a fixture. Each channel has a value from 0-255 (8-bit).

**Context:** A moving head might have channels for pan, tilt, dimmer, color, gobo, focus, etc. Each channel occupies one DMX address.

## Color Temperature

**Definition:** The warmth or coolness of white light, measured in Kelvin (K). Lower values (~2700K) are warm/amber, higher values (~6500K) are cool/blue.

**Context:** Important for matching lighting to the mood of a song.

## Cue

**Definition:** A stored lighting state containing fixture values (intensity, color, position) with timing information (fade time, delay).

**Context:** Shows are built as sequences of cues. Each cue represents a moment in the show.

## Cue List / Sequence

**Definition:** An ordered collection of cues that play back in order. Also called a "sequence" in grandMA3.

**Context:** The primary structure for programming a show. Each cue in the list transitions to the next.

## DMX (DMX512)

**Definition:** Digital Multiplex — a standard for digital communication networks used to control lighting. Each DMX "universe" has 512 channels.

**Context:** The foundational protocol for all stage lighting control.

## Executor

**Definition:** A physical or virtual control on the grandMA3 console used to trigger playback of sequences, macros, or other functions.

**Context:** Executors have faders, buttons, and encoders for real-time control.

## Fixture

**Definition:** A physical or virtual lighting device. Examples: moving heads, LED pars, spotlights, hazers, lasers.

**Context:** Fixtures are defined by GDTF files and patched to DMX addresses.

## GDTF (General Device Type Format)

**Definition:** An open-standard file format that describes the capabilities and channel mapping of lighting fixtures.

**Context:** grandMA3 natively supports GDTF. Fixtures are downloaded from gdtf-share.com.

## Intensity

**Definition:** The brightness level of a fixture, typically expressed as a percentage (0-100%) or DMX value (0-255).

**Context:** The most fundamental channel — every fixture has at least an intensity/dimmer channel.

## Look

**Definition:** A specific lighting state or aesthetic — the combination of all fixture values at a given moment.

**Context:** "Warm look," "blue wash look," "strobe look." A cue stores a look.

## MVR (My Virtual Rig)

**Definition:** A file format for sharing 3D stage data between lighting consoles, visualizers, and CAD tools. Based on GDTF.

**Context:** RayFlow can generate MVR files from fixture patches for import to grandMA3's visualizer.

## OSC (Open Sound Control)

**Definition:** A network protocol for communication between computers and multimedia devices. Used by grandMA3 for remote control.

**Context:** RayFlow sends OSC commands to grandMA3 onPC to automate console operations.

## Pan / Tilt

**Definition:** The horizontal (pan) and vertical (tilt) movement axes of a moving head fixture.

**Context:** Moving heads have pan and tilt channels, typically 8-bit or 16-bit resolution.

## Patch

**Definition:** The assignment of fixtures to specific DMX addresses within a universe.

**Context:** "Patching" a fixture means giving it a starting DMX address so its channels map correctly.

## Programmer

**Definition:** The working area in grandMA3 where you set fixture values before storing them as a cue.

**Context:** You adjust values in the programmer, then "Store" to save as a cue.

## Rig

**Definition:** The complete set of fixtures arranged on a stage, including their positions and DMX assignments.

**Context:** "Building a rig" means creating the full fixture layout for a show.

## sACN (Streaming ACN / E1.31)

**Definition:** A protocol for transmitting DMX data over IP networks using multicast or unicast UDP. An alternative to Art-Net.

**Context:** More modern than Art-Net, supports more universes, uses multicast for efficient distribution.

## Universe

**Definition:** A single DMX network containing up to 512 channels. Multiple universes allow controlling more fixtures.

**Context:** grandMA3 onPC supports multiple universes. Art-Net supports 16 universes (0-15).

## Wheel

**Definition:** A physical or virtual rotating element in a fixture that selects colors, gobos, prisms, or effects.

**Context:** Color wheels, gobo wheels, and effect wheels are common in moving head fixtures.
