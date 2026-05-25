"""Preview and critique packet builder for RayFlow shows."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rayflow.design.context import build_context_bundle
from rayflow.design.models import Cue, Rig, Show, resolve_presets
from rayflow.engine.rendering import render_section_to_dmx, render_show_to_dmx
from rayflow.engine.rendering.dmx import RenderedCueGroup

CRITIQUE_PROMPTS: dict[str, list[str]] = {
    "intensity": [
        "Is each section bright enough relative to its musical energy?",
        "Do peak sections clearly lift above verses and intros?",
    ],
    "color": [
        "Do the warm/cool choices match the section moods?",
        "Are accent colors used intentionally rather than everywhere at once?",
    ],
    "distribution": [
        "Does the show clearly separate front, back, and full-stage looks?",
        "Are fixture groups targeted in ways that support the song structure?",
    ],
    "movement_texture": [
        "Are moving fixtures used only where motion is intended?",
        "Do beam, gobo, shutter, or zoom looks add texture without hiding the wash?",
    ],
}


@dataclass(frozen=True)
class PreviewPacket:
    """A critique-ready dry-run packet for a RayFlow show or section."""

    show: str
    rig: str
    scope: str
    section: str
    show_summary: dict[str, Any]
    rig_summary: dict[str, Any]
    fixture_groups: dict[str, Any]
    fixture_capabilities: dict[str, Any]
    effective_presets: dict[str, Any]
    selected_cues: list[dict[str, Any]]
    rendered: RenderedCueGroup
    warnings: list[dict[str, Any]] = field(default_factory=list)
    critique_prompts: dict[str, list[str]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        readiness = _readiness(self.rendered, self.warnings)
        return {
            "show": self.show,
            "rig": self.rig,
            "scope": self.scope,
            "section": self.section,
            "show_summary": dict(self.show_summary),
            "rig_summary": dict(self.rig_summary),
            "fixture_groups": dict(self.fixture_groups),
            "fixture_capabilities": dict(self.fixture_capabilities),
            "effective_presets": dict(self.effective_presets),
            "selected_cues": list(self.selected_cues),
            "rendered": self.rendered.as_dict(),
            "warnings": list(self.warnings),
            "readiness": readiness,
            "critique_prompts": dict(self.critique_prompts),
            "visual_fidelity": {
                "kind": "dry-run evidence packet",
                "summary": (
                    "This packet summarizes rendered DMX evidence and critique "
                    "questions; it is not a 3D scene render."
                ),
            },
        }


def build_preview_packet(
    show: Show,
    rig: Rig,
    *,
    fixture_dir: str | Path = "data/fixtures/samples",
    section_name: str = "all",
) -> PreviewPacket:
    """Build a dry-run preview packet for a complete show or one section."""
    section = section_name.strip() or "all"
    if section.lower() == "all":
        selected_cues = sorted(show.cues, key=lambda cue: (cue.timestamp, cue.number))
        rendered = render_show_to_dmx(show, rig, fixture_dir=fixture_dir)
    else:
        selected_cues = sorted(
            show.cues_for_section(section),
            key=lambda cue: (cue.timestamp, cue.number),
        )
        if not selected_cues:
            raise ValueError(f"Section has no cues: {section}")
        rendered = render_section_to_dmx(show, rig, section, fixture_dir=fixture_dir)

    context = build_context_bundle(show, rig, fixture_dir)
    warnings = [
        warning.as_dict()
        for rendered_cue in rendered.rendered_cues
        for warning in rendered_cue.warnings
    ]
    return PreviewPacket(
        show=show.name,
        rig=rig.name,
        scope=rendered.scope,
        section=section if section.lower() != "all" else "all",
        show_summary=_show_summary(show),
        rig_summary=_rig_summary(rig),
        fixture_groups=_fixture_groups(rig),
        fixture_capabilities=context["fixture_capabilities"],
        effective_presets={
            name: preset.as_dict()
            for name, preset in resolve_presets(rig, show).items()
        },
        selected_cues=[_cue_preview(cue) for cue in selected_cues],
        rendered=rendered,
        warnings=warnings,
        critique_prompts=_critique_prompts(warnings),
    )


def _show_summary(show: Show) -> dict[str, Any]:
    return {
        "name": show.name,
        "rig_name": show.rig_name,
        "song": show.song.as_dict(),
        "cue_count": len(show.cues),
        "preset_override_count": len(show.preset_overrides),
        "has_vibe": show.vibe is not None,
    }


def _rig_summary(rig: Rig) -> dict[str, Any]:
    return {
        "name": rig.name,
        "venue": rig.venue.as_dict(),
        "fixture_count": len(rig.fixtures),
        "preset_count": len(rig.presets),
    }


def _fixture_groups(rig: Rig) -> dict[str, Any]:
    groups: dict[str, Any] = {}
    for slot in rig.fixtures:
        key = slot.fixture_name
        group = groups.setdefault(
            key,
            {
                "fixture_name": key,
                "count": 0,
                "labels": [],
                "channels": [],
            },
        )
        group["count"] += 1
        group["labels"].append(slot.label)
        if slot.channels:
            group["channels"].append(slot.channels)
    return groups


def _cue_preview(cue: Cue) -> dict[str, Any]:
    return {
        "number": cue.number,
        "label": cue.label,
        "section": cue.section,
        "timestamp": cue.timestamp,
        "preset": cue.preset,
        "channels": cue.channels,
        "attributes": dict(cue.attributes),
        "fade_time": cue.fade_time,
    }


def _critique_prompts(warnings: list[dict[str, Any]]) -> dict[str, list[str]]:
    prompts = {key: list(value) for key, value in CRITIQUE_PROMPTS.items()}
    if warnings:
        prompts.setdefault("capability_gaps", []).append(
            "Review warnings first: are missing fixture capabilities acceptable, "
            "or should the AI retarget those cues?"
        )
    return prompts


def _readiness(
    rendered: RenderedCueGroup, warnings: list[dict[str, Any]]
) -> dict[str, str]:
    frame_count = sum(len(cue.frames) for cue in rendered.rendered_cues)
    if not rendered.rendered_cues or frame_count == 0:
        return {
            "status": "blocked",
            "summary": "No rendered DMX frames were produced for this preview scope.",
        }
    if warnings:
        return {
            "status": "warnings",
            "summary": f"Preview rendered with {len(warnings)} warning(s).",
        }
    return {
        "status": "ready",
        "summary": "Preview rendered cleanly and is ready for critique.",
    }
