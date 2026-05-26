"""Tests for QLC+ fixture definition (.qxf) export."""

from pathlib import Path
from xml.etree import ElementTree as ET

from rayflow.engine.fixtures.parser import GdtfParser
from rayflow.engine.fixtures.qlcplus_qxf import (
    build_qlcplus_fixture_definition,
    export_qlcplus_fixture_definition,
    export_qlcplus_fixture_definitions,
    qxf_filename_for_fixture,
)

SAMPLE_FIXTURE = Path("data/fixtures/samples/BlenderDMX_LED_PAR_64_RGBW.gdtf")
MOVER_FIXTURE = Path("data/fixtures/samples/Robe_Robin_iSpiiderX.gdtf")


def test_build_qxf_fixture_definition_structure() -> None:
    parser = GdtfParser(SAMPLE_FIXTURE)

    root = build_qlcplus_fixture_definition(parser)

    assert root.tag == "FixtureDefinition"
    assert root.get("xmlns") == "http://www.qlcplus.org/FixtureDefinition"
    assert root.findtext("Manufacturer") == parser.manufacturer
    assert root.findtext("Model") == parser.name
    assert root.find("Mode") is not None
    assert root.find("Channel") is not None


def test_build_qxf_includes_channel_metadata() -> None:
    parser = GdtfParser(SAMPLE_FIXTURE)

    root = build_qlcplus_fixture_definition(parser)
    channels = root.findall("Channel")
    mode_channels = root.findall("./Mode/Channel")

    assert channels
    assert mode_channels
    assert any(channel.findtext("Group") == "Colour" for channel in channels)
    assert all(channel.get("Name") is not None for channel in channels)
    assert all(channel.get("Number") is not None for channel in mode_channels)


def test_build_qxf_detects_moving_head_type() -> None:
    parser = GdtfParser(MOVER_FIXTURE)

    root = build_qlcplus_fixture_definition(parser)

    assert root.findtext("Type") == "Moving Head"


def test_build_qxf_moving_head_mode_channel_names_are_unique() -> None:
    parser = GdtfParser(MOVER_FIXTURE)

    root = build_qlcplus_fixture_definition(parser)

    for mode in root.findall("Mode"):
        names = [channel.text for channel in mode.findall("Channel")]
        assert len(names) == len(set(names))
    top_level_names = [channel.get("Name") for channel in root.findall("Channel")]
    assert "Pan Fine" in top_level_names
    assert "Tilt Fine" in top_level_names


def test_export_qxf_writes_parseable_file(tmp_path: Path) -> None:
    parser = GdtfParser(SAMPLE_FIXTURE)

    result = export_qlcplus_fixture_definition(parser, tmp_path)

    assert result.path.name == qxf_filename_for_fixture(parser)
    assert result.path.exists()
    content = result.path.read_text(encoding="UTF-8")
    assert "<!DOCTYPE FixtureDefinition>" in content
    parsed = ET.parse(result.path)
    assert parsed.getroot().tag.endswith("FixtureDefinition")


def test_export_qxf_deduplicates_parsers(tmp_path: Path) -> None:
    parser = GdtfParser(SAMPLE_FIXTURE)

    results = export_qlcplus_fixture_definitions([parser, parser], tmp_path)

    assert len(results) == 1
    assert results[0].path.exists()
