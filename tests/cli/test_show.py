"""CLI tests for show management commands."""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from rayflow.cli import app

runner = CliRunner()

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


SHOW_COMMANDS = [
    "add-cue",
    "add-preset-override",
    "add-section",
    "batch-update-cues",
    "context",
    "create",
    "delete-cue",
    "delete-section",
    "diff",
    "export",
    "export-mvr",
    "generate-cues",
    "import-sections",
    "info",
    "list",
    "output-cue",
    "output-section",
    "plan-cues",
    "plan-practice-cues",
    "push-section",
    "push-to-ma3",
    "render-cue",
    "renumber",
    "restore",
    "save",
    "set-song-meta",
    "set-vibe",
    "update-cue",
    "update-section",
    "versions",
    "workflow-report",
]


def test_show_help_registers_all_commands() -> None:
    result = runner.invoke(app, ["show", "--help"])

    assert result.exit_code == 0
    for command in SHOW_COMMANDS:
        assert command in result.output


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


class TestShowRenderCue:
    def test_render_cue_outputs_json_for_sample_show(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "render-cue",
                "sample_show",
                "6",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Sample Rig",
                "--rig-dir",
                "data/rigs",
                "--fixture-dir",
                str(SAMPLE_FIXTURE_DIR),
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["cue"]["number"] == 6
        assert payload["frames"][0]["universe"] == 0
        assert payload["frames"][0]["channels"]["13"] == 255
        assert payload["frames"][0]["channels"]["14"] == 51
        assert payload["frames"][0]["channels"]["15"] == 102
        assert payload["frames"][0]["channels"]["16"] == 255
        assert payload["warnings"]

    def test_output_cue_dry_run_outputs_backend_evidence(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "output-cue",
                "sample_show",
                "6",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Sample Rig",
                "--rig-dir",
                "data/rigs",
                "--fixture-dir",
                str(SAMPLE_FIXTURE_DIR),
                "--backend",
                "artnet",
                "--target",
                "192.0.2.10",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["backend"] == "artnet"
        assert payload["mode"] == "dry-run"
        assert payload["target"] == "192.0.2.10:6454"
        assert payload["frames"][0]["channels"]["13"] == 255
        assert payload["observed"] == {"status": "not-applied"}

    def test_output_cue_rejects_unknown_backend(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "output-cue",
                "sample_show",
                "6",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Sample Rig",
                "--rig-dir",
                "data/rigs",
                "--backend",
                "missing",
            ],
        )

        assert result.exit_code == 2
        assert "Unknown backend" in result.output

    def test_output_section_dry_run_outputs_grouped_evidence(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "output-section",
                "sample_show",
                "Chorus 1",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Sample Rig",
                "--rig-dir",
                "data/rigs",
                "--fixture-dir",
                str(SAMPLE_FIXTURE_DIR),
                "--backend",
                "artnet",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["scope"] == "section:Chorus 1"
        assert payload["backend"] == "artnet"
        assert payload["mode"] == "dry-run"
        assert [cue["frames"][0]["channels"]["13"] for cue in payload["cues"]] == [
            255,
            255,
            255,
            178,
        ]

    def test_output_section_rejects_missing_section(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "output-section",
                "sample_show",
                "Missing",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Sample Rig",
                "--rig-dir",
                "data/rigs",
            ],
        )

        assert result.exit_code == 1
        assert "Section has no cues" in result.output


    def test_workflow_report_outputs_practice_show_json(self) -> None:
        with patch("rayflow.engine.backends.dmx.ArtNetDmxBackend.apply") as apply:
            result = runner.invoke(
                app,
                [
                    "show",
                    "workflow-report",
                    "phase9_practice_show",
                    "--dir",
                    "data/shows/samples",
                    "--rig",
                    "Practice Small Club",
                    "--rig-dir",
                    "data/rigs",
                    "--fixture-dir",
                    str(SAMPLE_FIXTURE_DIR),
                    "--backend",
                    "artnet",
                    "--json",
                ],
            )

        assert result.exit_code == 0
        apply.assert_not_called()
        payload = json.loads(result.output)
        assert payload["show"] == "Phase 9 Practice Show"
        assert payload["rig"] == "Practice Small Club"
        assert payload["backend"] == "artnet"
        assert payload["mode"] == "dry-run"
        assert payload["section"] == "all"
        assert payload["cue_count"] == 8
        assert payload["frame_count"] == 8
        assert payload["readiness"]["status"] == "ready"
        assert payload["warnings"] == {"render": [], "backend": []}
        assert payload["evidence"][0]["observed"] == {"status": "not-applied"}

    def test_workflow_report_execute_captures_live_evidence_when_gated(self) -> None:
        sender_class = patch("rayflow.engine.bridge.artnet.ArtNetSender").start()
        receiver_class = patch("rayflow.engine.bridge.artnet.ArtNetReceiver").start()
        receiver_class.return_value.get_buffer.return_value = [0] * 512
        try:
            result = runner.invoke(
                app,
                [
                    "show",
                    "workflow-report",
                    "phase9_practice_show",
                    "--dir",
                    "data/shows/samples",
                    "--rig",
                    "Practice Small Club",
                    "--rig-dir",
                    "data/rigs",
                    "--fixture-dir",
                    str(SAMPLE_FIXTURE_DIR),
                    "--backend",
                    "artnet",
                    "--section",
                    "Chorus",
                    "--execute",
                    "--capture-evidence",
                    "--evidence-timeout",
                    "0",
                    "--json",
                ],
            )
        finally:
            patch.stopall()

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["mode"] == "apply"
        assert payload["readiness"]["status"] == "warnings"
        assert sender_class.call_count == 2
        assert receiver_class.call_count == 2
        assert payload["evidence"][0]["observed"]["evidence_quality"] == (
            "receiver-buffer-mismatch"
        )
        assert payload["warnings"]["backend"]

    def test_workflow_report_filters_section_and_writes_output(
        self, tmp_path: Path
    ) -> None:
        output = tmp_path / "reports" / "chorus.json"
        result = runner.invoke(
            app,
            [
                "show",
                "workflow-report",
                "phase9_practice_show",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                "data/rigs",
                "--fixture-dir",
                str(SAMPLE_FIXTURE_DIR),
                "--backend",
                "sacn",
                "--section",
                "Chorus",
                "--output",
                str(output),
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        written = json.loads(output.read_text())
        assert written == payload
        assert payload["backend"] == "sacn"
        assert payload["scope"] == "section:Chorus"
        assert payload["section"] == "Chorus"
        assert payload["cue_count"] == 2
        assert [cue["cue"]["number"] for cue in payload["rendered"]["cues"]] == [5, 6]
        assert payload["evidence"][0]["frames"][0]["sacn_universe"] == 1

    def test_workflow_report_rejects_missing_section(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "workflow-report",
                "phase9_practice_show",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                "data/rigs",
                "--section",
                "Missing",
            ],
        )

        assert result.exit_code == 1
        assert "Section has no cues" in result.output

    def test_workflow_report_rejects_unknown_backend(self) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "workflow-report",
                "phase9_practice_show",
                "--dir",
                "data/shows/samples",
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                "data/rigs",
                "--backend",
                "missing",
            ],
        )

        assert result.exit_code == 2
        assert "Unknown backend" in result.output


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


class TestShowLibrary:
    def test_save_show_version(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Library Show.yaml").write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Library Song"
  artist: "Artist"
  duration: 245.0
cues:
  - number: 1
    label: "First"
    section: "Intro"
    timestamp: 0
"""
        )
        library_dir = tmp_path / "library"

        result = runner.invoke(
            app,
            [
                "show",
                "save",
                "Library Show",
                "--message",
                "ready",
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Saved show version" in result.output
        metadata_files = list(library_dir.glob("library-show/*/metadata.json"))
        assert len(metadata_files) == 1
        metadata = json.loads(metadata_files[0].read_text())
        assert metadata["show_name"] == "Library Show"
        assert metadata["message"] == "ready"
        assert metadata["cue_count"] == 1

    def test_versions_lists_saved_versions(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        (show_dir / "Library Show.yaml").write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Library Song"
  artist: "Artist"
  duration: 245.0
cues: []
"""
        )
        library_dir = tmp_path / "library"
        save_result = runner.invoke(
            app,
            [
                "show",
                "save",
                "Library Show",
                "--message",
                "snapshot",
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )
        assert save_result.exit_code == 0

        result = runner.invoke(
            app,
            [
                "show",
                "versions",
                "Library Show",
                "--library-dir",
                str(library_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Show Versions" in result.output
        assert "snapshot" in result.output

    def test_restore_refuses_changed_show_without_force(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        show_path = show_dir / "Library Show.yaml"
        show_path.write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Library Song"
  artist: "Artist"
  duration: 245.0
cues: []
"""
        )
        library_dir = tmp_path / "library"
        save_result = runner.invoke(
            app,
            [
                "show",
                "save",
                "Library Show",
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )
        assert save_result.exit_code == 0
        version = json.loads(
            next(library_dir.glob("library-show/*/metadata.json")).read_text()
        )["version_id"]
        show_path.write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Changed Song"
  artist: "Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "restore",
                "Library Show",
                "--version",
                version,
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )
        assert result.exit_code == 1
        assert "pass --force" in result.output

        forced = runner.invoke(
            app,
            [
                "show",
                "restore",
                "Library Show",
                "--version",
                version,
                "--force",
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )
        assert forced.exit_code == 0
        assert "Restored show version" in forced.output
        assert "Library Song" in show_path.read_text()

    def test_diff_show_version(self, tmp_path: Path) -> None:
        show_dir = tmp_path / "shows"
        show_dir.mkdir()
        show_path = show_dir / "Library Show.yaml"
        show_path.write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Library Song"
  artist: "Artist"
  duration: 245.0
cues: []
"""
        )
        library_dir = tmp_path / "library"
        save_result = runner.invoke(
            app,
            [
                "show",
                "save",
                "Library Show",
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )
        assert save_result.exit_code == 0
        version = json.loads(
            next(library_dir.glob("library-show/*/metadata.json")).read_text()
        )["version_id"]
        show_path.write_text(
            """name: "Library Show"
rig_name: "Test Rig"
song:
  title: "Changed Song"
  artist: "Artist"
  duration: 245.0
cues: []
"""
        )

        result = runner.invoke(
            app,
            [
                "show",
                "diff",
                "Library Show",
                "--version",
                version,
                "--dir",
                str(show_dir),
                "--library-dir",
                str(library_dir),
            ],
        )

        assert result.exit_code == 0
        assert "--- Library Show@" in result.output
        assert '-  title: "Library Song"' in result.output
        assert '+  title: "Changed Song"' in result.output

    def test_save_missing_show(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "save",
                "Missing",
                "--dir",
                str(tmp_path),
                "--library-dir",
                str(tmp_path / "library"),
            ],
        )
        assert result.exit_code == 1
        assert "Show not found" in result.output

    def test_restore_missing_version(self, tmp_path: Path) -> None:
        result = runner.invoke(
            app,
            [
                "show",
                "restore",
                "Missing",
                "--version",
                "20260520T120000Z",
                "--dir",
                str(tmp_path),
                "--library-dir",
                str(tmp_path / "library"),
            ],
        )
        assert result.exit_code == 1
        assert "Show version not found" in result.output


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
        assert "Store Sequence 1 Cue 1 /Overwrite /NoConfirmation" in result.output
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
        assert "Delete Sequence 1 /NoConfirmation" in result.output
        assert "Store Sequence 1 /Overwrite /NoConfirmation" in result.output


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
        assert "Store Sequence 1 Cue 1 /Overwrite /NoConfirmation" in result.output
        assert "Store Sequence 1 Cue 2 /Overwrite /NoConfirmation" not in result.output


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


class TestShowPlanPracticeCues:
    def _copy_practice_files(self, tmp_path: Path) -> tuple[Path, Path]:
        show_dir = tmp_path / "shows"
        rig_dir = tmp_path / "rigs"
        show_dir.mkdir()
        rig_dir.mkdir()
        source_show = Path("data/shows/samples/phase9_practice_show.yaml")
        source_rig = Path("data/rigs/Practice Small Club.yaml")
        show_path = show_dir / "phase9_practice_show.yaml"
        rig_path = rig_dir / "Practice Small Club.yaml"
        show_path.write_text(source_show.read_text())
        rig_path.write_text(source_rig.read_text())
        return show_dir, rig_dir

    def test_plan_practice_cues_proposal_does_not_modify_show(
        self, tmp_path: Path
    ) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)
        show_path = show_dir / "phase9_practice_show.yaml"
        before = show_path.read_text()

        result = runner.invoke(
            app,
            [
                "show",
                "plan-practice-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "Chorus",
                "--json",
            ],
        )

        assert result.exit_code == 0
        assert show_path.read_text() == before
        payload = json.loads(result.output)
        assert payload["mode"] == "proposal"
        assert payload["section"] == "Chorus"
        assert len(payload["proposed_cues"]) == 2
        assert payload["next_command"].startswith("rayflow show workflow-report")

    def test_plan_practice_cues_apply_modifies_only_selected_section(
        self, tmp_path: Path
    ) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-practice-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "Intro",
                "--style",
                "front-back",
                "--apply",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["mode"] == "apply"
        assert payload["style"] == "front-back"
        assert payload["replaced_cue_numbers"] == [1, 2]

        from rayflow.design.serializers import load_show

        show = load_show(show_dir / "phase9_practice_show.yaml")
        intro_labels = [cue.label for cue in show.cues if cue.section == "Intro"]
        chorus_labels = [cue.label for cue in show.cues if cue.section == "Chorus"]
        assert intro_labels == ["Intro Front Warm", "Intro Back Blue"]
        assert "Chorus Open Cyan" in chorus_labels

    def test_plan_practice_cues_apply_all_refreshes_all_sections(
        self, tmp_path: Path
    ) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-practice-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "all",
                "--apply",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["mode"] == "apply"
        assert payload["section"] == "all"
        assert len(payload["proposed_cues"]) == 8

    def test_plan_practice_cues_rejects_missing_section(self, tmp_path: Path) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-practice-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "Missing",
            ],
        )

        assert result.exit_code == 1
        assert "Section not found" in result.output

    def test_plan_practice_cues_rejects_missing_rig(self, tmp_path: Path) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-practice-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Missing Rig",
                "--rig-dir",
                str(rig_dir),
            ],
        )

        assert result.exit_code == 1
        assert "Rig not found" in result.output


class TestShowPlanCues:
    def _copy_practice_files(self, tmp_path: Path) -> tuple[Path, Path]:
        show_dir = tmp_path / "shows"
        rig_dir = tmp_path / "rigs"
        show_dir.mkdir()
        rig_dir.mkdir()
        source_show = Path("data/shows/samples/phase9_practice_show.yaml")
        source_rig = Path("data/rigs/Practice Small Club.yaml")
        show_path = show_dir / "phase9_practice_show.yaml"
        rig_path = rig_dir / "Practice Small Club.yaml"
        show_path.write_text(source_show.read_text())
        rig_path.write_text(source_rig.read_text())
        return show_dir, rig_dir

    def test_plan_cues_proposal_does_not_modify_show(self, tmp_path: Path) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)
        show_path = show_dir / "phase9_practice_show.yaml"
        before = show_path.read_text()

        result = runner.invoke(
            app,
            [
                "show",
                "plan-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "Chorus",
                "--style",
                "vibe-palette",
                "--cues-per-section",
                "3",
                "--json",
            ],
        )

        assert result.exit_code == 0
        assert show_path.read_text() == before
        payload = json.loads(result.output)
        assert payload["mode"] == "proposal"
        assert payload["style"] == "vibe-palette"
        assert payload["section"] == "Chorus"
        assert len(payload["proposed_cues"]) == 3
        assert [cue["attributes"]["color"] for cue in payload["proposed_cues"]] == [
            "Warm Amber",
            "#3366FF",
            "#00CCFF",
        ]

    def test_plan_cues_apply_modifies_only_selected_section(
        self, tmp_path: Path
    ) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--section",
                "Intro",
                "--style",
                "warm-cool",
                "--apply",
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["mode"] == "apply"
        assert payload["replaced_cue_numbers"] == [1, 2]

        from rayflow.design.serializers import load_show

        show = load_show(show_dir / "phase9_practice_show.yaml")
        intro_labels = [cue.label for cue in show.cues if cue.section == "Intro"]
        chorus_labels = [cue.label for cue in show.cues if cue.section == "Chorus"]
        assert intro_labels == ["Intro Warm Front", "Intro Cool Lift"]
        assert "Chorus Open Cyan" in chorus_labels

    def test_plan_cues_rejects_bad_cue_count(self, tmp_path: Path) -> None:
        show_dir, rig_dir = self._copy_practice_files(tmp_path)

        result = runner.invoke(
            app,
            [
                "show",
                "plan-cues",
                "phase9_practice_show",
                "--dir",
                str(show_dir),
                "--rig",
                "Practice Small Club",
                "--rig-dir",
                str(rig_dir),
                "--cues-per-section",
                "0",
            ],
        )

        assert result.exit_code == 1
        assert "cues_per_section must be >= 1" in result.output


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
        timecode_path = output_dir / "timecode.xml"
        assert timecode_path.read_bytes().startswith(b"\xef\xbb\xbf")
        timecode = ET.fromstring(timecode_path.read_text(encoding="utf-8-sig"))
        assert timecode.find(".//Track").attrib["Target"].endswith(".7")
        assert timecode.find(".//CmdEvent").attrib["Name"] == "Goto"
        commands = (output_dir / "ma3_push_commands.txt").read_text()
        assert "Delete Sequence 7 /NoConfirmation" in commands
        assert "Store Sequence 7" in commands
        assert "Store Sequence 7 Cue 1 /Overwrite /NoConfirmation" in commands
        readme = (output_dir / "README.md").read_text()
        assert "Import `rig.mvr` into grandMA3" in readme
        assert "dry-run OSC command list for Sequence 7" in readme
        assert "--execute" in readme
        metadata = json.loads((output_dir / "metadata.json").read_text())
        assert metadata["show"] == "Export Show"
        assert metadata["rig"] == "Export Rig"
        assert metadata["sequence"] == 7
        assert metadata["cue_count"] == 1

    def test_show_export_timecode_writes_ma3_xml_with_bom(self, tmp_path: Path) -> None:
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
        output_path = tmp_path / "timecode.xml"

        result = runner.invoke(
            app,
            [
                "show",
                "export-timecode",
                "Export Show",
                "--output",
                str(output_path),
                "--sequence",
                "4",
                "--dir",
                str(show_dir),
            ],
        )

        assert result.exit_code == 0
        assert "Timecode XML exported" in result.output
        assert output_path.read_bytes().startswith(b"\xef\xbb\xbf")
        root = ET.fromstring(output_path.read_text(encoding="utf-8-sig"))
        assert root.attrib["DataVersion"] == "2.3.2.0"
        assert root.find(".//Track").attrib["Target"].endswith(".4")
        event = root.find(".//CmdEvent")
        assert event.attrib["Name"] == "Goto"
        assert event.attrib["Time"] == "0.000"

    def test_show_export_timecode_rejects_invalid_sequence(
        self, tmp_path: Path
    ) -> None:
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
                "export-timecode",
                "Export Show",
                "--output",
                str(tmp_path / "timecode.xml"),
                "--sequence",
                "0",
                "--dir",
                str(show_dir),
            ],
        )

        assert result.exit_code == 1
        assert "sequence must be > 0" in result.output

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
