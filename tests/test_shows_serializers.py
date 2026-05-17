"""Tests for show & rig YAML serialization."""

import tempfile
from pathlib import Path

from rayflow.shows.models import (
    ColorPalette,
    Cue,
    FixtureSlot,
    Position3D,
    Preset,
    Rig,
    Section,
    Show,
    Song,
    Venue,
    Vibe,
)
from rayflow.shows.serializers import load_rig, load_show, save_rig, save_show


def _make_venue() -> Venue:
    return Venue(name="Test Venue", dimensions=(12.0, 6.0, 4.0))


def _make_rig() -> Rig:
    venue = _make_venue()
    fixtures = [
        FixtureSlot(
            fixture_name="Robe Robin iSpiider X",
            mode="Zones",
            label="Spiider 1",
            universe=0,
            start_address=1,
            position=Position3D(x=-2, y=4, z=1),
            channels="1",
        ),
        FixtureSlot(
            fixture_name="BlenderDMX LEDPAR64RGBW",
            mode="Default",
            label="Front Left PAR 1",
            universe=0,
            start_address=13,
            position=Position3D(x=-3, y=3, z=0),
            channels="2",
        ),
    ]
    presets = {
        "warm_wash": Preset(
            name="warm_wash",
            description="Warm amber wash",
            attributes={"dimmer": "80", "color": "Warm Amber"},
            channels="2 Thru 9",
            tags=["warm", "wash"],
        ),
        "blackout": Preset(
            name="blackout",
            description="All off",
            attributes={"dimmer": "0"},
            channels="1 Thru 20",
            tags=["blackout"],
        ),
    }
    return Rig(
        name="Club Rig v1",
        venue=venue,
        fixtures=fixtures,
        presets=presets,
        notes="Test rig",
    )


def _make_song() -> Song:
    return Song(
        title="All in Time",
        artist="Paul McFartney",
        duration=245.0,
        bpm=120,
        sections=[
            Section(name="Intro", start=0, end=15, energy=0.3, mood="ambient"),
            Section(name="Verse 1", start=15, end=45, energy=0.5, mood="mellow"),
            Section(name="Chorus", start=45, end=75, energy=0.9, mood="uplifting"),
        ],
    )


def _make_show() -> Show:
    palette = ColorPalette(
        name="Warm to Cool",
        colors=["#FF6600", "#FF3366", "#3366FF", "#00CCFF"],
        description="Start warm, transition to cool",
    )
    vibe = Vibe(
        palette=palette,
        intensity_curve="low → medium → high → medium",
        movement_style="slow sweep in verses, dynamic in chorus",
        mood_keywords=["cinematic", "building"],
        description="Warm amber intro building to cool blue energy",
    )
    cues = [
        Cue(number=1, label="Intro Wash", section="Intro", timestamp=0, fade_time=3.0),
        Cue(
            number=2,
            label="Verse Build",
            section="Verse 1",
            timestamp=15,
            attributes={"dimmer": "60", "color": "Warm Amber"},
            channels="2 Thru 9",
            fade_time=2.0,
        ),
        Cue(
            number=3,
            label="Chorus Hit",
            section="Chorus",
            timestamp=45,
            attributes={"dimmer": "Full", "color": "Cool Blue"},
            channels="1 Thru 20",
            fade_time=0.5,
        ),
    ]
    return Show(
        name="All in Time — Show v1",
        rig_name="Club Rig v1",
        song=_make_song(),
        vibe=vibe,
        cues=cues,
    )


class TestRigSerialization:
    def test_round_trip(self) -> None:
        rig = _make_rig()
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = Path(f.name)
            try:
                save_rig(rig, path)
                loaded = load_rig(path)
                assert loaded.name == rig.name
                assert loaded.venue.name == rig.venue.name
                assert loaded.venue.dimensions == rig.venue.dimensions
                assert len(loaded.fixtures) == len(rig.fixtures)
                assert loaded.fixtures[0].label == rig.fixtures[0].label
                assert loaded.fixtures[0].start_address == rig.fixtures[0].start_address
                assert len(loaded.presets) == len(rig.presets)
                assert "warm_wash" in loaded.presets
                assert loaded.presets["warm_wash"].attributes["dimmer"] == "80"
            finally:
                path.unlink()

    def test_creates_parent_directory(self) -> None:
        rig = _make_rig()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "rig.yaml"
            save_rig(rig, path)
            assert path.exists()
            loaded = load_rig(path)
            assert loaded.name == rig.name

    def test_empty_rig_round_trip(self) -> None:
        rig = Rig(name="Empty", venue=_make_venue())
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = Path(f.name)
            try:
                save_rig(rig, path)
                loaded = load_rig(path)
                assert loaded.name == "Empty"
                assert loaded.fixtures == []
                assert loaded.presets == {}
            finally:
                path.unlink()


class TestShowSerialization:
    def test_round_trip(self) -> None:
        show = _make_show()
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = Path(f.name)
            try:
                save_show(show, path)
                loaded = load_show(path)
                assert loaded.name == show.name
                assert loaded.rig_name == show.rig_name
                assert loaded.song.title == show.song.title
                assert loaded.song.artist == show.song.artist
                assert loaded.song.duration == show.song.duration
                assert loaded.song.bpm == show.song.bpm
                assert len(loaded.song.sections) == len(show.song.sections)
                assert loaded.song.sections[0].name == "Intro"
                assert loaded.vibe is not None
                assert loaded.vibe.palette.name == show.vibe.palette.name
                assert len(loaded.vibe.mood_keywords) == 2
                assert len(loaded.cues) == 3
                assert loaded.cues[0].label == "Intro Wash"
                assert loaded.cues[2].attributes["dimmer"] == "Full"
            finally:
                path.unlink()

    def test_show_without_vibe_round_trip(self) -> None:
        show = Show(
            name="No Vibe",
            rig_name="Test Rig",
            song=_make_song(),
        )
        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            path = Path(f.name)
            try:
                save_show(show, path)
                loaded = load_show(path)
                assert loaded.name == "No Vibe"
                assert loaded.vibe is None
                assert loaded.cues == []
            finally:
                path.unlink()

    def test_creates_parent_directory(self) -> None:
        show = _make_show()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "nested" / "dir" / "show.yaml"
            save_show(show, path)
            assert path.exists()
            loaded = load_show(path)
            assert loaded.name == show.name
