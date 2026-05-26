"""CLI tests for rig management commands."""

import json
from pathlib import Path

from typer.testing import CliRunner

from rayflow.cli import app

runner = CliRunner()

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


def _copy_samples(tmp_path: Path) -> Path:
    dest = tmp_path / "fixtures"
    dest.mkdir()
    for f in SAMPLE_FIXTURE_DIR.glob("*.gdtf"):
        (dest / f.name).write_bytes(f.read_bytes())
    return dest


def _create_test_rig(tmp_path: Path) -> Path:
    path = tmp_path / "Test Rig.yaml"
    path.write_text(
        """name: "Test Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures: []
presets: {}
"""
    )
    return path


class TestRigCreate:
    def test_rig_create(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "rig",
                "create",
                "New Rig",
                "--venue",
                "My Venue",
                "--dimensions",
                "12,6,4",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Rig created" in result.output
        assert (tmp_path / "New Rig.yaml").exists()

    def test_rig_create_template(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "rig",
                "create",
                "Template Rig",
                "--venue",
                "Venue",
                "--dimensions",
                "10,5,3",
                "--template",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        data = (tmp_path / "Template Rig.yaml").read_text()
        assert "template: true" in data

    def test_rig_create_invalid_dimensions(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "rig",
                "create",
                "Bad Rig",
                "--venue",
                "Venue",
                "--dimensions",
                "10,5",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestRigPlanBuild:
    def test_rig_plan_build_proposal_json_does_not_write(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "plan-build",
                "Generated Rig",
                "--description",
                "medium theater with beams",
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["mode"] == "proposal"
        assert payload["scale"] == "medium"
        assert not (tmp_path / "Generated Rig.yaml").exists()

    def test_rig_plan_build_apply_writes_rig(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "plan-build",
                "Generated Rig",
                "--description",
                "small club wash",
                "--overrides-json",
                '{"fixture_counts":{"wash":2,"pixel":0,"beam":0}}',
                "--apply",
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Rig build apply" in result.output
        assert (tmp_path / "Generated Rig.yaml").exists()


class TestRigQlcExports:
    def test_rig_export_qxf_writes_fixture_definitions(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_path = tmp_path / "Qlc Rig.yaml"
        rig_path.write_text(
            """name: "Qlc Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures:
  - fixture_name: "LED PAR 64 RGBW"
    mode: "Default"
    label: "PAR 1"
    universe: 0
    start_address: 1
presets: {}
"""
        )
        output_dir = tmp_path / "qxf"

        result = runner.invoke(
            app,
            [
                "rig",
                "export-qxf",
                "Qlc Rig",
                "--output-dir",
                str(output_dir),
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )

        assert result.exit_code == 0
        assert "QXF exported" in result.output
        assert list(output_dir.glob("*.qxf"))

    def test_rig_export_qxw_with_qxf_dir_references_definitions(
        self, tmp_path: Path
    ) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_path = tmp_path / "Qlc Rig.yaml"
        rig_path.write_text(
            """name: "Qlc Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures:
  - fixture_name: "LED PAR 64 RGBW"
    mode: "Default"
    label: "PAR 1"
    universe: 0
    start_address: 1
presets: {}
"""
        )
        qxf_dir = tmp_path / "qxf"
        output = tmp_path / "rig.qxw"

        result = runner.invoke(
            app,
            [
                "rig",
                "export-qxw",
                "Qlc Rig",
                "--output",
                str(output),
                "--qxf-dir",
                str(qxf_dir),
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )

        assert result.exit_code == 0
        assert output.exists()
        assert list(qxf_dir.glob("*.qxf"))
        assert "FixtureDefinition" not in output.read_text(encoding="UTF-8")


class TestRigList:
    def test_rig_list_empty(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["rig", "list", "--dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No rigs found" in result.output

    def test_rig_list_with_rigs(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        runner.invoke(
            app,
            [
                "rig",
                "create",
                "Template",
                "--venue",
                "V",
                "--dimensions",
                "10,5,3",
                "--template",
                "--dir",
                str(tmp_path),
            ],
        )
        result = runner.invoke(app, ["rig", "list", "--dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "Test Rig" in result.output
        assert "Template" in result.output

    def test_rig_list_templates_only(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        runner.invoke(
            app,
            [
                "rig",
                "create",
                "Template",
                "--venue",
                "V",
                "--dimensions",
                "10,5,3",
                "--template",
                "--dir",
                str(tmp_path),
            ],
        )
        result = runner.invoke(
            app, ["rig", "list", "--dir", str(tmp_path), "--templates-only"]
        )
        assert result.exit_code == 0
        assert "Template" in result.output
        assert "Test Rig" not in result.output


class TestRigInfo:
    def test_rig_info(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(app, ["rig", "info", "Test Rig", "--dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "Test Rig" in result.output
        assert "Test Venue" in result.output

    def test_rig_info_json(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app, ["rig", "info", "Test Rig", "--dir", str(tmp_path), "--json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Test Rig"

    def test_rig_info_not_found(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["rig", "info", "Missing", "--dir", str(tmp_path)])
        assert result.exit_code == 1


class TestRigCopy:
    def test_rig_copy(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "copy",
                "Test Rig",
                "Copy Rig",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Copied" in result.output
        assert (tmp_path / "Copy Rig.yaml").exists()

    def test_rig_copy_not_found(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "rig",
                "copy",
                "Missing",
                "Copy",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestRigAddFixture:
    def test_rig_add_fixture(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-fixture",
                "Test Rig",
                "--fixture",
                "Robin iSpiiderX",
                "--mode",
                "Mode 1 - Zones",
                "--address",
                "1",
                "--label",
                "Spiider 1",
                "--position",
                '{"x":-2,"y":4,"z":1}',
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Added fixture" in result.output

    def test_rig_add_fixture_invalid_fixture(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-fixture",
                "Test Rig",
                "--fixture",
                "Nonexistent",
                "--mode",
                "Default",
                "--address",
                "1",
                "--label",
                "F1",
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 1

    def test_rig_add_fixture_no_validate(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-fixture",
                "Test Rig",
                "--fixture",
                "Made Up Fixture",
                "--mode",
                "Default",
                "--address",
                "1",
                "--label",
                "F1",
                "--no-validate",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0

    def test_rig_add_fixture_invalid_position(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-fixture",
                "Test Rig",
                "--fixture",
                "Robin iSpiiderX",
                "--mode",
                "Mode 1 - Zones",
                "--address",
                "1",
                "--label",
                "F1",
                "--position",
                "not json",
                "--dir",
                str(tmp_path),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 1


class TestRigAddPreset:
    def test_rig_add_preset(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-preset",
                "Test Rig",
                "warm_wash",
                "--description",
                "Warm wash",
                "--attributes",
                '{"dimmer": "80", "color": "Warm Amber"}',
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Added preset" in result.output

    def test_rig_add_preset_invalid_attributes(self, tmp_path: Path) -> None:
        _create_test_rig(tmp_path)
        result = runner.invoke(
            app,
            [
                "rig",
                "add-preset",
                "Test Rig",
                "bad",
                "--description",
                "Bad",
                "--attributes",
                '{"invalid_attr": "value"}',
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestRigExportMvr:
    def test_rig_export_mvr(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        rig_path = rig_dir / "MVR Rig.yaml"
        rig_path.write_text(
            """name: "MVR Rig"
venue:
  name: "Test"
  dimensions: [10, 5, 3]
fixtures:
  - fixture_name: "Robin iSpiiderX"
    mode: "Mode 1 - Zones"
    label: "Spiider 1"
    universe: 0
    start_address: 1
    position: {x: -2, y: 4, z: 1, pan: 0, tilt: 0}
    channels: "1"
presets: {}
"""
        )
        output = tmp_path / "test.mvr"
        result = runner.invoke(
            app,
            [
                "rig",
                "export-mvr",
                "MVR Rig",
                "--output",
                str(output),
                "--dir",
                str(rig_dir),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 0
        assert "MVR exported" in result.output
        assert output.exists()
