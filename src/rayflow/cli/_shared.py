"""Shared utilities for RayFlow CLI modules."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rayflow.config import config

console = Console()


def resolve_show_name(provided_name: str | None) -> str:
    """Resolve the show name, falling back to the active workspace show."""
    if provided_name:
        return provided_name
    if config.workspace.active_show:
        return config.workspace.active_show
    raise typer.BadParameter(
        "No show name provided and no active show set. "
        "Use 'rayflow show switch <name>' to set an active show."
    )


def resolve_rig_name(provided_name: str | None) -> str | None:
    """Resolve the rig name, falling back to the active workspace rig."""
    if provided_name:
        return provided_name
    if config.workspace.active_rig:
        return config.workspace.active_rig
    return None


def list_yaml_files(directory: Path) -> list[Path]:
    """List YAML files in a directory, sorted by name."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.yaml"))
