"""General deterministic cue authoring helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from rayflow.design.cue_generator import auto_number_cues
from rayflow.design.models import Cue, Rig, Section, Show

AuthoringStyle = Literal[
    "energy-arc",
    "warm-cool",
    "front-back",
    "vibe-palette",
    "movement-sweep",
    "movement-circle",
    "movement-figure8",
    "beam-chase",
]

SUPPORTED_AUTHORING_STYLES: tuple[AuthoringStyle, ...] = (
    "energy-arc",
    "warm-cool",
    "front-back",
    "vibe-palette",
    "movement-sweep",
    "movement-circle",
    "movement-figure8",
    "beam-chase",
)
SUPPORTED_ATTRIBUTES = frozenset(
    {
        "dimmer",
        "color",
        "pan",
        "tilt",
        "zoom",
        "focus",
        "shutter",
        "gobo",
        "movement.type",
        "movement.speed",
        "movement.center",
        "movement.size",
        "gobo.speed",
        "gobo.rotation",
    }
)
FALLBACK_PALETTE = ("Warm Amber", "#3366FF", "#00CCFF", "White")


@dataclass(frozen=True)
class CueAuthoringPlan:
    """Proposed deterministic cue edits for a RayFlow show."""

    show: str
    rig: str
    section: str
    style: AuthoringStyle
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


def plan_cues(
    show: Show,
    rig: Rig,
    *,
    section_name: str = "all",
    style: str = "energy-arc",
    cues_per_section: int = 2,
    apply: bool = False,
) -> CueAuthoringPlan:
    """Plan or apply deterministic renderer-safe cues for any RayFlow show."""
    cue_style = _parse_style(style)
    if cues_per_section < 1:
        raise ValueError(f"cues_per_section must be >= 1, got {cues_per_section}")

    selected_sections = _selected_sections(show, section_name)
    selected_names = {section.name for section in selected_sections}
    replacing_all = section_name.lower() == "all"
    replaced_cue_numbers = [
        cue.number
        for cue in show.cues
        if replacing_all or cue.section in selected_names
    ]
    warnings: list[str] = []
    proposed = _generate_cues(
        show,
        rig,
        selected_sections,
        cue_style,
        cues_per_section,
        warnings,
    )
    warnings.extend(_plan_warnings(proposed))
    next_command = (
        f'rayflow show workflow-report {show.name} --rig "{rig.name}" '
        f"--section {section_name} --json"
    )

    if apply:
        show.cues = [cue for cue in show.cues if cue.section not in selected_names]
        show.cues.extend(proposed)
        auto_number_cues(show)
        proposed = [cue for cue in show.cues if cue.section in selected_names]

    return CueAuthoringPlan(
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


def _parse_style(style: str) -> AuthoringStyle:
    normalized = style.strip().lower()
    if normalized not in SUPPORTED_AUTHORING_STYLES:
        supported = ", ".join(SUPPORTED_AUTHORING_STYLES)
        raise ValueError(f"Unsupported cue authoring style: {style}. Use {supported}.")
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
    style: AuthoringStyle,
    cues_per_section: int,
    warnings: list[str],
) -> list[Cue]:
    cues: list[Cue] = []
    next_number = 1
    channel_groups = _fixture_channel_groups(rig)
    if not channel_groups:
        warnings.append(
            "Rig has no fixture channel groups; using broad channel fallback."
        )

    for section in sections:
        looks = _section_looks(show, section, style, cues_per_section, warnings)
        for index, look in enumerate(looks):
            timestamp = _cue_timestamp(show, section, index, len(looks))
            cues.append(
                Cue(
                    number=next_number,
                    label=f"{section.name} {look['label']}",
                    section=section.name,
                    timestamp=timestamp,
                    channels=_channels_for_style(
                        channel_groups,
                        fixture_count=len(rig.fixtures),
                        style=style,
                        index=index,
                    ),
                    preset=look.get("preset"),
                    attributes={
                        k: str(v)
                        for k, v in look.items()
                        if k not in ("label", "preset", "fade_time")
                    },
                    fade_time=float(look["fade_time"]),
                )
            )
            next_number += 1
    return cues


def _section_looks(
    show: Show,
    section: Section,
    style: AuthoringStyle,
    cues_per_section: int,
    warnings: list[str],
) -> list[dict[str, str | int | float]]:
    energy = section.energy if section.energy is not None else 0.5
    dimmer = _energy_to_dimmer(energy)
    secondary = max(20, min(100, dimmer + 12))

    if style == "warm-cool":
        seeds = [
            _look("Warm Front", dimmer, "Warm Amber", 2.0),
            _look("Cool Lift", secondary, "#3366FF", 1.5),
        ]
    elif style == "front-back":
        seeds = [
            _look("Front Warm", dimmer, "Warm Amber", 2.0, "front_warm"),
            _look("Back Blue", secondary, "#3366FF", 1.5, "back_blue"),
        ]
    elif style == "vibe-palette":
        colors = _vibe_colors(show, warnings)
        seeds = [
            _look(f"Palette {index + 1}", _dimmer_for_index(energy, index), color, 1.5)
            for index, color in enumerate(colors)
        ]
    elif style == "movement-sweep":
        seeds = [
            _look("Sweep Left", dimmer, _energy_color(energy), 2.0, pan=25),
            _look("Sweep Right", dimmer, _energy_lift_color(energy), 2.0, pan=75),
        ]
    elif style == "movement-circle":
        color = _energy_color(energy)
        seeds = [
            _look("Circle 1", dimmer, color, 1.0, pan=50, tilt=75),
            _look("Circle 2", dimmer, color, 1.0, pan=75, tilt=50),
            _look("Circle 3", dimmer, color, 1.0, pan=50, tilt=25),
            _look("Circle 4", dimmer, color, 1.0, pan=25, tilt=50),
        ]
    elif style == "movement-figure8":
        color = _energy_color(energy)
        seeds = [
            _look("Fig8 1", dimmer, color, 0.5, pan=50, tilt=50),
            _look("Fig8 2", dimmer, color, 0.5, pan=65, tilt=75),
            _look("Fig8 3", dimmer, color, 0.5, pan=80, tilt=50),
            _look("Fig8 4", dimmer, color, 0.5, pan=65, tilt=25),
            _look("Fig8 5", dimmer, color, 0.5, pan=50, tilt=50),
            _look("Fig8 6", dimmer, color, 0.5, pan=35, tilt=75),
            _look("Fig8 7", dimmer, color, 0.5, pan=20, tilt=50),
            _look("Fig8 8", dimmer, color, 0.5, pan=35, tilt=25),
        ]
    elif style == "beam-chase":
        seeds = [
            _look("Beam Wide", dimmer, _energy_color(energy), 0.5, zoom=100),
            _look("Beam Narrow", secondary, _energy_lift_color(energy), 0.5, zoom=0),
        ]
    else:
        seeds = [
            _look("Energy Base", dimmer, _energy_color(energy), 2.0),
            _look("Energy Lift", secondary, _energy_lift_color(energy), 1.0),
        ]

    looks = _fit_look_count(seeds, cues_per_section, energy)

    if show.song.bpm and show.song.bpm > 0:
        fade_multiplier = 120.0 / show.song.bpm
        for look in looks:
            look["fade_time"] = round(float(look["fade_time"]) * fade_multiplier, 2)

    return looks


def _look(
    label: str,
    dimmer: int,
    color: str,
    fade_time: float,
    preset: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "label": label,
        "dimmer": dimmer,
        "color": color,
        "fade_time": fade_time,
    }
    if preset:
        result["preset"] = preset
    result.update(kwargs)
    return result


def _fit_look_count(
    seeds: list[dict[str, Any]],
    count: int,
    energy: float,
) -> list[dict[str, Any]]:
    if count <= len(seeds):
        return seeds[:count]

    result = list(seeds)
    while len(result) < count:
        seed = seeds[len(result) % len(seeds)]
        kwargs = {
            k: v
            for k, v in seed.items()
            if k not in ("label", "dimmer", "color", "fade_time", "preset")
        }
        result.append(
            _look(
                f"{seed['label']} {len(result) + 1}",
                _dimmer_for_index(energy, len(result)),
                str(seed["color"]),
                float(seed["fade_time"]),  # type: ignore[arg-type]
                seed.get("preset") if isinstance(seed.get("preset"), str) else None,
                **kwargs,
            )
        )
    return result


def _cue_timestamp(show: Show, section: Section, index: int, count: int) -> float:
    if count <= 1:
        return round(section.start, 2)
    spacing = (section.end - section.start) / count
    timestamp = section.start + index * spacing

    if show.song.bpm and show.song.bpm > 0:
        beat_duration = 60.0 / show.song.bpm
        beats_since_start = round((timestamp - section.start) / beat_duration)
        timestamp = section.start + beats_since_start * beat_duration

    return round(timestamp, 2)


def _energy_to_dimmer(energy: float) -> int:
    bounded = max(0.0, min(1.0, energy))
    return int(round(25 + bounded * 70))


def _dimmer_for_index(energy: float, index: int) -> int:
    return max(20, min(100, _energy_to_dimmer(energy) + index * 8))


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


def _vibe_colors(show: Show, warnings: list[str]) -> list[str]:
    if show.vibe is not None and show.vibe.palette.colors:
        return list(show.vibe.palette.colors)
    warnings.append("Show has no vibe palette; using fallback authoring colors.")
    return list(FALLBACK_PALETTE)


def _fixture_channel_groups(rig: Rig) -> list[str]:
    return [
        slot.channels.strip()
        for slot in rig.fixtures
        if slot.channels is not None and slot.channels.strip().isdigit()
    ]


def _channels_for_style(
    channel_groups: list[str],
    *,
    fixture_count: int,
    style: AuthoringStyle,
    index: int,
) -> str:
    if not channel_groups:
        return f"1 Thru {max(1, fixture_count)}"
    if style == "front-back" and len(channel_groups) >= 4:
        midpoint = len(channel_groups) // 2
        selected = (
            channel_groups[:midpoint] if index == 0 else channel_groups[midpoint:]
        )
        return " ".join(selected)
    return f"1 Thru {len(channel_groups)}"


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
        return "Cue authoring plan uses renderer-supported attributes only."
    return f"Cue authoring plan produced {len(warnings)} warning(s)."
