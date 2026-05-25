"""Tests for general deterministic show authoring helpers."""

from rayflow.design.authoring import plan_cues
from rayflow.design.models import (
    ColorPalette,
    Cue,
    FixtureSlot,
    Rig,
    Section,
    Show,
    Song,
    Venue,
    Vibe,
)


def _rig() -> Rig:
    return Rig(
        name="Authoring Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 1", 0, 1, channels="1"),
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 2", 0, 6, channels="2"),
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 3", 0, 11, channels="3"),
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 4", 0, 16, channels="4"),
        ],
    )


def _show(*, with_vibe: bool = True) -> Show:
    vibe = None
    if with_vibe:
        vibe = Vibe(
            palette=ColorPalette(
                name="Show Palette",
                colors=["#111111", "#222222", "#333333"],
                description="Test palette",
            ),
            intensity_curve="build",
            movement_style="static",
        )
    return Show(
        name="Authoring Show",
        rig_name="Authoring Rig",
        song=Song(
            title="Song",
            artist="Artist",
            duration=90,
            sections=[
                Section(name="Intro", start=0, end=30, energy=0.2),
                Section(name="Chorus", start=30, end=75, energy=0.8),
            ],
        ),
        vibe=vibe,
        cues=[
            Cue(number=1, label="Old Intro", section="Intro", timestamp=0),
            Cue(number=2, label="Old Chorus", section="Chorus", timestamp=30),
        ],
    )


def test_plan_cues_generates_stable_renderer_safe_cues() -> None:
    plan = plan_cues(_show(), _rig(), section_name="all", cues_per_section=2)

    assert [cue.section for cue in plan.proposed_cues] == [
        "Intro",
        "Intro",
        "Chorus",
        "Chorus",
    ]
    assert [cue.timestamp for cue in plan.proposed_cues] == [0, 15, 30, 52.5]
    assert all(set(cue.attributes) == {"dimmer", "color"} for cue in plan.proposed_cues)
    assert plan.replaced_cue_numbers == [1, 2]
    assert plan.as_dict()["readiness"]["status"] == "ready"


def test_plan_cues_vibe_palette_uses_show_colors() -> None:
    plan = plan_cues(
        _show(),
        _rig(),
        section_name="Chorus",
        style="vibe-palette",
        cues_per_section=3,
    )

    assert [cue.attributes["color"] for cue in plan.proposed_cues] == [
        "#111111",
        "#222222",
        "#333333",
    ]
    assert not plan.warnings


def test_plan_cues_vibe_palette_warns_and_falls_back_without_vibe() -> None:
    plan = plan_cues(
        _show(with_vibe=False),
        _rig(),
        section_name="Intro",
        style="vibe-palette",
    )

    assert [cue.attributes["color"] for cue in plan.proposed_cues] == [
        "Warm Amber",
        "#3366FF",
    ]
    assert any("fallback" in warning for warning in plan.warnings)
    assert plan.as_dict()["readiness"]["status"] == "warnings"


def test_plan_cues_apply_preserves_untouched_sections() -> None:
    show = _show()

    plan = plan_cues(
        show,
        _rig(),
        section_name="Intro",
        style="front-back",
        apply=True,
    )

    assert plan.mode == "apply"
    assert [cue.section for cue in show.cues] == ["Intro", "Intro", "Chorus"]
    assert show.cues[-1].label == "Old Chorus"
    assert {cue.channels for cue in plan.proposed_cues} == {"1 2", "3 4"}


def test_plan_cues_rejects_invalid_inputs() -> None:
    for kwargs, expected in [
        ({"section_name": "Missing"}, "Section not found"),
        ({"style": "missing"}, "Unsupported cue authoring style"),
        ({"cues_per_section": 0}, "cues_per_section must be >= 1"),
    ]:
        try:
            plan_cues(_show(), _rig(), **kwargs)
        except ValueError as exc:
            assert expected in str(exc)
        else:  # pragma: no cover
            raise AssertionError(f"Expected error containing {expected}")
