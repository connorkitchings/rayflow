"""Tests for AI context bundle builder."""

from pathlib import Path

from rayflow.design.context import build_context_bundle
from rayflow.design.models import (
    Cue,
    FixtureSlot,
    Position3D,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
)

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


def _make_venue() -> Venue:
    return Venue(name="Test Venue", dimensions=(10, 5, 3))


def _make_song() -> Song:
    return Song(
        title="Test Song",
        artist="Test Artist",
        duration=245.0,
        sections=[Section(name="Intro", start=0, end=15)],
    )


def _make_rig_with_fixtures(fixture_dir: Path) -> Rig:
    rig = Rig(name="Test Rig", venue=_make_venue())
    rig.add_fixture(
        FixtureSlot(
            fixture_name="Robin iSpiiderX",
            mode="Mode 1 - Zones",
            label="Spiider 1",
            universe=0,
            start_address=1,
            position=Position3D(x=-2, y=4, z=1),
        )
    )
    rig.add_preset(
        Preset(
            name="warm_wash",
            description="Warm wash",
            attributes={"dimmer": "80"},
        )
    )
    return rig


def _make_show() -> Show:
    return Show(
        name="Test Show",
        rig_name="Test Rig",
        song=_make_song(),
        cues=[Cue(number=1, label="Intro", section="Intro", timestamp=0)],
    )


class TestContextBundle:
    def test_bundle_has_all_sections(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig = _make_rig_with_fixtures(fixture_dir)
        show = _make_show()
        bundle = build_context_bundle(show, rig, fixture_dir)
        assert "show" in bundle
        assert "rig" in bundle
        assert "presets" in bundle
        assert "fixture_capabilities" in bundle
        assert "available_actions" in bundle

    def test_fixture_capabilities_match_gdtf(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig = _make_rig_with_fixtures(fixture_dir)
        show = _make_show()
        bundle = build_context_bundle(show, rig, fixture_dir)

        caps = bundle["fixture_capabilities"]
        assert "Robin iSpiiderX" in caps
        spiider_caps = caps["Robin iSpiiderX"]
        assert spiider_caps["label"] == "Spiider 1"
        assert spiider_caps["mode"] == "Mode 1 - Zones"
        assert "position" in spiider_caps["supported_attributes"]
        assert "dimmer" in spiider_caps["supported_attributes"]
        assert spiider_caps["channel_count"] > 0

    def test_available_actions_includes_console_commands(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig = _make_rig_with_fixtures(fixture_dir)
        show = _make_show()
        bundle = build_context_bundle(show, rig, fixture_dir)

        actions = bundle["available_actions"]
        assert "read" in actions
        assert "write" in actions
        assert "push" in actions
        assert "analysis" in actions
        assert "console_commands" in actions
        assert "store_cue" in actions["console_commands"]
        assert "channel_at" in actions["console_commands"]
        assert "clear_programmer" in actions["console_commands"]

    def test_merged_presets_correct(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig = _make_rig_with_fixtures(fixture_dir)
        show = Show(
            name="Test Show",
            rig_name="Test Rig",
            song=_make_song(),
            preset_overrides={
                "warm_wash": Preset(
                    name="warm_wash",
                    description="Override",
                    attributes={"dimmer": "Full"},
                )
            },
        )
        bundle = build_context_bundle(show, rig, fixture_dir)
        assert bundle["presets"]["warm_wash"]["attributes"]["dimmer"] == "Full"

    def test_missing_fixture_silently_skipped(self, tmp_path: Path) -> None:
        fixture_dir = _copy_samples(tmp_path)
        rig = Rig(name="Test Rig", venue=_make_venue())
        rig.add_fixture(
            FixtureSlot(
                fixture_name="Nonexistent Fixture",
                mode="Default",
                label="Missing",
                universe=0,
                start_address=1,
            )
        )
        rig.add_preset(
            Preset(name="test", description="Test", attributes={"dimmer": "80"})
        )
        show = _make_show()
        bundle = build_context_bundle(show, rig, fixture_dir)
        assert "Nonexistent Fixture" not in bundle["fixture_capabilities"]


def _copy_samples(tmp_path: Path) -> Path:
    dest = tmp_path / "fixtures"
    dest.mkdir()
    for f in SAMPLE_FIXTURE_DIR.glob("*.gdtf"):
        (dest / f.name).write_bytes(f.read_bytes())
    return dest
