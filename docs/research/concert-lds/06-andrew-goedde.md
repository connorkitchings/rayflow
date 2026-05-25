# Andrew Goedde — Goose

**Era:** 2010s – present
**Role:** Lighting Director, Goose

## The Modern Jam Band Aesthetic

Andrew Goedde has risen with Goose, one of the most prominent jam bands of the current generation. His lighting brings a modern, visually dense aesthetic to the improvisational tradition — saturated colors, intricate movement patterns, and a polished production sensibility that reflects Goose's blend of indie rock, funk, and extended improvisation.

## Programming Style

### Modern Busking with Production Polish
Goedde is fundamentally a busker in the Kuroda lineage — the Goose show is lit moment to moment, not timecoded. But his style incorporates modern production values:

- **Saturated, contemporary palettes:** Deep teals, vivid magentas, neon-inspired accents alongside classic warm ambers and cool lavenders
- **Dense look construction:** Multiple fixture groups active simultaneously, each contributing a distinct color, texture, or movement layer
- **Music-video sensibility:** Looks are designed to be camera-ready for the live streams and social media clips that drive Goose's fan engagement

### Band Chemistry
Goedde's lighting reflects Goose's musical dynamics: tight, syncopated grooves that open into soaring improvisational peaks. His chases lock to the rhythm section, his color shifts follow harmonic changes, and his movement expands and contracts with the band's energy arc.

### Social Media Awareness
Goose's rise has been amplified by live streams and social media clips. Goedde programs with the camera in mind — ensuring that even short clips (15–60 seconds) contain visually striking moments. This means every section of every song gets attention; there are no "coasting" sections where the lighting runs on autopilot.

## Technical Workflow

Goedde's approach represents the offline-first development pipeline that RayFlow aims to enable:

### Console and Pre-Viz
- **Console:** grandMA3 (onPC for offline programming, full-size console live)
- **Pre-viz:** Uses pre-visualization software (Capture, Depence², or MA3 3D) for offline programming and look development
- **Workflow:** Build show file in MA3 onPC → validate in pre-viz → iterate → load onto physical console at venue → calibrate focus to real rig → showtime

### What Gets Built Offline
Like most touring LDs, Goedde likely spends 20–35 hours pre-building infrastructure before tour:
- Extensive palette library (position, color, beam, dimmer presets)
- Effect templates (BPM-linked chases, movements, color sweeps)
- Busking executor layout with layered sequences
- Song-specific cue stacks for known composed sections
- Speed master hierarchy for global tempo control

### The Virtual-to-Real Translation
The show file built offline is the same file loaded into the console at the venue. The transition requires only focus calibration — fixture positions adjusted to the real room. Everything else (palettes, effects, sequences, layout) transfers directly.

This is exactly the workflow RayFlow targets: develop everything possible on a computer, arrive at the venue with a near-complete show, and spend limited on-site time on calibration rather than creation. See `docs/research/design-concepts/24-virtual-show-development.md` for the full pipeline analysis.

## RayFlow Relevance

1. **Camera-aware authoring:** For acts with heavy live stream/social media presence, generate short-duration visual peaks (every 30–60 seconds) to ensure any clipped segment contains a striking moment.
2. **Contemporary palette generation:** Expand the palette library beyond theater-standard warm/cool to include modern color combinations (teal + magenta, neon cyan + amber, deep violet + gold).
3. **Density management:** The authoring system should support "look density" as a parameter — how many fixture groups are active simultaneously — and vary it across song sections.
