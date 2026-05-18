"""Tests for section import module."""

import json
from pathlib import Path

import pytest

from rayflow.shows.models import Section, Song
from rayflow.shows.section_import import (
    _validate_import_data,
    import_sections_to_song,
    parse_section_import,
)


def _make_sections_json(tmp_path: Path, **overrides) -> Path:
    data = {
        "title": "Test Song",
        "artist": "Test Artist",
        "duration": 120.0,
        "bpm": 128,
        "sections": [
            {"name": "Intro", "start": 0, "end": 10, "energy": 0.3, "mood": "ambient"},
            {"name": "Verse", "start": 10, "end": 40, "energy": 0.5},
            {
                "name": "Chorus",
                "start": 40,
                "end": 70,
                "energy": 0.9,
                "mood": "energetic",
            },
            {"name": "Outro", "start": 70, "end": 120, "energy": 0.2},
        ],
    }
    data.update(overrides)
    path = tmp_path / "sections.json"
    path.write_text(json.dumps(data))
    return path


class TestParseSectionImport:
    def test_parse_valid(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path)
        result = parse_section_import(path)
        assert result.title == "Test Song"
        assert result.artist == "Test Artist"
        assert result.duration == 120.0
        assert result.bpm == 128
        assert len(result.sections) == 4
        assert result.sections[0].name == "Intro"
        assert result.sections[0].start == 0
        assert result.sections[0].end == 10
        assert result.sections[0].energy == 0.3
        assert result.sections[0].mood == "ambient"
        assert result.warnings == []

    def test_parse_minimal(self, tmp_path: Path) -> None:
        data = {
            "title": "Minimal",
            "artist": "Artist",
            "duration": 60.0,
            "sections": [{"name": "Only", "start": 0, "end": 60}],
        }
        path = tmp_path / "minimal.json"
        path.write_text(json.dumps(data))
        result = parse_section_import(path)
        assert result.bpm is None
        assert len(result.sections) == 1

    def test_parse_missing_title(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, title="")
        with pytest.raises(ValueError, match="title"):
            parse_section_import(path)

    def test_parse_missing_artist(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, artist="")
        with pytest.raises(ValueError, match="artist"):
            parse_section_import(path)

    def test_parse_missing_duration(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path)
        data = json.loads(path.read_text())
        del data["duration"]
        path.write_text(json.dumps(data))
        with pytest.raises(ValueError, match="duration"):
            parse_section_import(path)

    def test_parse_negative_duration(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, duration=-5)
        with pytest.raises(ValueError, match="duration"):
            parse_section_import(path)

    def test_parse_bad_bpm(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, bpm="fast")
        with pytest.raises(ValueError, match="bpm"):
            parse_section_import(path)

    def test_parse_no_sections(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, sections=[])
        with pytest.raises(ValueError, match="no sections"):
            parse_section_import(path)

    def test_parse_duplicate_section_names(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "Intro", "start": 0, "end": 10},
                {"name": "Intro", "start": 10, "end": 20},
            ],
        )
        with pytest.raises(ValueError, match="Duplicate section name"):
            parse_section_import(path)

    def test_parse_missing_section_start(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, sections=[{"name": "Bad", "end": 10}])
        with pytest.raises(ValueError, match="start"):
            parse_section_import(path)

    def test_parse_missing_section_end(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, sections=[{"name": "Bad", "start": 0}])
        with pytest.raises(ValueError, match="end"):
            parse_section_import(path)

    def test_parse_bad_section_energy(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path, sections=[{"name": "Bad", "start": 0, "end": 10, "energy": 1.5}]
        )
        with pytest.raises(ValueError, match="energy"):
            parse_section_import(path)

    def test_parse_section_exceeds_duration_warning(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path, sections=[{"name": "Intro", "start": 0, "end": 200}]
        )
        result = parse_section_import(path)
        assert len(result.warnings) == 1
        assert "exceeds song duration" in result.warnings[0]

    def test_parse_section_end_before_start(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path, sections=[{"name": "Bad", "start": 50, "end": 10}]
        )
        with pytest.raises(ValueError, match="must be > start"):
            parse_section_import(path)

    def test_parse_bad_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json")
        with pytest.raises(json.JSONDecodeError):
            parse_section_import(path)

    def test_parse_non_numeric_duration(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, duration="abc")
        with pytest.raises(ValueError, match="duration must be a number"):
            parse_section_import(path)

    def test_parse_zero_bpm_raises(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path, bpm=0)
        with pytest.raises(ValueError, match="bpm must be positive"):
            parse_section_import(path)

    def test_parse_blank_section_name_raises(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "   ", "start": 0, "end": 10},
            ],
        )
        with pytest.raises(ValueError, match="name"):
            parse_section_import(path)

    def test_parse_non_numeric_section_start(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "S", "start": "abc", "end": 10},
            ],
        )
        with pytest.raises(ValueError, match="start must be a number"):
            parse_section_import(path)

    def test_parse_non_numeric_section_end(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "S", "start": 0, "end": "abc"},
            ],
        )
        with pytest.raises(ValueError, match="end must be a number"):
            parse_section_import(path)

    def test_parse_non_numeric_section_energy(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "S", "start": 0, "end": 10, "energy": "high"},
            ],
        )
        with pytest.raises(ValueError, match="energy must be a number"):
            parse_section_import(path)

    def test_parse_blank_mood_normalized(self, tmp_path: Path) -> None:
        path = _make_sections_json(
            tmp_path,
            sections=[
                {"name": "S", "start": 0, "end": 10, "mood": "   "},
            ],
        )
        result = parse_section_import(path)
        assert result.sections[0].mood is None

    def test_parse_real_sample(self) -> None:
        path = Path("data/shows/samples/all_in_time_sections.json")
        result = parse_section_import(path)
        assert result.title == "All in Time"
        assert result.artist == "Paul McFartney"
        assert result.duration == 245.0
        assert result.bpm == 120
        assert len(result.sections) == 9
        assert result.sections[3].name == "Chorus"
        assert result.sections[3].energy == 0.9


class TestImportSectionsToSong:
    def test_creates_new_song(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path)
        song = import_sections_to_song(path)
        assert song.title == "Test Song"
        assert song.artist == "Test Artist"
        assert song.duration == 120.0
        assert song.bpm == 128
        assert len(song.sections) == 4

    def test_replaces_existing_song_sections(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path)
        song = Song(title="Old", artist="Oldie", duration=60.0, bpm=100)
        song.add_section(Section(name="Old Section", start=0, end=60))
        result = import_sections_to_song(path, song=song)
        assert result is song
        assert result.title == "Test Song"
        assert result.artist == "Test Artist"
        assert result.duration == 120.0
        assert result.bpm == 128
        assert len(result.sections) == 4
        assert result.sections[0].name == "Intro"

    def test_import_preserves_section_order(self, tmp_path: Path) -> None:
        path = _make_sections_json(tmp_path)
        song = import_sections_to_song(path)
        names = [s.name for s in song.sections]
        assert names == ["Intro", "Verse", "Chorus", "Outro"]


class TestValidateImportData:
    def test_empty_sections(self) -> None:
        with pytest.raises(ValueError, match="no sections"):
            _validate_import_data(
                {
                    "title": "T",
                    "artist": "A",
                    "duration": 60,
                    "sections": [],
                }
            )

    def test_whitespace_title(self) -> None:
        with pytest.raises(ValueError, match="title"):
            _validate_import_data(
                {
                    "title": "   ",
                    "artist": "A",
                    "duration": 60,
                    "sections": [{"name": "S", "start": 0, "end": 60}],
                }
            )
