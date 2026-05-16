"""Tests for GDTF parsing and fixture library behavior."""

from pathlib import Path
from zipfile import ZipFile

import pytest

from rayflow.fixtures.library import FixtureLibrary
from rayflow.fixtures.parser import GdtfParser


class TestGdtfParser:
    """Tests for parsing real GDTF zip archives."""

    def test_reads_fixture_identity(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        assert parser.manufacturer == "RayFlow"
        assert parser.name == "Sample Dimmer"
        assert parser.mode_count == 1
        assert parser.mode_names() == ["Basic"]

    def test_reads_mode_and_channel_summary(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        mode = parser.get_mode_summary()

        assert mode.name == "Basic"
        assert mode.channel_count == 1
        assert mode.channels[0]["dmx"] == 1
        assert mode.channels[0]["attribute"] == "Dimmer"
        assert mode.channels[0]["geometry"] == "Body"

    def test_reads_fixture_summary(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        summary = parser.get_summary()

        assert summary.manufacturer == "RayFlow"
        assert summary.name == "Sample Dimmer"
        assert summary.mode_count == 1
        assert summary.modes[0].channel_count == 1

    def test_rejects_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError, match="GDTF file not found"):
            GdtfParser(tmp_path / "missing.gdtf.zip")

    def test_rejects_non_zip_file(self, tmp_path: Path):
        not_zip = tmp_path / "broken.gdtf.zip"
        not_zip.write_text("not a zip")

        with pytest.raises(ValueError, match="valid ZIP archive"):
            GdtfParser(not_zip)

    def test_rejects_zip_without_description(self, tmp_path: Path):
        gdtf_path = tmp_path / "missing_description.gdtf.zip"
        with ZipFile(gdtf_path, "w") as archive:
            archive.writestr("Device.xml", "<Device />")

        with pytest.raises(ValueError, match="description.xml"):
            GdtfParser(gdtf_path)

    def test_rejects_mode_index_out_of_range(self, sample_gdtf_file: Path):
        parser = GdtfParser(sample_gdtf_file)

        with pytest.raises(IndexError, match="out of range"):
            parser.get_mode(2)


class TestFixtureLibrary:
    """Tests for loading and searching fixture libraries."""

    def test_loads_fixture_directory(self, sample_gdtf_library: Path):
        library = FixtureLibrary(sample_gdtf_library)

        loaded = library.load()

        assert loaded == 1
        assert library.count == 1
        assert library.list_fixtures() == ["RayFlow@Sample Dimmer"]

    def test_loads_single_fixture_file(self, sample_gdtf_file: Path):
        library = FixtureLibrary()

        loaded = library.load(sample_gdtf_file)

        assert loaded == 1
        assert library.get("sample dimmer") is not None

    def test_searches_by_name_and_manufacturer(self, sample_gdtf_library: Path):
        library = FixtureLibrary(sample_gdtf_library)
        library.load()

        assert library.search("dimmer") == ["RayFlow@Sample Dimmer"]
        assert library.search("rayflow") == ["RayFlow@Sample Dimmer"]
        assert library.search("missing") == []

    def test_get_exact_fixture(self, sample_gdtf_library: Path):
        library = FixtureLibrary(sample_gdtf_library)
        library.load()

        parser = library.get_exact("RayFlow", "Sample Dimmer")

        assert parser is not None
        assert parser.name == "Sample Dimmer"

    def test_lists_manufacturers(self, sample_gdtf_library: Path):
        library = FixtureLibrary(sample_gdtf_library)
        library.load()

        assert library.manufacturers() == ["RayFlow"]
        assert library.by_manufacturer("RayFlow") == ["RayFlow@Sample Dimmer"]

    def test_returns_summaries(self, sample_gdtf_library: Path):
        library = FixtureLibrary(sample_gdtf_library)
        library.load()

        summaries = library.summaries()

        assert len(summaries) == 1
        assert summaries[0].name == "Sample Dimmer"
        assert summaries[0].modes[0].name == "Basic"

    def test_load_missing_path_raises(self, tmp_path: Path):
        library = FixtureLibrary()

        with pytest.raises(FileNotFoundError, match="Fixture path not found"):
            library.load(tmp_path / "missing")

    def test_load_unsupported_file_raises(self, tmp_path: Path):
        fixture_file = tmp_path / "fixture.txt"
        fixture_file.write_text("nope")
        library = FixtureLibrary()

        with pytest.raises(ValueError, match="Unsupported fixture file type"):
            library.load(fixture_file)
