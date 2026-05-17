# Phase 5 Architecture — Show & Rig Framework

> **Purpose**: Define the data model, file structure, and design decisions for Phase 5 — the foundation that enables AI-assisted show creation.

## Vision

RayFlow manages **rigs** (stage configurations with fixtures, positions, and presets) and **shows** (a rig + a song + a timecoded cue sequence). An AI coding tool reads the rig and show context, receives natural-language direction from the user, and generates concrete modifications that are pushed to grandMA3 onPC via OSC.

The output is a timecoded light show for recorded music, played back through MA3's native timecode feature.

## Data Model

### Core Entities

```
Venue ──┐
         ├── Rig ──┐
Preset ──┘         │
                    ├── Show ──┐
Song ───────────────┘          │
Vibe ──────────────────────────┘
                    └── Cue (many per Show)
```

### Venue

A physical or virtual space where a rig is placed.

```python
@dataclass
class Venue:
    name: str
    dimensions: tuple[float, float, float]  # width, depth, height in meters
    notes: str | None = None
```

### Preset

A named, preprogrammed lighting look that can be referenced by name during show building. Presets are the building blocks AI uses to construct shows quickly.

Each preset maps to a set of channel commands organized by **attribute family**:

| Attribute Family | Description | Example Values |
|-----------------|-------------|----------------|
| **Dimmer** | Intensity/brightness | `Full`, `50%`, `0` |
| **Position** | Pan and tilt angles | `Pan 45 Tilt 30` |
| **Color** | Color wheel, CTB/CTO, RGB mixing | `Red`, `CTO Full`, `#FF6600` |
| **Beam** | Zoom, iris, frost, shutter/strobe | `Zoom 25`, `Strobe 4Hz` |
| **Focus** | Focus distance (for fixtures that support it) | `Focus Far` |
| **Gobo** | Gobo wheel selection and rotation | `Gobo 3`, `GoboRotate Fast` |

```python
@dataclass
class Preset:
    name: str
    description: str
    attributes: dict[str, str]  # {"dimmer": "Full", "color": "Warm Amber", ...}
    channels: str | None = None  # MA3 channel spec, e.g. "1 Thru 8"
    tags: list[str] = field(default_factory=list)  # ["warm", "wash", "front"]
```

**Example presets**:
- `"warm_wash"` — dimmer 80%, color warm amber, all front fixtures
- `"cold_beam"` — dimmer full, color cool blue, narrow zoom, spot fixtures
- `"blackout"` — all dimmers to 0
- `"strobe_pulse"` — dimmer full, strobe 8Hz, white color

### FixtureSlot

A single fixture placed in a rig with its DMX addressing and physical position.

```python
@dataclass
class Position3D:
    x: float  # meters, stage-left/right
    y: float  # meters, height
    z: float  # meters, upstage/downstage
    pan: float  # degrees, 0 = center
    tilt: float  # degrees, 0 = straight down

@dataclass
class FixtureSlot:
    fixture_name: str       # Must match a fixture in the GDTF library
    mode: str               # DMX mode name (e.g., "Standard")
    label: str              # Human-readable label ("Front Left PAR 1")
    universe: int
    start_address: int
    position: Position3D
    channels: str | None = None  # MA3 channel number or range
```

### Rig

A complete stage configuration — the "instrument" that the show is programmed on.

```python
@dataclass
class Rig:
    name: str
    venue: Venue
    fixtures: list[FixtureSlot]
    presets: dict[str, Preset]  # Named presets keyed by name
    notes: str | None = None
```

### Song

Metadata about the audio track, plus imported section markers.

```python
@dataclass
class Section:
    name: str           # "Verse 1", "Chorus", "Bridge", "Intro"
    start: float        # Start time in seconds
    end: float          # End time in seconds
    energy: float | None = None    # 0-1, from external audio analysis
    mood: str | None = None        # "dark", "uplifting", "aggressive"

@dataclass
class Song:
    title: str
    artist: str
    duration: float     # Total duration in seconds
    bpm: float | None = None
    sections: list[Section] = field(default_factory=list)
```

### Vibe

An AI-generated organizing principle for a show — the creative direction before specific cues are built.

```python
@dataclass
class ColorPalette:
    name: str
    colors: list[str]   # Hex codes or gel references (e.g., "#FF6600", "R02")
    description: str

@dataclass
class Vibe:
    palette: ColorPalette
    intensity_curve: str        # "low → medium → high → low"
    movement_style: str         # "static", "slow sweep", "dynamic pan/tilt"
    beam_style: str | None = None  # "tight beams", "wide wash", "mixed"
    mood_keywords: list[str] = field(default_factory=list)
    description: str
```

### Cue

A single lighting state at a specific point in the song.

```python
@dataclass
class Cue:
    number: int
    label: str
    section: str            # Which song section this belongs to
    timestamp: float        # Timecode in seconds from song start
    preset: str | None = None  # Reference to a rig preset, if used
    channels: str | None = None  # MA3 channel spec
    attributes: dict[str, str] = field(default_factory=dict)  # {"dimmer": "80", "color": "Red"}
    fade_time: float = 0.0
    follow_time: float | None = None
    notes: str | None = None
```

### Show

The complete artifact — a rig applied to a song with cues and an optional vibe.

```python
@dataclass
class Show:
    name: str
    rig_name: str           # Reference to a rig YAML file
    song: Song
    vibe: Vibe | None = None
    cues: list[Cue] = field(default_factory=list)
    notes: str | None = None
```

## File Structure

```
data/
├── fixtures/              # GDTF fixture library (existing)
├── rigs/                  # NEW — Rig definitions
│   ├── venues/
│   │   └── my_venue.yaml
│   └── my_rig.yaml        # References venue, defines fixtures + presets
├── shows/                 # NEW — Show definitions
│   ├── my_show.yaml       # References rig + song, contains cues + vibe
│   └── songs/
│       └── song_metadata.yaml  # Song metadata + sections
└── presets/               # NEW — Reusable preset libraries (optional)
    └── standard_presets.yaml
```

### Rig YAML Format

```yaml
name: "Club Rig v1"
venue:
  name: "Small Club"
  dimensions: [12, 6, 4]  # width, depth, height (meters)
fixtures:
  - fixture_name: "Robe Robin iSpiider X"
    mode: "Zones"
    label: "Spiider 1"
    universe: 0
    start_address: 1
    position: {x: -2, y: 4, z: 1, pan: 0, tilt: 0}
    channels: "1"
  - fixture_name: "BlenderDMX LEDPAR64RGBW"
    mode: "Default"
    label: "Front Left PAR 1"
    universe: 0
    start_address: 13
    position: {x: -3, y: 3, z: 0, pan: 0, tilt: 0}
    channels: "2"
presets:
  warm_wash:
    name: "Warm Wash"
    description: "Warm amber wash across all front fixtures"
    attributes:
      dimmer: "80"
      color: "Warm Amber"
    channels: "2 Thru 9"
    tags: ["warm", "wash", "front"]
  blackout:
    name: "Blackout"
    description: "All fixtures off"
    attributes:
      dimmer: "0"
    channels: "1 Thru 20"
    tags: ["blackout"]
```

### Show YAML Format

```yaml
name: "All in Time — Show v1"
rig_name: "Club Rig v1"
song:
  title: "All in Time"
  artist: "Paul McFartney"
  duration: 245.0
  bpm: 120
  sections:
    - {name: "Intro", start: 0, end: 15, energy: 0.3, mood: "ambient"}
    - {name: "Verse 1", start: 15, end: 45, energy: 0.5, mood: "mellow"}
    - {name: "Chorus", start: 45, end: 75, energy: 0.9, mood: "uplifting"}
vibe:
  palette:
    name: "Warm to Cool"
    colors: ["#FF6600", "#FF3366", "#3366FF", "#00CCFF"]
    description: "Start warm, transition to cool blues by chorus"
  intensity_curve: "low → medium → high → medium"
  movement_style: "slow sweep in verses, dynamic in chorus"
  mood_keywords: ["cinematic", "building", "emotional"]
  description: "Warm amber intro building to cool blue energy"
cues:
  - number: 1
    label: "Intro Wash"
    section: "Intro"
    timestamp: 0
    preset: "warm_wash"
    fade_time: 3.0
  - number: 2
    label: "Verse Build"
    section: "Verse 1"
    timestamp: 15
    attributes:
      dimmer: "60"
      color: "Warm Amber"
    channels: "2 Thru 9"
    fade_time: 2.0
  - number: 3
    label: "Chorus Hit"
    section: "Chorus"
    timestamp: 45
    attributes:
      dimmer: "Full"
      color: "Cool Blue"
    channels: "1 Thru 20"
    fade_time: 0.5
```

## Serialization

- **Format**: YAML for human readability and version control. JSON supported for programmatic access.
- **Location**: All data files live under `data/` for easy git tracking.
- **Validation**: Dataclasses with type hints. Pydantic or dataclass validation on load.
- **References**: Shows reference rigs by name (not embedded). Rigs reference fixtures by name from the GDTF library.

## Integration with Existing Code

Phase 5 builds directly on Phases 1-4:

| Existing Module | How Phase 5 Uses It |
|----------------|---------------------|
| `fixtures/library.py` | Resolves fixture references in FixtureSlot to actual GDTF data |
| `fixtures/patch.py` | Validates DMX addressing, builds channel maps |
| `fixtures/mvr_export.py` | Exports rig to MVR for MA3 import |
| `console/osc.py` | Pushes cue commands to MA3 |
| `console/cue.py` | Converts Cue dataclass to Ma3Command sequences |
| `bridge/artnet.py` | Optional: direct DMX playback without MA3 |

## Export Path

The completed show flows to MA3 through three channels:

1. **MVR Export** — Rig geometry and fixture positions → MA3 scene (already implemented)
2. **OSC Cue Commands** — Cue data → MA3 sequences via existing `console/cue.py` builders
3. **Timecode** — Cue timestamps → MA3 timecode triggers (new, Phase 7)

```
Show YAML ──┬── MVR Export ──→ MA3 scene
            ├── Cue Commands ──→ MA3 sequences (via OSC)
            └── Timecode Map ──→ MA3 timecode triggers
```

## Design Decisions

### Why YAML over JSON?
YAML is more readable for humans editing rigs and shows directly. JSON is supported for programmatic/AI access. The AI interaction contract uses JSON for structured context but YAML for persistent storage.

### Why separate Rig from Show?
A rig is reusable across multiple shows. The same stage setup might light 10 different songs. Separating them avoids duplication and makes rig development independent of show work.

### Why presets as named references?
Presets are the vocabulary AI uses to talk about lighting. Instead of generating raw channel values, the AI can say "apply warm_wash to the chorus" or "create a preset called verse_glow." Named presets make the AI's reasoning traceable and editable.

### Why attribute-based preset definition?
Attribute families (dimmer, position, color, beam, focus, gobo) map to how lighting designers think and how MA3 organizes its programmer. This makes presets intuitive to define and easy to translate to MA3 commands.

### Why not embed fixture GDTF data in rigs?
Fixtures are managed by the existing GDTF library. Rigs reference them by name. This keeps rig files small and ensures fixture definitions stay in sync with the library.

### Why not build an MCP server now?

An MCP (Model Context Protocol) server would expose RayFlow's capabilities as tools and resources to any MCP-compatible AI client. We analyzed this and decided to defer it:

**Current approach (YAML + CLI + direct file access):**
- AI coding tools (Claude Code, Codex) already have file system access
- They can read/write YAML and run CLI commands directly
- No additional server needed

**When MCP becomes valuable:**
- Connecting AI assistants that don't have file access
- Real-time MA3 state queries (live show state, sequence status)
- Exposing RayFlow to any MCP-compatible AI client, not just coding tools

**Design for it anyway:**
- Models are pure data with no side effects
- Clean `as_dict()` methods on all models for MCP resource serialization
- Validation is explicit and testable
- No global state — everything is passed as parameters
- The MCP server (Phase 6+) can reuse the serialization layer directly

## Future Considerations (Out of Scope for Phase 5)

- **Fixture groups**: Named groups of fixtures for easier cue targeting
- **Cue timing curves**: Non-linear fade shapes (ease-in, ease-out)
- **Multi-universe rigs**: Support for large rigs spanning multiple DMX universes
- **3D position import**: Import fixture positions from MVR or CAD files
- **Preset blending**: Crossfade between presets within a cue
- **MCP server**: Expose RayFlow as MCP tools/resources for any AI client (Phase 6+)
