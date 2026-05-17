"""Tests for MVR (My Virtual Rig) export."""

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from rayflow.fixtures.mvr_export import (
    FixturePosition,
    build_mvr_scene_element,
    build_patch_entry,
    export_mvr,
)

MVR_NS = "http://www.gdtf-share.com/MVR"


def test_build_patch_entry_defaults():
    entry = build_patch_entry(
        name="LED PAR 1",
        manufacturer="TestCo",
        fixture_type="TestCo@LED PAR",
        dmx_mode="Standard",
        universe=0,
        address=10,
    )

    assert entry.name == "LED PAR 1"
    assert entry.manufacturer == "TestCo"
    assert entry.universe == 0
    assert entry.address == 10
    assert entry.gdtf_uuid is not None
    assert entry.position.name == "LED PAR 1"


def test_build_patch_entry_with_position():
    position = FixturePosition(name="PAR 1", x=2.0, y=3.0, z=-1.0, pan=45, tilt=90)

    entry = build_patch_entry(
        name="PAR 1",
        manufacturer="TestCo",
        fixture_type="TestCo@LED PAR",
        dmx_mode="Standard",
        universe=1,
        address=5,
        position=position,
    )

    assert entry.position.x == 2.0
    assert entry.position.y == 3.0
    assert entry.position.z == -1.0
    assert entry.position.pan == 45
    assert entry.position.tilt == 90


def test_build_mvr_scene_element_contains_root():
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=1,
        ),
    ]

    root = build_mvr_scene_element(patches)

    assert root.tag == f"{{{MVR_NS}}}GeneralSceneDescription"
    assert root.get("versionMajor") == "1"
    assert root.get("versionMinor") == "8"


def test_build_mvr_scene_element_has_user_data():
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=1,
        ),
    ]

    root = build_mvr_scene_element(patches)

    user_data = root.find(f"{{{MVR_NS}}}UserData")
    assert user_data is not None
    assert user_data.get("provider") == "RayFlow"


def test_build_mvr_scene_element_has_scene_and_layer():
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=1,
        ),
    ]

    root = build_mvr_scene_element(patches, scene_name="My Show")

    scene = root.find(f"{{{MVR_NS}}}Scene")
    assert scene is not None
    assert scene.get("name") == "My Show"

    layer = scene.find(f"{{{MVR_NS}}}Layers/{{{MVR_NS}}}Layer")
    assert layer is not None
    assert layer.get("name") == "Fixtures"


def test_build_mvr_scene_element_fixture_has_addressing():
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=42,
        ),
    ]

    root = build_mvr_scene_element(patches)

    fixture = root.find(
        f".//{{{MVR_NS}}}Fixture"
    )
    assert fixture is not None
    assert fixture.get("name") == "PAR 1"

    addressing = fixture.find(f"{{{MVR_NS}}}Addressing")
    assert addressing is not None
    assert addressing.get("universe") == "1"
    assert addressing.get("address") == "42"


def test_build_mvr_scene_element_fixture_has_position():
    position = FixturePosition(name="MH 1", x=3.5, y=2.0, z=-4.0, pan=180, tilt=45)
    patches = [
        build_patch_entry(
            name="MH 1",
            manufacturer="TestCo",
            fixture_type="TestCo@Moving Head",
            dmx_mode="Extended",
            universe=0,
            address=50,
            position=position,
        ),
    ]

    root = build_mvr_scene_element(patches)

    matrix = root.find(f".//{{{MVR_NS}}}Fixture/{{{MVR_NS}}}Matrix")
    assert matrix is not None
    assert matrix.get("x") == "3.5000"
    assert matrix.get("y") == "2.0000"
    assert matrix.get("z") == "-4.0000"
    assert matrix.get("pan") == "180.0000"
    assert matrix.get("tilt") == "45.0000"


def test_build_mvr_scene_multiple_fixtures():
    patches = [
        build_patch_entry(
            name=f"PAR {i}",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=i * 5,
        )
        for i in range(1, 5)
    ]

    root = build_mvr_scene_element(patches)

    fixtures = root.findall(f".//{{{MVR_NS}}}Fixture")
    assert len(fixtures) == 4
    assert fixtures[0].get("name") == "PAR 1"
    assert fixtures[3].get("name") == "PAR 4"


def test_export_mvr_creates_valid_zip(tmp_path: Path):
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=0,
            address=1,
        ),
    ]

    output = tmp_path / "test_rig.mvr"
    result = export_mvr(patches, output)

    assert result.exists()
    assert result.suffix == ".mvr"

    with ZipFile(result) as archive:
        names = archive.namelist()
        assert "myvirtualrig.xml" in names
        xml_content = archive.read("myvirtualrig.xml").decode()
        assert "PAR 1" in xml_content
        assert "GeneralSceneDescription" in xml_content


def test_export_mvr_xml_is_parseable(tmp_path: Path):
    patches = [
        build_patch_entry(
            name="PAR 1",
            manufacturer="TestCo",
            fixture_type="TestCo@LED PAR",
            dmx_mode="Standard",
            universe=1,
            address=10,
        ),
    ]

    output = tmp_path / "rig.mvr"
    export_mvr(patches, output)

    with ZipFile(output) as archive:
        xml_text = archive.read("myvirtualrig.xml").decode()
        root = ET.fromstring(xml_text)
        assert root.tag == f"{{{MVR_NS}}}GeneralSceneDescription"


def test_export_mvr_scene_name_flows_through(tmp_path: Path):
    patches = [
        build_patch_entry(
            name="P1",
            manufacturer="TC",
            fixture_type="TC@P1",
            dmx_mode="M1",
            universe=0,
            address=1,
        ),
    ]

    output = tmp_path / "named.mvr"
    export_mvr(patches, output, scene_name="Festival Rig 2026")

    with ZipFile(output) as archive:
        xml_text = archive.read("myvirtualrig.xml").decode()
        assert "Festival Rig 2026" in xml_text


def test_fixture_position_as_dict():
    pos = FixturePosition(name="Test", x=1, y=2, z=3, pan=90, tilt=45)

    d = pos.as_dict()

    assert d["name"] == "Test"
    assert d["x"] == 1
    assert d["y"] == 2
    assert d["z"] == 3
    assert d["pan"] == 90
    assert d["tilt"] == 45
