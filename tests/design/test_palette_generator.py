"""Tests for generated show-specific palette overrides."""

from pathlib import Path

from rayflow.design.models import FixtureSlot, Preset, Rig, Show, Song, Venue
from rayflow.design.palette_generator import GENERATED_PREFIX, plan_show_palettes

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


def _mixed_rig() -> Rig:
    return Rig(
        name="Mixed Rig",
        venue=Venue(name="Room", dimensions=(12, 8, 5)),
        fixtures=[
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 1", 0, 1, channels="1"),
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 2", 0, 33, channels="2"),
            FixtureSlot(
                "Robin MMX Blade",
                "Mode 1 - Standard",
                "Blade 1",
                0,
                65,
                channels="3",
            ),
        ],
    )


def _show() -> Show:
    return Show(
        name="Palette Show",
        rig_name="Mixed Rig",
        song=Song(title="Song", artist="Artist", duration=120),
        preset_overrides={
            "custom_keep": Preset(
                name="custom_keep",
                description="User preset",
                attributes={"dimmer": "55"},
            ),
            f"{GENERATED_PREFIX}old": Preset(
                name=f"{GENERATED_PREFIX}old",
                description="Old generated preset",
                attributes={"dimmer": "10"},
            ),
        },
    )


def test_plan_show_palettes_generates_minimal_library() -> None:
    plan = plan_show_palettes(_show(), _mixed_rig(), fixture_dir=SAMPLE_FIXTURE_DIR)

    names = [preset.name for preset in plan.proposed_presets]
    assert 8 <= len(names) <= 12
    assert all(name.startswith(GENERATED_PREFIX) for name in names)
    assert f"{GENERATED_PREFIX}blackout" in names
    assert f"{GENERATED_PREFIX}warm_front" in names
    assert f"{GENERATED_PREFIX}beam_narrow" in names
    assert f"{GENERATED_PREFIX}gobo_slow" in names
    assert plan.replaced_override_names == [f"{GENERATED_PREFIX}old"]
    assert plan.as_dict()["readiness"]["status"] == "ready"


def test_plan_show_palettes_apply_replaces_only_namespaced_overrides() -> None:
    show = _show()
    plan = plan_show_palettes(
        show,
        _mixed_rig(),
        fixture_dir=SAMPLE_FIXTURE_DIR,
        apply=True,
    )

    assert plan.mode == "apply"
    assert "custom_keep" in show.preset_overrides
    assert f"{GENERATED_PREFIX}old" not in show.preset_overrides
    assert f"{GENERATED_PREFIX}blackout" in show.preset_overrides


def test_plan_show_palettes_skips_position_beam_gobo_without_capabilities() -> None:
    rig = Rig(
        name="PAR Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 1", 0, 1, channels="1")
        ],
    )

    plan = plan_show_palettes(_show(), rig, fixture_dir=SAMPLE_FIXTURE_DIR)
    names = {preset.name for preset in plan.proposed_presets}
    assert f"{GENERATED_PREFIX}position_center" not in names
    assert f"{GENERATED_PREFIX}beam_narrow" not in names
    assert f"{GENERATED_PREFIX}gobo_slow" not in names
