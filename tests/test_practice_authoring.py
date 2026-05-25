"""Tests for deterministic practice-show authoring helpers."""

from rayflow.shows.models import Cue, FixtureSlot, Rig, Section, Show, Song, Venue
from rayflow.shows.practice_authoring import plan_practice_cues


def _rig() -> Rig:
    return Rig(
        name="Practice Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 1",
                universe=0,
                start_address=1,
                channels="1",
            ),
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 2",
                universe=0,
                start_address=6,
                channels="2",
            ),
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 3",
                universe=0,
                start_address=11,
                channels="3",
            ),
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 4",
                universe=0,
                start_address=16,
                channels="4",
            ),
        ],
    )


def _show() -> Show:
    return Show(
        name="Practice Show",
        rig_name="Practice Rig",
        song=Song(
            title="Song",
            artist="Artist",
            duration=60,
            sections=[
                Section(name="Intro", start=0, end=20, energy=0.2),
                Section(name="Chorus", start=20, end=50, energy=0.9),
            ],
        ),
        cues=[
            Cue(number=1, label="Old Intro", section="Intro", timestamp=0),
            Cue(number=2, label="Old Chorus", section="Chorus", timestamp=20),
        ],
    )


def test_plan_practice_cues_generates_stable_order_and_supported_attributes() -> None:
    plan = plan_practice_cues(_show(), _rig(), section_name="all")

    assert [cue.section for cue in plan.proposed_cues] == [
        "Intro",
        "Intro",
        "Chorus",
        "Chorus",
    ]
    assert [cue.timestamp for cue in plan.proposed_cues] == [0, 10, 20, 35]
    assert all(set(cue.attributes) == {"dimmer", "color"} for cue in plan.proposed_cues)
    assert all(cue.fade_time >= 0 for cue in plan.proposed_cues)
    assert plan.replaced_cue_numbers == [1, 2]
    assert plan.as_dict()["readiness"]["status"] == "ready"


def test_plan_practice_cues_maps_energy_to_dimmer_values() -> None:
    plan = plan_practice_cues(_show(), _rig(), section_name="all")

    dimmers = [cue.attributes["dimmer"] for cue in plan.proposed_cues]
    assert dimmers == ["39", "51", "88", "100"]


def test_plan_practice_cues_apply_preserves_untouched_sections() -> None:
    show = _show()

    plan = plan_practice_cues(
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


def test_plan_practice_cues_rejects_missing_section() -> None:
    try:
        plan_practice_cues(_show(), _rig(), section_name="Missing")
    except ValueError as exc:
        assert "Section not found" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected missing section error")
