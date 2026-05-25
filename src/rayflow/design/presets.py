"""Preset attribute families and validation helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from rayflow.engine.fixtures.parser import GdtfParser

ATTRIBUTE_FAMILIES: frozenset[str] = frozenset(
    {
        "dimmer",
        "position",
        "color",
        "beam",
        "focus",
        "gobo",
    }
)

POSITION_SUB_ATTRIBUTES: frozenset[str] = frozenset({"pan", "tilt"})
BEAM_SUB_ATTRIBUTES: frozenset[str] = frozenset(
    {"zoom", "iris", "frost", "strobe", "shutter"}
)


def validate_preset_attributes(attributes: dict[str, str]) -> list[str]:
    """Validate preset attribute keys against known families.

    Returns a list of validation errors (empty if valid).
    """
    errors: list[str] = []
    valid = sorted(ATTRIBUTE_FAMILIES)
    for key in attributes:
        if key not in ATTRIBUTE_FAMILIES:
            errors.append(f"Unknown attribute family: '{key}'. Valid: {valid}")
    return errors


def fixture_supports_attribute(
    parser: GdtfParser, mode_index: int, attribute: str
) -> bool:
    """Check if a fixture in a given mode supports an attribute family.

    Maps attribute families to GDTF physical attribute names.
    """
    try:
        parser.get_mode(mode_index)
    except (IndexError, AttributeError):
        return False

    mode_channels = parser.get_channels_as_dict(mode_index)
    channel_attributes = {
        ch.get("attribute") for ch in mode_channels if ch.get("attribute")
    }

    attribute_mapping: dict[str, set[str]] = {
        "dimmer": {"Dimmer", "Intensity"},
        "position": {"Pan", "Tilt"},
        "color": {
            "ColorWheel",
            "ColorRGB",
            "ColorAdd",
            "ColorSub",
            "ColorTemperature",
            "CTO",
            "CTB",
        },
        "beam": {"Zoom", "Iris", "Frost", "Shutter", "Strobe"},
        "focus": {"Focus"},
        "gobo": {"GoboWheel", "Gobo", "GoboRotation", "GoboIndex"},
    }

    expected = attribute_mapping.get(attribute, set())
    return bool(channel_attributes & expected)


def validate_preset_against_fixture(
    attributes: dict[str, str],
    parser: GdtfParser,
    mode_index: int = 0,
) -> list[str]:
    """Validate preset attributes against a fixture's capabilities.

    Returns a list of validation errors (empty if all supported).
    """
    errors: list[str] = []
    for attr in attributes:
        if not fixture_supports_attribute(parser, mode_index, attr):
            errors.append(
                f"Fixture '{parser.name}' mode {mode_index} "
                f"does not support attribute '{attr}'"
            )
    return errors
