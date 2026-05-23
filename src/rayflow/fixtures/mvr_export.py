"""MVR (My Virtual Rig) export for grandMA3 import."""

from __future__ import annotations

import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

MVR_XML_FILENAME = "GeneralSceneDescription.xml"
MVR_NS = ""


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
    root = ET.Element("GeneralSceneDescription")
    root.set("captureStart", _now_iso())
    root.set("date", _today_date())
    root.set("verMajor", "1")
    root.set("verMinor", "8")

    _add_user_data(root)
    scene = ET.SubElement(root, "Scene")
    scene.set("name", scene_name)
    layers = ET.SubElement(scene, "Layers")
    layer = ET.SubElement(layers, "Layer")
    layer.set("name", layer_name)
    child_list = ET.SubElement(layer, "ChildList")

    for fixture_id, patch in enumerate(patches, start=1):
        _add_fixture(child_list, patch, fixture_id=fixture_id)

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
    user_data = ET.SubElement(root, "UserData")
    user_data.set("provider", "RayFlow")
    user_data.set("createdBy", "RayFlow mvr_export")


def _embed_gdtf_files(
    archive: zipfile.ZipFile, patches: list[FixturePatchEntry]
) -> None:
    written: set[str] = set()
    for patch in patches:
        if patch.gdtf_file and patch.gdtf_file.exists():
            gdtf_name = f"{_gdtf_spec_name(patch)}.gdtf"
            if gdtf_name not in written:
                archive.write(patch.gdtf_file, gdtf_name)
                written.add(gdtf_name)


def _add_fixture(
    parent: ET.Element, patch: FixturePatchEntry, *, fixture_id: int
) -> None:
    fixture = ET.SubElement(parent, "Fixture")
    fixture.set("name", patch.name)
    fixture.set("uuid", patch.gdtf_uuid)
    if patch.gdtf_file and patch.gdtf_file.exists():
        spec = _gdtf_spec_name(patch)
    else:
        spec = _gdtf_spec_name(patch)

    _add_position(fixture, patch.position)
    ET.SubElement(fixture, "GDTFSpec").text = spec
    ET.SubElement(fixture, "GDTFMode").text = patch.dmx_mode
    _add_addressing(fixture, patch)
    ET.SubElement(fixture, "FixtureID").text = str(fixture_id)
    ET.SubElement(fixture, "UnitNumber").text = "0"
    ET.SubElement(fixture, "FixtureTypeId").text = "0"
    ET.SubElement(fixture, "CustomId").text = "0"
    ET.SubElement(fixture, "CastShadow").text = "false"
    ET.SubElement(fixture, "Mappings")


def _gdtf_spec_name(patch: FixturePatchEntry) -> str:
    if "@" in patch.fixture_type:
        return patch.fixture_type
    return f"{patch.manufacturer}@{patch.fixture_type}"


def _add_addressing(parent: ET.Element, patch: FixturePatchEntry) -> None:
    addresses = ET.SubElement(parent, "Addresses")
    address = ET.SubElement(addresses, "Address")
    address.set("break", "0")
    address.text = str((patch.universe * 512) + patch.address)


def _add_position(parent: ET.Element, position: FixturePosition) -> None:
    matrix = ET.SubElement(parent, "Matrix")
    matrix.text = (
        "{1.000000,0.000000,0.000000}"
        "{0.000000,1.000000,0.000000}"
        "{0.000000,0.000000,1.000000}"
        f"{{{position.x * 1000:.6f},{position.y * 1000:.6f},{position.z * 1000:.6f}}}"
    )


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _today_date() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")
