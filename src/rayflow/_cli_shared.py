"""Shared utilities for RayFlow CLI modules."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

console = Console()


def list_yaml_files(directory: Path) -> list[Path]:
    """List YAML files in a directory, sorted by name."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.yaml"))
