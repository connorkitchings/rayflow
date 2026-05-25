"""Fixture-aware DMX rendering."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from rayflow.design.models import Cue, FixtureSlot, Rig, Show, resolve_presets
from rayflow.engine.fixtures.channel_map import ChannelMap, ChannelMapEntry
from rayflow.engine.fixtures.library import FixtureLibrary

NAMED_COLORS: dict[str, tuple[int, int, int]] = {
    "warm amber": (255, 153, 51),
    "amber": (255, 153, 51),
    "blue": (51, 102, 255),
    "cyan": (0, 204, 255),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "white": (255, 255, 255),
}

POSITION_ATTRIBUTES = {
    "pan": "Pan",
    "position.pan": "Pan",
    "tilt": "Tilt",
    "position.tilt": "Tilt",
}
NUMERIC_FAMILIES = frozenset({"zoom", "focus", "shutter", "gobo"})


@dataclass(frozen=True)
class DmxFrame:
    """Sparse DMX channel values for one universe."""

    universe: int
    channels: dict[int, int] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "universe": self.universe,
            "channels": dict(sorted(self.channels.items())),
        }


@dataclass(frozen=True)
class DmxRenderWarning:
    """Non-fatal renderer warning."""

    cue: int
    fixture: str | None
    attribute: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "cue": self.cue,
            "fixture": self.fixture,
            "attribute": self.attribute,
            "message": self.message,
        }


@dataclass(frozen=True)
class RenderedCue:
    """Dry-run DMX render result for one cue."""

    cue_number: int
    cue_label: str
    section: str
    timestamp: float
    frames: list[DmxFrame] = field(default_factory=list)
    warnings: list[DmxRenderWarning] = field(default_factory=list)
    rendered_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "cue": {
                "number": self.cue_number,
                "label": self.cue_label,
                "section": self.section,
                "timestamp": self.timestamp,
            },
            "frames": [frame.as_dict() for frame in self.frames],
            "warnings": [warning.as_dict() for warning in self.warnings],
            "rendered_at": self.rendered_at,
        }


@dataclass(frozen=True)
class RenderedCueGroup:
    """Ordered render results for a section or complete show."""

    scope: str
    rendered_cues: list[RenderedCue]
    rendered_at: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "cues": [cue.as_dict() for cue in self.rendered_cues],
            "rendered_at": self.rendered_at,
        }


def render_cue_to_dmx(
    show: Show,
    rig: Rig,
    cue: Cue,
    fixture_dir: str | Path = "data/fixtures/samples",
) -> RenderedCue:
    """Render one RayFlow cue to sparse DMX universe frames."""
    library = FixtureLibrary(fixture_dir)
    warnings: list[DmxRenderWarning] = []
    try:
        library.load()
    except (FileNotFoundError, ValueError) as exc:
        return _result(
            cue,
            frames=[],
            warnings=[
                DmxRenderWarning(
                    cue=cue.number,
                    fixture=None,
                    attribute="fixture",
                    message=str(exc),
                )
            ],
        )

    attributes = _effective_attributes(show, rig, cue)
    target_channels = _effective_channels(show, rig, cue)
    target_slots = _target_fixture_slots(rig, target_channels)
    frame_values: dict[int, dict[int, int]] = {}

    for slot in target_slots:
        parser = library.get(slot.fixture_name)
        if parser is None:
            warnings.append(
                DmxRenderWarning(
                    cue=cue.number,
                    fixture=slot.label,
                    attribute="fixture",
                    message=f"Fixture profile not found: {slot.fixture_name}",
                )
            )
            continue

        try:
            channel_map = parser.get_channel_map(
                mode_name=slot.mode,
                start_address=slot.start_address,
                universe=slot.universe,
            )
        except (IndexError, ValueError) as exc:
            warnings.append(
                DmxRenderWarning(
                    cue=cue.number,
                    fixture=slot.label,
                    attribute="mode",
                    message=str(exc),
                )
            )
            continue

        slot_values, slot_warnings = _render_fixture_attributes(
            show=show,
            cue=cue,
            slot=slot,
            channel_map=channel_map,
            attributes=attributes,
        )
        warnings.extend(slot_warnings)
        if slot_values:
            universe_values = frame_values.setdefault(slot.universe, {})
            universe_values.update(slot_values)

    frames = [
        DmxFrame(universe=universe, channels=channels)
        for universe, channels in sorted(frame_values.items())
    ]
    return _result(cue, frames=frames, warnings=warnings)


def render_section_to_dmx(
    show: Show,
    rig: Rig,
    section_name: str,
    fixture_dir: str | Path = "data/fixtures/samples",
) -> RenderedCueGroup:
    """Render all cues in one section in stable cue order."""
    cues = sorted(
        show.cues_for_section(section_name), key=lambda c: (c.timestamp, c.number)
    )
    return RenderedCueGroup(
        scope=f"section:{section_name}",
        rendered_cues=[
            render_cue_to_dmx(show, rig, cue, fixture_dir=fixture_dir) for cue in cues
        ],
    )


def render_show_to_dmx(
    show: Show,
    rig: Rig,
    fixture_dir: str | Path = "data/fixtures/samples",
) -> RenderedCueGroup:
    """Render all show cues in stable cue order."""
    cues = sorted(show.cues, key=lambda c: (c.timestamp, c.number))
    return RenderedCueGroup(
        scope=f"show:{show.name}",
        rendered_cues=[
            render_cue_to_dmx(show, rig, cue, fixture_dir=fixture_dir) for cue in cues
        ],
    )


def _result(
    cue: Cue, *, frames: list[DmxFrame], warnings: list[DmxRenderWarning]
) -> RenderedCue:
    return RenderedCue(
        cue_number=cue.number,
        cue_label=cue.label,
        section=cue.section,
        timestamp=cue.timestamp,
        frames=frames,
        warnings=warnings,
    )


def _effective_attributes(show: Show, rig: Rig, cue: Cue) -> dict[str, str]:
    attributes: dict[str, str] = {}
    if cue.preset:
        preset = resolve_presets(rig, show).get(cue.preset)
        if preset is not None:
            attributes.update(preset.attributes)
    attributes.update(cue.attributes)
    return attributes


def _effective_channels(show: Show, rig: Rig, cue: Cue) -> str | None:
    if cue.channels:
        return cue.channels
    if cue.preset:
        preset = resolve_presets(rig, show).get(cue.preset)
        if preset is not None:
            return preset.channels
    return None


def _target_fixture_slots(rig: Rig, channels: str | None) -> list[FixtureSlot]:
    if not channels:
        return list(rig.fixtures)

    selected = _parse_channel_selector(channels)
    if selected is None:
        return list(rig.fixtures)

    return [
        slot
        for slot in rig.fixtures
        if slot.channels is not None and _slot_channel_number(slot.channels) in selected
    ]


def _parse_channel_selector(selector: str) -> set[int] | None:
    normalized = selector.replace(",", " ")
    parts = normalized.split()
    if not parts:
        return None

    selected: set[int] = set()
    index = 0
    while index < len(parts):
        part = parts[index]
        if not part.isdigit():
            return None
        start = int(part)
        if index + 2 < len(parts) and parts[index + 1].lower() == "thru":
            end_part = parts[index + 2]
            if not end_part.isdigit():
                return None
            end = int(end_part)
            selected.update(range(min(start, end), max(start, end) + 1))
            index += 3
            continue
        selected.add(start)
        index += 1
    return selected


def _slot_channel_number(channels: str) -> int | None:
    parts = channels.split()
    if len(parts) != 1 or not parts[0].isdigit():
        return None
    return int(parts[0])


def _render_fixture_attributes(
    *,
    show: Show,
    cue: Cue,
    slot: FixtureSlot,
    channel_map: ChannelMap,
    attributes: dict[str, str],
) -> tuple[dict[int, int], list[DmxRenderWarning]]:
    values: dict[int, int] = {}
    warnings: list[DmxRenderWarning] = []

    # Copy attributes to avoid mutating the original dictionary
    attrs = dict(attributes)

    # Process movement attributes if movement.type is present
    if "movement.type" in attrs:
        m_type = attrs.get("movement.type", "static").strip().lower()
        if m_type == "static":
            center_str = attrs.get("movement.center", "50,50")
            try:
                parts = [float(p.strip()) for p in center_str.split(",") if p.strip()]
                if len(parts) >= 2:
                    attrs["pan"] = f"{parts[0]}%"
                    attrs["tilt"] = f"{parts[1]}%"
                elif len(parts) == 1:
                    attrs["pan"] = f"{parts[0]}%"
                    attrs["tilt"] = f"{parts[0]}%"
            except ValueError:
                pass
        else:
            speed_str = attrs.get("movement.speed", "1.0").strip()
            try:
                speed = float(speed_str)
            except ValueError:
                speed = 1.0

            center_str = attrs.get("movement.center", "50,50")
            center_pan, center_tilt = 50.0, 50.0
            try:
                parts = [float(p.strip()) for p in center_str.split(",") if p.strip()]
                if len(parts) >= 2:
                    center_pan, center_tilt = parts[0], parts[1]
                elif len(parts) == 1:
                    center_pan, center_tilt = parts[0], parts[0]
            except ValueError:
                pass

            size_str = attrs.get("movement.size", "25")
            size_pan, size_tilt = 25.0, 25.0
            try:
                parts = [float(p.strip()) for p in size_str.split(",") if p.strip()]
                if len(parts) >= 2:
                    size_pan, size_tilt = parts[0], parts[1]
                elif len(parts) == 1:
                    size_pan, size_tilt = parts[0], parts[0]
            except ValueError:
                pass

            if show.song and show.song.bpm and show.song.bpm > 0:
                t = cue.timestamp * (show.song.bpm / 60.0)
            else:
                t = cue.timestamp

            phase = 2 * math.pi * speed * t

            if m_type == "sine":
                pan = center_pan + size_pan * math.sin(phase)
                tilt = center_tilt
            elif m_type == "circle":
                pan = center_pan + size_pan * math.cos(phase)
                tilt = center_tilt + size_tilt * math.sin(phase)
            elif m_type == "figure8":
                pan = center_pan + size_pan * math.sin(phase)
                tilt = center_tilt + size_tilt * math.sin(2 * phase)
            else:
                pan = center_pan
                tilt = center_tilt

            pan = max(0.0, min(100.0, pan))
            tilt = max(0.0, min(100.0, tilt))

            attrs["pan"] = f"{round(pan, 4)}%"
            attrs["tilt"] = f"{round(tilt, 4)}%"

    # Filter out movement.* attributes so they don't produce warnings
    renderable_attributes = {
        k: v for k, v in attrs.items() if not k.startswith("movement.")
    }

    for family, raw_value in renderable_attributes.items():
        if family == "dimmer":
            dimmer_value = _parse_dimmer_value(raw_value)
            if dimmer_value is None:
                warnings.append(
                    _warning(
                        cue,
                        slot,
                        family,
                        f"Unsupported dimmer value: {raw_value}",
                    )
                )
                continue
            entry = _first_entry_by_family(channel_map, "dimmer")
            if entry is None:
                warnings.append(_warning(cue, slot, family, "No dimmer channel found"))
                continue
            values.update(_channel_values(entry, dimmer_value, channel_map))
            continue

        if family == "color":
            rgb = _parse_color(raw_value)
            if rgb is None:
                warnings.append(
                    _warning(
                        cue,
                        slot,
                        family,
                        f"Unsupported color value for v1 renderer: {raw_value}",
                    )
                )
                continue
            color_values, color_warnings = _render_rgbw(
                cue=cue,
                slot=slot,
                channel_map=channel_map,
                rgb=rgb,
            )
            values.update(color_values)
            warnings.extend(color_warnings)
            continue

        if family.lower() in POSITION_ATTRIBUTES:
            position_values, position_warning = _render_named_numeric_attribute(
                cue=cue,
                slot=slot,
                channel_map=channel_map,
                family=family,
                attribute=POSITION_ATTRIBUTES[family.lower()],
                raw_value=raw_value,
            )
            values.update(position_values)
            if position_warning is not None:
                warnings.append(position_warning)
            continue

        if family == "gobo.speed":
            value = _parse_numeric_attribute_value(raw_value)
            if value is None:
                warnings.append(
                    _warning(
                        cue,
                        slot,
                        family,
                        f"Unsupported numeric value: {raw_value}",
                    )
                )
                continue
            entry = None
            for e in channel_map.entries:
                norm = e.normalized_attribute.lower()
                if "gobo" in norm and (
                    "speed" in norm
                    or "spin" in norm
                    or "rate" in norm
                    or "time" in norm
                ):
                    entry = e
                    break
            if entry is None:
                warnings.append(
                    _warning(cue, slot, family, "No gobo speed/spin channel found")
                )
                continue
            values.update(_channel_values(entry, value, channel_map))
            continue

        if family == "gobo.rotation":
            value = _parse_numeric_attribute_value(raw_value)
            if value is None:
                warnings.append(
                    _warning(
                        cue,
                        slot,
                        family,
                        f"Unsupported numeric value: {raw_value}",
                    )
                )
                continue
            entry = None
            for e in channel_map.entries:
                norm = e.normalized_attribute.lower()
                if "gobo" in norm and (
                    "rot" in norm or "pos" in norm or "index" in norm
                ):
                    entry = e
                    break
            if entry is None:
                warnings.append(
                    _warning(
                        cue, slot, family, "No gobo rotation/position channel found"
                    )
                )
                continue
            values.update(_channel_values(entry, value, channel_map))
            continue

        if family in NUMERIC_FAMILIES:
            family_values, family_warning = _render_family_numeric_attribute(
                cue=cue,
                slot=slot,
                channel_map=channel_map,
                family=family,
                raw_value=raw_value,
            )
            values.update(family_values)
            if family_warning is not None:
                warnings.append(family_warning)
            continue

        warnings.append(
            _warning(
                cue,
                slot,
                family,
                f"Unsupported attribute family for renderer: {family}",
            )
        )

    return values, warnings


def _render_named_numeric_attribute(
    *,
    cue: Cue,
    slot: FixtureSlot,
    channel_map: ChannelMap,
    family: str,
    attribute: str,
    raw_value: str,
) -> tuple[dict[int, int], DmxRenderWarning | None]:
    value = _parse_numeric_attribute_value(raw_value)
    if value is None:
        return {}, _warning(
            cue, slot, family, f"Unsupported numeric value: {raw_value}"
        )

    entry = _first_entry_by_attribute(channel_map, attribute)
    if entry is None:
        return {}, _warning(cue, slot, family, f"No {attribute} channel found")

    return _channel_values(entry, value, channel_map), None


def _render_family_numeric_attribute(
    *,
    cue: Cue,
    slot: FixtureSlot,
    channel_map: ChannelMap,
    family: str,
    raw_value: str,
) -> tuple[dict[int, int], DmxRenderWarning | None]:
    value = _parse_numeric_attribute_value(raw_value)
    if value is None:
        return {}, _warning(
            cue, slot, family, f"Unsupported numeric value: {raw_value}"
        )

    entry = _first_entry_by_family(channel_map, family)
    if entry is None:
        return {}, _warning(cue, slot, family, f"No {family} channel found")

    return _channel_values(entry, value, channel_map), None


def _parse_dimmer_value(raw_value: str) -> int | None:
    value = str(raw_value).strip().lower()
    if value == "full":
        return 255
    if value in {"off", "blackout"}:
        return 0
    if value.endswith("%"):
        value = value[:-1].strip()
    try:
        percent = float(value)
    except ValueError:
        return None
    if not 0 <= percent <= 100:
        return None
    return int(round(percent * 255 / 100))


def _parse_numeric_attribute_value(raw_value: str) -> int | None:
    value = str(raw_value).strip().lower()
    if value in {"full", "open"}:
        return 255
    if value in {"off", "closed", "blackout"}:
        return 0
    if value.endswith("%"):
        value = value[:-1].strip()
    try:
        percent = float(value)
    except ValueError:
        return None
    if not 0 <= percent <= 100:
        return None
    return int(round(percent * 255 / 100))


def _parse_hex_color(raw_value: str) -> tuple[int, int, int] | None:
    value = str(raw_value).strip()
    if len(value) != 7 or not value.startswith("#"):
        return None
    try:
        return (
            int(value[1:3], 16),
            int(value[3:5], 16),
            int(value[5:7], 16),
        )
    except ValueError:
        return None


def _render_rgbw(
    *,
    cue: Cue,
    slot: FixtureSlot,
    channel_map: ChannelMap,
    rgb: tuple[int, int, int],
) -> tuple[dict[int, int], list[DmxRenderWarning]]:
    values: dict[int, int] = {}
    warnings: list[DmxRenderWarning] = []
    components = {
        "ColorAdd_R": rgb[0],
        "ColorAdd_G": rgb[1],
        "ColorAdd_B": rgb[2],
    }

    for attribute, value in components.items():
        entry = _first_entry_by_attribute(channel_map, attribute)
        if entry is None:
            warnings.append(
                _warning(cue, slot, "color", f"No {attribute} channel found")
            )
            continue
        values.update(_channel_values(entry, value, channel_map))

    white_entry = _first_entry_by_attribute(channel_map, "ColorAdd_W")
    if white_entry is not None:
        values.update(_channel_values(white_entry, min(rgb), channel_map))

    if not values:
        warnings.append(_warning(cue, slot, "color", "No RGB/RGBW channels found"))
    return values, warnings


def _first_entry_by_family(
    channel_map: ChannelMap, family: str
) -> ChannelMapEntry | None:
    for entry in channel_map.entries:
        if entry.family == family and not entry.attribute.startswith("+"):
            return entry
    for entry in channel_map.entries:
        if entry.family == family:
            return entry
    return None


def _first_entry_by_attribute(
    channel_map: ChannelMap, attribute: str
) -> ChannelMapEntry | None:
    for entry in channel_map.entries:
        if entry.normalized_attribute == attribute and not entry.attribute.startswith(
            "+"
        ):
            return entry
    return None


def _channel_values(
    entry: ChannelMapEntry, value: int, channel_map: ChannelMap
) -> dict[int, int]:
    fine_entry = _fine_entry_for(entry, channel_map)
    if fine_entry is None:
        return {entry.dmx_address: value}
    sixteen_bit = value * 257
    return {
        entry.dmx_address: (sixteen_bit >> 8) & 0xFF,
        fine_entry.dmx_address: sixteen_bit & 0xFF,
    }


def _fine_entry_for(
    entry: ChannelMapEntry, channel_map: ChannelMap
) -> ChannelMapEntry | None:
    for candidate in channel_map.entries:
        if candidate.attribute != f"+{entry.normalized_attribute}":
            continue
        if candidate.dmx_address == entry.dmx_address:
            continue
        return candidate
    return None


def _parse_color(raw_value: str) -> tuple[int, int, int] | None:
    return _parse_hex_color(raw_value) or NAMED_COLORS.get(
        str(raw_value).strip().lower()
    )


def _warning(
    cue: Cue, slot: FixtureSlot, attribute: str, message: str
) -> DmxRenderWarning:
    return DmxRenderWarning(
        cue=cue.number,
        fixture=slot.label,
        attribute=attribute,
        message=message,
    )
