"""Integration tests for grandMA3 onPC.

These tests require a running grandMA3 onPC instance at 127.0.0.1.
Run with: uv run pytest -m integration --no-cov
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

pytestmark = pytest.mark.integration

MA3_IP = "127.0.0.1"
MA3_OSC_PORT = 8000
FIXTURE_DIR = "data/fixtures/samples"
OBSERVATION_DIR = Path(FIXTURE_DIR) / "observations"


@pytest.fixture
def osc_client():
    from rayflow.engine.console.osc import Ma3OscClient

    return Ma3OscClient(ip=MA3_IP, port=MA3_OSC_PORT)


@pytest.fixture
def library():
    from rayflow.engine.fixtures.library import FixtureLibrary

    lib = FixtureLibrary(FIXTURE_DIR)
    lib.load()
    return lib


class TestOscConnection:
    def test_about_command_sends(self, osc_client):
        osc_client.about()

    def test_send_command_does_not_raise(self, osc_client):
        osc_client.send("About")

    def test_send_empty_command_raises(self, osc_client):
        with pytest.raises(ValueError, match="must not be empty"):
            osc_client.send("")


class TestOscCommands:
    def test_clear_command(self, osc_client):
        osc_client.clear()

    def test_set_intensity(self, osc_client):
        osc_client.set_intensity(50)

    def test_store_cue(self, osc_client):
        osc_client.store_cue(999)

    def test_go_sequence(self, osc_client):
        osc_client.go_sequence(999)


class TestFixtureComparison:
    def test_all_observations_are_from_ma3(self):
        for obs_file in sorted(OBSERVATION_DIR.glob("*.json")):
            data = json.loads(obs_file.read_text())
            assert data["source"] == "captured-from-grandma3", (
                f"{obs_file.name} is not a real MA3 capture"
            )

    def test_compare_all_samples_passes(self):
        from rayflow.engine.fixtures.ma3_compare import compare_all_samples

        results = compare_all_samples("data/fixtures", start_address=1)
        assert len(results) >= 14

        failures = [r for r in results if not r.matches]
        assert not failures, (
            f"{len(failures)} fixture/mode comparisons failed:\n"
            + "\n".join(
                f"  {r.rayflow.fixture} ({r.rayflow.mode}): {r.mismatches}"
                for r in failures
            )
        )

    def test_led_par_observation_matches_rayflow(self, library):
        from rayflow.engine.fixtures.ma3_compare import (
            build_patch_report,
            compare_ma3_observation,
            discover_observation,
        )

        fixture = library.get("LED PAR")
        assert fixture is not None

        report = build_patch_report(fixture, start_address=1)
        obs_path = discover_observation(
            "data/fixtures", fixture.name, mode_name="Default"
        )
        assert obs_path is not None

        observation = json.loads(obs_path.read_text())
        result = compare_ma3_observation(report, observation)
        assert result.matches, f"Mismatches: {result.mismatches}"


class TestMvrExport:
    def test_mvr_contains_gdtf_files(self, library, tmp_path):
        from rayflow.engine.fixtures.mvr_export import (
            build_patch_entry,
            export_mvr,
        )

        patches = []
        for key in library.list_fixtures():
            parser = library.get_exact(*key.split("@", 1))
            if parser is None:
                continue
            gdtf_file = getattr(parser, "path", None)
            patches.append(
                build_patch_entry(
                    name=parser.name,
                    manufacturer=parser.manufacturer,
                    fixture_type=key,
                    dmx_mode=parser.mode_names()[0],
                    universe=0,
                    address=1,
                    gdtf_file=gdtf_file,
                )
            )

        output = tmp_path / "test.mvr"
        export_mvr(patches, output)

        with zipfile.ZipFile(output) as z:
            names = z.namelist()
            assert "GeneralSceneDescription.xml" in names
            gdtf_files = [n for n in names if n.endswith(".gdtf")]
            assert len(gdtf_files) >= 3

    def test_mvr_xml_has_gdtf_mode(self, library, tmp_path):
        from rayflow.engine.fixtures.mvr_export import (
            build_patch_entry,
            export_mvr,
        )

        parser = library.get("LED PAR")
        assert parser is not None

        patches = [
            build_patch_entry(
                name=parser.name,
                manufacturer=parser.manufacturer,
                fixture_type=f"{parser.manufacturer}@{parser.name}",
                dmx_mode="Default",
                universe=0,
                address=1,
                gdtf_file=getattr(parser, "path", None),
            )
        ]

        output = tmp_path / "test.mvr"
        export_mvr(patches, output)

        with zipfile.ZipFile(output) as z:
            with z.open("GeneralSceneDescription.xml") as f:
                tree = ET.parse(f)
                fixtures = tree.findall(".//Fixture")
                assert len(fixtures) == 1
                mode = fixtures[0].find("GDTFMode")
                assert mode is not None
                assert mode.text == "Default"


class TestArtNet:
    def test_send_single_channel(self):
        from rayflow.engine.bridge.artnet import ArtNetSender

        sender = ArtNetSender(universe=0, target_ip=MA3_IP)
        sender.set_channel(1, 255)

    def test_send_multiple_channels(self):
        from rayflow.engine.bridge.artnet import ArtNetSender

        sender = ArtNetSender(universe=0, target_ip=MA3_IP)
        sender.set_channels({1: 255, 2: 128, 3: 0})
