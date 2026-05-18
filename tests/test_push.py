"""Tests for push-to-MA3 functionality."""

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
        assert "Store Cue 1" in command_strings
        assert 'Label Cue 1 "Test"' in command_strings

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
        assert "Channel 1 Thru 8 At Warm Amber" in command_strings

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
        assert "Channel 1 Thru 512 At Red" in command_strings

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
        assert "Cue 1 Time 3" in command_strings

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
        assert "Store Cue 1" in command_strings
        assert "Store Cue 2" in command_strings

    def test_filter_by_section(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        show.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=15))
        commands = commands_for_show(show, {}, section="Intro")
        command_strings = [c.command for c in commands]
        assert "Store Cue 1" in command_strings
        assert "Store Cue 2" not in command_strings

    def test_cues_sorted_by_timestamp(self) -> None:
        show = _make_show()
        show.add_cue(Cue(number=2, label="B", section="Chorus", timestamp=15))
        show.add_cue(Cue(number=1, label="A", section="Intro", timestamp=0))
        commands = commands_for_show(show, {})
        store_commands = [c.command for c in commands if c.command.startswith("Store")]
        assert store_commands[0] == "Store Cue 1"
        assert store_commands[1] == "Store Cue 2"

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
