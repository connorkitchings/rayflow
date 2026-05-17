"""Tests for RayFlow-to-grandMA3 fixture comparison reports."""

import json
from pathlib import Path

from rayflow.fixtures.ma3_compare import (
    build_library_patch_report,
    build_patch_report,
    compare_ma3_observation,
)
from rayflow.fixtures.parser import GdtfParser

SAMPLES_DIR = Path("data/fixtures/samples")


def test_generated_dimmer_report_matches_expected_shape(sample_gdtf_file: Path):
    report = build_patch_report(
        GdtfParser(sample_gdtf_file),
        start_address=10,
        universe=2,
    )

    assert report.manufacturer == "RayFlow"
    assert report.fixture == "Sample Dimmer"
    assert report.mode == "Basic"
    assert report.universe == 2
    assert report.start_address == 10
    assert report.end_address == 10
    assert report.channel_count == 1
    assert report.attributes == ["Dimmer"]


def test_real_led_par_report_includes_expected_attributes():
    report = build_library_patch_report(
        "LED PAR",
        fixture_dir=SAMPLES_DIR,
        start_address=20,
        universe=1,
    )

    assert report.fixture == "LED PAR 64 RGBW"
    assert report.mode == "Default"
    assert report.end_address == 24
    assert {"Dimmer", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"} <= set(
        report.attributes
    )


def test_real_mmx_blade_report_includes_expected_attributes():
    report = build_library_patch_report(
        "MMX Blade",
        fixture_dir=SAMPLES_DIR,
        mode_name="Mode 1 - Standard",
    )

    assert report.fixture == "Robin MMX Blade"
    assert report.channel_count == 45
    assert {"Pan", "Tilt", "Gobo1", "Color1"} <= set(report.attributes)


def test_ma3_observation_comparison_passes(sample_gdtf_file: Path):
    report = build_patch_report(GdtfParser(sample_gdtf_file), start_address=10)
    observation = {
        "manufacturer": "RayFlow",
        "fixture": "Sample Dimmer",
        "mode": "Basic",
        "universe": 0,
        "start_address": 10,
        "end_address": 10,
        "channel_count": 1,
        "required_attributes": ["Dimmer"],
    }

    result = compare_ma3_observation(report, observation)

    assert result.matches is True
    assert result.mismatches == []


def test_ma3_observation_comparison_reports_mismatches(sample_gdtf_file: Path):
    report = build_patch_report(GdtfParser(sample_gdtf_file), start_address=10)
    observation = {
        "manufacturer": "RayFlow",
        "fixture": "Sample Dimmer",
        "mode": "Wrong",
        "universe": 1,
        "start_address": 10,
        "end_address": 11,
        "channel_count": 2,
        "required_attributes": ["Pan"],
    }

    result = compare_ma3_observation(report, observation)

    assert result.matches is False
    assert any("mode" in mismatch for mismatch in result.mismatches)
    assert any(
        "required attribute missing: Pan" in mismatch for mismatch in result.mismatches
    )


def test_ma3_json_payload_shape_round_trips(sample_gdtf_file: Path, tmp_path: Path):
    report = build_patch_report(GdtfParser(sample_gdtf_file), start_address=10)
    payload = report.as_dict()
    path = tmp_path / "rayflow-report.json"
    path.write_text(json.dumps(payload))

    assert json.loads(path.read_text())["fixture"] == "Sample Dimmer"


def test_generate_observation_produces_expected_shape(sample_gdtf_file: Path):
    from rayflow.fixtures.ma3_compare import generate_observation

    parser = GdtfParser(sample_gdtf_file)
    obs = generate_observation(parser, start_address=10, universe=2)

    assert obs["manufacturer"] == "RayFlow"
    assert obs["fixture"] == "Sample Dimmer"
    assert obs["mode"] == "Basic"
    assert obs["universe"] == 2
    assert obs["start_address"] == 10
    assert obs["end_address"] == 10
    assert obs["channel_count"] == 1
    assert "Dimmer" in obs["required_attributes"]
    assert obs["source"] == "generated-from-rayflow"


def test_generate_observation_file_writes_json(sample_gdtf_file: Path, tmp_path: Path):
    from rayflow.fixtures.ma3_compare import generate_observation_file

    parser = GdtfParser(sample_gdtf_file)
    out_dir = tmp_path / "observations"
    saved = generate_observation_file(parser, out_dir, start_address=10)

    assert saved.exists()
    content = json.loads(saved.read_text())
    assert content["fixture"] == "Sample Dimmer"


def test_discover_observation_detects_ground_truth():
    from rayflow.fixtures.ma3_compare import discover_observation

    obs_path = discover_observation("data/fixtures", "LED PAR", mode_name="Default")

    assert obs_path is not None
    assert obs_path.name == "BlenderDMX_LEDPAR64RGBW_Default.json"


def test_discover_observation_returns_none_for_missing():
    from rayflow.fixtures.ma3_compare import discover_observation

    obs_path = discover_observation("data/fixtures", "NonexistentFixture")

    assert obs_path is None


def test_compare_all_samples_includes_led_par():
    from rayflow.fixtures.ma3_compare import compare_all_samples

    results = compare_all_samples("data/fixtures", start_address=1)

    assert len(results) >= 1

    led_par_results = [r for r in results if "LED PAR" in r.rayflow.fixture]
    assert len(led_par_results) >= 1
    assert led_par_results[0].matches is True


def test_compare_all_samples_produces_results_per_mode():
    from rayflow.fixtures.ma3_compare import compare_all_samples

    results = compare_all_samples("data/fixtures", start_address=1)

    assert len(results) >= 3

    mmx_results = [r for r in results if "MMX Blade" in r.rayflow.fixture]
    assert len(mmx_results) >= 1
    matching = [r for r in mmx_results if r.matches]
    missing = [r for r in mmx_results if "no observation" in str(r.mismatches)]
    attribute_mismatches = [
        r
        for r in mmx_results
        if not r.matches and any("required attribute" in m for m in r.mismatches)
    ]
    assert len(matching) + len(missing) + len(attribute_mismatches) == len(mmx_results)


def test_compare_all_samples_json_output():
    from rayflow.fixtures.ma3_compare import compare_all_samples

    results = compare_all_samples("data/fixtures", start_address=1)

    serialized = [r.as_dict() for r in results]
    assert len(serialized) >= 3

    for entry in serialized:
        assert "matches" in entry
        assert "mismatches" in entry
        assert "rayflow" in entry
