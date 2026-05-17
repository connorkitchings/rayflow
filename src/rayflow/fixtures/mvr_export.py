"""MVR (My Virtual Rig) export for grandMA3 import."""

from __future__ import annotations

import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

MVR_XML_FILENAME = "myvirtualrig.xml"
MVR_NS = "http://www.gdtf-share.com/MVR"


@dataclass(frozen=True)
class FixturePosition:
    """3D position and orientation for a fixture in the rig."""

    name: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    pan: float = 0.0
    tilt: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "pan": self.pan,
            "tilt": self.tilt,
        }


@dataclass(frozen=True)
class FixturePatchEntry:
    """Patch data for one fixture in an MVR scene."""

    name: str
    manufacturer: str
    fixture_type: str
    dmx_mode: str
    universe: int
    address: int
    gdtf_uuid: str
    position: FixturePosition
    gdtf_file: Path | None = None


def build_mvr_scene_element(
    patches: list[FixturePatchEntry],
    *,
    scene_name: str = "RayFlow Rig",
    layer_name: str = "Fixtures",
) -> ET.Element:
    """Build the MVR myvirtualrig.xml root element with fixture data."""
    ET.register_namespace("", MVR_NS)
    root = ET.Element(f"{{{MVR_NS}}}GeneralSceneDescription")
    root.set("captureStart", _now_iso())
    root.set("date", _today_date())
    root.set("versionMajor", "1")
    root.set("versionMinor", "8")

    _add_user_data(root)
    scene = ET.SubElement(root, f"{{{MVR_NS}}}Scene")
    scene.set("name", scene_name)
    layers = ET.SubElement(scene, f"{{{MVR_NS}}}Layers")
    layer = ET.SubElement(layers, f"{{{MVR_NS}}}Layer")
    layer.set("name", layer_name)
    child_list = ET.SubElement(layer, f"{{{MVR_NS}}}ChildList")

    for patch in patches:
        _add_fixture(child_list, patch)

    return root


def export_mvr(
    patches: list[FixturePatchEntry],
    output_path: str | Path,
    *,
    scene_name: str = "RayFlow Rig",
) -> Path:
    """Export a fixture patch list as an MVR file (.mvr)."""
    output_path = Path(output_path)
    root = build_mvr_scene_element(patches, scene_name=scene_name)
    xml_content = ET.tostring(root, encoding="unicode")

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(MVR_XML_FILENAME, xml_content)
        _embed_gdtf_files(archive, patches)

    return output_path


def build_patch_entry(
    *,
    name: str,
    manufacturer: str,
    fixture_type: str,
    dmx_mode: str,
    universe: int,
    address: int,
    gdtf_uuid: str | None = None,
    position: FixturePosition | None = None,
    gdtf_file: str | Path | None = None,
) -> FixturePatchEntry:
    """Build a FixturePatchEntry from fixture data."""
    if gdtf_uuid is None:
        gdtf_uuid = str(uuid.uuid4())
    if position is None:
        position = FixturePosition(name=name)
    resolved_file = Path(gdtf_file) if gdtf_file else None
    return FixturePatchEntry(
        name=name,
        manufacturer=manufacturer,
        fixture_type=fixture_type,
        dmx_mode=dmx_mode,
        universe=universe,
        address=address,
        gdtf_uuid=gdtf_uuid,
        position=position,
        gdtf_file=resolved_file,
    )


def _add_user_data(root: ET.Element) -> None:
    user_data = ET.SubElement(root, f"{{{MVR_NS}}}UserData")
    user_data.set("provider", "RayFlow")
    user_data.set("createdBy", "RayFlow mvr_export")


def _embed_gdtf_files(
    archive: zipfile.ZipFile, patches: list[FixturePatchEntry]
) -> None:
    written: set[str] = set()
    for patch in patches:
        if patch.gdtf_file and patch.gdtf_file.exists():
            gdtf_name = patch.gdtf_file.name
            if gdtf_name not in written:
                archive.write(patch.gdtf_file, gdtf_name)
                written.add(gdtf_name)


def _add_fixture(parent: ET.Element, patch: FixturePatchEntry) -> None:
    fixture = ET.SubElement(parent, f"{{{MVR_NS}}}Fixture")
    fixture.set("name", patch.name)
    if patch.gdtf_file and patch.gdtf_file.exists():
        fixture.set("gdtfSpec", patch.gdtf_file.name)
    else:
        fixture.set("gdtfSpec", patch.gdtf_uuid)
    if patch.dmx_mode:
        fixture.set("gdtfMode", patch.dmx_mode)

    _add_addressing(fixture, patch)
    _add_position(fixture, patch.position)


def _add_addressing(parent: ET.Element, patch: FixturePatchEntry) -> None:
    addressing = ET.SubElement(parent, f"{{{MVR_NS}}}Addressing")
    addressing.set("universe", str(patch.universe + 1))
    addressing.set("address", str(patch.address))


def _add_position(parent: ET.Element, position: FixturePosition) -> None:
    matrix = ET.SubElement(parent, f"{{{MVR_NS}}}Matrix")
    matrix.set("x", f"{position.x:.4f}")
    matrix.set("y", f"{position.y:.4f}")
    matrix.set("z", f"{position.z:.4f}")
    matrix.set("pan", f"{position.pan:.4f}")
    matrix.set("tilt", f"{position.tilt:.4f}")


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _today_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
