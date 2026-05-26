"""QLC+ fixture definition (.qxf) export from parsed GDTF profiles."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from rayflow.engine.fixtures.parser import GdtfParser

QXF_CREATOR_VERSION = "4.12.4"


@dataclass(frozen=True)
class QxfExportResult:
    """Generated QLC+ fixture definition file."""

    manufacturer: str
    model: str
    path: Path
    modes: list[str]
    channel_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "manufacturer": self.manufacturer,
            "model": self.model,
            "path": str(self.path),
            "modes": self.modes,
            "channel_count": self.channel_count,
        }


def qxf_filename_for_fixture(parser: GdtfParser) -> str:
    """Return a stable QXF filename for a fixture parser."""
    manufacturer = _filename_part(parser.manufacturer or "Unknown")
    model = _filename_part(parser.name or parser.path.stem)
    return f"{manufacturer}-{model}.qxf"


def build_qlcplus_fixture_definition(parser: GdtfParser) -> ET.Element:
    """Build a QLC+ FixtureDefinition XML element from a GDTF parser.

    This first-pass translator preserves manufacturer/model, modes, channels,
    GDTF attributes, and pragmatic channel groups. It intentionally avoids
    inventing QLC+ capability ranges that are not present in the GDTF summary.
    """
    root = ET.Element("FixtureDefinition")
    root.set("xmlns", "http://www.qlcplus.org/FixtureDefinition")

    _add_creator(root)
    ET.SubElement(root, "Manufacturer").text = parser.manufacturer
    ET.SubElement(root, "Model").text = parser.name
    ET.SubElement(root, "Type").text = (
        "Moving Head" if _has_movement(parser) else "Other"
    )

    channel_names_by_mode = _add_channels(root, parser)
    for mode_index, mode_name in enumerate(parser.mode_names()):
        _add_mode(
            root, parser, mode_index, mode_name, channel_names_by_mode[mode_index]
        )

    return root


def export_qlcplus_fixture_definition(
    parser: GdtfParser,
    output_dir: str | Path,
) -> QxfExportResult:
    """Write one QLC+ fixture definition file and return export metadata."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / qxf_filename_for_fixture(parser)

    root = build_qlcplus_fixture_definition(parser)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    with output_path.open("wb") as fh:
        fh.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write(b"<!DOCTYPE FixtureDefinition>\n")
        tree.write(fh, encoding="UTF-8", xml_declaration=False)

    return QxfExportResult(
        manufacturer=parser.manufacturer,
        model=parser.name,
        path=output_path,
        modes=parser.mode_names(),
        channel_count=max(
            (parser.get_channel_count(i) for i in range(parser.mode_count)),
            default=0,
        ),
    )


def export_qlcplus_fixture_definitions(
    parsers: list[GdtfParser],
    output_dir: str | Path,
) -> list[QxfExportResult]:
    """Write unique QXF files for a list of GDTF parsers."""
    seen: set[tuple[str, str]] = set()
    results: list[QxfExportResult] = []
    for parser in parsers:
        key = (parser.manufacturer, parser.name)
        if key in seen:
            continue
        seen.add(key)
        results.append(export_qlcplus_fixture_definition(parser, output_dir))
    return results


def _add_creator(root: ET.Element) -> None:
    creator = ET.SubElement(root, "Creator")
    ET.SubElement(creator, "Name").text = "RayFlow"
    ET.SubElement(creator, "Version").text = QXF_CREATOR_VERSION
    ET.SubElement(creator, "Author").text = "RayFlow"


def _add_channels(root: ET.Element, parser: GdtfParser) -> dict[int, list[str]]:
    channel_names_by_mode: dict[int, list[str]] = {}
    emitted: set[str] = set()
    for mode_index in range(parser.mode_count):
        channels = parser.get_channel_map(mode_index=mode_index).entries
        channel_names: list[str] = []
        mode_names: set[str] = set()
        for entry in channels:
            name = _channel_name(
                entry.attribute,
                entry.normalized_attribute,
                entry.relative_channel,
                used_in_mode=mode_names,
            )
            mode_names.add(name)
            channel_names.append(name)
            if name in emitted:
                continue
            emitted.add(name)
            channel_el = ET.SubElement(root, "Channel")
            channel_el.set("Name", name)
            channel_el.set(
                "Preset", _preset_for_entry(entry.normalized_attribute, entry.family)
            )
            group_el = ET.SubElement(channel_el, "Group")
            group_el.set("Byte", "0")
            group_el.text = _group_for_family(entry.family)
            capability = ET.SubElement(channel_el, "Capability")
            capability.set("Min", "0")
            capability.set("Max", "255")
            capability.text = _capability_label(entry.family, 0)
        channel_names_by_mode[mode_index] = channel_names
    return channel_names_by_mode


def _add_mode(
    root: ET.Element,
    parser: GdtfParser,
    mode_index: int,
    mode_name: str,
    channel_names: list[str],
) -> None:
    mode_el = ET.SubElement(root, "Mode")
    mode_el.set("Name", mode_name)

    for index, channel_name in enumerate(channel_names):
        channel_el = ET.SubElement(mode_el, "Channel")
        channel_el.set("Number", str(index))
        channel_el.text = channel_name


def _has_movement(parser: GdtfParser) -> bool:
    for mode_index in range(parser.mode_count):
        if any(
            entry.family == "position"
            for entry in parser.get_channel_map(mode_index=mode_index).entries
        ):
            return True
    return False


def _preset_for_entry(attribute: str, family: str) -> str:
    normalized = attribute.lower()
    if normalized.endswith("_r") or normalized.endswith("red"):
        return "IntensityRed"
    if normalized.endswith("_g") or normalized.endswith("green"):
        return "IntensityGreen"
    if normalized.endswith("_b") or normalized.endswith("blue"):
        return "IntensityBlue"
    if normalized.endswith("_w") or normalized.endswith("white"):
        return "IntensityWhite"
    return {
        "dimmer": "IntensityDimmer",
        "color": "Intensity",
        "position": "PositionPan" if "pan" in normalized else "PositionTilt",
        "gobo": "Gobo",
        "shutter": "Shutter",
        "zoom": "Beam",
        "focus": "Beam",
        "control": "Maintenance",
    }.get(family, "Generic")


def _group_for_family(family: str) -> str:
    return {
        "dimmer": "Intensity",
        "color": "Colour",
        "position": "Pan/Tilt",
        "gobo": "Gobo",
        "shutter": "Shutter",
        "zoom": "Beam",
        "focus": "Beam",
        "control": "Control",
    }.get(family, "Generic")


def _capability_label(family: str, index: int) -> str:
    labels = {
        "dimmer": "Intensity range",
        "color": "Color component",
        "position": "Pan/tilt range",
        "gobo": "Gobo selection",
        "shutter": "Shutter/strobe range",
        "zoom": "Zoom range",
        "focus": "Focus range",
        "control": "Control range",
    }
    base = labels.get(family, "DMX range")
    return base if index == 0 else f"{base} {index + 1}"


def _channel_name(
    raw_attribute: str,
    normalized_attribute: str,
    relative_channel: int,
    *,
    used_in_mode: set[str],
) -> str:
    base = normalized_attribute or f"Channel {relative_channel}"
    if raw_attribute.startswith("+"):
        base = f"{base} Fine"
    if base not in used_in_mode:
        return base
    candidate = f"{base} Ch {relative_channel}"
    suffix = 2
    while candidate in used_in_mode:
        candidate = f"{base} Ch {relative_channel}.{suffix}"
        suffix += 1
    return candidate


def _filename_part(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9]+", "-", value.strip())
    return value.strip("-") or "Fixture"
