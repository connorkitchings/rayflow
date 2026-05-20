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


class TestShowSetSongMeta:
    def test_set_song_meta(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Old Title"
  artist: "Old Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "set-song-meta",
                "Test Show",
                "--title",
                "New Title",
                "--artist",
                "New Artist",
                "--duration",
                "300",
                "--bpm",
                "128",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Updated song meta" in result.output
        assert "New Title" in result.output
        assert "New Artist" in result.output


class TestShowPushToMa3:
    def test_push_dry_run(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    label: "Intro Wash"
    section: "Intro"
    timestamp: 0
    preset: "warm_wash"
    fade_time: 2.0
"""
        )
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Test Rig.yaml").write_text(
            """name: "Test Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures: []
presets:
  warm_wash:
    name: "Warm Wash"
    description: "Warm wash"
    attributes:
      dimmer: "80"
      color: "Warm Amber"
    channels: "1 Thru 4"
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "push-to-ma3",
                "Test Show",
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "Store Cue 1" in result.output
        assert "Channel 1 Thru 4 At 80" in result.output

    def test_push_empty_show(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Test Rig.yaml").write_text(
            """name: "Test Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures: []
presets: {}
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "push-to-ma3",
                "Test Show",
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Delete Sequence 1" in result.output
        assert "Store Sequence 1" in result.output


class TestShowPushSection:
    def test_push_section_dry_run(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    - name: "Verse"
      start: 15
      end: 45
cues:
  - number: 1
    label: "Intro Wash"
    section: "Intro"
    timestamp: 0
  - number: 2
    label: "Verse Build"
    section: "Verse"
    timestamp: 15
"""
        )
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Test Rig.yaml").write_text(
            """name: "Test Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures: []
presets: {}
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "push-section",
                "Test Show",
                "--section",
                "Intro",
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "Store Cue 1" in result.output
        assert "Store Cue 2" not in result.output


class TestShowUpdateSection:
    def test_update_section_energy(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "update-section",
                "Test Show",
                "--name",
                "Intro",
                "--energy",
                "0.7",
                "--mood",
                "uplifting",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Updated section" in result.output

    def test_update_section_not_found(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "update-section",
                "Test Show",
                "--name",
                "NoSuch",
                "--energy",
                "0.5",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 1


class TestShowDeleteSection:
    def test_delete_section(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "delete-section",
                "Test Show",
                "--name",
                "Intro",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted section" in result.output

    def test_delete_section_with_cues(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    label: "A"
    section: "Intro"
    timestamp: 0
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "delete-section",
                "Test Show",
                "--name",
                "Intro",
                "--delete-cues",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted section" in result.output


class TestShowDeleteCue:
    def test_delete_cue(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    label: "First"
    section: "Intro"
    timestamp: 0
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "delete-cue",
                "Test Show",
                "--number",
                "1",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted cue" in result.output


class TestShowRenumber:
    def test_renumber_cues(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
  - number: 5
    label: "A"
    section: "Intro"
    timestamp: 0
  - number: 10
    label: "B"
    section: "Intro"
    timestamp: 5
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "renumber",
                "Test Show",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Renumbered" in result.output


class TestShowGenerateCues:
    def test_generate_cues(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "generate-cues",
                "Test Show",
                "--section",
                "Intro",
                "--preset",
                "warm_wash",
                "--count",
                "3",
                "--spacing",
                "5",
                "--fade",
                "2.0",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Generated" in result.output
        assert "warm_wash" in result.output


class TestShowBatchUpdateCues:
    def test_batch_update(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    label: "A"
    section: "Intro"
    timestamp: 0
  - number: 2
    label: "B"
    section: "Intro"
    timestamp: 5
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "batch-update-cues",
                "Test Show",
                "--section",
                "Intro",
                "--attributes",
                '{"dimmer":"Full"}',
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Updated" in result.output

    def test_batch_delete(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
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
    label: "A"
    section: "Intro"
    timestamp: 0
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "batch-update-cues",
                "Test Show",
                "--section",
                "Intro",
                "--delete",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Deleted" in result.output


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


class TestShowExportBundle:
    def test_show_export_bundle(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Export Rig.yaml").write_text(
            """name: "Export Rig"
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
        (show_dir / "Export Show.yaml").write_text(
            """name: "Export Show"
rig_name: "Export Rig"
song:
  title: "Export Song"
  artist: "Artist"
  duration: 180
cues:
  - number: 1
    label: "First Look"
    section: "Intro"
    timestamp: 0
    fade_time: 2.0
"""
        )
        output_dir = tmp_path / "bundle"

        result = runner.invoke(
            app,
            [
                "show",
                "export",
                "Export Show",
                "--output-dir",
                str(output_dir),
                "--sequence",
                "7",
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )

        assert result.exit_code == 0
        assert "MA3 show export created" in result.output
        assert "Sequence: 7" in result.output
        assert (output_dir / "rig.mvr").exists()
        commands = (output_dir / "ma3_push_commands.txt").read_text()
        assert "Delete Sequence 7" in commands
        assert "Store Sequence 7" in commands
        assert "Store Cue 1" in commands
        readme = (output_dir / "README.md").read_text()
        assert "Import `rig.mvr` into grandMA3" in readme
        assert "dry-run OSC command list for Sequence 7" in readme
        assert "--execute" in readme
        metadata = json.loads((output_dir / "metadata.json").read_text())
        assert metadata["show"] == "Export Show"
        assert metadata["rig"] == "Export Rig"
        assert metadata["sequence"] == 7
        assert metadata["cue_count"] == 1

    def test_show_export_bundle_missing_show(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "export",
                "Missing Show",
                "--output-dir",
                str(tmp_path / "bundle"),
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1
        assert "Show not found" in result.output

    def test_show_export_bundle_missing_rig(self, tmp_path: Path) -> None:
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

        result = runner.invoke(
            app,
            [
                "show",
                "export",
                "Bad Show",
                "--output-dir",
                str(tmp_path / "bundle"),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 1
        assert "Rig not found" in result.output

    def test_show_export_bundle_invalid_sequence(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Export Rig.yaml").write_text(
            """name: "Export Rig"
venue:
  name: "Test"
  dimensions: [10, 5, 3]
fixtures:
  - fixture_name: "Robin iSpiiderX"
    mode: "Mode 1 - Zones"
    label: "Spiider 1"
    universe: 0
    start_address: 1
presets: {}
"""
        )
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Export Show.yaml").write_text(
            """name: "Export Show"
rig_name: "Export Rig"
song:
  title: "Export Song"
  artist: "Artist"
  duration: 180
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "export",
                "Export Show",
                "--output-dir",
                str(tmp_path / "bundle"),
                "--sequence",
                "0",
                "--dir",
                str(show_dir),
                "--rig-dir",
                str(rig_dir),
                "--fixture-dir",
                str(fixture_dir),
            ],
        )
        assert result.exit_code == 1
        assert "sequence must be > 0" in result.output


class TestShowSetVibe:
    def test_set_vibe_from_json(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )

        vibe_path = tmp_path / "vibe.json"
        vibe_path.write_text(
            json.dumps(
                {
                    "palette": {
                        "name": "Warm Sunset",
                        "colors": ["#FF6600", "#FF3366", "#FFCC00"],
                        "description": "Warm sunset vibes",
                    },
                    "intensity_curve": "low -> medium -> high",
                    "movement_style": "slow sweep",
                    "beam_style": "wide wash",
                    "mood_keywords": ["warm", "cinematic"],
                    "description": "A warm, cinematic vibe",
                }
            )
        )

        result = runner.invoke(
            app,
            [
                "show",
                "set-vibe",
                "Test Show",
                "--vibe-json",
                str(vibe_path),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Vibe set" in result.output
        assert "Warm Sunset" in result.output
        assert "#FF6600" in result.output

    def test_set_vibe_inline(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "set-vibe",
                "Test Show",
                "--palette-name",
                "Cool Blues",
                "--colors",
                '["#3366FF","#00CCFF"]',
                "--intensity",
                "medium -> high",
                "--movement",
                "dynamic",
                "--beam",
                "tight beams",
                "--description",
                "Cool blue energy",
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Vibe set" in result.output
        assert "Cool Blues" in result.output

    def test_set_vibe_show_not_found(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "set-vibe",
                "No Show",
                "--palette-name",
                "Test",
                "--colors",
                '["#FFF"]',
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1


class TestShowImportSections:
    def test_import_sections(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )
        rig_dir = tmp_path / "rigs"
        rig_dir.mkdir()
        (rig_dir / "Test Rig.yaml").write_text(
            """name: "Test Rig"
venue:
  name: "Test Venue"
  dimensions: [10, 5, 3]
fixtures: []
presets: {}
"""
        )

        sections_file = tmp_path / "sections.json"
        sections_file.write_text(
            json.dumps(
                {
                    "title": "New Song",
                    "artist": "New Artist",
                    "duration": 200.0,
                    "bpm": 140,
                    "sections": [
                        {"name": "Intro", "start": 0, "end": 15, "energy": 0.3},
                        {"name": "Chorus", "start": 15, "end": 45, "energy": 0.9},
                    ],
                }
            )
        )

        result = runner.invoke(
            app,
            [
                "show",
                "import-sections",
                "Test Show",
                str(sections_file),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 0
        assert "Imported sections" in result.output
        assert "New Song" in result.output
        assert "New Artist" in result.output

    def test_import_sections_bad_json(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )

        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json")

        result = runner.invoke(
            app,
            [
                "show",
                "import-sections",
                "Test Show",
                str(bad_file),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 1

    def test_import_sections_file_not_found(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Test Show.yaml").write_text(
            """name: "Test Show"
rig_name: "Test Rig"
song:
  title: "Test Song"
  artist: "Test Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "import-sections",
                "Test Show",
                str(tmp_path / "missing.json"),
                "--dir",
                str(show_dir),
            ],
        )
        assert result.exit_code == 1
        assert "File not found" in result.output

    def test_import_sections_show_not_found(self, tmp_path: Path) -> None:
        sections_file = tmp_path / "sections.json"
        sections_file.write_text(
            json.dumps(
                {
                    "title": "Test",
                    "artist": "Artist",
                    "duration": 60,
                    "sections": [{"name": "Only", "start": 0, "end": 60}],
                }
            )
        )

        result = runner.invoke(
            app,
            [
                "show",
                "import-sections",
                "No Such Show",
                str(sections_file),
                "--dir",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 1
