"""Tests for show & rig data models."""

import pytest

from rayflow.design.models import (
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
    resolve_presets,
)


class TestPosition3D:
    def test_defaults(self) -> None:
        pos = Position3D()
        assert pos.x == 0.0
        assert pos.y == 0.0
        assert pos.z == 0.0
        assert pos.pan == 0.0
        assert pos.tilt == 0.0

    def test_as_dict(self) -> None:
        pos = Position3D(x=1.0, y=2.0, z=3.0, pan=45.0, tilt=30.0)
        d = pos.as_dict()
        assert d == {"x": 1.0, "y": 2.0, "z": 3.0, "pan": 45.0, "tilt": 30.0}


class TestVenue:
    def test_valid(self) -> None:
        v = Venue(name="Club", dimensions=(12.0, 6.0, 4.0))
        assert v.width == 12.0
        assert v.depth == 6.0
        assert v.height == 4.0

    def test_invalid_dimensions(self) -> None:
        with pytest.raises(ValueError, match="positive"):
            Venue(name="Bad", dimensions=(-1, 6, 4))

    def test_as_dict(self) -> None:
        v = Venue(name="Club", dimensions=(12.0, 6.0, 4.0), notes="Small venue")
        d = v.as_dict()
        assert d["name"] == "Club"
        assert d["dimensions"] == [12.0, 6.0, 4.0]
        assert d["notes"] == "Small venue"


class TestPreset:
    def test_valid(self) -> None:
        p = Preset(
            name="warm_wash",
            description="Warm amber wash",
            attributes={"dimmer": "80", "color": "Warm Amber"},
            channels="1 Thru 8",
            tags=["warm", "wash"],
        )
        assert p.name == "warm_wash"
        assert p.attributes["dimmer"] == "80"

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Preset(name="", description="test", attributes={"dimmer": "Full"})

    def test_invalid_attribute_family_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown attribute family"):
            Preset(name="bad", description="test", attributes={"invalid_attr": "value"})

    def test_as_dict(self) -> None:
        p = Preset(name="blackout", description="All off", attributes={"dimmer": "0"})
        d = p.as_dict()
        assert d["name"] == "blackout"
        assert d["attributes"] == {"dimmer": "0"}


class TestFixtureSlot:
    def test_valid(self) -> None:
        pos = Position3D(x=-2, y=4, z=1)
        slot = FixtureSlot(
            fixture_name="Robe Robin iSpiider X",
            mode="Zones",
            label="Spiider 1",
            universe=0,
            start_address=1,
            position=pos,
            channels="1",
        )
        assert slot.fixture_name == "Robe Robin iSpiider X"
        assert slot.start_address == 1

    def test_invalid_address_raises(self) -> None:
        with pytest.raises(ValueError, match=">= 1"):
            FixtureSlot(
                fixture_name="Test",
                mode="Default",
                label="T1",
                universe=0,
                start_address=0,
            )

    def test_invalid_universe_raises(self) -> None:
        with pytest.raises(ValueError, match=">= 0"):
            FixtureSlot(
                fixture_name="Test",
                mode="Default",
                label="T1",
                universe=-1,
                start_address=1,
            )

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            FixtureSlot(
                fixture_name="",
                mode="Default",
                label="T1",
                universe=0,
                start_address=1,
            )


class TestRig:
    def _make_venue(self) -> Venue:
        return Venue(name="Test Venue", dimensions=(10, 5, 3))

    def _make_slot(self, label: str = "F1") -> FixtureSlot:
        return FixtureSlot(
            fixture_name="Test Fixture",
            mode="Default",
            label=label,
            universe=0,
            start_address=1,
        )

    def test_valid(self) -> None:
        rig = Rig(name="Test Rig", venue=self._make_venue())
        assert rig.name == "Test Rig"
        assert rig.fixtures == []
        assert rig.presets == {}

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Rig(name="", venue=self._make_venue())

    def test_duplicate_labels_raises(self) -> None:
        with pytest.raises(ValueError, match="unique"):
            Rig(
                name="Test",
                venue=self._make_venue(),
                fixtures=[self._make_slot("F1"), self._make_slot("F1")],
            )

    def test_add_fixture(self) -> None:
        rig = Rig(name="Test", venue=self._make_venue())
        rig.add_fixture(self._make_slot("F1"))
        assert len(rig.fixtures) == 1
        assert rig.fixtures[0].label == "F1"

    def test_add_duplicate_fixture_raises(self) -> None:
        rig = Rig(name="Test", venue=self._make_venue())
        rig.add_fixture(self._make_slot("F1"))
        with pytest.raises(ValueError, match="already exists"):
            rig.add_fixture(self._make_slot("F1"))

    def test_add_preset(self) -> None:
        rig = Rig(name="Test", venue=self._make_venue())
        preset = Preset(name="wash", description="Wash", attributes={"dimmer": "80"})
        rig.add_preset(preset)
        assert rig.get_preset("wash") == preset

    def test_fixture_labels(self) -> None:
        rig = Rig(
            name="Test",
            venue=self._make_venue(),
            fixtures=[self._make_slot("F1"), self._make_slot("F2")],
        )
        assert rig.fixture_labels() == ["F1", "F2"]

    def test_template_defaults_false(self) -> None:
        rig = Rig(name="Test", venue=self._make_venue())
        assert rig.template is False

    def test_template_can_be_true(self) -> None:
        rig = Rig(name="Test", venue=self._make_venue(), template=True)
        assert rig.template is True


class TestSection:
    def test_valid(self) -> None:
        s = Section(name="Verse 1", start=0, end=30, energy=0.5, mood="mellow")
        assert s.name == "Verse 1"
        assert s.energy == 0.5

    def test_invalid_end_raises(self) -> None:
        with pytest.raises(ValueError, match="must be > start"):
            Section(name="Bad", start=30, end=0)

    def test_negative_energy_raises(self) -> None:
        with pytest.raises(ValueError, match="0-1"):
            Section(name="Bad", start=0, end=30, energy=-0.1)

    def test_energy_above_one_raises(self) -> None:
        with pytest.raises(ValueError, match="0-1"):
            Section(name="Bad", start=0, end=30, energy=1.5)


class TestSong:
    def test_valid(self) -> None:
        s = Song(title="Test Song", artist="Artist", duration=245.0, bpm=120)
        assert s.title == "Test Song"
        assert s.bpm == 120

    def test_empty_title_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Song(title="", artist="Artist", duration=245.0)

    def test_zero_duration_raises(self) -> None:
        with pytest.raises(ValueError, match="> 0"):
            Song(title="Test", artist="Artist", duration=0)

    def test_add_section(self) -> None:
        s = Song(title="Test", artist="Artist", duration=245.0)
        s.add_section(Section(name="Verse", start=0, end=30))
        assert len(s.sections) == 1


class TestColorPalette:
    def test_valid(self) -> None:
        p = ColorPalette(
            name="Warm",
            colors=["#FF6600", "#FF3366"],
            description="Warm tones",
        )
        assert len(p.colors) == 2

    def test_empty_colors_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            ColorPalette(name="Empty", colors=[], description="No colors")


class TestVibe:
    def test_valid(self) -> None:
        palette = ColorPalette(name="Test", colors=["#FF6600"], description="Test")
        v = Vibe(
            palette=palette,
            intensity_curve="low → high",
            movement_style="slow sweep",
            mood_keywords=["cinematic"],
        )
        assert v.movement_style == "slow sweep"
        assert v.mood_keywords == ["cinematic"]

    def test_from_dict(self) -> None:
        data = {
            "palette": {
                "name": "Warm",
                "colors": ["#FF6600", "#FF3366"],
                "description": "Warm tones",
            },
            "intensity_curve": "low → high",
            "movement_style": "slow sweep",
            "beam_style": "tight beams",
            "mood_keywords": ["cinematic", "emotional"],
            "description": "Full vibe",
        }
        vibe = Vibe.from_dict(data)
        assert vibe.palette.name == "Warm"
        assert vibe.palette.colors == ["#FF6600", "#FF3366"]
        assert vibe.intensity_curve == "low → high"
        assert vibe.movement_style == "slow sweep"
        assert vibe.beam_style == "tight beams"
        assert vibe.mood_keywords == ["cinematic", "emotional"]
        assert vibe.description == "Full vibe"

    def test_from_dict_minimal(self) -> None:
        data = {
            "palette": {"name": "Simple", "colors": ["#FFFFFF"], "description": ""},
            "intensity_curve": "flat",
            "movement_style": "static",
        }
        vibe = Vibe.from_dict(data)
        assert vibe.beam_style is None
        assert vibe.mood_keywords == []

    def test_from_dict_missing_colors_raises(self) -> None:
        data = {
            "palette": {"name": "Bad", "colors": [], "description": ""},
            "intensity_curve": "flat",
            "movement_style": "static",
        }
        with pytest.raises(ValueError, match="at least one color"):
            Vibe.from_dict(data)

    def test_from_dict_missing_intensity_raises(self) -> None:
        data = {
            "palette": {"name": "Test", "colors": ["#FFF"], "description": ""},
            "movement_style": "static",
        }
        with pytest.raises(ValueError, match="intensity_curve"):
            Vibe.from_dict(data)

    def test_from_dict_missing_movement_raises(self) -> None:
        data = {
            "palette": {"name": "Test", "colors": ["#FFF"], "description": ""},
            "intensity_curve": "flat",
        }
        with pytest.raises(ValueError, match="movement_style"):
            Vibe.from_dict(data)


class TestCue:
    def test_valid(self) -> None:
        c = Cue(number=1, label="Intro", section="Intro", timestamp=0, fade_time=3.0)
        assert c.number == 1
        assert c.fade_time == 3.0

    def test_zero_number_raises(self) -> None:
        with pytest.raises(ValueError, match="> 0"):
            Cue(number=0, label="Bad", section="Intro", timestamp=0)

    def test_negative_timestamp_raises(self) -> None:
        with pytest.raises(ValueError, match=">= 0"):
            Cue(number=1, label="Bad", section="Intro", timestamp=-1)

    def test_negative_fade_raises(self) -> None:
        with pytest.raises(ValueError, match=">= 0"):
            Cue(number=1, label="Bad", section="Intro", timestamp=0, fade_time=-1)


class TestShow:
    def _make_song(self) -> Song:
        return Song(title="Test", artist="Artist", duration=245.0)

    def test_valid(self) -> None:
        s = Show(name="Test Show", rig_name="Test Rig", song=self._make_song())
        assert s.name == "Test Show"
        assert s.cues == []

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Show(name="", rig_name="Rig", song=self._make_song())

    def test_empty_rig_raises(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Show(name="Show", rig_name="", song=self._make_song())

    def test_duplicate_cue_numbers_raises(self) -> None:
        with pytest.raises(ValueError, match="unique"):
            Show(
                name="Test",
                rig_name="Rig",
                song=self._make_song(),
                cues=[
                    Cue(number=1, label="A", section="Intro", timestamp=0),
                    Cue(number=1, label="B", section="Verse", timestamp=15),
                ],
            )

    def test_add_cue(self) -> None:
        s = Show(name="Test", rig_name="Rig", song=self._make_song())
        s.add_cue(Cue(number=1, label="Intro", section="Intro", timestamp=0))
        assert len(s.cues) == 1

    def test_add_duplicate_cue_raises(self) -> None:
        s = Show(name="Test", rig_name="Rig", song=self._make_song())
        s.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        with pytest.raises(ValueError, match="already exists"):
            s.add_cue(Cue(number=1, label="B", section="Verse", timestamp=15))

    def test_get_cue(self) -> None:
        s = Show(name="Test", rig_name="Rig", song=self._make_song())
        cue = Cue(number=1, label="Intro", section="Intro", timestamp=0)
        s.add_cue(cue)
        assert s.get_cue(1) == cue
        assert s.get_cue(99) is None

    def test_cues_for_section(self) -> None:
        s = Show(name="Test", rig_name="Rig", song=self._make_song())
        s.add_cue(Cue(number=1, label="A", section="Verse", timestamp=15))
        s.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=45))
        s.add_cue(Cue(number=3, label="C", section="Verse", timestamp=30))
        verse_cues = s.cues_for_section("Verse")
        assert len(verse_cues) == 2
        assert all(c.section == "Verse" for c in verse_cues)

    def test_preset_overrides_defaults_empty(self) -> None:
        s = Show(name="Test", rig_name="Rig", song=self._make_song())
        assert s.preset_overrides == {}

    def test_preset_overrides_can_be_set(self) -> None:
        override = Preset(
            name="chorus_boost",
            description="Brighter chorus",
            attributes={"dimmer": "Full"},
        )
        s = Show(
            name="Test",
            rig_name="Rig",
            song=self._make_song(),
            preset_overrides={"chorus_boost": override},
        )
        assert "chorus_boost" in s.preset_overrides


class TestResolvePresets:
    def _make_venue(self) -> Venue:
        return Venue(name="Test", dimensions=(10, 5, 3))

    def _make_song(self) -> Song:
        return Song(title="Test", artist="Artist", duration=245.0)

    def test_rig_only(self) -> None:
        rig = Rig(name="Rig", venue=self._make_venue())
        rig.add_preset(
            Preset(name="wash", description="Wash", attributes={"dimmer": "80"})
        )
        show = Show(name="Show", rig_name="Rig", song=self._make_song())
        merged = resolve_presets(rig, show)
        assert "wash" in merged
        assert merged["wash"].attributes["dimmer"] == "80"

    def test_show_overrides_rig(self) -> None:
        rig = Rig(name="Rig", venue=self._make_venue())
        rig.add_preset(
            Preset(name="wash", description="Rig wash", attributes={"dimmer": "80"})
        )
        show = Show(
            name="Show",
            rig_name="Rig",
            song=self._make_song(),
            preset_overrides={
                "wash": Preset(
                    name="wash",
                    description="Show wash",
                    attributes={"dimmer": "Full"},
                )
            },
        )
        merged = resolve_presets(rig, show)
        assert merged["wash"].attributes["dimmer"] == "Full"
        assert merged["wash"].description == "Show wash"

    def test_show_adds_new_preset(self) -> None:
        rig = Rig(name="Rig", venue=self._make_venue())
        show = Show(
            name="Show",
            rig_name="Rig",
            song=self._make_song(),
            preset_overrides={
                "new_preset": Preset(
                    name="new_preset",
                    description="New",
                    attributes={"color": "Red"},
                )
            },
        )
        merged = resolve_presets(rig, show)
        assert "new_preset" in merged
        assert merged["new_preset"].attributes["color"] == "Red"
