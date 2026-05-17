"""CLI tests for show management commands."""

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
    rig_dir = tmp_path / "rigs"
    rig_dir.mkdir()
    path = rig_dir / "Test Rig.yaml"
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


def _create_test_show(tmp_path: Path) -> Path:
    path = tmp_path / "Test Show.yaml"
    path.write_text(
        """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
  sections:
    - name: "Intro"
      start: 0
      end: 15
cues:
  - number: 1
    label: "Intro Cue"
    section: "Intro"
    timestamp: 0
    fade_time: 2.0
"""
    )
    return path


class TestShowCreate:
    def test_show_create(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "create",
                "New Show",
                "--rig",
                "Test Rig",
                "--title",
                "Song",
                "--artist",
                "Artist",
                "--duration",
                "180",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Show created" in result.output
        assert (tmp_path / "New Show.yaml").exists()


class TestShowList:
    def test_show_list_empty(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["show", "list", "--dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "No shows found" in result.output

    def test_show_list_with_shows(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(app, ["show", "list", "--dir", str(tmp_path)])
        assert result.exit_code == 0
        assert "Test Show" in result.output


class TestShowInfo:
    def test_show_info(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app, ["show", "info", "Test Show", "--dir", str(tmp_path)]
        )
        assert result.exit_code == 0
        assert "Test Show" in result.output
        assert "Test Song" in result.output
        assert "Intro" in result.output

    def test_show_info_json(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app, ["show", "info", "Test Show", "--dir", str(tmp_path), "--json"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "Test Show"

    def test_show_info_not_found(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["show", "info", "Missing", "--dir", str(tmp_path)])
        assert result.exit_code == 1


class TestShowAddSection:
    def test_show_add_section(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-section",
                "Test Show",
                "--name",
                "Verse",
                "--start",
                "15",
                "--end",
                "45",
                "--energy",
                "0.6",
                "--mood",
                "mellow",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Added section" in result.output

    def test_show_add_section_invalid(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-section",
                "Test Show",
                "--name",
                "Bad",
                "--start",
                "45",
                "--end",
                "15",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestShowAddCue:
    def test_show_add_cue(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-cue",
                "Test Show",
                "--number",
                "2",
                "--label",
                "Verse Cue",
                "--section",
                "Verse",
                "--timestamp",
                "15",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Added cue" in result.output

    def test_show_add_cue_invalid_timestamp(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-cue",
                "Test Show",
                "--number",
                "2",
                "--label",
                "Bad",
                "--section",
                "Verse",
                "--timestamp",
                "-1",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1

    def test_show_add_cue_duplicate_number(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-cue",
                "Test Show",
                "--number",
                "1",
                "--label",
                "Duplicate",
                "--section",
                "Intro",
                "--timestamp",
                "5",
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestShowAddPresetOverride:
    def test_show_add_preset_override(self, tmp_path: Path) -> None:
        _create_test_show(tmp_path)
        result = runner.invoke(
            app,
            [
                "show",
                "add-preset-override",
                "Test Show",
                "chorus_boost",
                "--description",
                "Brighter chorus",
                "--attributes",
                '{"dimmer": "Full"}',
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "Added preset override" in result.output


class TestShowExportMvr:
    def test_show_export_mvr(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "MVR Rig.yaml").write_text(
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
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "MVR Show.yaml").write_text(
            """name: "MVR Show"
rig_name: "MVR Rig"
song:
  title: "Song"
  artist: "Artist"
  duration: 180
cues: []
"""
        )
        output = tmp_path / "show.mvr"
        result = runner.invoke(
            app,
            [
                "show",
                "export-mvr",
                "MVR Show",
                "--output",
                str(output),
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 0
        assert "MVR exported" in result.output
        assert output.exists()

    def test_show_export_mvr_rig_not_found(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Bad Show.yaml").write_text(
            """name: "Bad Show"
rig_name: "Missing Rig"
song:
  title: "Song"
  artist: "Artist"
  duration: 180
cues: []
"""
        )
        output = tmp_path / "bad.mvr"
        result = runner.invoke(
            app,
            [
                "show",
                "export-mvr",
                "Bad Show",
                "--output",
                str(output),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 1
