"""Deterministic practice-show cue planning."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from rayflow.shows.cue_generator import auto_number_cues
from rayflow.shows.models import Cue, Rig, Section, Show

PracticeCueStyle = Literal["energy-arc", "warm-cool", "front-back"]

SUPPORTED_STYLES: tuple[PracticeCueStyle, ...] = (
    "energy-arc",
    "warm-cool",
    "front-back",
)
SUPPORTED_ATTRIBUTES = frozenset({"dimmer", "color"})


@dataclass(frozen=True)
class PracticeCuePlan:
    """Proposed deterministic cue edits for a practice show."""

    show: str
    rig: str
    section: str
    style: PracticeCueStyle
    mode: Literal["proposal", "apply"]
    proposed_cues: list[Cue]
    replaced_cue_numbers: list[int]
    warnings: list[str] = field(default_factory=list)
    next_command: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "show": self.show,
            "rig": self.rig,
            "section": self.section,
            "mode": self.mode,
            "style": self.style,
            "proposed_cues": [cue.as_dict() for cue in self.proposed_cues],
            "replaced_cue_numbers": list(self.replaced_cue_numbers),
            "warnings": list(self.warnings),
            "readiness": {
                "status": "ready" if not self.warnings else "warnings",
                "summary": _readiness_summary(self.warnings),
            },
            "next_command": self.next_command,
        }


def plan_practice_cues(
    show: Show,
    rig: Rig,
    *,
    section_name: str = "all",
    style: str = "energy-arc",
    apply: bool = False,
) -> PracticeCuePlan:
    """Plan or apply deterministic fixture-safe practice cues."""
    cue_style = _parse_style(style)
    selected_sections = _selected_sections(show, section_name)
    replaced_cue_numbers = [
        cue.number
        for cue in show.cues
        if section_name.lower() == "all" or cue.section == section_name
    ]
    proposed = _generate_cues(show, rig, selected_sections, cue_style)
    warnings = _plan_warnings(proposed)
    next_command = (
        f'rayflow show workflow-report {show.name} --rig "{rig.name}" '
        f"--section {section_name} --json"
    )

    if apply:
        selected_names = {section.name for section in selected_sections}
        show.cues = [cue for cue in show.cues if cue.section not in selected_names]
        show.cues.extend(proposed)
        auto_number_cues(show)
        proposed = [cue for cue in show.cues if cue.section in selected_names]

    return PracticeCuePlan(
        show=show.name,
        rig=rig.name,
        section=section_name,
        style=cue_style,
        mode="apply" if apply else "proposal",
        proposed_cues=proposed,
        replaced_cue_numbers=sorted(replaced_cue_numbers),
        warnings=warnings,
        next_command=next_command,
    )


def _parse_style(style: str) -> PracticeCueStyle:
    normalized = style.strip().lower()
    if normalized not in SUPPORTED_STYLES:
        supported = ", ".join(SUPPORTED_STYLES)
        raise ValueError(f"Unsupported practice cue style: {style}. Use {supported}.")
    return normalized  # type: ignore[return-value]


def _selected_sections(show: Show, section_name: str) -> list[Section]:
    if section_name.lower() == "all":
        if not show.song.sections:
            raise ValueError("Show has no song sections")
        return list(show.song.sections)

    for section in show.song.sections:
        if section.name == section_name:
            return [section]
    raise ValueError(f"Section not found: {section_name}")


def _generate_cues(
    show: Show,
    rig: Rig,
    sections: list[Section],
    style: PracticeCueStyle,
) -> list[Cue]:
    cues: list[Cue] = []
    next_number = 1
    for section in sections:
        looks = _section_looks(section, style)
        for index, look in enumerate(looks):
            timestamp = _cue_timestamp(section, index, len(looks))
            cues.append(
                Cue(
                    number=next_number,
                    label=f"{section.name} {look['label']}",
                    section=section.name,
                    timestamp=timestamp,
                    channels=_channels_for_style(rig, style, index),
                    preset=look.get("preset"),
                    attributes={
                        "dimmer": str(look["dimmer"]),
                        "color": str(look["color"]),
                    },
                    fade_time=float(look["fade_time"]),
                )
            )
            next_number += 1
    return cues


def _section_looks(
    section: Section, style: PracticeCueStyle
) -> list[dict[str, str | int | float]]:
    energy = section.energy if section.energy is not None else 0.5
    dimmer = _energy_to_dimmer(energy)
    secondary = max(20, min(100, dimmer + 12))
    if style == "warm-cool":
        return [
            _look("Warm Front", dimmer, "Warm Amber", 2.0),
            _look("Cool Lift", secondary, "#3366FF", 1.5),
        ]
    if style == "front-back":
        return [
            _look("Front Warm", dimmer, "Warm Amber", 2.0, "front_warm"),
            _look("Back Blue", secondary, "#3366FF", 1.5, "back_blue"),
        ]
    return [
        _look("Energy Base", dimmer, _energy_color(energy), 2.0),
        _look("Energy Lift", secondary, _energy_lift_color(energy), 1.0),
    ]


def _look(
    label: str,
    dimmer: int,
    color: str,
    fade_time: float,
    preset: str | None = None,
) -> dict[str, str | int | float]:
    result: dict[str, str | int | float] = {
        "label": label,
        "dimmer": dimmer,
        "color": color,
        "fade_time": fade_time,
    }
    if preset:
        result["preset"] = preset
    return result


def _cue_timestamp(section: Section, index: int, count: int) -> float:
    if count <= 1:
        return round(section.start, 2)
    spacing = (section.end - section.start) / count
    return round(section.start + index * spacing, 2)


def _energy_to_dimmer(energy: float) -> int:
    bounded = max(0.0, min(1.0, energy))
    return int(round(25 + bounded * 70))


def _energy_color(energy: float) -> str:
    if energy < 0.35:
        return "Warm Amber"
    if energy < 0.7:
        return "#3366FF"
    return "#00CCFF"


def _energy_lift_color(energy: float) -> str:
    if energy < 0.35:
        return "#3366FF"
    if energy < 0.7:
        return "#00CCFF"
    return "White"


def _channels_for_style(rig: Rig, style: PracticeCueStyle, index: int) -> str:
    channel_numbers = [
        slot.channels
        for slot in rig.fixtures
        if slot.channels is not None and slot.channels.strip().isdigit()
    ]
    if not channel_numbers:
        return "1 Thru 4"
    if style == "front-back" and len(channel_numbers) >= 4:
        midpoint = len(channel_numbers) // 2
        selected = (
            channel_numbers[:midpoint] if index == 0 else channel_numbers[midpoint:]
        )
        return " ".join(selected)
    return f"1 Thru {len(channel_numbers)}"


def _plan_warnings(cues: list[Cue]) -> list[str]:
    warnings: list[str] = []
    for cue in cues:
        unsupported = set(cue.attributes) - SUPPORTED_ATTRIBUTES
        if unsupported:
            warnings.append(
                f"Cue {cue.number} has unsupported attributes: "
                f"{', '.join(sorted(unsupported))}"
            )
    return warnings


def _readiness_summary(warnings: list[str]) -> str:
    if not warnings:
        return "Practice cue plan uses renderer-supported attributes only."
    return f"Practice cue plan produced {len(warnings)} warning(s)."
