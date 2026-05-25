"""Tests for cue generation helpers."""

import pytest

from rayflow.design.cue_generator import (
    auto_number_cues,
    batch_update_cues,
    delete_cues_for_section,
    generate_cues_for_section,
    generate_cues_for_show,
    remove_cue,
    update_cue,
)
from rayflow.design.models import Cue, Section, Show, Song


def _make_song() -> Song:
    song = Song(title="Test", artist="Artist", duration=120.0)
    song.add_section(Section(name="Intro", start=0, end=15))
    song.add_section(Section(name="Verse", start=15, end=45))
    song.add_section(Section(name="Chorus", start=45, end=75))
    return song


def _make_show(cues: list[Cue] | None = None) -> Show:
    show = Show(name="Test Show", rig_name="Test Rig", song=_make_song())
    if cues:
        for c in cues:
            show.add_cue(c)
    return show


class TestAutoNumberCues:
    def test_empty_show(self) -> None:
        show = _make_show()
        auto_number_cues(show)
        assert show.cues == []

    def test_renumbers_sequentially(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=5, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Intro", timestamp=5))
        show.add_cue(Cue(number=99, label="C", section="Verse", timestamp=15))
        auto_number_cues(show)
        numbers = [c.number for c in show.cues]
        assert numbers == [1, 2, 3]

    def test_orders_by_timestamp(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="B", section="Verse", timestamp=15))
        show.add_cue(Cue(number=2, label="A", section="Intro", timestamp=0))
        auto_number_cues(show)
        assert show.cues[0].number == 1
        assert show.cues[0].label == "A"
        assert show.cues[1].number == 2
        assert show.cues[1].label == "B"


class TestGenerateCuesForSection:
    def test_basic_generation(self) -> None:
        show = _make_show()
        cues = generate_cues_for_section(
            show,
            "Intro",
            preset="warm_wash",
            count=3,
            spacing=5.0,
        )
        assert len(cues) == 3
        assert cues[0].label == "warm_wash 1"
        assert cues[0].section == "Intro"
        assert cues[0].timestamp == 0.0
        assert cues[1].timestamp == 5.0
        assert cues[2].timestamp == 10.0

    def test_generation_stops_at_section_end(self) -> None:
        show = _make_show()
        cues = generate_cues_for_section(
            show,
            "Intro",
            count=10,
            spacing=2.0,
        )
        assert len(cues) < 10  # section is only 15s

    def test_section_not_found(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="Section not found"):
            generate_cues_for_section(show, "Outro", count=3)

    def test_zero_count_raises(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="count"):
            generate_cues_for_section(show, "Intro", count=0)

    def test_negative_spacing_raises(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="spacing"):
            generate_cues_for_section(show, "Intro", spacing=-1)

    def test_with_attributes(self) -> None:
        show = _make_show()
        cues = generate_cues_for_section(
            show,
            "Intro",
            attributes={"dimmer": "80", "color": "Red"},
            count=2,
            spacing=5.0,
        )
        assert cues[0].attributes == {"dimmer": "80", "color": "Red"}

    def test_custom_base_label(self) -> None:
        show = _make_show()
        cues = generate_cues_for_section(
            show,
            "Intro",
            count=1,
            spacing=1.0,
            base_label="Custom",
        )
        assert cues[0].label == "Custom 1"

    def test_fade_time(self) -> None:
        show = _make_show()
        cues = generate_cues_for_section(
            show,
            "Intro",
            count=1,
            spacing=1.0,
            fade_time=3.0,
        )
        assert cues[0].fade_time == 3.0


class TestGenerateCuesForShow:
    def test_generates_for_all_sections(self) -> None:
        show = _make_show()
        result = generate_cues_for_show(
            show,
            section_presets={
                "Intro": "warm_wash",
                "Verse": "warm_wash",
                "Chorus": "cold_beam",
            },
            cues_per_section=2,
            spacing=5.0,
        )
        assert len(result.cues) > 0
        unique_sections = {c.section for c in result.cues}
        assert unique_sections == {"Intro", "Verse", "Chorus"}

    def test_replaces_existing_cues(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="Old", section="Intro", timestamp=0))
        result = generate_cues_for_show(
            show,
            section_presets={"Intro": "warm_wash"},
            cues_per_section=2,
        )
        assert all(c.label != "Old" for c in result.cues)


class TestDeleteCuesForSection:
    def test_deletes_all_section_cues(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Intro", timestamp=5))
        show.add_cue(Cue(number=3, label="C", section="Verse", timestamp=15))
        deleted = delete_cues_for_section(show, "Intro")
        assert deleted == 2
        assert len(show.cues) == 1
        assert show.cues[0].section == "Verse"

    def test_renumbers_after_delete(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=10, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=20, label="B", section="Verse", timestamp=15))
        delete_cues_for_section(show, "Intro")
        assert show.cues[0].number == 1


class TestUpdateCue:
    def test_update_label(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="Old", section="Intro", timestamp=0))
        update_cue(show, 1, label="New")
        assert show.cues[0].label == "New"

    def test_update_multiple_fields(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(
            show,
            1,
            label="B",
            timestamp=5.0,
            preset="warm_wash",
            fade_time=2.0,
        )
        cue = show.cues[0]
        assert cue.label == "B"
        assert cue.timestamp == 5.0
        assert cue.preset == "warm_wash"
        assert cue.fade_time == 2.0

    def test_update_attributes(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(show, 1, attributes={"dimmer": "80"})
        assert show.cues[0].attributes == {"dimmer": "80"}

    def test_cue_not_found(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="Cue not found"):
            update_cue(show, 99, label="X")

    def test_bad_timestamp_raises(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        with pytest.raises(ValueError, match=">= 0"):
            update_cue(show, 1, timestamp=-5)

    def test_bad_fade_raises(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        with pytest.raises(ValueError, match=">= 0"):
            update_cue(show, 1, fade_time=-1)

    def test_update_channels(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(show, 1, channels="1 Thru 4")
        assert show.cues[0].channels == "1 Thru 4"

    def test_update_follow_time(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(show, 1, follow_time=1.5)
        assert show.cues[0].follow_time == 1.5

    def test_update_notes(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(show, 1, notes="Test note")
        assert show.cues[0].notes == "Test note"

    def test_update_section(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        update_cue(show, 1, section="Verse")
        assert show.cues[0].section == "Verse"


class TestRemoveCue:
    def test_remove_existing(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        removed = remove_cue(show, 1)
        assert removed.label == "A"
        assert len(show.cues) == 0

    def test_remove_not_found(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="Cue not found"):
            remove_cue(show, 99)


class TestBatchUpdateCues:
    def test_batch_update_by_section(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Intro", timestamp=5))
        show.add_cue(Cue(number=3, label="C", section="Verse", timestamp=15))
        affected = batch_update_cues(
            show,
            section="Intro",
            attributes={"dimmer": "Full"},
        )
        assert affected == 2
        for cue in show.cues:
            if cue.section == "Intro":
                assert cue.attributes == {"dimmer": "Full"}

    def test_batch_set_fade(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        affected = batch_update_cues(show, set_fade=5.0)
        assert affected == 1
        assert show.cues[0].fade_time == 5.0

    def test_batch_set_preset(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        batch_update_cues(show, set_preset="warm_wash")
        assert show.cues[0].preset == "warm_wash"

    def test_batch_delete_by_section(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Intro", timestamp=5))
        show.add_cue(Cue(number=3, label="C", section="Verse", timestamp=15))
        affected = batch_update_cues(show, section="Intro", delete=True)
        assert affected == 2
        assert len(show.cues) == 1

    def test_batch_delete_all(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Verse", timestamp=15))
        affected = batch_update_cues(show, delete=True)
        assert affected == 2
        assert len(show.cues) == 0

    def test_bad_fade_raises(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        with pytest.raises(ValueError, match=">= 0"):
            batch_update_cues(show, set_fade=-1)
