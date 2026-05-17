"""AI context bundle builder for show context command."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rayflow.fixtures.library import FixtureLibrary
from rayflow.shows.models import Rig, Show
from rayflow.shows.presets import (
    ATTRIBUTE_FAMILIES,
    fixture_supports_attribute,
)

AVAILABLE_ACTIONS: dict[str, list[str]] = {
    "read": [
        "read_rig",
        "read_show",
        "list_presets",
        "get_fixture_capabilities",
        "get_cues_for_section",
    ],
    "write": [
        "add_cue",
        "update_cue",
        "delete_cue",
        "add_preset",
        "set_vibe",
        "save_show",
        "add_preset_override",
    ],
    "push": [
        "push_to_ma3",
        "push_section_to_ma3",
        "export_mvr",
    ],
    "analysis": [
        "check_dmx_conflicts",
        "suggest_cue_times",
        "validate_preset_coverage",
    ],
    "console_commands": [
        "store_cue",
        "label_cue",
        "set_cue_time",
        "go_sequence",
        "channel_at",
        "clear_programmer",
    ],
}


def build_context_bundle(
    show: Show,
    rig: Rig,
    fixture_dir: str | Path,
) -> dict[str, Any]:
    """Build the full AI context bundle for a show.

    Includes show data, rig data, merged presets, fixture capabilities,
    and available actions.
    """
    from rayflow.shows.models import resolve_presets

    fixture_path = Path(fixture_dir)
    library = FixtureLibrary(fixture_path)
    library.load()

    fixture_capabilities: dict[str, Any] = {}
    for slot in rig.fixtures:
        parser = library.get(slot.fixture_name)
        if parser is None:
            continue

        mode_idx = 0
        mode_names = parser.mode_names()
        if slot.mode in mode_names:
            mode_idx = mode_names.index(slot.mode)

        supported = [
            attr
            for attr in sorted(ATTRIBUTE_FAMILIES)
            if fixture_supports_attribute(parser, mode_idx, attr)
        ]

        channels = parser.get_channels_as_dict(mode_idx)
        fixture_capabilities[slot.fixture_name] = {
            "label": slot.label,
            "mode": slot.mode,
            "supported_attributes": supported,
            "channel_count": len(channels),
            "channels": channels,
        }

    merged_presets = resolve_presets(rig, show)

    return {
        "show": show.as_dict(),
        "rig": rig.as_dict(),
        "presets": {name: p.as_dict() for name, p in merged_presets.items()},
        "fixture_capabilities": fixture_capabilities,
        "available_actions": AVAILABLE_ACTIONS,
    }
