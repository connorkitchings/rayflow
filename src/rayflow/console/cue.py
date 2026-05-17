"""Typed grandMA3 cue command builders."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Ma3Command:
    """A grandMA3 command-line command."""

    command: str
    label: str | None = None


@dataclass(frozen=True)
class CueStep:
    """One cue programming step."""

    cue: int
    label: str | None = None
    channels: str | None = None
    at: str | None = None
    fade: float | None = None
    clear_after: bool = False


@dataclass(frozen=True)
class CueStack:
    """A lightweight cue stack command input."""

    sequence: int
    name: str
    cues: list[CueStep]


def store_cue(cue: int, label: str | None = None) -> Ma3Command:
    """Build a Store Cue command."""
    _validate_positive_int("cue", cue)
    return Ma3Command(command=f"Store Cue {cue}", label=label)


def label_cue(cue: int, label: str) -> Ma3Command:
    """Build a Label Cue command."""
    _validate_positive_int("cue", cue)
    label = _validate_non_empty("label", label)
    return Ma3Command(command=f'Label Cue {cue} "{label}"', label=label)


def set_cue_time(cue: int, fade: float) -> Ma3Command:
    """Build a Cue Time command."""
    _validate_positive_int("cue", cue)
    if fade < 0:
        raise ValueError("fade must be >= 0")
    return Ma3Command(command=f"Cue {cue} Time {fade:g}")


def go_sequence(sequence: int) -> Ma3Command:
    """Build a Go Sequence command."""
    _validate_positive_int("sequence", sequence)
    return Ma3Command(command=f"Go Sequence {sequence}")


def channel_at(channels: str, value: str) -> Ma3Command:
    """Build a Channel At command."""
    channels = _validate_non_empty("channels", channels)
    value = _validate_non_empty("value", value)
    return Ma3Command(command=f"Channel {channels} At {value}")


def clear_programmer() -> Ma3Command:
    """Build a Clear command."""
    return Ma3Command(command="Clear")


def commands_for_cue_step(step: CueStep) -> list[Ma3Command]:
    """Build commands for one cue step in deterministic order."""
    _validate_positive_int("cue", step.cue)
    commands: list[Ma3Command] = []
    if step.channels is not None or step.at is not None:
        if step.channels is None or step.at is None:
            raise ValueError("cue steps must include both channels and at")
        commands.append(channel_at(step.channels, step.at))
    commands.append(store_cue(step.cue, step.label))
    if step.label:
        commands.append(label_cue(step.cue, step.label))
    if step.fade is not None:
        commands.append(set_cue_time(step.cue, step.fade))
    if step.clear_after:
        commands.append(clear_programmer())
    return commands


def commands_for_cue_stack(stack: CueStack) -> list[Ma3Command]:
    """Build commands for a cue stack in cue order."""
    _validate_positive_int("sequence", stack.sequence)
    commands: list[Ma3Command] = []
    for cue in stack.cues:
        commands.extend(commands_for_cue_step(cue))
    return commands


def load_cue_stack(path: str | Path) -> CueStack:
    """Load a lightweight cue stack JSON file."""
    try:
        payload = json.loads(Path(path).read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid cue stack JSON: {exc}") from exc

    cues = [_cue_step_from_dict(item) for item in payload.get("cues", [])]
    if not cues:
        raise ValueError("cue stack must include at least one cue")
    stack = CueStack(
        sequence=int(payload.get("sequence", 0)),
        name=str(payload.get("name") or ""),
        cues=cues,
    )
    _validate_positive_int("sequence", stack.sequence)
    return stack


def _cue_step_from_dict(payload: dict[str, Any]) -> CueStep:
    return CueStep(
        cue=int(payload.get("cue", 0)),
        label=payload.get("label"),
        channels=payload.get("channels"),
        at=payload.get("at"),
        fade=payload.get("fade"),
        clear_after=bool(payload.get("clear_after", False)),
    )


def _validate_positive_int(name: str, value: int) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be > 0")


def _validate_non_empty(name: str, value: str) -> str:
    if not value.strip():
        raise ValueError(f"{name} must not be empty")
    return value.strip()
