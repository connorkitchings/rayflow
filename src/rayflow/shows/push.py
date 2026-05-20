"""Push show cues to grandMA3 onPC via OSC."""

from __future__ import annotations

from rayflow.console.cue import (
    Ma3Command,
    channel_at,
    clear_all,
    clear_programmer,
    delete_sequence,
    label_cue,
    label_sequence,
    set_cue_time,
    store_cue,
    store_sequence,
)
from rayflow.shows.models import Cue, Preset, Show


def commands_for_show_cue(
    cue: Cue,
    preset: Preset | None = None,
) -> list[Ma3Command]:
    """Build OSC commands for a single show cue.

    If a preset is provided, its attributes are used for channel_at.
    Cue-level attributes override preset attributes.
    """
    commands: list[Ma3Command] = []

    merged_attrs = dict(preset.attributes) if preset else {}
    merged_attrs.update(cue.attributes)

    if merged_attrs:
        channels = cue.channels or (preset.channels if preset else None) or "1 Thru 512"
        for attr_family, value in merged_attrs.items():
            commands.append(channel_at(channels, value))

    commands.append(store_cue(cue.number, cue.label))
    if cue.label:
        commands.append(label_cue(cue.number, cue.label))
    if cue.fade_time > 0:
        commands.append(set_cue_time(cue.number, cue.fade_time))

    commands.append(clear_programmer())
    return commands


def commands_for_show(
    show: Show,
    presets: dict[str, Preset],
    *,
    section: str | None = None,
    sequence: int | None = None,
) -> list[Ma3Command]:
    """Build OSC commands for all cues in a show (or filtered by section).

    When *sequence* is provided, prepend sequence management commands:
    delete existing, create, label from song title, then ClearAll before
    cue programming so Store Cue targets the intended sequence.
    """
    cues = show.cues
    if section is not None:
        cues = [c for c in cues if c.section == section]

    sorted_cues = sorted(cues, key=lambda c: (c.timestamp, c.number))

    all_commands: list[Ma3Command] = []

    if sequence is not None:
        if sequence <= 0:
            raise ValueError("sequence must be > 0")
        all_commands.extend(_sequence_setup_commands(sequence, show.song.title))

    for cue in sorted_cues:
        preset = None
        if cue.preset and cue.preset in presets:
            preset = presets[cue.preset]
        all_commands.extend(commands_for_show_cue(cue, preset))

    return all_commands


def _sequence_setup_commands(sequence: int, label: str) -> list[Ma3Command]:
    """Build sequence management commands: tear down, create, label, reset."""
    return [
        delete_sequence(sequence),
        store_sequence(sequence),
        label_sequence(sequence, label),
        clear_all(),
    ]
