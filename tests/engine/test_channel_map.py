"""Tests for GDTF channel mapping."""

from pathlib import Path

import pytest

from rayflow.engine.fixtures.channel_map import (
    build_channel_map,
    classify_attribute,
    normalize_attribute,
)
from rayflow.engine.fixtures.parser import GdtfParser

SAMPLES_DIR = Path("data/fixtures/samples")


class TestGeneratedFixtureChannelMap:
    """Validate mapping behavior against generated fixtures."""

    def test_maps_single_channel_dimmer(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        channel_map = parser.get_channel_map(start_address=10, universe=2)

        assert channel_map.fixture_name == "Sample Dimmer"
        assert channel_map.mode_name == "Basic"
        assert channel_map.start_address == 10
        assert channel_map.end_address == 10
        assert channel_map.channel_count == 1

        entry = channel_map.entries[0]
        assert entry.dmx_address == 10
        assert entry.relative_channel == 1
        assert entry.attribute == "Dimmer"
        assert entry.normalized_attribute == "Dimmer"
        assert entry.family == "dimmer"
        assert entry.geometry == "Body"
        assert entry.break_number == 1
        assert entry.resolution == 1
        assert entry.fixture_name == "Sample Dimmer"
        assert entry.mode_name == "Basic"
        assert entry.universe == 2

    @pytest.mark.parametrize("start_address", [0, 513])
    def test_rejects_invalid_start_address(
        self, sample_gdtf_file: Path, start_address: int
    ):
        parser = GdtfParser(sample_gdtf_file)

        with pytest.raises(ValueError, match="start_address"):
            parser.get_channel_map(start_address=start_address)

    def test_allows_last_address_for_single_channel_fixture(
        self, sample_gdtf_file: Path
    ):
        parser = GdtfParser(sample_gdtf_file)

        channel_map = parser.get_channel_map(start_address=512)

        assert channel_map.entries[0].dmx_address == 512

    def test_rejects_map_that_exceeds_universe_bounds(self):
        parser = GdtfParser(SAMPLES_DIR / "BlenderDMX_LED_PAR_64_RGBW.gdtf")

        with pytest.raises(ValueError, match="exceeds universe bounds"):
            parser.get_channel_map(start_address=509)

    def test_rejects_invalid_mode_index(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        with pytest.raises(IndexError, match="out of range"):
            parser.get_channel_map(mode_index=10)

    def test_rejects_invalid_mode_name(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        with pytest.raises(ValueError, match="DMX mode not found"):
            parser.get_channel_map(mode_name="Missing")

    def test_builds_from_fixture_summary(self, sample_gdtf_file: Path):
        summary = GdtfParser(sample_gdtf_file).get_summary()

        channel_map = build_channel_map(
            summary,
            mode_name="Basic",
            start_address=101,
            universe=4,
        )

        assert channel_map.fixture_name == "Sample Dimmer"
        assert channel_map.mode_name == "Basic"
        assert channel_map.entries[0].dmx_address == 101
        assert channel_map.entries[0].universe == 4


class TestRealSampleChannelMaps:
    """Validate mapping behavior against checked-in real GDTF samples."""

    def test_led_par_maps_dimmer_and_rgbw_attributes(self):
        parser = GdtfParser(SAMPLES_DIR / "BlenderDMX_LED_PAR_64_RGBW.gdtf")

        channel_map = parser.get_channel_map(start_address=20, universe=1)
        attributes = {entry.attribute for entry in channel_map.entries}
        families = {entry.family for entry in channel_map.entries}

        assert channel_map.mode_name == "Default"
        assert [entry.dmx_address for entry in channel_map.entries] == [
            20,
            21,
            22,
            23,
            24,
        ]
        assert {"Dimmer", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"} <= (
            attributes
        )
        assert {"dimmer", "color"} <= families

    def test_mmx_blade_maps_position_gobo_color_and_effect_families(self):
        parser = GdtfParser(SAMPLES_DIR / "Robe_Robin_MMX_Blade.gdtf")

        channel_map = parser.get_channel_map(mode_name="Mode 1 - Standard")
        by_attribute = {entry.attribute: entry for entry in channel_map.entries}
        families = {entry.family for entry in channel_map.entries}

        assert by_attribute["Pan"].dmx_address == 1
        assert by_attribute["+Pan"].dmx_address == 2
        assert by_attribute["Pan"].family == "position"
        assert by_attribute["+Pan"].family == "position"
        assert by_attribute["+Pan"].normalized_attribute == "Pan"
        assert by_attribute["Pan"].resolution == 2
        assert by_attribute["+Pan"].resolution == 2
        assert {"position", "gobo", "color", "zoom", "focus", "shutter"} <= families

    def test_ispider_maps_multi_pixel_color_and_dimmer_attributes(self):
        parser = GdtfParser(SAMPLES_DIR / "Robe_Robin_iSpiiderX.gdtf")

        channel_map = parser.get_channel_map(mode_name="Mode 10 - Pattern full RGBW")
        attributes = {entry.attribute for entry in channel_map.entries}
        families = {entry.family for entry in channel_map.entries}

        assert {"ColorAdd_R", "+ColorAdd_R", "ColorAdd_G", "Dimmer", "+Dimmer"} <= (
            attributes
        )
        assert {"color", "dimmer", "position", "zoom"} <= families


class TestAttributeClassification:
    """Validate attribute normalization and family classification."""

    @pytest.mark.parametrize(
        ("attribute", "normalized", "family"),
        [
            ("Dimmer", "Dimmer", "dimmer"),
            ("+Dimmer", "Dimmer", "dimmer"),
            ("ColorAdd_R", "ColorAdd_R", "color"),
            ("+ColorAdd_R", "ColorAdd_R", "color"),
            ("Pan", "Pan", "position"),
            ("+Pan", "Pan", "position"),
            ("Tilt", "Tilt", "position"),
            ("Gobo1", "Gobo1", "gobo"),
            ("Zoom", "Zoom", "zoom"),
            ("Focus1", "Focus1", "focus"),
            ("Shutter1", "Shutter1", "shutter"),
            ("Control1", "Control1", "control"),
            ("Frost1", "Frost1", "other"),
        ],
    )
    def test_classifies_common_families(
        self, attribute: str, normalized: str, family: str
    ):
        assert normalize_attribute(attribute) == normalized
        assert classify_attribute(attribute) == family
