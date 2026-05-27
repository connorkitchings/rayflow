"""General deterministic cue authoring helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
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
    "look-ambient",
    "look-groove",
    "look-peak",
    "look-psychedelic",
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
    "look-ambient",
    "look-groove",
    "look-peak",
    "look-psychedelic",
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
SUPPORTED_REFINEMENT_CRITIQUES = (
    "too-busy",
    "less-movement",
    "more-psychedelic",
    "bigger-chorus",
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


@dataclass(frozen=True)
class CueRefinementPlan:
    """Proposed targeted cue edits from user critique."""

    show: str
    rig: str
    section: str
    critique: str
    mode: Literal["proposal", "apply"]
    proposed_cues: list[Cue]
    changed_cue_numbers: list[int]
    warnings: list[str] = field(default_factory=list)
    next_command: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "show": self.show,
            "rig": self.rig,
            "section": self.section,
            "critique": self.critique,
            "mode": self.mode,
            "proposed_cues": [cue.as_dict() for cue in self.proposed_cues],
            "changed_cue_numbers": list(self.changed_cue_numbers),
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
    fixture_dir: str | Path = "data/fixtures/samples",
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
        fixture_dir,
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


def refine_cues(
    show: Show,
    rig: Rig,
    *,
    section_name: str = "all",
    critique: str,
    fixture_dir: str | Path = "data/fixtures/samples",
    apply: bool = False,
) -> CueRefinementPlan:
    """Plan or apply targeted cue edits from a small critique vocabulary."""
    normalized = _parse_refinement_critique(critique)
    selected_sections = _selected_sections(show, section_name)
    selected_names = {section.name for section in selected_sections}
    selected_cues = [
        cue
        for cue in show.cues
        if section_name.lower() == "all" or cue.section in selected_names
    ]
    if not selected_cues:
        raise ValueError(f"Selected scope has no cues: {section_name}")

    warnings: list[str] = []
    capabilities = _rig_capabilities(rig, fixture_dir, warnings)
    proposed = [
        _refined_cue(show, cue, normalized, capabilities)
        for cue in selected_cues
    ]
    changed_numbers = [cue.number for cue in proposed]
    next_command = (
        f'rayflow show preview {show.name} --rig "{rig.name}" '
        f"--section {section_name} --json"
    )

    if apply:
        proposed_by_number = {cue.number: cue for cue in proposed}
        show.cues = [proposed_by_number.get(cue.number, cue) for cue in show.cues]

    return CueRefinementPlan(
        show=show.name,
        rig=rig.name,
        section=section_name,
        critique=normalized,
        mode="apply" if apply else "proposal",
        proposed_cues=proposed,
        changed_cue_numbers=changed_numbers,
        warnings=warnings,
        next_command=next_command,
    )


def _parse_refinement_critique(critique: str) -> str:
    normalized = critique.strip().lower().replace("_", "-")
    if normalized not in SUPPORTED_REFINEMENT_CRITIQUES:
        supported = ", ".join(SUPPORTED_REFINEMENT_CRITIQUES)
        raise ValueError(
            f"Unsupported cue refinement critique: {critique}. Use {supported}."
        )
    return normalized


def _refined_cue(
    show: Show,
    cue: Cue,
    critique: str,
    capabilities: dict[str, bool],
) -> Cue:
    attrs = dict(cue.attributes)
    label = cue.label
    fade_time = cue.fade_time

    if critique == "too-busy":
        attrs = _remove_motion_texture(attrs)
        attrs["dimmer"] = str(max(20, _attribute_percent(attrs.get("dimmer"), 65) - 15))
        fade_time = max(fade_time, 1.5)
        label = _with_refinement_label(label, "simplified")
    elif critique == "less-movement":
        attrs = _remove_movement(attrs)
        fade_time = max(fade_time, 1.25)
        label = _with_refinement_label(label, "less movement")
    elif critique == "more-psychedelic":
        colors = _vibe_colors(show, [])
        attrs["color"] = colors[1 % len(colors)]
        if capabilities["position"]:
            attrs.update(
                {
                    "movement.type": "circle",
                    "movement.speed": "0.75",
                    "movement.size": "28",
                }
            )
        if capabilities["gobo"]:
            attrs["gobo"] = "75"
            attrs.update(_gobo_motion_attrs(capabilities, speed=70, rotation=65))
        if capabilities["beam"]:
            attrs["zoom"] = "18"
        fade_time = min(fade_time or 0.75, 0.75)
        label = _with_refinement_label(label, "psychedelic")
    elif critique == "bigger-chorus":
        attrs["dimmer"] = str(
            min(100, _attribute_percent(attrs.get("dimmer"), 75) + 20)
        )
        if capabilities["beam"]:
            attrs["zoom"] = "10"
            attrs["shutter"] = "70"
        if capabilities["position"]:
            attrs.setdefault("movement.type", "sine")
            attrs.setdefault("movement.speed", "0.8")
            attrs.setdefault("movement.size", "24,12")
        fade_time = min(fade_time or 0.5, 0.5)
        label = _with_refinement_label(label, "bigger")

    return Cue(
        number=cue.number,
        label=label,
        section=cue.section,
        timestamp=cue.timestamp,
        preset=cue.preset,
        channels=cue.channels,
        attributes=attrs,
        fade_time=fade_time,
        follow_time=cue.follow_time,
        notes=cue.notes,
    )


def _remove_motion_texture(attrs: dict[str, str]) -> dict[str, str]:
    simplified = _remove_movement(attrs)
    for key in ("gobo.speed", "gobo.rotation", "shutter"):
        simplified.pop(key, None)
    return simplified


def _remove_movement(attrs: dict[str, str]) -> dict[str, str]:
    return {
        key: value for key, value in attrs.items() if not key.startswith("movement.")
    }


def _attribute_percent(value: str | None, fallback: int) -> int:
    if value is None:
        return fallback
    normalized = value.strip().lower().replace("%", "")
    if normalized == "full":
        return 100
    if normalized in {"off", "blackout"}:
        return 0
    try:
        return max(0, min(100, int(float(normalized))))
    except ValueError:
        return fallback


def _with_refinement_label(label: str, suffix: str) -> str:
    marker = f" ({suffix})"
    if label.endswith(marker):
        return label
    return f"{label}{marker}"


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
    fixture_dir: str | Path,
) -> list[Cue]:
    cues: list[Cue] = []
    next_number = 1
    channel_groups = _fixture_channel_groups(rig)
    if not channel_groups:
        warnings.append(
            "Rig has no fixture channel groups; using broad channel fallback."
        )
    capabilities = _rig_capabilities(rig, fixture_dir, warnings)

    for section in sections:
        looks = _section_looks(
            show,
            section,
            style,
            cues_per_section,
            warnings,
            capabilities,
        )
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
    capabilities: dict[str, bool],
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
    elif style == "look-ambient":
        seeds = [
            _complete_look(
                "Ambient Hold",
                max(20, dimmer - 18),
                _soft_color(show, energy),
                3.0,
                capabilities,
                preset=_generated_preset(show, "rf_low_wash"),
                pan=50,
                tilt=45,
                zoom=100,
                focus=65,
            ),
            _complete_look(
                "Ambient Lift",
                max(25, dimmer - 10),
                "#3366FF",
                2.5,
                capabilities,
                preset=_generated_preset(show, "rf_cool_back"),
                pan=50,
                tilt=55,
                zoom=85,
            ),
        ]
    elif style == "look-groove":
        seeds = [
            _complete_look(
                "Groove Sweep",
                max(45, dimmer),
                _energy_color(energy),
                1.0,
                capabilities,
                preset=_generated_preset(show, "rf_full_wash"),
                **_movement_attrs("sine", speed=0.5, size="18,8"),
                zoom=45,
                gobo=35,
            ),
            _complete_look(
                "Groove Texture",
                secondary,
                _energy_lift_color(energy),
                1.0,
                capabilities,
                **_movement_attrs("circle", speed=0.35, size="14"),
                zoom=35,
                gobo=45,
            ),
        ]
    elif style == "look-peak":
        seeds = [
            _complete_look(
                "Peak Blast",
                100,
                "White",
                0.35,
                capabilities,
                preset=_generated_preset(show, "rf_beam_narrow"),
                **_movement_attrs("circle", speed=1.0, size="25"),
                zoom=0,
                shutter=100,
                gobo=65,
                **_gobo_motion_attrs(capabilities, speed=70, rotation=35),
            ),
            _complete_look(
                "Peak Color Hit",
                95,
                "#00CCFF",
                0.5,
                capabilities,
                **_movement_attrs("figure8", speed=0.9, size="25,18"),
                zoom=12,
                shutter=80,
                gobo=80,
                **_gobo_motion_attrs(capabilities, speed=85, rotation=65),
            ),
        ]
    elif style == "look-psychedelic":
        colors = _vibe_colors(show, warnings)
        seeds = [
            _complete_look(
                "Psychedelic Orbit",
                secondary,
                colors[0],
                0.75,
                capabilities,
                preset=_generated_preset(show, "rf_gobo_slow"),
                **_movement_attrs("circle", speed=0.65, size="30"),
                zoom=20,
                gobo=55,
                **_gobo_motion_attrs(capabilities, speed=55, rotation=25),
            ),
            _complete_look(
                "Psychedelic Figure 8",
                min(100, secondary + 8),
                colors[1 % len(colors)],
                0.75,
                capabilities,
                **_movement_attrs("figure8", speed=0.75, size="28,20"),
                zoom=10,
                shutter=45,
                gobo=75,
                **_gobo_motion_attrs(capabilities, speed=75, rotation=80),
            ),
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


def _complete_look(
    label: str,
    dimmer: int,
    color: str,
    fade_time: float,
    capabilities: dict[str, bool],
    preset: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    filtered: dict[str, Any] = {}
    for key, value in kwargs.items():
        if key in {"pan", "tilt"} and not capabilities["position"]:
            continue
        if key in {"zoom", "focus", "shutter"} and not capabilities["beam"]:
            continue
        if key.startswith("movement.") and not capabilities["position"]:
            continue
        if key.startswith("gobo") and not capabilities["gobo"]:
            continue
        filtered[key] = value
    return _look(label, dimmer, color, fade_time, preset, **filtered)


def _movement_attrs(
    movement_type: str,
    *,
    speed: float,
    size: str,
    center: str = "50,50",
) -> dict[str, str]:
    return {
        "movement.type": movement_type,
        "movement.center": center,
        "movement.size": size,
        "movement.speed": str(speed),
    }


def _gobo_motion_attrs(
    capabilities: dict[str, bool],
    *,
    speed: int,
    rotation: int,
) -> dict[str, str]:
    if not capabilities["gobo"]:
        return {}
    return {
        "gobo.speed": f"{speed}%",
        "gobo.rotation": f"{rotation}%",
    }


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


def _soft_color(show: Show, energy: float) -> str:
    if show.vibe is not None and show.vibe.palette.colors:
        return show.vibe.palette.colors[0]
    return "Warm Amber" if energy < 0.6 else "#3366FF"


def _generated_preset(show: Show, name: str) -> str | None:
    return name if name in show.preset_overrides else None


def _rig_capabilities(
    rig: Rig,
    fixture_dir: str | Path,
    warnings: list[str],
) -> dict[str, bool]:
    capabilities = {"position": False, "beam": False, "gobo": False}
    try:
        from rayflow.design.presets import fixture_supports_attribute
        from rayflow.engine.fixtures.library import FixtureLibrary

        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as exc:
        warnings.append(f"Fixture library could not be loaded: {exc}")
        return capabilities

    for slot in rig.fixtures:
        parser = library.get(slot.fixture_name)
        if parser is None:
            warnings.append(
                f"Fixture not found for authoring capability check: {slot.fixture_name}"
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
