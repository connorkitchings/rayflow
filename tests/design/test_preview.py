"""Tests for preview and critique packets."""

from pathlib import Path

import pytest

from rayflow.design.models import (
    Cue,
    FixtureSlot,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
)
from rayflow.design.preview import build_preview_packet

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


def _rig() -> Rig:
    return Rig(
        name="Preview Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 1", 0, 1, channels="1"),
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 2", 0, 6, channels="2"),
        ],
        presets={
            "warm": Preset(
                name="warm",
                description="Warm look",
                attributes={"dimmer": "70", "color": "Warm Amber"},
                channels="1 Thru 2",
            )
        },
    )


def _show() -> Show:
    return Show(
        name="Preview Show",
        rig_name="Preview Rig",
        song=Song(
            title="Song",
            artist="Artist",
            duration=90,
            sections=[
                Section(name="Intro", start=0, end=30, energy=0.2),
                Section(name="Chorus", start=30, end=60, energy=0.8),
            ],
        ),
        cues=[
            Cue(
                number=1,
                label="Intro Warm",
                section="Intro",
                timestamp=0,
                preset="warm",
            ),
            Cue(
                number=2,
                label="Chorus Blue",
                section="Chorus",
                timestamp=30,
                attributes={"dimmer": "Full", "color": "#3366FF"},
            ),
        ],
    )


def test_preview_packet_full_show_contains_critique_context() -> None:
    packet = build_preview_packet(_show(), _rig(), fixture_dir=SAMPLE_FIXTURE_DIR)
    payload = packet.as_dict()

    assert payload["show"] == "Preview Show"
    assert payload["scope"] == "show:Preview Show"
    assert payload["readiness"]["status"] == "ready"
    assert len(payload["selected_cues"]) == 2
    assert "warm" in payload["effective_presets"]
    assert "LED PAR 64 RGBW" in payload["fixture_groups"]
    assert "LED PAR 64 RGBW" in payload["fixture_capabilities"]
    assert payload["rendered"]["cues"][0]["frames"]
    assert "intensity" in payload["critique_prompts"]
    assert payload["visual_fidelity"]["kind"] == "dry-run evidence packet"


def test_preview_packet_filters_section() -> None:
    packet = build_preview_packet(
        _show(),
        _rig(),
        fixture_dir=SAMPLE_FIXTURE_DIR,
        section_name="Chorus",
    )
    payload = packet.as_dict()

    assert payload["scope"] == "section:Chorus"
    assert payload["section"] == "Chorus"
    assert [cue["section"] for cue in payload["selected_cues"]] == ["Chorus"]


def test_preview_packet_missing_section_raises() -> None:
    with pytest.raises(ValueError, match="Section has no cues"):
        build_preview_packet(
            _show(),
            _rig(),
            fixture_dir=SAMPLE_FIXTURE_DIR,
            section_name="Missing",
        )


def test_preview_packet_warns_for_missing_fixture_capability() -> None:
    rig = Rig(
        name="Bad Rig",
        venue=Venue(name="Room", dimensions=(10, 6, 4)),
        fixtures=[
            FixtureSlot("Missing Fixture", "Default", "Missing 1", 0, 1, channels="1")
        ],
    )
    show = Show(
        name="Bad Show",
        rig_name="Bad Rig",
        song=Song(title="Song", artist="Artist", duration=30),
        cues=[
            Cue(
                number=1,
                label="Look",
                section="Intro",
                timestamp=0,
                attributes={"dimmer": "Full"},
            )
        ],
    )

    packet = build_preview_packet(show, rig, fixture_dir=SAMPLE_FIXTURE_DIR)
    payload = packet.as_dict()
    assert payload["readiness"]["status"] == "blocked"
    assert "capability_gaps" in payload["critique_prompts"]
