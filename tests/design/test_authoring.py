"""Tests for general deterministic show authoring helpers."""

from rayflow.design.authoring import plan_cues
from rayflow.design.models import (
    ColorPalette,
    Cue,
    FixtureSlot,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
    Vibe,
)
from rayflow.engine.rendering import render_cue_to_dmx

SAMPLE_FIXTURE_DIR = "data/fixtures/samples"


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


def _moving_rig() -> Rig:
    return Rig(
        name="Moving Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot("Robin MMX Blade", "Mode 1", "Spot 1", 0, 1, channels="1"),
            FixtureSlot("Robin MMX Blade", "Mode 1", "Spot 2", 0, 41, channels="2"),
        ],
    )


def _preset_rig() -> Rig:
    rig = _moving_rig()
    rig.presets = {
        "front_warm": Preset(
            name="Front Warm",
            description="Warm front light.",
            attributes={"dimmer": "60", "color": "Warm Amber"},
            tags=["front", "warm"],
        ),
        "electric_blue_cyan": Preset(
            name="Electric Blue Cyan",
            description="Blue/cyan back aerial bed.",
            attributes={"dimmer": "72", "color": "#00D8FF", "beam": "wide_aerial"},
            tags=["back", "blue", "cyan", "aerial"],
        ),
        "full_blue_cyan": Preset(
            name="Full Blue Cyan",
            description="Full-rig blue/cyan atmosphere.",
            attributes={"dimmer": "76", "color": "#00BFFF", "beam": "wide_aerial"},
            tags=["full", "blue", "cyan", "atmosphere"],
        ),
        "full_white_blue_peak": Preset(
            name="Full White Blue Peak",
            description="Full-rig white/blue peak.",
            attributes={"dimmer": "92", "color": "White", "beam": "tight_aerial"},
            tags=["full", "white", "blue", "peak"],
        ),
        "full_magenta_lime": Preset(
            name="Full Magenta Lime",
            description="Psychedelic full-rig look.",
            attributes={"dimmer": "80", "color": "#D800FF", "beam": "cross_center_x"},
            tags=["full", "magenta", "lime", "psychedelic"],
        ),
        "tight_aerial": Preset(
            name="Tight Aerial",
            description="Narrow profile beams.",
            attributes={"dimmer": "82", "beam": "tight_aerial", "focus": "70"},
            tags=["beam", "tight", "aerial"],
        ),
    }
    return rig


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


def test_plan_cues_prefers_rig_presets_for_front_back_and_warm_cool() -> None:
    for style in ("front-back", "warm-cool"):
        plan = plan_cues(
            _show(),
            _preset_rig(),
            section_name="Intro",
            style=style,
            fixture_dir=SAMPLE_FIXTURE_DIR,
        )

        assert not plan.warnings
        assert [cue.preset for cue in plan.proposed_cues] == [
            "front_warm",
            "electric_blue_cyan",
        ]
        assert all(
            {"dimmer", "color"} <= set(cue.attributes)
            for cue in plan.proposed_cues
        )


def test_plan_cues_prefers_peak_preset_when_available() -> None:
    plan = plan_cues(
        _show(),
        _preset_rig(),
        section_name="Chorus",
        style="look-peak",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert not plan.warnings
    assert plan.proposed_cues[0].preset == "full_white_blue_peak"
    assert plan.proposed_cues[1].preset == "full_white_blue_peak"
    assert all("dimmer" in cue.attributes for cue in plan.proposed_cues)


def test_plan_cues_generic_rig_preserves_raw_attribute_behavior() -> None:
    plan = plan_cues(
        _show(),
        _moving_rig(),
        section_name="Chorus",
        style="look-peak",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert not plan.warnings
    assert [cue.preset for cue in plan.proposed_cues] == [None, None]
    assert all("dimmer" in cue.attributes for cue in plan.proposed_cues)


def test_plan_cues_apply_with_presets_preserves_untouched_sections() -> None:
    show = _show()

    plan = plan_cues(
        show,
        _preset_rig(),
        section_name="Intro",
        style="warm-cool",
        fixture_dir=SAMPLE_FIXTURE_DIR,
        apply=True,
    )

    assert plan.mode == "apply"
    assert [cue.section for cue in show.cues] == ["Intro", "Intro", "Chorus"]
    assert [cue.preset for cue in plan.proposed_cues] == [
        "front_warm",
        "electric_blue_cyan",
    ]
    assert show.cues[-1].label == "Old Chorus"


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


def test_plan_cues_movement_circle() -> None:
    plan = plan_cues(
        _show(),
        _rig(),
        section_name="Chorus",
        style="movement-circle",
        cues_per_section=4,
    )
    assert not plan.warnings
    assert len(plan.proposed_cues) == 4
    for cue in plan.proposed_cues:
        assert "pan" in cue.attributes
        assert "tilt" in cue.attributes


def test_plan_cues_beam_chase() -> None:
    plan = plan_cues(
        _show(),
        _rig(),
        section_name="Chorus",
        style="beam-chase",
        cues_per_section=2,
    )
    assert not plan.warnings
    assert len(plan.proposed_cues) == 2
    for cue in plan.proposed_cues:
        assert "zoom" in cue.attributes


def test_plan_cues_with_movement_and_gobo_attributes() -> None:
    rig = _rig()
    show = _show()
    cue = Cue(
        number=3,
        label="Movement Cue",
        section="Intro",
        timestamp=5.0,
        attributes={
            "dimmer": "100%",
            "movement.type": "circle",
            "movement.center": "50,50",
            "movement.size": "20",
            "movement.speed": "0.5",
            "gobo.speed": "50%",
            "gobo.rotation": "25%",
        },
    )
    show.cues.append(cue)
    plan = plan_cues(show, rig, section_name="Intro", style="energy-arc", apply=True)
    assert not plan.warnings


def test_plan_cues_complete_look_styles_are_capability_aware() -> None:
    show = _show()
    rig = _moving_rig()

    for style in ("look-ambient", "look-groove", "look-peak", "look-psychedelic"):
        plan = plan_cues(
            show,
            rig,
            section_name="Chorus",
            style=style,
            fixture_dir=SAMPLE_FIXTURE_DIR,
        )
        assert not plan.warnings
        assert len(plan.proposed_cues) == 2
        attributes = set().union(*(cue.attributes for cue in plan.proposed_cues))
        assert {"dimmer", "color"} <= attributes
        assert attributes <= {
            "dimmer",
            "color",
            "pan",
            "tilt",
            "zoom",
            "focus",
            "shutter",
            "gobo",
            "movement.type",
            "movement.center",
            "movement.size",
            "movement.speed",
            "gobo.speed",
            "gobo.rotation",
        }


def test_plan_cues_complete_looks_skip_unsupported_par_attributes() -> None:
    plan = plan_cues(
        _show(),
        _rig(),
        section_name="Chorus",
        style="look-peak",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert not plan.warnings
    for cue in plan.proposed_cues:
        assert set(cue.attributes) == {"dimmer", "color"}


def test_plan_cues_complete_look_renders_without_unsupported_warnings() -> None:
    show = _show()
    rig = _moving_rig()
    plan = plan_cues(
        show,
        rig,
        section_name="Chorus",
        style="look-peak",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    rendered = [
        render_cue_to_dmx(show, rig, cue, fixture_dir=SAMPLE_FIXTURE_DIR)
        for cue in plan.proposed_cues
    ]

    warning_messages = [
        warning.message for cue_render in rendered for warning in cue_render.warnings
    ]
    assert not [
        message
        for message in warning_messages
        if "Unsupported attribute family" in message
    ]
