"""Tests for QLC+ workspace (.qxw) export."""

from pathlib import Path
from xml.etree import ElementTree as ET

from rayflow.engine.fixtures.qlcplus_export import (
    QlcFixturePatch,
    build_qlc_patch,
    build_qlcplus_workspace,
    export_qlcplus_workspace,
)

# ---------------------------------------------------------------------------
# QlcFixturePatch unit tests
# ---------------------------------------------------------------------------


def test_qlc_fixture_patch_address_conversion():
    """QLC+ address is 0-based, RayFlow address is 1-based."""
    patch = QlcFixturePatch(
        fixture_id=0,
        name="PAR 1",
        manufacturer="TestCo",
        model="LED PAR",
        mode="Standard",
        universe=0,
        address=1,  # 1-based (RayFlow)
        channel_count=4,
    )
    assert patch.qlc_address == 0  # 0-based (QLC+)
    assert patch.qlc_universe == 0


def test_qlc_fixture_patch_address_offset():
    """Address offset is consistently applied."""
    patch = QlcFixturePatch(
        fixture_id=1,
        name="SPOT 1",
        manufacturer="BrandX",
        model="Spot 300",
        mode="16-bit",
        universe=1,
        address=51,  # 1-based
        channel_count=16,
    )
    assert patch.qlc_address == 50  # 0-based
    assert patch.qlc_universe == 1


def test_build_qlc_patch_helper():
    """build_qlc_patch constructs QlcFixturePatch correctly."""
    patch = build_qlc_patch(
        fixture_id=3,
        name="Washer 1",
        manufacturer="ACME",
        model="LED Washer",
        mode="RGBW",
        universe=2,
        address=100,
        channel_count=8,
    )
    assert isinstance(patch, QlcFixturePatch)
    assert patch.fixture_id == 3
    assert patch.name == "Washer 1"
    assert patch.manufacturer == "ACME"
    assert patch.model == "LED Washer"
    assert patch.mode == "RGBW"
    assert patch.universe == 2
    assert patch.address == 100
    assert patch.channel_count == 8
    assert patch.qlc_address == 99  # 0-based


def test_qlc_fixture_patch_as_dict():
    """as_dict returns expected keys."""
    patch = build_qlc_patch(
        fixture_id=0,
        name="Dimmer 1",
        manufacturer="Generic",
        model="1Ch Dimmer",
        mode="Basic",
        universe=0,
        address=1,
        channel_count=1,
    )
    d = patch.as_dict()
    assert d["fixture_id"] == 0
    assert d["name"] == "Dimmer 1"
    assert d["address"] == 1
    assert d["channel_count"] == 1


# ---------------------------------------------------------------------------
# build_qlcplus_workspace XML structure tests
# ---------------------------------------------------------------------------


def _make_patches() -> list[QlcFixturePatch]:
    return [
        build_qlc_patch(
            fixture_id=0,
            name="PAR 1",
            manufacturer="TestCo",
            model="LED PAR",
            mode="Standard",
            universe=0,
            address=1,
            channel_count=4,
        ),
        build_qlc_patch(
            fixture_id=1,
            name="PAR 2",
            manufacturer="TestCo",
            model="LED PAR",
            mode="Standard",
            universe=0,
            address=5,
            channel_count=4,
        ),
    ]


def test_workspace_root_element():
    """Workspace root has correct tag and xmlns attribute."""
    patches = _make_patches()
    root = build_qlcplus_workspace(patches)
    assert root.tag == "Workspace"
    assert root.get("xmlns") == "http://www.qlcplus.org/Workspace"
    assert root.get("CurrentWindow") == "FixtureManager"


def test_workspace_creator_block():
    """Creator block has Name, Version, and Author."""
    patches = _make_patches()
    root = build_qlcplus_workspace(patches, author="Test Author")
    creator = root.find("Creator")
    assert creator is not None
    assert creator.findtext("Name") == "Q Light Controller Plus"
    assert creator.findtext("Version") is not None
    assert creator.findtext("Author") == "Test Author"


def test_workspace_default_author():
    """Default author is RayFlow."""
    patches = _make_patches()
    root = build_qlcplus_workspace(patches)
    creator = root.find("Creator")
    assert creator is not None
    assert creator.findtext("Author") == "RayFlow"


def test_workspace_engine_present():
    """Engine element is present in the workspace."""
    patches = _make_patches()
    root = build_qlcplus_workspace(patches)
    engine = root.find("Engine")
    assert engine is not None


def test_workspace_input_output_map():
    """InputOutputMap contains Universe entries for all used universes."""
    patches = [
        build_qlc_patch(
            fixture_id=0,
            name="A",
            manufacturer="X",
            model="M",
            mode="Mode1",
            universe=0,
            address=1,
            channel_count=1,
        ),
        build_qlc_patch(
            fixture_id=1,
            name="B",
            manufacturer="X",
            model="M",
            mode="Mode1",
            universe=2,
            address=1,
            channel_count=1,
        ),
    ]
    root = build_qlcplus_workspace(patches)
    engine = root.find("Engine")
    assert engine is not None
    io_map = engine.find("InputOutputMap")
    assert io_map is not None

    universes = io_map.findall("Universe")
    universe_ids = {u.get("ID") for u in universes}
    assert "0" in universe_ids
    assert "2" in universe_ids
    assert "1" not in universe_ids  # not used


def test_workspace_fixture_count():
    """Correct number of Fixture elements are generated."""
    patches = _make_patches()
    root = build_qlcplus_workspace(patches)
    engine = root.find("Engine")
    assert engine is not None
    fixtures = engine.findall("Fixture")
    assert len(fixtures) == 2


def test_workspace_fixture_fields():
    """Each Fixture element contains the correct child elements."""
    patches = [
        build_qlc_patch(
            fixture_id=7,
            name="Spot FOH",
            manufacturer="BrandY",
            model="Spot 350",
            mode="Extended",
            universe=1,
            address=101,  # 1-based
            channel_count=20,
        )
    ]
    root = build_qlcplus_workspace(patches)
    engine = root.find("Engine")
    assert engine is not None
    fixture = engine.find("Fixture")
    assert fixture is not None

    assert fixture.findtext("Manufacturer") == "BrandY"
    assert fixture.findtext("Model") == "Spot 350"
    assert fixture.findtext("Mode") == "Extended"
    assert fixture.findtext("Name") == "Spot FOH"
    assert fixture.findtext("Universe") == "1"
    assert fixture.findtext("Address") == "100"  # 0-based
    assert fixture.findtext("ID") == "7"
    assert fixture.findtext("Channels") == "20"


def test_workspace_multi_universe_fixtures():
    """Fixtures on multiple universes are all represented."""
    patches = [
        build_qlc_patch(
            fixture_id=i,
            name=f"Fix {i}",
            manufacturer="Generic",
            model="Model",
            mode="Basic",
            universe=i % 3,
            address=(i * 4) + 1,
            channel_count=4,
        )
        for i in range(6)
    ]
    root = build_qlcplus_workspace(patches)
    engine = root.find("Engine")
    assert engine is not None
    fixtures = engine.findall("Fixture")
    assert len(fixtures) == 6


# ---------------------------------------------------------------------------
# export_qlcplus_workspace file I/O tests
# ---------------------------------------------------------------------------


def test_export_creates_file(tmp_path: Path):
    """export_qlcplus_workspace writes a .qxw file."""
    patches = _make_patches()
    output = tmp_path / "test_rig.qxw"
    result = export_qlcplus_workspace(patches, output)
    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0


def test_export_file_is_valid_xml(tmp_path: Path):
    """The exported file is valid XML parseable by ElementTree."""
    patches = _make_patches()
    output = tmp_path / "test_rig.qxw"
    export_qlcplus_workspace(patches, output)
    content = output.read_text(encoding="utf-8")
    # XML declaration must be present
    assert "<?xml version" in content
    # DOCTYPE declaration must be present
    assert "<!DOCTYPE Workspace>" in content
    # Parse to confirm validity — namespace is embedded in tag name by ElementTree
    lines = content.splitlines()
    xml_start = next(i for i, line in enumerate(lines) if "<Workspace" in line)
    root = ET.fromstring("\n".join(lines[xml_start:]))
    # Tag includes namespace: {http://www.qlcplus.org/Workspace}Workspace
    assert "Workspace" in root.tag


def test_export_fixture_data_roundtrip(tmp_path: Path):
    """Exported fixture data can be read back from file."""
    patches = [
        build_qlc_patch(
            fixture_id=0,
            name="My Dimmer",
            manufacturer="RayFlow",
            model="Sample Dimmer",
            mode="Basic",
            universe=0,
            address=1,
            channel_count=1,
        )
    ]
    output = tmp_path / "rig.qxw"
    export_qlcplus_workspace(patches, output, author="TestSuite")
    content = output.read_text(encoding="utf-8")
    # Parse without XML preamble lines; namespace is part of tag in ET
    ns = "http://www.qlcplus.org/Workspace"
    lines = content.splitlines()
    xml_start = next(i for i, line in enumerate(lines) if "<Workspace" in line)
    root = ET.fromstring("\n".join(lines[xml_start:]))

    creator = root.find(f"{{{ns}}}Creator")
    assert creator is not None
    assert creator.findtext(f"{{{ns}}}Author") == "TestSuite"

    engine = root.find(f"{{{ns}}}Engine")
    assert engine is not None
    fixture = engine.find(f"{{{ns}}}Fixture")
    assert fixture is not None
    assert fixture.findtext(f"{{{ns}}}Manufacturer") == "RayFlow"
    assert fixture.findtext(f"{{{ns}}}Model") == "Sample Dimmer"
    assert fixture.findtext(f"{{{ns}}}Address") == "0"  # 0-based


def test_export_returns_path(tmp_path: Path):
    """export_qlcplus_workspace returns the output Path."""
    patches = _make_patches()
    output = tmp_path / "workspace.qxw"
    returned = export_qlcplus_workspace(patches, output)
    assert isinstance(returned, Path)
    assert returned == output


def test_export_accepts_string_path(tmp_path: Path):
    """export_qlcplus_workspace accepts string paths."""
    patches = _make_patches()
    output_str = str(tmp_path / "workspace.qxw")
    result = export_qlcplus_workspace(patches, output_str)
    assert Path(result).exists()
