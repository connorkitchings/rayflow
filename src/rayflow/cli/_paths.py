"""Shared path helpers for show CLI modules."""

from __future__ import annotations

from pathlib import Path


def show_dir_path(directory: str) -> Path:
    """Return the configured show directory path."""
    return Path(directory)


def show_path(name: str, directory: Path) -> Path:
    """Return the YAML path for a show name in a directory."""
    return directory / f"{name}.yaml"
