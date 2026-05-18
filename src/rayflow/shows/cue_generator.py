"""Cue generation helpers for AI-assisted show building."""

from __future__ import annotations

from rayflow.shows.models import Cue, Show


def auto_number_cues(show: Show) -> Show:
    """Renumber all cues sequentially starting from 1, preserving order."""
    show.cues.sort(key=lambda c: (c.timestamp, c.number))
    for i, cue in enumerate(show.cues):
        cue.number = i + 1
    return show


def generate_cues_for_section(
    show: Show,
    section_name: str,
    preset: str | None = None,
    count: int = 4,
    spacing: float = 5.0,
    attributes: dict[str, str] | None = None,
    channels: str | None = None,
    fade_time: float = 0.0,
    base_label: str | None = None,
) -> list[Cue]:
    """Generate evenly spaced cues for a song section.

    Returns the list of generated Cue objects. They are NOT added to the show
    automatically — use show.add_cue() or the CLI for that.
    """
    section = None
    for s in show.song.sections:
        if s.name == section_name:
            section = s
            break
    if section is None:
        raise ValueError(f"Section not found: {section_name}")

    start = section.start
    end = section.end
    duration = end - start

    if count < 1:
        raise ValueError(f"count must be >= 1, got {count}")
    if spacing <= 0:
        raise ValueError(f"spacing must be > 0, got {spacing}")
    if duration <= 0:
        raise ValueError(f"Section duration must be > 0, got {duration}")

    if base_label is None:
        base_label = section_name

    cues: list[Cue] = []
    for i in range(count):
        timestamp = start + i * spacing
        if timestamp >= end:
            break

        label = f"{base_label} {i + 1}"
        if preset:
            label = f"{preset} {i + 1}"

        cue = Cue(
            number=i + 1,
            label=label,
            section=section_name,
            timestamp=round(timestamp, 2),
            preset=preset,
            channels=channels,
            attributes=dict(attributes) if attributes else {},
            fade_time=fade_time,
        )
        cues.append(cue)

    return cues


def generate_cues_for_show(
    show: Show,
    section_presets: dict[str, str],
    cues_per_section: int = 4,
    spacing: float = 5.0,
    fade_time: float = 0.0,
) -> Show:
    """Generate cues for every section in the show using preset mapping.

    section_presets maps section_name -> preset_name.
    Existing cues are replaced.
    """
    show.cues.clear()

    next_number = 1
    for section in show.song.sections:
        preset = section_presets.get(section.name)
        generated = generate_cues_for_section(
            show,
            section.name,
            preset=preset,
            count=cues_per_section,
            spacing=spacing,
            fade_time=fade_time,
        )
        for cue in generated:
            cue.number = next_number
            next_number += 1
            show.cues.append(cue)

    return show


def delete_cues_for_section(show: Show, section_name: str) -> int:
    """Remove all cues belonging to a section. Returns count of deleted cues."""
    old_count = len(show.cues)
    show.cues = [c for c in show.cues if c.section != section_name]
    deleted = old_count - len(show.cues)
    auto_number_cues(show)
    return deleted


def update_cue(
    show: Show,
    cue_number: int,
    *,
    label: str | None = None,
    timestamp: float | None = None,
    preset: str | None = None,
    channels: str | None = None,
    attributes: dict[str, str] | None = None,
    fade_time: float | None = None,
    follow_time: float | None = None,
    notes: str | None = None,
    section: str | None = None,
) -> Cue:
    """Update fields on an existing cue. Returns the modified cue."""
    cue = show.get_cue(cue_number)
    if cue is None:
        raise ValueError(f"Cue not found: {cue_number}")

    if label is not None:
        cue.label = label
    if timestamp is not None:
        if timestamp < 0:
            raise ValueError(f"Timestamp must be >= 0, got {timestamp}")
        cue.timestamp = timestamp
    if preset is not None:
        cue.preset = preset
    if channels is not None:
        cue.channels = channels
    if attributes is not None:
        cue.attributes = dict(attributes)
    if fade_time is not None:
        if fade_time < 0:
            raise ValueError(f"Fade time must be >= 0, got {fade_time}")
        cue.fade_time = fade_time
    if follow_time is not None:
        cue.follow_time = follow_time
    if notes is not None:
        cue.notes = notes
    if section is not None:
        cue.section = section

    return cue


def remove_cue(show: Show, cue_number: int) -> Cue:
    """Remove a cue by number. Returns the removed cue."""
    cue = show.get_cue(cue_number)
    if cue is None:
        raise ValueError(f"Cue not found: {cue_number}")
    show.cues = [c for c in show.cues if c.number != cue_number]
    return cue


def batch_update_cues(
    show: Show,
    *,
    section: str | None = None,
    attributes: dict[str, str] | None = None,
    set_fade: float | None = None,
    set_preset: str | None = None,
    delete: bool = False,
) -> int:
    """Batch update or delete cues matching a filter.

    Returns the count of cues affected.
    """
    targets = show.cues
    if section is not None:
        targets = [c for c in targets if c.section == section]

    if delete:
        for cue in targets:
            show.cues = [c for c in show.cues if c.number != cue.number]
        auto_number_cues(show)
        return len(targets)

    count = 0
    for cue in targets:
        if set_preset is not None:
            cue.preset = set_preset
            count += 1
        if attributes is not None:
            cue.attributes.update(attributes)
            count += 1
        if set_fade is not None:
            if set_fade < 0:
                raise ValueError(f"Fade time must be >= 0, got {set_fade}")
            cue.fade_time = set_fade
            count += 1

    return count
