"""Tests for typed grandMA3 cue command builders."""

import json

import pytest

from rayflow.console.cue import (
    CueStack,
    CueStep,
    channel_at,
    clear_all,
    clear_programmer,
    commands_for_cue_stack,
    commands_for_cue_step,
    delete_sequence,
    go_sequence,
    label_cue,
    label_sequence,
    load_cue_stack,
    set_cue_time,
    store_cue,
    store_sequence,
)


def test_basic_command_builders():
    assert store_cue(1).command == "Store Cue 1"
    assert label_cue(1, "Intro").command == 'Label Cue 1 "Intro"'
    assert set_cue_time(1, 2.5).command == "Cue 1 Time 2.5"
    assert go_sequence(2).command == "Go Sequence 2"
    assert channel_at("1 Thru 8", "Full").command == "Channel 1 Thru 8 At Full"
    assert clear_programmer().command == "Clear"


@pytest.mark.parametrize(
    "builder",
    [
        lambda: store_cue(0),
        lambda: set_cue_time(-1, 1),
        lambda: go_sequence(0),
        lambda: channel_at(" ", "Full"),
        lambda: channel_at("1", " "),
        lambda: label_cue(1, ""),
    ],
)
def test_builders_validate_inputs(builder):
    with pytest.raises(ValueError):
        builder()


def test_cue_step_command_order():
    step = CueStep(
        cue=1,
        label="Intro",
        channels="1 Thru 8",
        at="Full",
        fade=2.5,
        clear_after=True,
    )

    commands = [command.command for command in commands_for_cue_step(step)]

    assert commands == [
        "Channel 1 Thru 8 At Full",
        "Store Cue 1",
        'Label Cue 1 "Intro"',
        "Cue 1 Time 2.5",
        "Clear",
    ]


def test_cue_stack_generates_deterministic_commands():
    stack = CueStack(
        sequence=1,
        name="Demo",
        cues=[
            CueStep(cue=1, channels="1", at="Full", clear_after=True),
            CueStep(cue=2, channels="2", at="50", fade=1.5),
        ],
    )

    commands = [command.command for command in commands_for_cue_stack(stack)]

    assert commands == [
        "Channel 1 At Full",
        "Store Cue 1",
        "Clear",
        "Channel 2 At 50",
        "Store Cue 2",
        "Cue 2 Time 1.5",
    ]


def test_load_cue_stack_from_json(tmp_path):
    path = tmp_path / "stack.json"
    path.write_text(
        json.dumps(
            {
                "sequence": 1,
                "name": "Demo Stack",
                "cues": [
                    {
                        "cue": 1,
                        "label": "Intro",
                        "channels": "1 Thru 8",
                        "at": "Full",
                        "fade": 2.5,
                        "clear_after": True,
                    }
                ],
            }
        )
    )

    stack = load_cue_stack(path)

    assert stack.sequence == 1
    assert stack.name == "Demo Stack"
    assert stack.cues[0].cue == 1
    assert stack.cues[0].clear_after is True


def test_load_cue_stack_rejects_malformed_json(tmp_path):
    path = tmp_path / "stack.json"
    path.write_text("{")

    with pytest.raises(ValueError, match="Invalid cue stack JSON"):
        load_cue_stack(path)


def test_load_cue_stack_requires_cues(tmp_path):
    path = tmp_path / "stack.json"
    path.write_text(json.dumps({"sequence": 1, "name": "Empty", "cues": []}))

    with pytest.raises(ValueError, match="at least one cue"):
        load_cue_stack(path)


def test_set_cue_time_negative_fade():
    with pytest.raises(ValueError, match="fade must be >= 0"):
        set_cue_time(1, -1.0)


def test_cue_step_requires_both_channels_and_at():
    step = CueStep(cue=1, label="Test", channels="1", at=None)
    with pytest.raises(ValueError, match="both channels and at"):
        commands_for_cue_step(step)

    step2 = CueStep(cue=1, label="Test", channels=None, at="Full")
    with pytest.raises(ValueError, match="both channels and at"):
        commands_for_cue_step(step2)


class TestSequenceCommands:
    def test_store_sequence(self) -> None:
        assert store_sequence(1).command == "Store Sequence 1"
        assert store_sequence(5).command == "Store Sequence 5"

    def test_label_sequence(self) -> None:
        cmd = label_sequence(1, "My Show")
        assert cmd.command == 'Label Sequence 1 "My Show"'

    def test_delete_sequence(self) -> None:
        assert delete_sequence(3).command == "Delete Sequence 3"

    def test_clear_all(self) -> None:
        assert clear_all().command == "ClearAll"

    def test_store_sequence_validation(self) -> None:
        with pytest.raises(ValueError):
            store_sequence(0)
        with pytest.raises(ValueError):
            store_sequence(-1)

    def test_label_sequence_validation(self) -> None:
        with pytest.raises(ValueError):
            label_sequence(0, "Show")
        with pytest.raises(ValueError):
            label_sequence(1, "")

    def test_delete_sequence_validation(self) -> None:
        with pytest.raises(ValueError):
            delete_sequence(0)
