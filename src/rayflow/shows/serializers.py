"""YAML serialization for rigs and shows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from rayflow.shows.models import (
    ColorPalette,
    Cue,
    FixtureSlot,
    Position3D,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
    Vibe,
)


def _position_from_dict(data: dict[str, Any]) -> Position3D:
    return Position3D(
        x=data.get("x", 0.0),
        y=data.get("y", 0.0),
        z=data.get("z", 0.0),
        pan=data.get("pan", 0.0),
        tilt=data.get("tilt", 0.0),
    )


def _venue_from_dict(data: dict[str, Any]) -> Venue:
    dims = data.get("dimensions", [0, 0, 0])
    return Venue(
        name=data["name"],
        dimensions=(float(dims[0]), float(dims[1]), float(dims[2])),
        notes=data.get("notes"),
    )


def _preset_from_dict(data: dict[str, Any]) -> Preset:
    return Preset(
        name=data["name"],
        description=data["description"],
        attributes=data.get("attributes", {}),
        channels=data.get("channels"),
        tags=data.get("tags", []),
    )


def _fixture_slot_from_dict(data: dict[str, Any]) -> FixtureSlot:
    pos_data = data.get("position", {})
    return FixtureSlot(
        fixture_name=data["fixture_name"],
        mode=data["mode"],
        label=data["label"],
        universe=data["universe"],
        start_address=data["start_address"],
        position=_position_from_dict(pos_data),
        channels=data.get("channels"),
    )


def _rig_from_dict(data: dict[str, Any]) -> Rig:
    venue = _venue_from_dict(data["venue"])
    fixtures = [_fixture_slot_from_dict(f) for f in data.get("fixtures", [])]
    presets = {
        name: _preset_from_dict(p) for name, p in data.get("presets", {}).items()
    }
    return Rig(
        name=data["name"],
        venue=venue,
        fixtures=fixtures,
        presets=presets,
        template=bool(data.get("template", False)),
        notes=data.get("notes"),
    )


def _section_from_dict(data: dict[str, Any]) -> Section:
    return Section(
        name=data["name"],
        start=data["start"],
        end=data["end"],
        energy=data.get("energy"),
        mood=data.get("mood"),
    )


def _song_from_dict(data: dict[str, Any]) -> Song:
    sections = [_section_from_dict(s) for s in data.get("sections", [])]
    return Song(
        title=data["title"],
        artist=data["artist"],
        duration=data["duration"],
        bpm=data.get("bpm"),
        sections=sections,
    )


def _color_palette_from_dict(data: dict[str, Any]) -> ColorPalette:
    return ColorPalette(
        name=data["name"],
        colors=data.get("colors", []),
        description=data.get("description", ""),
    )


def _vibe_from_dict(data: dict[str, Any]) -> Vibe:
    return Vibe(
        palette=_color_palette_from_dict(data["palette"]),
        intensity_curve=data["intensity_curve"],
        movement_style=data["movement_style"],
        beam_style=data.get("beam_style"),
        mood_keywords=data.get("mood_keywords", []),
        description=data.get("description", ""),
    )


def _cue_from_dict(data: dict[str, Any]) -> Cue:
    return Cue(
        number=data["number"],
        label=data["label"],
        section=data["section"],
        timestamp=data["timestamp"],
        preset=data.get("preset"),
        channels=data.get("channels"),
        attributes=data.get("attributes", {}),
        fade_time=data.get("fade_time", 0.0),
        follow_time=data.get("follow_time"),
        notes=data.get("notes"),
    )


def _show_from_dict(data: dict[str, Any]) -> Show:
    song = _song_from_dict(data["song"])
    vibe = _vibe_from_dict(data["vibe"]) if "vibe" in data else None
    cues = [_cue_from_dict(c) for c in data.get("cues", [])]
    preset_overrides = {
        name: _preset_from_dict(p)
        for name, p in data.get("preset_overrides", {}).items()
    }
    return Show(
        name=data["name"],
        rig_name=data["rig_name"],
        song=song,
        vibe=vibe,
        cues=cues,
        preset_overrides=preset_overrides,
        notes=data.get("notes"),
    )


def _represent_tuple(dumper: yaml.Dumper, data: tuple) -> yaml.Node:
    return dumper.represent_list(list(data))


yaml.add_representer(tuple, _represent_tuple)


def save_rig(rig: Rig, path: str | Path) -> Path:
    """Serialize a rig to YAML."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = rig.as_dict()
    text = yaml.dump(data, default_flow_style=False, sort_keys=False)
    target.write_text(text, encoding="utf-8")
    return target


def load_rig(path: str | Path) -> Rig:
    """Load a rig from YAML."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return _rig_from_dict(data)


def save_show(show: Show, path: str | Path) -> Path:
    """Serialize a show to YAML."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    data = show.as_dict()
    text = yaml.dump(data, default_flow_style=False, sort_keys=False)
    target.write_text(text, encoding="utf-8")
    return target


def load_show(path: str | Path) -> Show:
    """Load a show from YAML."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return _show_from_dict(data)
