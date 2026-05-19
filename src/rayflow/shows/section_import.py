"""Import audio section markers from external analysis tools."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rayflow.shows.models import Section, Song


@dataclass
class SectionImportResult:
    """Result of importing section markers from an external tool."""

    title: str
    artist: str
    duration: float
    bpm: float | None = None
    sections: list[Section] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_section_import(path: str | Path) -> SectionImportResult:
    """Parse a section-import JSON file and return validated data.

    The JSON format supports multiple audio analysis tool outputs
    (Mixed In Key, rekordbox, Ableton, etc.) through a common schema:

    {
      "title": "Song Title",
      "artist": "Artist Name",
      "duration": 245.0,
      "bpm": 120.0,
      "sections": [
        {"name": "Intro", "start": 0.0, "end": 15.0, "energy": 0.3, "mood": "ambient"},
        {"name": "Verse 1", "start": 15.0, "end": 45.0, "energy": 0.5, "mood": "mellow"}
      ]
    }
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return _validate_import_data(raw, source=Path(path).name)


def import_sections_to_song(
    import_path: str | Path,
    song: Song | None = None,
) -> Song:
    """Import section markers into a Song object.

    If song is provided, its sections are replaced with the imported ones.
    The song's title, artist, duration, and bpm are updated from the import.
    """
    result = parse_section_import(import_path)

    if song is None:
        song = Song(
            title=result.title,
            artist=result.artist,
            duration=result.duration,
            bpm=result.bpm,
        )
    else:
        song.title = result.title
        song.artist = result.artist
        song.duration = result.duration
        song.bpm = result.bpm
        song.sections.clear()

    for section in result.sections:
        song.add_section(section)

    return song


def _validate_import_data(
    data: dict[str, Any],
    *,
    source: str = "input",
) -> SectionImportResult:
    """Validate raw JSON import data and produce a SectionImportResult."""
    warnings: list[str] = []

    title = data.get("title")
    if not title or not str(title).strip():
        raise ValueError("Import file is missing required 'title' field")
    title = str(title).strip()

    artist = data.get("artist")
    if not artist or not str(artist).strip():
        raise ValueError("Import file is missing required 'artist' field")
    artist = str(artist).strip()

    duration = data.get("duration")
    if duration is None:
        raise ValueError("Import file is missing required 'duration' field")
    try:
        duration = float(duration)
    except (TypeError, ValueError):
        raise ValueError(f"duration must be a number, got {duration!r}")
    if duration <= 0:
        raise ValueError(f"duration must be positive, got {duration}")

    bpm = data.get("bpm")
    if bpm is not None:
        try:
            bpm = float(bpm)
        except (TypeError, ValueError):
            raise ValueError(f"bpm must be a number, got {bpm!r}")
        if bpm <= 0:
            raise ValueError(f"bpm must be positive, got {bpm}")

    raw_sections = data.get("sections", [])
    if not raw_sections:
        raise ValueError("Import file has no sections")

    sections: list[Section] = []
    section_names: set[str] = set()
    for i, s_raw in enumerate(raw_sections):
        sec_name = s_raw.get("name")
        if not sec_name or not str(sec_name).strip():
            raise ValueError(f"Section {i}: missing required 'name' field")
        sec_name = str(sec_name).strip()
        if sec_name in section_names:
            raise ValueError(f"Duplicate section name: {sec_name}")
        section_names.add(sec_name)

        sec_start = s_raw.get("start")
        if sec_start is None:
            raise ValueError(f"Section '{sec_name}': missing required 'start' field")
        try:
            sec_start = float(sec_start)
        except (TypeError, ValueError):
            raise ValueError(
                f"Section '{sec_name}': start must be a number, got {sec_start!r}"
            )

        sec_end = s_raw.get("end")
        if sec_end is None:
            raise ValueError(f"Section '{sec_name}': missing required 'end' field")
        try:
            sec_end = float(sec_end)
        except (TypeError, ValueError):
            raise ValueError(
                f"Section '{sec_name}': end must be a number, got {sec_end!r}"
            )

        energy = s_raw.get("energy")
        if energy is not None:
            try:
                energy = float(energy)
            except (TypeError, ValueError):
                raise ValueError(
                    f"Section '{sec_name}': energy must be a number, got {energy!r}"
                )
            if not (0 <= energy <= 1):
                raise ValueError(
                    f"Section '{sec_name}': energy must be 0-1, got {energy}"
                )

        mood = s_raw.get("mood")
        if mood is not None and not str(mood).strip():
            mood = None

        try:
            section = Section(
                name=sec_name,
                start=sec_start,
                end=sec_end,
                energy=energy,
                mood=mood,
            )
        except ValueError as e:
            raise ValueError(f"Section '{sec_name}': {e}")

        if sec_end > duration:
            warnings.append(
                f"Section '{sec_name}' end ({sec_end}s) exceeds song duration "
                f"({duration}s)"
            )

        sections.append(section)

    return SectionImportResult(
        title=title,
        artist=artist,
        duration=float(duration),
        bpm=float(bpm) if bpm is not None else None,
        sections=sections,
        warnings=warnings,
    )
