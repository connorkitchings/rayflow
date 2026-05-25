"""Fixture-capability-aware preset generation for shows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rayflow.design.models import Preset, Rig, Show
from rayflow.design.presets import fixture_supports_attribute
from rayflow.engine.fixtures.library import FixtureLibrary

GENERATED_PREFIX = "rf_"


@dataclass(frozen=True)
class PaletteGenerationPlan:
    """A proposed or applied show-specific preset library."""

    show: str
    rig: str
    mode: str
    proposed_presets: list[Preset]
    replaced_override_names: list[str]
    warnings: list[str] = field(default_factory=list)
    next_command: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "show": self.show,
            "rig": self.rig,
            "mode": self.mode,
            "proposed_presets": [preset.as_dict() for preset in self.proposed_presets],
            "replaced_override_names": list(self.replaced_override_names),
            "warnings": list(self.warnings),
            "readiness": {
                "status": "ready" if not self.warnings else "warnings",
                "summary": _readiness_summary(self.warnings),
            },
            "next_command": self.next_command,
        }


def plan_show_palettes(
    show: Show,
    rig: Rig,
    *,
    fixture_dir: str | Path = "data/fixtures/samples",
    apply: bool = False,
) -> PaletteGenerationPlan:
    """Plan or apply a minimal generated preset library as show overrides."""
    warnings: list[str] = []
    capabilities = _rig_capabilities(rig, fixture_dir, warnings)
    channels = _all_channels(rig)
    front_channels, back_channels = _split_channels(rig)

    presets = [
        Preset(
            name=f"{GENERATED_PREFIX}blackout",
            description="Generated blackout across the rig",
            attributes={"dimmer": "0"},
            channels=channels,
            tags=["rayflow", "generated", "dimmer"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}low_wash",
            description="Generated low-intensity wash",
            attributes={"dimmer": "35"},
            channels=channels,
            tags=["rayflow", "generated", "dimmer"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}full_wash",
            description="Generated full-stage wash",
            attributes={"dimmer": "Full"},
            channels=channels,
            tags=["rayflow", "generated", "dimmer"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}warm_front",
            description="Generated warm front color look",
            attributes={"dimmer": "70", "color": "Warm Amber"},
            channels=front_channels,
            tags=["rayflow", "generated", "color", "front"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}cool_back",
            description="Generated cool back color look",
            attributes={"dimmer": "70", "color": "#3366FF"},
            channels=back_channels,
            tags=["rayflow", "generated", "color", "back"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}white_open",
            description="Generated open white look",
            attributes={"dimmer": "80", "color": "White"},
            channels=channels,
            tags=["rayflow", "generated", "color"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}accent_magenta",
            description="Generated accent color look",
            attributes={"dimmer": "75", "color": "#FF33CC"},
            channels=channels,
            tags=["rayflow", "generated", "color", "accent"],
        ),
        Preset(
            name=f"{GENERATED_PREFIX}accent_cyan",
            description="Generated cyan accent look",
            attributes={"dimmer": "75", "color": "#00CCFF"},
            channels=channels,
            tags=["rayflow", "generated", "color", "accent"],
        ),
    ]

    if capabilities["position"]:
        presets.append(
            Preset(
                name=f"{GENERATED_PREFIX}position_center",
                description="Generated centered moving-light position",
                attributes={"position": "center", "dimmer": "70"},
                channels=channels,
                tags=["rayflow", "generated", "position"],
            )
        )
    if capabilities["beam"]:
        presets.append(
            Preset(
                name=f"{GENERATED_PREFIX}beam_narrow",
                description="Generated narrow beam look",
                attributes={"beam": "narrow", "dimmer": "75"},
                channels=channels,
                tags=["rayflow", "generated", "beam"],
            )
        )
    if capabilities["gobo"]:
        presets.append(
            Preset(
                name=f"{GENERATED_PREFIX}gobo_slow",
                description="Generated slow gobo look",
                attributes={"gobo": "50", "dimmer": "70"},
                channels=channels,
                tags=["rayflow", "generated", "gobo"],
            )
        )

    replaced = sorted(
        name for name in show.preset_overrides if name.startswith(GENERATED_PREFIX)
    )
    if apply:
        show.preset_overrides = {
            name: preset
            for name, preset in show.preset_overrides.items()
            if not name.startswith(GENERATED_PREFIX)
        }
        show.preset_overrides.update({preset.name: preset for preset in presets})

    return PaletteGenerationPlan(
        show=show.name,
        rig=rig.name,
        mode="apply" if apply else "proposal",
        proposed_presets=presets,
        replaced_override_names=replaced,
        warnings=warnings,
        next_command=f'rayflow show info "{show.name}" --json',
    )


def _rig_capabilities(
    rig: Rig,
    fixture_dir: str | Path,
    warnings: list[str],
) -> dict[str, bool]:
    capabilities = {"position": False, "beam": False, "gobo": False}
    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as exc:
        warnings.append(f"Fixture library could not be loaded: {exc}")
        return capabilities

    for slot in rig.fixtures:
        parser = library.get(slot.fixture_name)
        if parser is None:
            warnings.append(
                f"Fixture not found for palette capability check: {slot.fixture_name}"
            )
            continue
        mode_idx = 0
        mode_names = parser.mode_names()
        if slot.mode in mode_names:
            mode_idx = mode_names.index(slot.mode)
        for family in capabilities:
            capabilities[family] = capabilities[family] or fixture_supports_attribute(
                parser, mode_idx, family
            )
    return capabilities


def _all_channels(rig: Rig) -> str:
    channel_ids = [slot.channels.strip() for slot in rig.fixtures if slot.channels]
    if not channel_ids:
        return f"1 Thru {max(1, len(rig.fixtures))}"
    if all(item.isdigit() for item in channel_ids):
        return f"1 Thru {len(channel_ids)}"
    return " ".join(channel_ids)


def _split_channels(rig: Rig) -> tuple[str, str]:
    channel_ids = [slot.channels.strip() for slot in rig.fixtures if slot.channels]
    if not channel_ids:
        return _all_channels(rig), _all_channels(rig)
    midpoint = max(1, len(channel_ids) // 2)
    return " ".join(channel_ids[:midpoint]), " ".join(
        channel_ids[midpoint:] or channel_ids
    )


def _readiness_summary(warnings: list[str]) -> str:
    if not warnings:
        return "Palette generation plan is ready to apply."
    return f"Palette generation plan produced {len(warnings)} warning(s)."
