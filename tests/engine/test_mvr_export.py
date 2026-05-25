"""Tests for MVR (My Virtual Rig) export."""

from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from rayflow.engine.fixtures.mvr_export import (
    FixturePosition,
    build_mvr_scene_element,
    build_patch_entry,
    export_mvr,
)


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

    assert root.tag == "GeneralSceneDescription"
    assert root.get("verMajor") == "1"
    assert root.get("verMinor") == "8"


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

    user_data = root.find("UserData")
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

    scene = root.find("Scene")
    assert scene is not None
    assert scene.get("name") == "My Show"

    layer = scene.find("Layers/Layer")
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

    fixture = root.find(".//Fixture")
    assert fixture is not None
    assert fixture.get("name") == "PAR 1"

    address = fixture.find("Addresses/Address")
    assert address is not None
    assert address.get("break") == "0"
    assert address.text == "42"


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

    matrix = root.find(".//Fixture/Matrix")
    assert matrix is not None
    assert matrix.text == (
        "{1.000000,0.000000,0.000000}"
        "{0.000000,1.000000,0.000000}"
        "{0.000000,0.000000,1.000000}"
        "{3500.000000,2000.000000,-4000.000000}"
    )


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

    fixtures = root.findall(".//Fixture")
    assert len(fixtures) == 4
    assert fixtures[0].get("name") == "PAR 1"
    assert fixtures[3].get("name") == "PAR 4"
    fixture_ids = [fixture.find("FixtureID").text for fixture in fixtures]
    assert fixture_ids == ["1", "2", "3", "4"]


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
        assert "GeneralSceneDescription.xml" in names
        xml_content = archive.read("GeneralSceneDescription.xml").decode()
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
        xml_text = archive.read("GeneralSceneDescription.xml").decode()
        root = ET.fromstring(xml_text)
        assert root.tag == "GeneralSceneDescription"


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
        xml_text = archive.read("GeneralSceneDescription.xml").decode()
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
