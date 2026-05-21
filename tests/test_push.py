"""Tests for push-to-MA3 functionality."""

import pytest

from rayflow.shows.models import Cue, Preset, Section, Show, Song
from rayflow.shows.push import commands_for_show, commands_for_show_cue


def _make_show(cues: list[Cue] | None = None) -> Show:
    song = Song(title="Test", artist="Artist", duration=120.0)
    song.add_section(Section(name="Intro", start=0, end=15))
    song.add_section(Section(name="Chorus", start=15, end=45))
    show = Show(name="Test Show", rig_name="Test Rig", song=song)
    if cues:
        for c in cues:
            show.add_cue(c)
    return show


class TestCommandsForShowCue:
    def test_basic_cue_no_attributes(self) -> None:
        cue = Cue(number=1, label="Test", section="Intro", timestamp=0)
        commands = commands_for_show_cue(cue)
        command_strings = [c.command for c in commands]
        assert "Store Cue 1 /Overwrite /NoConfirmation" in command_strings
        assert 'Label Cue 1 "Test"' in command_strings

    def test_basic_cue_with_sequence_targets_sequence_cue(self) -> None:
        cue = Cue(number=1, label="Test", section="Intro", timestamp=0)
        commands = commands_for_show_cue(cue, sequence=3)
        command_strings = [c.command for c in commands]
        assert "Store Sequence 3 Cue 1 /Overwrite /NoConfirmation" in command_strings
        assert 'Label Sequence 3 Cue 1 "Test"' in command_strings

    def test_cue_with_attributes(self) -> None:
        cue = Cue(
            number=1,
            label="Wash",
            section="Intro",
            timestamp=0,
            attributes={"dimmer": "80"},
            channels="1 Thru 4",
        )
        commands = commands_for_show_cue(cue)
        command_strings = [c.command for c in commands]
        assert "Channel 1 Thru 4 At 80" in command_strings

    def test_cue_with_preset(self) -> None:
        preset = Preset(
            name="warm_wash",
            description="Warm wash",
            attributes={"dimmer": "Full", "color": "Warm Amber"},
            channels="1 Thru 8",
        )
        cue = Cue(
            number=1,
            label="Wash",
            section="Intro",
            timestamp=0,
            preset="warm_wash",
        )
        commands = commands_for_show_cue(cue, preset)
        command_strings = [c.command for c in commands]
        assert "Channel 1 Thru 8 At Full" in command_strings
        assert "Channel 1 Thru 8 At Warm Amber" not in command_strings

    def test_cue_overrides_preset_attributes(self) -> None:
        preset = Preset(
            name="warm_wash",
            description="Warm wash",
            attributes={"dimmer": "Full", "color": "Red"},
        )
        cue = Cue(
            number=1,
            label="Wash",
            section="Intro",
            timestamp=0,
            attributes={"dimmer": "50"},
        )
        commands = commands_for_show_cue(cue, preset)
        command_strings = [c.command for c in commands]
        assert "Channel 1 Thru 512 At 50" in command_strings
        assert "Channel 1 Thru 512 At Red" not in command_strings

    def test_cue_with_fade(self) -> None:
        cue = Cue(
            number=1,
            label="Fade In",
            section="Intro",
            timestamp=0,
            fade_time=3.0,
        )
        commands = commands_for_show_cue(cue)
        command_strings = [c.command for c in commands]
        assert "Cue 1 CueFade 3" in command_strings

    def test_cue_without_fade_skips_time(self) -> None:
        cue = Cue(number=1, label="Snap", section="Intro", timestamp=0)
        commands = commands_for_show_cue(cue)
        command_strings = [c.command for c in commands]
        assert not any("Time" in c for c in command_strings)

    def test_cue_empty_label_skips_label_command(self) -> None:
        cue = Cue(number=1, label="", section="Intro", timestamp=0)
        commands = commands_for_show_cue(cue)
        command_strings = [c.command for c in commands]
        assert not any("Label" in c for c in command_strings)


class TestCommandsForShow:
    def test_empty_show(self) -> None:
        show = _make_show()
        commands = commands_for_show(show, {})
        assert commands == []

    def test_multiple_cues(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=15))
        commands = commands_for_show(show, {})
        assert len(commands) > 0
        command_strings = [c.command for c in commands]
        assert "Store Cue 1 /Overwrite /NoConfirmation" in command_strings
        assert "Store Cue 2 /Overwrite /NoConfirmation" in command_strings

    def test_filter_by_section(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=15))
        commands = commands_for_show(show, {}, section="Intro")
        command_strings = [c.command for c in commands]
        assert "Store Cue 1 /Overwrite /NoConfirmation" in command_strings
        assert "Store Cue 2 /Overwrite /NoConfirmation" not in command_strings

    def test_cues_sorted_by_timestamp(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=15))
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {})
        store_commands = [c.command for c in commands if c.command.startswith("Store")]
        assert store_commands[0] == "Store Cue 1 /Overwrite /NoConfirmation"
        assert store_commands[1] == "Store Cue 2 /Overwrite /NoConfirmation"

    def test_with_presets(self) -> None:
        presets = {
            "warm_wash": Preset(
                name="warm_wash",
                description="Warm wash",
                attributes={"dimmer": "80"},
            ),
        }
        show = _make_show()
        show.add_cue(
            Cue(
                number=1,
                label="Wash",
                section="Intro",
                timestamp=0,
                preset="warm_wash",
            )
        )
        commands = commands_for_show(show, presets)
        command_strings = [c.command for c in commands]
        assert "Channel 1 Thru 512 At 80" in command_strings

    def test_with_sequence_prepends_setup_commands(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {}, sequence=1)
        command_strings = [c.command for c in commands]
        assert command_strings[0] == "Delete Sequence 1 /NoConfirmation"
        assert command_strings[1] == "Store Sequence 1 /Overwrite /NoConfirmation"
        assert command_strings[2] == 'Label Sequence 1 "Test"'
        assert command_strings[3] == "ClearAll"
        assert "Store Sequence 1 Cue 1 /Overwrite /NoConfirmation" in command_strings

    def test_with_sequence_uses_song_title_as_label(self) -> None:
        song = Song(title="My Lighting Show", artist="Artist", duration=120.0)
        show = Show(name="Test", rig_name="Rig", song=song)
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {}, sequence=3)
        command_strings = [c.command for c in commands]
        assert command_strings[0] == "Delete Sequence 3 /NoConfirmation"
        assert command_strings[1] == "Store Sequence 3 /Overwrite /NoConfirmation"
        assert command_strings[2] == 'Label Sequence 3 "My Lighting Show"'
        assert "Store Sequence 3 Cue 1 /Overwrite /NoConfirmation" in command_strings

    def test_with_sequence_and_section_filter(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {}, section="Intro", sequence=1)
        command_strings = [c.command for c in commands]
        assert command_strings[0] == "Delete Sequence 1 /NoConfirmation"
        assert "Store Sequence 1 Cue 1 /Overwrite /NoConfirmation" in command_strings

    def test_sequence_setup_before_cues(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {}, sequence=2)
        command_strings = [c.command for c in commands]
        setup_indices = [
            command_strings.index("Delete Sequence 2 /NoConfirmation"),
            command_strings.index("Store Sequence 2 /Overwrite /NoConfirmation"),
            command_strings.index('Label Sequence 2 "Test"'),
            command_strings.index("ClearAll"),
        ]
        cue_index = command_strings.index(
            "Store Sequence 2 Cue 1 /Overwrite /NoConfirmation"
        )
        assert all(i < cue_index for i in setup_indices)

    def test_sequence_validation(self) -> None:
        show = _make_show()
        with pytest.raises(ValueError, match="sequence must be > 0"):
            commands_for_show(show, {}, sequence=0)
        with pytest.raises(ValueError, match="sequence must be > 0"):
            commands_for_show(show, {}, sequence=-1)

    def test_no_sequence_produces_no_setup_commands(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {})
        command_strings = [c.command for c in commands]
        assert "Delete Sequence" not in command_strings
        assert "Store Sequence" not in command_strings
        assert "Label Sequence" not in command_strings
        assert "ClearAll" not in command_strings

    def test_empty_show_with_sequence_still_has_setup(self) -> None:
        show = _make_show()
        commands = commands_for_show(show, {}, sequence=1)
        command_strings = [c.command for c in commands]
        assert command_strings == [
            "Delete Sequence 1 /NoConfirmation",
            "Store Sequence 1 /Overwrite /NoConfirmation",
            'Label Sequence 1 "Test"',
            "ClearAll",
        ]
