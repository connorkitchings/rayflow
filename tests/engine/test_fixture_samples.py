"""Tests for checked-in real GDTF fixture samples."""

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from rayflow.cli import app
from rayflow.engine.fixtures.library import FixtureLibrary
from rayflow.engine.fixtures.parser import GdtfParser

SAMPLES_DIR = Path("data/fixtures/samples")
MANIFEST_PATH = SAMPLES_DIR / "manifest.json"


def _load_manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def _channel_attributes(parser: GdtfParser) -> set[str]:
    attributes: set[str] = set()
    for mode_index in range(parser.mode_count):
        for channel in parser.get_channels_as_dict(mode_index):
            attribute = channel.get("attribute")
            if attribute:
                attributes.add(str(attribute).lstrip("+"))
    return attributes


class TestRealFixtureSamples:
    """Validate checked-in real fixture samples against the manifest."""

    def test_manifest_has_expected_shape(self):
        manifest = _load_manifest()

        assert manifest["schema_version"] == 1
        assert len(manifest["samples"]) == 3

    def test_manifest_files_exist_and_hashes_match(self):
        for sample in _load_manifest()["samples"]:
            path = SAMPLES_DIR / sample["filename"]

            assert path.exists(), f"Missing sample file: {path}"
            assert hashlib.sha256(path.read_bytes()).hexdigest() == sample["sha256"]

    def test_samples_parse_and_match_manifest_identity(self):
        for sample in _load_manifest()["samples"]:
            parser = GdtfParser(SAMPLES_DIR / sample["filename"])

            assert parser.manufacturer == sample["manufacturer"]
            assert parser.name == sample["model"]
            assert parser.mode_count >= 1

    def test_samples_include_expected_modes_and_channel_counts(self):
        for sample in _load_manifest()["samples"]:
            parser = GdtfParser(SAMPLES_DIR / sample["filename"])
            mode_names = parser.mode_names()

            for expected_mode in sample["expected_mode_names"]:
                assert expected_mode in mode_names

            for mode_name, min_count in sample["expected_min_channel_counts"].items():
                mode_index = mode_names.index(mode_name)
                assert parser.get_channel_count(mode_index) >= min_count

    def test_samples_include_expected_channel_attributes(self):
        for sample in _load_manifest()["samples"]:
            parser = GdtfParser(SAMPLES_DIR / sample["filename"])
            attributes = _channel_attributes(parser)

            for expected_attribute in sample["expected_attributes"]:
                assert expected_attribute in attributes


class TestRealFixtureLibrary:
    """Validate FixtureLibrary and CLI behavior against real samples."""

    def test_library_loads_all_manifest_samples(self):
        library = FixtureLibrary(SAMPLES_DIR)

        loaded = library.load()

        assert loaded == len(_load_manifest()["samples"])
        assert library.count == len(_load_manifest()["samples"])

    def test_fixture_list_cli_reads_real_samples(self):
        result = CliRunner().invoke(app, ["fixture", "list", "--dir", str(SAMPLES_DIR)])

        assert result.exit_code == 0
        assert "LED PAR 64 RGBW" in result.output
        assert "Robin MMX Blade" in result.output
        assert "Robin iSpiiderX" in result.output

    def test_fixture_info_cli_reads_real_sample(self):
        result = CliRunner().invoke(
            app,
            ["fixture", "info", "MMX Blade", "--dir", str(SAMPLES_DIR)],
        )

        assert result.exit_code == 0
        assert "Robe Lighting" in result.output
        assert "Robin MMX Blade" in result.output
        assert "Mode 1 - Standard" in result.output

    def test_fixture_patch_cli_reads_real_sample(self):
        result = CliRunner().invoke(
            app,
            [
                "fixture",
                "patch",
                "MMX Blade",
                "--dir",
                str(SAMPLES_DIR),
                "--mode",
                "Mode 1 - Standard",
                "--address",
                "1",
            ],
        )

        assert result.exit_code == 0
        assert "Robin MMX Blade" in result.output
        assert "Mode: Mode 1 - Standard" in result.output
        assert "Address: 1-45" in result.output
        assert "Pan" in result.output
        assert "Gobo" in result.output
        assert "Color" in result.output
