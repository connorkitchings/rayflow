"""Tests for versioned show library storage."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from rayflow.shows.library import (
    diff_show_version,
    list_show_versions,
    restore_show_version,
    save_show_version,
)


def _write_show(path: Path, title: str = "Song") -> None:
    path.write_text(
        f"""name: "Library Show"
rig_name: "Test Rig"
song:
  title: "{title}"
  artist: "Artist"
  duration: 180
cues:
  - number: 1
    label: "First"
    section: "Intro"
    timestamp: 0
""",
        encoding="utf-8",
    )


def test_save_show_version_writes_snapshot_and_metadata(tmp_path: Path) -> None:
    show_path = tmp_path / "Library Show.yaml"
    _write_show(show_path)
    library_dir = tmp_path / "library"
    created = datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc)

    saved = save_show_version(
        show_path,
        library_dir=library_dir,
        message="first version",
        created_at=created,
    )

    assert saved.metadata.version_id == "20260520T120000Z"
    assert saved.metadata.show_name == "Library Show"
    assert saved.metadata.cue_count == 1
    assert saved.metadata.message == "first version"
    assert saved.show_path.exists()
    assert saved.metadata_path.exists()


def test_list_show_versions_newest_first(tmp_path: Path) -> None:
    show_path = tmp_path / "Library Show.yaml"
    _write_show(show_path)
    library_dir = tmp_path / "library"

    save_show_version(
        show_path,
        library_dir=library_dir,
        created_at=datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc),
    )
    save_show_version(
        show_path,
        library_dir=library_dir,
        created_at=datetime(2026, 5, 20, 12, 1, 0, tzinfo=timezone.utc),
    )

    versions = list_show_versions("Library Show", library_dir=library_dir)

    assert [v.version_id for v in versions] == [
        "20260520T120100Z",
        "20260520T120000Z",
    ]


def test_restore_show_version_requires_force_for_changed_target(tmp_path: Path) -> None:
    show_path = tmp_path / "Library Show.yaml"
    _write_show(show_path)
    library_dir = tmp_path / "library"
    saved = save_show_version(
        show_path,
        library_dir=library_dir,
        created_at=datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc),
    )
    _write_show(show_path, title="Changed Song")

    with pytest.raises(FileExistsError):
        restore_show_version(
            "Library Show",
            saved.metadata.version_id,
            target_path=show_path,
            library_dir=library_dir,
        )

    restored = restore_show_version(
        "Library Show",
        saved.metadata.version_id,
        target_path=show_path,
        library_dir=library_dir,
        force=True,
    )
    assert restored == show_path
    assert 'title: "Song"' in show_path.read_text(encoding="utf-8")


def test_diff_show_version_against_current_show(tmp_path: Path) -> None:
    show_path = tmp_path / "Library Show.yaml"
    _write_show(show_path)
    library_dir = tmp_path / "library"
    saved = save_show_version(
        show_path,
        library_dir=library_dir,
        created_at=datetime(2026, 5, 20, 12, 0, 0, tzinfo=timezone.utc),
    )
    _write_show(show_path, title="Changed Song")

    diff = diff_show_version(
        "Library Show",
        saved.metadata.version_id,
        current_path=show_path,
        library_dir=library_dir,
    )

    assert "--- Library Show@20260520T120000Z" in diff
    assert f"+++ {show_path}" in diff
    assert '-  title: "Song"' in diff
    assert '+  title: "Changed Song"' in diff
