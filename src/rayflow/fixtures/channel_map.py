"""DMX channel mapping for parsed GDTF fixture modes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rayflow.fixtures.parser import DmxModeSummary, FixtureSummary, GdtfParser


@dataclass(frozen=True)
class ChannelMapEntry:
    """A concrete DMX address for one GDTF channel."""

    dmx_address: int
    relative_channel: int
    attribute: str
    normalized_attribute: str
    family: str
    geometry: str | None
    break_number: int | str | None
    default: int | float | None
    highlight: int | float | None
    resolution: int
    fixture_name: str
    mode_name: str
    universe: int

    def as_dict(self) -> dict[str, Any]:
        """Return a CLI/docs-friendly dictionary representation."""
        return {
            "dmx_address": self.dmx_address,
            "relative_channel": self.relative_channel,
            "attribute": self.attribute,
            "normalized_attribute": self.normalized_attribute,
            "family": self.family,
            "geometry": self.geometry,
            "break": self.break_number,
            "default": self.default,
            "highlight": self.highlight,
            "resolution": self.resolution,
            "fixture_name": self.fixture_name,
            "mode_name": self.mode_name,
            "universe": self.universe,
        }


@dataclass(frozen=True)
class ChannelMap:
    """Ordered DMX channel map for a fixture mode at a start address."""

    fixture_name: str
    mode_name: str
    start_address: int
    universe: int
    entries: list[ChannelMapEntry]

    @property
    def channel_count(self) -> int:
        return len(self.entries)

    @property
    def end_address(self) -> int:
        if not self.entries:
            return self.start_address - 1
        return self.entries[-1].dmx_address

    def as_dicts(self) -> list[dict[str, Any]]:
        """Return entries as serializable dictionaries."""
        return [entry.as_dict() for entry in self.entries]


def normalize_attribute(attribute: str) -> str:
    """Normalize an attribute for family classification."""
    return attribute.lstrip("+")


def classify_attribute(attribute: str) -> str:
    """Classify a GDTF channel attribute into a pragmatic lookup family."""
    normalized = normalize_attribute(attribute).lower()

    if "gobo" in normalized:
        return "gobo"
    if "zoom" in normalized:
        return "zoom"
    if "focus" in normalized:
        return "focus"
    if "shutter" in normalized or "strobe" in normalized:
        return "shutter"
    if (
        normalized.startswith("pan")
        or normalized.startswith("tilt")
        or "position" in normalized
    ):
        return "position"
    if "dimmer" in normalized or "intensity" in normalized:
        return "dimmer"
    if (
        normalized.startswith(("color", "colour", "cto", "ctb"))
        or "color" in normalized
        or "colour" in normalized
    ):
        return "color"
    if any(
        token in normalized
        for token in (
            "control",
            "reset",
            "lamp",
            "fan",
            "mode",
            "speed",
            "macro",
            "effect",
        )
    ):
        return "control"
    return "other"


def build_channel_map(
    fixture: GdtfParser | FixtureSummary,
    *,
    mode_index: int = 0,
    mode_name: str | None = None,
    start_address: int = 1,
    universe: int = 0,
) -> ChannelMap:
    """Build a concrete DMX channel map for a parsed GDTF mode."""
    if start_address < 1 or start_address > 512:
        raise ValueError("DMX start_address must be in the range 1..512")

    resolved_mode_index = _resolve_mode_index(fixture, mode_index, mode_name)
    mode = _mode_summary(fixture, resolved_mode_index)
    fixture_name = _fixture_name(fixture)

    end_address = start_address + mode.channel_count - 1
    if end_address > 512:
        raise ValueError(
            "DMX channel map exceeds universe bounds: "
            f"start_address={start_address}, channel_count={mode.channel_count}, "
            f"end_address={end_address}"
        )

    entries = [
        _entry_from_channel(
            channel,
            fixture_name=fixture_name,
            mode_name=mode.name,
            start_address=start_address,
            universe=universe,
        )
        for channel in sorted(mode.channels, key=lambda item: int(item["dmx"]))
    ]
    return ChannelMap(
        fixture_name=fixture_name,
        mode_name=mode.name,
        start_address=start_address,
        universe=universe,
        entries=entries,
    )


def _resolve_mode_index(
    fixture: GdtfParser | FixtureSummary, mode_index: int, mode_name: str | None
) -> int:
    if mode_name is None:
        return mode_index

    mode_names = _mode_names(fixture)
    try:
        return mode_names.index(mode_name)
    except ValueError as exc:
        raise ValueError(f"DMX mode not found: {mode_name}") from exc


def _mode_names(fixture: GdtfParser | FixtureSummary) -> list[str]:
    if hasattr(fixture, "mode_names"):
        return fixture.mode_names()
    return [mode.name for mode in fixture.modes]


def _mode_summary(
    fixture: GdtfParser | FixtureSummary, mode_index: int
) -> DmxModeSummary:
    if hasattr(fixture, "get_mode_summary"):
        return fixture.get_mode_summary(mode_index)

    if mode_index < 0 or mode_index >= fixture.mode_count:
        raise IndexError(
            f"DMX mode index {mode_index} out of range for {fixture.mode_count} modes"
        )
    return fixture.modes[mode_index]


def _fixture_name(fixture: GdtfParser | FixtureSummary) -> str:
    return fixture.name


def _entry_from_channel(
    channel: dict[str, Any],
    *,
    fixture_name: str,
    mode_name: str,
    start_address: int,
    universe: int,
) -> ChannelMapEntry:
    relative_channel = int(channel["dmx"])
    attribute = str(channel.get("attribute") or "")
    normalized_attribute = normalize_attribute(attribute)
    return ChannelMapEntry(
        dmx_address=start_address + relative_channel - 1,
        relative_channel=relative_channel,
        attribute=attribute,
        normalized_attribute=normalized_attribute,
        family=classify_attribute(attribute),
        geometry=_optional_string(channel.get("geometry")),
        break_number=channel.get("break"),
        default=channel.get("default"),
        highlight=channel.get("highlight"),
        resolution=_channel_resolution(channel),
        fixture_name=fixture_name,
        mode_name=mode_name,
        universe=universe,
    )


def _channel_resolution(channel: dict[str, Any]) -> int:
    offset = channel.get("offset")
    if isinstance(offset, list):
        return max(1, len(offset))
    if offset is None:
        return 1
    return 1


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
