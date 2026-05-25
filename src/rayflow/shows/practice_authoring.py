"""Compatibility wrappers for Phase 9 practice-show cue planning."""

from __future__ import annotations

from typing import TypeAlias

from rayflow.shows.authoring import CueAuthoringPlan, plan_cues
from rayflow.shows.models import Rig, Show

PracticeCuePlan: TypeAlias = CueAuthoringPlan


def plan_practice_cues(
    show: Show,
    rig: Rig,
    *,
    section_name: str = "all",
    style: str = "energy-arc",
    apply: bool = False,
) -> PracticeCuePlan:
    """Plan or apply deterministic fixture-safe practice cues."""
    return plan_cues(
        show,
        rig,
        section_name=section_name,
        style=style,
        cues_per_section=2,
        apply=apply,
    )
