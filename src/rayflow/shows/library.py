"""Versioned show snapshot storage."""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import yaml

from rayflow import __version__
from rayflow.shows.serializers import load_show

TIMESTAMP_FORMAT = "%Y%m%dT%H%M%SZ"


@dataclass(frozen=True)
class ShowVersion:
    """Metadata for one saved show version."""

    version_id: str
    show_name: str
    source_path: str
    created_at: str
    rayflow_version: str
    cue_count: int
    message: str | None = None

    @classmethod
    def from_dict(cls, data: dict) -> ShowVersion:
        return cls(
            version_id=data["version_id"],
            show_name=data["show_name"],
            source_path=data["source_path"],
            created_at=data["created_at"],
            rayflow_version=data["rayflow_version"],
            cue_count=int(data["cue_count"]),
            message=data.get("message"),
        )

    def as_dict(self) -> dict:
        result = {
            "version_id": self.version_id,
            "show_name": self.show_name,
            "source_path": self.source_path,
            "created_at": self.created_at,
            "rayflow_version": self.rayflow_version,
            "cue_count": self.cue_count,
        }
        if self.message:
            result["message"] = self.message
        return result


@dataclass(frozen=True)
class SavedShowVersion:
    """Paths and metadata for a saved show snapshot."""

    metadata: ShowVersion
    version_dir: Path
    show_path: Path
    metadata_path: Path


def save_show_version(
    show_path: str | Path,
    *,
    library_dir: str | Path = "data/show_library",
    message: str | None = None,
    created_at: datetime | None = None,
) -> SavedShowVersion:
    """Save an immutable snapshot of a show YAML file."""
    source = Path(show_path)
    if not source.exists():
        raise FileNotFoundError(f"Show not found: {source}")

    show = load_show(source)
    timestamp = created_at or datetime.now(timezone.utc)
    version_id = timestamp.astimezone(timezone.utc).strftime(TIMESTAMP_FORMAT)
    version_dir = _version_dir(library_dir, show.name, version_id)
    if version_dir.exists():
        raise FileExistsError(f"Show version already exists: {version_id}")
    version_dir.mkdir(parents=True)

    snapshot_path = version_dir / "show.yaml"
    snapshot_path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    metadata = ShowVersion(
        version_id=version_id,
        show_name=show.name,
        source_path=str(source),
        created_at=timestamp.astimezone(timezone.utc).isoformat(),
        rayflow_version=__version__,
        cue_count=len(show.cues),
        message=message,
    )
    metadata_path = version_dir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata.as_dict(), indent=2) + "\n",
        encoding="utf-8",
    )

    return SavedShowVersion(
        metadata=metadata,
        version_dir=version_dir,
        show_path=snapshot_path,
        metadata_path=metadata_path,
    )


def list_show_versions(
    show_name: str,
    *,
    library_dir: str | Path = "data/show_library",
) -> list[ShowVersion]:
    """List saved versions for a show, newest first."""
    show_dir = _show_library_dir(library_dir, show_name)
    if not show_dir.exists():
        return []

    versions = []
    for metadata_path in sorted(show_dir.glob("*/metadata.json")):
        data = json.loads(metadata_path.read_text(encoding="utf-8"))
        versions.append(ShowVersion.from_dict(data))
    return sorted(versions, key=lambda version: version.version_id, reverse=True)


def restore_show_version(
    show_name: str,
    version_id: str,
    *,
    target_path: str | Path,
    library_dir: str | Path = "data/show_library",
    force: bool = False,
) -> Path:
    """Restore a saved version to a show YAML path."""
    snapshot_path = _snapshot_path(library_dir, show_name, version_id)
    if not snapshot_path.exists():
        raise FileNotFoundError(f"Show version not found: {show_name} {version_id}")

    target = Path(target_path)
    snapshot_text = snapshot_path.read_text(encoding="utf-8")
    if target.exists() and target.read_text(encoding="utf-8") != snapshot_text:
        if not force:
            raise FileExistsError(
                f"Target show differs from version {version_id}; pass --force"
            )

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(snapshot_text, encoding="utf-8")
    return target


def diff_show_version(
    show_name: str,
    version_id: str,
    *,
    current_path: str | Path | None = None,
    other_version_id: str | None = None,
    library_dir: str | Path = "data/show_library",
) -> str:
    """Return a unified YAML diff for a saved show version."""
    left_path = _snapshot_path(library_dir, show_name, version_id)
    if not left_path.exists():
        raise FileNotFoundError(f"Show version not found: {show_name} {version_id}")

    if other_version_id is not None:
        right_path = _snapshot_path(library_dir, show_name, other_version_id)
        right_label = f"{show_name}@{other_version_id}"
        if not right_path.exists():
            raise FileNotFoundError(
                f"Show version not found: {show_name} {other_version_id}"
            )
    elif current_path is not None:
        right_path = Path(current_path)
        right_label = str(right_path)
        if not right_path.exists():
            raise FileNotFoundError(f"Show not found: {right_path}")
    else:
        raise ValueError("current_path or other_version_id is required")

    left_lines = left_path.read_text(encoding="utf-8").splitlines(keepends=True)
    right_lines = right_path.read_text(encoding="utf-8").splitlines(keepends=True)
    return "".join(
        difflib.unified_diff(
            left_lines,
            right_lines,
            fromfile=f"{show_name}@{version_id}",
            tofile=right_label,
        )
    )


def show_library_name(show_name: str) -> str:
    """Convert a show name to a stable library directory name."""
    safe = "-".join(show_name.lower().split())
    return "".join(ch for ch in safe if ch.isalnum() or ch in {"-", "_"})


def _show_library_dir(library_dir: str | Path, show_name: str) -> Path:
    return Path(library_dir) / show_library_name(show_name)


def _version_dir(library_dir: str | Path, show_name: str, version_id: str) -> Path:
    return _show_library_dir(library_dir, show_name) / version_id


def _snapshot_path(library_dir: str | Path, show_name: str, version_id: str) -> Path:
    return _version_dir(library_dir, show_name, version_id) / "show.yaml"


def metadata_to_yaml(version: ShowVersion) -> str:
    """Format version metadata for CLI display."""
    return yaml.dump(version.as_dict(), default_flow_style=False, sort_keys=False)
