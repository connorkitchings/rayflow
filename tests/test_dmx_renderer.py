"""Tests for fixture-aware DMX rendering."""

from pathlib import Path

from rayflow.rendering import render_cue_to_dmx, render_section_to_dmx
from rayflow.shows.models import (
    Cue,
    FixtureSlot,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
)

SAMPLES_DIR = Path("data/fixtures/samples")


def _rig_with_fixture(
    slot: FixtureSlot, presets: dict[str, Preset] | None = None
) -> Rig:
    return Rig(
        name="Render Rig",
        venue=Venue(name="Test Venue", dimensions=(10, 5, 4)),
        fixtures=[slot],
        presets=presets or {},
    )


def _show(cues: list[Cue], presets: dict[str, Preset] | None = None) -> Show:
    return Show(
        name="Render Show",
        rig_name="Render Rig",
        song=Song(
            title="Render Song",
            artist="Tester",
            duration=120,
            sections=[Section(name="Intro", start=0, end=30)],
        ),
        cues=cues,
        preset_overrides=presets or {},
    )


def test_single_generated_dimmer_fixture_renders_50_percent(
    sample_gdtf_file: Path,
) -> None:
    cue = Cue(
        number=1,
        label="Half",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "50%"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="Sample Dimmer",
            mode="Basic",
            label="Dimmer 1",
            universe=2,
            start_address=10,
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=sample_gdtf_file)

    assert rendered.frames[0].universe == 2
    assert rendered.frames[0].channels == {10: 128}
    assert rendered.warnings == []


def test_led_par_renders_dimmer_and_rgbw_channels() -> None:
    cue = Cue(
        number=1,
        label="Blue Hit",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "Full", "color": "#3366FF"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="LED PAR 64 RGBW",
            mode="Default",
            label="PAR 1",
            universe=0,
            start_address=13,
            channels="2",
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames[0].channels == {
        13: 255,
        14: 51,
        15: 102,
        16: 255,
        17: 51,
    }
    assert rendered.warnings == []


def test_cue_attributes_override_preset_attributes() -> None:
    preset = Preset(
        name="Warm Wash",
        description="Default warm look",
        attributes={"dimmer": "80", "color": "#FF6600"},
        channels="2",
    )
    cue = Cue(
        number=1,
        label="Override",
        section="Intro",
        timestamp=0,
        preset="Warm Wash",
        attributes={"dimmer": "20", "color": "#0000FF"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="LED PAR 64 RGBW",
            mode="Default",
            label="PAR 1",
            universe=0,
            start_address=20,
            channels="2",
        ),
        presets={"Warm Wash": preset},
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames[0].channels[20] == 51
    assert rendered.frames[0].channels[21] == 0
    assert rendered.frames[0].channels[22] == 0
    assert rendered.frames[0].channels[23] == 255


def test_named_color_maps_sample_warm_amber() -> None:
    cue = Cue(
        number=1,
        label="Amber",
        section="Intro",
        timestamp=0,
        attributes={"color": "Warm Amber"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="LED PAR 64 RGBW",
            mode="Default",
            label="PAR 1",
            universe=0,
            start_address=20,
            channels="2",
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames[0].channels[21] == 255
    assert rendered.frames[0].channels[22] == 153
    assert rendered.frames[0].channels[23] == 51
    assert rendered.frames[0].channels[24] == 51


def test_section_rendering_preserves_stable_cue_order() -> None:
    cues = [
        Cue(number=2, label="Later", section="Intro", timestamp=5),
        Cue(number=1, label="First", section="Intro", timestamp=0),
    ]
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="LED PAR 64 RGBW",
            mode="Default",
            label="PAR 1",
            universe=0,
            start_address=20,
        )
    )

    rendered = render_section_to_dmx(_show(cues), rig, "Intro", fixture_dir=SAMPLES_DIR)

    assert rendered.scope == "section:Intro"
    assert [cue.cue_number for cue in rendered.rendered_cues] == [1, 2]


def test_paired_fine_channels_render_16_bit_values() -> None:
    cue = Cue(
        number=1,
        label="Fine",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "50", "color": "#3366FF"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="Robin iSpiiderX",
            mode="Mode 10 - Pattern full RGBW",
            label="Spiider 1",
            universe=0,
            start_address=1,
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames[0].channels[8] == 51
    assert rendered.frames[0].channels[9] == 51
    assert rendered.frames[0].channels[18] == 128
    assert rendered.frames[0].channels[19] == 128


def test_unsupported_attributes_warn_without_blocking_supported_output(
    sample_gdtf_file: Path,
) -> None:
    cue = Cue(
        number=1,
        label="Mixed",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "50", "gobo": "Dots", "movement": "Sweep"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="Sample Dimmer",
            mode="Basic",
            label="Dimmer 1",
            universe=0,
            start_address=1,
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=sample_gdtf_file)

    assert rendered.frames[0].channels == {1: 128}
    assert {warning.attribute for warning in rendered.warnings} == {"gobo", "movement"}


def test_missing_fixture_returns_warning() -> None:
    cue = Cue(
        number=1,
        label="Missing Fixture",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "50"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="No Such Fixture",
            mode="Basic",
            label="Missing 1",
            universe=0,
            start_address=1,
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames == []
    assert rendered.warnings[0].fixture == "Missing 1"
    assert "not found" in rendered.warnings[0].message


def test_missing_mode_returns_warning() -> None:
    cue = Cue(
        number=1,
        label="Missing Mode",
        section="Intro",
        timestamp=0,
        attributes={"dimmer": "50"},
    )
    rig = _rig_with_fixture(
        FixtureSlot(
            fixture_name="LED PAR 64 RGBW",
            mode="No Such Mode",
            label="PAR 1",
            universe=0,
            start_address=1,
        )
    )

    rendered = render_cue_to_dmx(_show([cue]), rig, cue, fixture_dir=SAMPLES_DIR)

    assert rendered.frames == []
    assert rendered.warnings[0].fixture == "PAR 1"
    assert "DMX mode not found" in rendered.warnings[0].message
