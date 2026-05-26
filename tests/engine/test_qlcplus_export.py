"""Tests for QLC+ workspace (.qxw) export."""

from pathlib import Path
from xml.etree import ElementTree as ET

from rayflow.engine.fixtures.qlcplus_export import (
    QlcFixturePatch,
    build_qlc_patch,
    build_qlc_scene_function,
    build_qlcplus_workspace,
    copy_qxf_files_for_workspace,
    export_qlcplus_workspace,
    validate_qlcplus_workspace,
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


def test_workspace_includes_scene_functions():
    """Scene functions are exported in the Engine block."""
    patches = _make_patches()
    function = build_qlc_scene_function(
        function_id=0,
        name="1 Intro Look",
        cue_number=1,
        cue_label="Intro Look",
        fixture_values={
            0: [255, 128, 0, 0],
            1: [0, 0, 255, 128],
        },
        fade_ms=250,
    )

    root = build_qlcplus_workspace(patches, functions=[function])
    engine = root.find("Engine")
    assert engine is not None
    scene = engine.find("Function")
    assert scene is not None
    assert scene.get("ID") == "0"
    assert scene.get("Type") == "Scene"
    assert scene.get("Name") == "1 Intro Look"
    speed = scene.find("Speed")
    assert speed is not None
    assert speed.get("FadeIn") == "250"
    fixture_values = scene.findall("FixtureVal")
    assert [(fv.get("ID"), fv.text) for fv in fixture_values] == [
        ("0", "255,128,0,0"),
        ("1", "0,0,255,128"),
    ]


def test_workspace_adds_virtual_console_buttons_for_scene_functions():
    """Scene functions get export-only Virtual Console trigger buttons."""
    patches = _make_patches()
    functions = [
        build_qlc_scene_function(
            function_id=10,
            name="Intro",
            fixture_values={0: [255, 0, 0, 0]},
        ),
        build_qlc_scene_function(
            function_id=11,
            name="Verse",
            fixture_values={0: [128, 0, 0, 0]},
        ),
    ]

    root = build_qlcplus_workspace(patches, functions=functions)
    virtual_console = root.find("VirtualConsole")
    assert virtual_console is not None
    frame = virtual_console.find("Frame")
    assert frame is not None
    buttons = frame.findall("Button")
    assert [
        (button.get("Caption"), button.findtext("Function")) for button in buttons
    ] == [
        ("Intro", "10"),
        ("Verse", "11"),
    ]


def test_workspace_can_omit_virtual_console_buttons():
    """Virtual Console output can be disabled for file-shape validation."""
    patches = _make_patches()
    function = build_qlc_scene_function(
        function_id=10,
        name="Intro",
        fixture_values={0: [255, 0, 0, 0]},
    )

    root = build_qlcplus_workspace(
        patches,
        functions=[function],
        virtual_console=False,
    )

    assert root.find("Engine/Function") is not None
    assert root.find("VirtualConsole") is None


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


def test_export_scene_functions_roundtrip(tmp_path: Path):
    """Exported Scene functions are parseable from a QXW file."""
    patches = _make_patches()
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(
        patches,
        output,
        functions=[
            build_qlc_scene_function(
                function_id=3,
                name="Cue 3",
                fixture_values={0: [10, 20, 30, 40]},
            )
        ],
    )

    content = output.read_text(encoding="utf-8")
    ns = "http://www.qlcplus.org/Workspace"
    lines = content.splitlines()
    xml_start = next(i for i, line in enumerate(lines) if "<Workspace" in line)
    root = ET.fromstring("\n".join(lines[xml_start:]))
    scene = root.find(f".//{{{ns}}}Function")

    assert scene is not None
    assert scene.get("Type") == "Scene"
    assert scene.findtext(f"{{{ns}}}FixtureVal") == "10,20,30,40"


def test_validate_workspace_reports_scene_button_readiness(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(
        _make_patches(),
        output,
        functions=[
            build_qlc_scene_function(
                function_id=3,
                name="Cue 3",
                fixture_values={0: [10, 20, 30, 40]},
            )
        ],
    )

    report = validate_qlcplus_workspace(output)

    assert report.fixture_count == 2
    assert report.scene_function_count == 1
    assert report.virtual_console_button_count == 1
    assert report.linked_button_count == 1
    assert report.as_dict()["readiness"]["status"] == "ready"


def test_validate_workspace_reports_missing_button_link(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(
        _make_patches(),
        output,
        functions=[
            build_qlc_scene_function(
                function_id=3,
                name="Cue 3",
                fixture_values={0: [10, 20, 30, 40]},
            )
        ],
    )
    content = output.read_text(encoding="utf-8").replace(
        "<Function>3</Function>", "<Function>99</Function>"
    )
    output.write_text(content, encoding="utf-8")

    report = validate_qlcplus_workspace(output)

    assert report.linked_button_count == 0
    assert report.missing_function_links == ["Cue 3 -> 99"]
    assert report.as_dict()["readiness"]["status"] == "warnings"


def test_validate_workspace_reports_missing_scene_functions(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(_make_patches(), output)

    report = validate_qlcplus_workspace(output)

    assert report.scene_function_count == 0
    assert "no Scene functions" in report.warnings[0]


def test_validate_workspace_reports_malformed_xml(tmp_path: Path) -> None:
    output = tmp_path / "broken.qxw"
    output.write_text("<Workspace><Engine>", encoding="utf-8")

    report = validate_qlcplus_workspace(output)

    assert report.fixture_count == 0
    assert "Malformed QXW XML" in report.warnings[0]


def test_validate_workspace_checks_optional_qxf_dir(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    qxf_dir = tmp_path / "fixtures"
    qxf_dir.mkdir()
    export_qlcplus_workspace(_make_patches(), output)

    report = validate_qlcplus_workspace(output, qxf_dir=qxf_dir)

    assert report.missing_fixture_definitions == ["TestCo-LED-PAR.qxf"]


def test_validate_workspace_compares_live_functions(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(
        _make_patches(),
        output,
        functions=[
            build_qlc_scene_function(
                function_id=3,
                name="Cue 3",
                fixture_values={0: [10, 20, 30, 40]},
            )
        ],
    )

    report = validate_qlcplus_workspace(
        output,
        live_functions=[{"id": 3, "name": "Cue 3"}],
    )

    assert report.live_function_count == 1
    assert report.live_function_names == ["Cue 3"]
    assert report.live_missing_scene_names == []
    assert report.as_dict()["readiness"]["status"] == "ready"


def test_validate_workspace_reports_missing_live_scene(tmp_path: Path) -> None:
    output = tmp_path / "workspace.qxw"
    export_qlcplus_workspace(
        _make_patches(),
        output,
        functions=[
            build_qlc_scene_function(
                function_id=3,
                name="Cue 3",
                fixture_values={0: [10, 20, 30, 40]},
            )
        ],
    )

    report = validate_qlcplus_workspace(output, live_functions=[])

    assert report.live_missing_scene_names == ["Cue 3"]
    assert report.live_warnings
    assert report.as_dict()["readiness"]["status"] == "warnings"


def test_copy_qxf_files_for_workspace(tmp_path: Path) -> None:
    source_dir = tmp_path / "qxf"
    source_dir.mkdir()
    source = source_dir / "Fixture.qxf"
    source.write_text("<FixtureDefinition />", encoding="utf-8")
    workspace = tmp_path / "workspace" / "show.qxw"

    class Result:
        path = source

    copies = copy_qxf_files_for_workspace([Result()], workspace)

    assert copies[0].copied is True
    assert copies[0].destination == workspace.parent / source.name
    assert copies[0].destination.exists()
