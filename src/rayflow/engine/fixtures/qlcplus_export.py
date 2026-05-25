"""QLC+ workspace (.qxw) exporter.

Generates a QLC+ workspace XML file from a RayFlow rig configuration.
The exported file can be loaded directly into QLC+ to configure universes
and patch all fixtures in one step.

QLC+ workspace format reference:
- Root element: <Workspace>
- <Creator> metadata block
- <Engine> containing <InputOutputMap> (universes) and <Fixture> entries
- Universe and Address are 0-based in QLC+ (RayFlow uses 0-based universes,
  1-based addresses)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

# QLC+ workspace format version
QXW_VERSION = "4.12.4"
QXW_ENGINE_VERSION = "2"

# Universe limit for the InputOutputMap
_MAX_UNIVERSES = 4


@dataclass(frozen=True)
class QlcFixturePatch:
    """Patch data for a single fixture in a QLC+ workspace."""

    fixture_id: int
    name: str
    manufacturer: str
    model: str
    mode: str
    universe: int
    address: int  # 1-based (RayFlow convention)
    channel_count: int

    @property
    def qlc_address(self) -> int:
        """QLC+ uses 0-based addresses."""
        return self.address - 1

    @property
    def qlc_universe(self) -> int:
        """QLC+ uses 0-based universes."""
        return self.universe

    def as_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "mode": self.mode,
            "universe": self.universe,
            "address": self.address,
            "channel_count": self.channel_count,
        }


def build_qlcplus_workspace(
    patches: list[QlcFixturePatch],
    *,
    author: str = "RayFlow",
) -> ET.Element:
    """Build a QLC+ workspace XML element tree.

    Args:
        patches: List of QlcFixturePatch objects representing patched fixtures.
        author: Author name to embed in the workspace Creator block.

    Returns:
        The root XML element of the workspace.
    """
    root = ET.Element("Workspace")
    root.set("xmlns", "http://www.qlcplus.org/Workspace")
    root.set("CurrentWindow", "FixtureManager")

    _add_creator(root, author=author)
    engine = ET.SubElement(root, "Engine")
    _add_input_output_map(engine, patches)

    for patch in patches:
        _add_fixture(engine, patch)

    return root


def export_qlcplus_workspace(
    patches: list[QlcFixturePatch],
    output_path: str | Path,
    *,
    author: str = "RayFlow",
) -> Path:
    """Export a QLC+ workspace file (.qxw) from a fixture patch list.

    Args:
        patches: List of QlcFixturePatch objects representing patched fixtures.
        output_path: Destination path for the .qxw file.
        author: Author name embedded in the workspace Creator block.

    Returns:
        The resolved output path.
    """
    output_path = Path(output_path)
    root = build_qlcplus_workspace(patches, author=author)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")

    with output_path.open("wb") as fh:
        fh.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write(b"<!DOCTYPE Workspace>\n")
        tree.write(fh, encoding="UTF-8", xml_declaration=False)

    return output_path


def build_qlc_patch(
    *,
    fixture_id: int,
    name: str,
    manufacturer: str,
    model: str,
    mode: str,
    universe: int,
    address: int,
    channel_count: int,
) -> QlcFixturePatch:
    """Convenience constructor for a QlcFixturePatch."""
    return QlcFixturePatch(
        fixture_id=fixture_id,
        name=name,
        manufacturer=manufacturer,
        model=model,
        mode=mode,
        universe=universe,
        address=address,
        channel_count=channel_count,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _add_creator(root: ET.Element, *, author: str) -> None:
    creator = ET.SubElement(root, "Creator")
    ET.SubElement(creator, "Name").text = "Q Light Controller Plus"
    ET.SubElement(creator, "Version").text = QXW_VERSION
    ET.SubElement(creator, "Author").text = author


def _add_input_output_map(engine: ET.Element, patches: list[QlcFixturePatch]) -> None:
    """Add the InputOutputMap section with universe entries.

    QLC+ requires at least the universes that are in use to be declared here,
    otherwise imported fixtures may not map correctly.
    """
    universes_used = sorted({p.qlc_universe for p in patches})
    io_map = ET.SubElement(engine, "InputOutputMap")

    for uni_idx in universes_used:
        universe = ET.SubElement(io_map, "Universe")
        universe.set("ID", str(uni_idx))
        universe.set("Name", f"Universe {uni_idx + 1}")


def _add_fixture(engine: ET.Element, patch: QlcFixturePatch) -> None:
    """Add a single Fixture element to the Engine block."""
    fixture = ET.SubElement(engine, "Fixture")
    ET.SubElement(fixture, "Manufacturer").text = patch.manufacturer
    ET.SubElement(fixture, "Model").text = patch.model
    ET.SubElement(fixture, "Mode").text = patch.mode
    ET.SubElement(fixture, "Name").text = patch.name
    ET.SubElement(fixture, "Universe").text = str(patch.qlc_universe)
    ET.SubElement(fixture, "Address").text = str(patch.qlc_address)
    ET.SubElement(fixture, "ID").text = str(patch.fixture_id)
    ET.SubElement(fixture, "Channels").text = str(patch.channel_count)
