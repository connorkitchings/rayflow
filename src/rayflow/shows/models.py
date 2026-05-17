"""Show & Rig data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from rayflow.shows.presets import validate_preset_attributes


@dataclass(frozen=True)
class Position3D:
    """3D position with pan/tilt orientation."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    pan: float = 0.0
    tilt: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pan": self.pan,
            "tilt": self.tilt,
        }


@dataclass
class Venue:
    """A physical or virtual space where a rig is placed."""

    name: str
    dimensions: tuple[float, float, float]
    notes: str | None = None

    def __post_init__(self) -> None:
        w, d, h = self.dimensions
        if w <= 0 or d <= 0 or h <= 0:
            raise ValueError(
                f"Venue dimensions must be positive, got {self.dimensions}"
            )

    @property
    def width(self) -> float:
        return self.dimensions[0]

    @property
    def depth(self) -> float:
        return self.dimensions[1]

    @property
    def height(self) -> float:
        return self.dimensions[2]

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "dimensions": list(self.dimensions),
        }
        if self.notes:
            result["notes"] = self.notes
        return result


@dataclass
class Preset:
    """A named, preprogrammed lighting look.

    Attributes are keyed by attribute family: dimmer, position, color,
    beam, focus, and gobo.
    """

    name: str
    description: str
    attributes: dict[str, str]
    channels: str | None = None
    tags: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Preset name must not be empty")
        errors = validate_preset_attributes(self.attributes)
        if errors:
            raise ValueError(f"Invalid preset attributes: {'; '.join(errors)}")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
            "attributes": dict(self.attributes),
        }
        if self.channels:
            result["channels"] = self.channels
        if self.tags:
            result["tags"] = list(self.tags)
        return result


@dataclass
class FixtureSlot:
    """A single fixture placed in a rig with DMX addressing and position."""

    fixture_name: str
    mode: str
    label: str
    universe: int
    start_address: int
    position: Position3D = field(default_factory=Position3D)
    channels: str | None = None

    def __post_init__(self) -> None:
        if not self.fixture_name.strip():
            raise ValueError("Fixture name must not be empty")
        if self.start_address < 1:
            raise ValueError(
                f"DMX start address must be >= 1, got {self.start_address}"
            )
        if self.universe < 0:
            raise ValueError(f"Universe must be >= 0, got {self.universe}")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "fixture_name": self.fixture_name,
            "mode": self.mode,
            "label": self.label,
            "universe": self.universe,
            "start_address": self.start_address,
            "position": self.position.as_dict(),
        }
        if self.channels:
            result["channels"] = self.channels
        return result


@dataclass
class Rig:
    """A complete stage configuration — the instrument a show is programmed on."""

    name: str
    venue: Venue
    fixtures: list[FixtureSlot] = field(default_factory=list)
    presets: dict[str, Preset] = field(default_factory=dict)
    template: bool = False
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Rig name must not be empty")
        labels = [f.label for f in self.fixtures]
        if len(labels) != len(set(labels)):
            raise ValueError("Fixture labels must be unique")

    def add_fixture(self, slot: FixtureSlot) -> None:
        """Add a fixture slot to the rig."""
        for existing in self.fixtures:
            if existing.label == slot.label:
                raise ValueError(f"Fixture label '{slot.label}' already exists in rig")
        self.fixtures.append(slot)

    def add_preset(self, preset: Preset) -> None:
        """Add or replace a preset."""
        self.presets[preset.name] = preset

    def get_preset(self, name: str) -> Preset | None:
        """Get a preset by name."""
        return self.presets.get(name)

    def fixture_labels(self) -> list[str]:
        """Return all fixture labels."""
        return [f.label for f in self.fixtures]

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "venue": self.venue.as_dict(),
            "fixtures": [f.as_dict() for f in self.fixtures],
            "presets": {name: p.as_dict() for name, p in self.presets.items()},
        }
        if self.template:
            result["template"] = True
        if self.notes:
            result["notes"] = self.notes
        return result


@dataclass
class Section:
    """A part of a song with energy and mood metadata."""

    name: str
    start: float
    end: float
    energy: float | None = None
    mood: str | None = None

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError(f"Section start must be >= 0, got {self.start}")
        if self.end <= self.start:
            raise ValueError(f"Section end ({self.end}) must be > start ({self.start})")
        if self.energy is not None and not (0 <= self.energy <= 1):
            raise ValueError(f"Section energy must be 0-1, got {self.energy}")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "start": self.start,
            "end": self.end,
        }
        if self.energy is not None:
            result["energy"] = self.energy
        if self.mood is not None:
            result["mood"] = self.mood
        return result


@dataclass
class Song:
    """Metadata about the audio track with imported section markers."""

    title: str
    artist: str
    duration: float
    bpm: float | None = None
    sections: list[Section] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("Song title must not be empty")
        if self.duration <= 0:
            raise ValueError(f"Song duration must be > 0, got {self.duration}")

    def add_section(self, section: Section) -> None:
        """Add a section to the song."""
        self.sections.append(section)

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": self.title,
            "artist": self.artist,
            "duration": self.duration,
        }
        if self.bpm is not None:
            result["bpm"] = self.bpm
        if self.sections:
            result["sections"] = [s.as_dict() for s in self.sections]
        return result


@dataclass
class ColorPalette:
    """A named set of colors for a show's vibe."""

    name: str
    colors: list[str]
    description: str

    def __post_init__(self) -> None:
        if not self.colors:
            raise ValueError("Color palette must have at least one color")

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "colors": list(self.colors),
            "description": self.description,
        }


@dataclass
class Vibe:
    """AI-generated creative direction for a show."""

    palette: ColorPalette
    intensity_curve: str
    movement_style: str
    beam_style: str | None = None
    mood_keywords: list[str] = field(default_factory=list)
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "palette": self.palette.as_dict(),
            "intensity_curve": self.intensity_curve,
            "movement_style": self.movement_style,
        }
        if self.beam_style is not None:
            result["beam_style"] = self.beam_style
        if self.mood_keywords:
            result["mood_keywords"] = list(self.mood_keywords)
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class Cue:
    """A single lighting state at a specific point in the song."""

    number: int
    label: str
    section: str
    timestamp: float
    preset: str | None = None
    channels: str | None = None
    attributes: dict[str, str] = field(default_factory=dict)
    fade_time: float = 0.0
    follow_time: float | None = None
    notes: str | None = None

    def __post_init__(self) -> None:
        if self.number <= 0:
            raise ValueError(f"Cue number must be > 0, got {self.number}")
        if self.timestamp < 0:
            raise ValueError(f"Cue timestamp must be >= 0, got {self.timestamp}")
        if self.fade_time < 0:
            raise ValueError(f"Fade time must be >= 0, got {self.fade_time}")

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "number": self.number,
            "label": self.label,
            "section": self.section,
            "timestamp": self.timestamp,
        }
        if self.preset is not None:
            result["preset"] = self.preset
        if self.channels is not None:
            result["channels"] = self.channels
        if self.attributes:
            result["attributes"] = dict(self.attributes)
        if self.fade_time != 0.0:
            result["fade_time"] = self.fade_time
        if self.follow_time is not None:
            result["follow_time"] = self.follow_time
        if self.notes is not None:
            result["notes"] = self.notes
        return result


@dataclass
class Show:
    """The complete artifact — a rig applied to a song with cues and optional vibe."""

    name: str
    rig_name: str
    song: Song
    vibe: Vibe | None = None
    cues: list[Cue] = field(default_factory=list)
    preset_overrides: dict[str, Preset] = field(default_factory=dict)
    notes: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Show name must not be empty")
        if not self.rig_name.strip():
            raise ValueError("Rig name must not be empty")
        cue_numbers = [c.number for c in self.cues]
        if len(cue_numbers) != len(set(cue_numbers)):
            raise ValueError("Cue numbers must be unique")

    def add_cue(self, cue: Cue) -> None:
        """Add a cue to the show."""
        for existing in self.cues:
            if existing.number == cue.number:
                raise ValueError(f"Cue number {cue.number} already exists")
        self.cues.append(cue)

    def get_cue(self, number: int) -> Cue | None:
        """Get a cue by number."""
        for cue in self.cues:
            if cue.number == number:
                return cue
        return None

    def cues_for_section(self, section_name: str) -> list[Cue]:
        """Return all cues in a given section."""
        return [c for c in self.cues if c.section == section_name]

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": self.name,
            "rig_name": self.rig_name,
            "song": self.song.as_dict(),
        }
        if self.vibe is not None:
            result["vibe"] = self.vibe.as_dict()
        if self.cues:
            result["cues"] = [c.as_dict() for c in self.cues]
        if self.preset_overrides:
            result["preset_overrides"] = {
                name: p.as_dict() for name, p in self.preset_overrides.items()
            }
        if self.notes is not None:
            result["notes"] = self.notes
        return result


def resolve_presets(rig: Rig, show: Show) -> dict[str, Preset]:
    """Resolve effective presets: rig presets merged with show overrides.

    Show overrides take precedence over rig presets with the same name.
    """
    merged = dict(rig.presets)
    merged.update(show.preset_overrides)
    return merged
