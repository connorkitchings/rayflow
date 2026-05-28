"""Push show cues to grandMA3 onPC via OSC."""

from __future__ import annotations

from pathlib import Path

from rayflow.design.models import Cue, Preset, Rig, Show
from rayflow.engine.console.cue import (
    Ma3Command,
    clear_all,
    clear_programmer,
    delete_sequence,
    label_cue,
    label_sequence,
    set_cue_time,
    store_cue,
    store_sequence,
)


def commands_for_show_cue(
    cue: Cue,
    preset: Preset | None = None,
    *,
    sequence: int | None = None,
    rig: Rig | None = None,
    fixture_dir: str | Path = "data/fixtures/samples",
    show: Show | None = None,
) -> list[Ma3Command]:
    """Build OSC commands for a single show cue.

    If *rig* is provided, GDTF attribute mapping is used to generate
    fixture-specific Attribute commands (e.g. ColorAdd_R, Pan, Tilt).
    Otherwise, falls back to safe dimmer/intensity-only commands.
    """
    commands: list[Ma3Command] = []

    if rig is not None and show is not None and rig.fixtures:
        from rayflow.engine.console.cue import channel_at
        from rayflow.engine.fixtures.library import FixtureLibrary
        from rayflow.engine.rendering.dmx import (
            _effective_attributes,
            _effective_channels,
            _render_fixture_attributes,
            _target_fixture_slots,
        )

        library = FixtureLibrary(fixture_dir)
        library.load()

        attributes = _effective_attributes(show, rig, cue)
        target_channels = _effective_channels(show, rig, cue)
        target_slots = _target_fixture_slots(rig, target_channels)

        for slot in target_slots:
            if not slot.channels:
                continue
            parser = library.get(slot.fixture_name)
            if parser is None:
                if "dimmer" in attributes:
                    commands.append(channel_at(slot.channels, attributes["dimmer"]))
                continue
            try:
                channel_map = parser.get_channel_map(
                    mode_name=slot.mode,
                    start_address=slot.start_address,
                    universe=slot.universe,
                )
            except Exception:
                if "dimmer" in attributes:
                    commands.append(channel_at(slot.channels, attributes["dimmer"]))
                continue

            slot_values, _ = _render_fixture_attributes(
                show=show,
                cue=cue,
                slot=slot,
                channel_map=channel_map,
                attributes=attributes,
            )

            # Sort entries by DMX address to keep command output deterministic
            for entry in sorted(channel_map.entries, key=lambda e: e.dmx_address):
                # Skip fine channels (which start with '+')
                if entry.attribute.startswith("+"):
                    continue
                if entry.dmx_address in slot_values:
                    val = slot_values[entry.dmx_address]
                    attr_name = entry.normalized_attribute
                    cmd_str = (
                        f"Fixture {slot.channels} "
                        f'Attribute "{attr_name}" At Absolute Decimal8 {val}'
                    )
                    commands.append(Ma3Command(cmd_str))
    else:
        from rayflow.engine.console.cue import channel_at

        merged_attrs = dict(preset.attributes) if preset else {}
        merged_attrs.update(cue.attributes)

        if merged_attrs:
            channels = (
                cue.channels or (preset.channels if preset else None) or "1 Thru 512"
            )
            for attr_family, value in merged_attrs.items():
                if attr_family.lower() not in {"dimmer", "intensity"}:
                    continue
                commands.append(channel_at(channels, value))

    commands.append(store_cue(cue.number, cue.label, sequence=sequence))
    if cue.label:
        commands.append(label_cue(cue.number, cue.label, sequence=sequence))
    if cue.fade_time > 0:
        commands.append(set_cue_time(cue.number, cue.fade_time, sequence=sequence))

    commands.append(clear_programmer())
    return commands


def commands_for_show(
    show: Show,
    presets: dict[str, Preset],
    *,
    section: str | None = None,
    sequence: int | None = None,
    rig: Rig | None = None,
    fixture_dir: str | Path = "data/fixtures/samples",
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
        all_commands.extend(
            commands_for_show_cue(
                cue,
                preset,
                sequence=sequence,
                rig=rig,
                fixture_dir=fixture_dir,
                show=show,
            )
        )

    return all_commands


def _sequence_setup_commands(sequence: int, label: str) -> list[Ma3Command]:
    """Build sequence management commands: tear down, create, label, reset."""
    return [
        delete_sequence(sequence),
        store_sequence(sequence),
        label_sequence(sequence, label),
        clear_all(),
    ]
