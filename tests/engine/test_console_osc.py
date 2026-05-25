"""Tests for grandMA3 OSC helpers."""

from unittest.mock import MagicMock, patch

import pytest

from rayflow.engine.console.osc import Ma3OscClient, Ma3OscFeedbackReceiver


@patch("rayflow.engine.console.osc.udp_client.SimpleUDPClient")
def test_ma3_osc_client_sends_to_cmd_endpoint(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client

    client = Ma3OscClient(ip="127.0.0.1", port=8000)
    client.send("Store Cue 1")

    mock_client_cls.assert_called_once_with("127.0.0.1", 8000)
    mock_client.send_message.assert_called_once_with("/cmd", "Store Cue 1")


@patch("rayflow.engine.console.osc.udp_client.SimpleUDPClient")
def test_ma3_osc_client_rejects_empty_commands(mock_client_cls):
    client = Ma3OscClient()

    with pytest.raises(ValueError, match="must not be empty"):
        client.send("   ")

    mock_client_cls.return_value.send_message.assert_not_called()


@patch("rayflow.engine.console.osc.udp_client.SimpleUDPClient")
def test_ma3_osc_client_helper_methods_use_cmd_endpoint(mock_client_cls):
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    client = Ma3OscClient()

    client.about()
    client.store_cue(3)
    client.go_sequence(2)
    client.set_intensity(50)
    client.set_channels("1 Thru 8", "Full")
    client.clear()
    client.set_time(3, 1.5)

    commands = [call.args[1] for call in mock_client.send_message.call_args_list]
    assert commands == [
        "About",
        "Store Cue 3",
        "Go Sequence 2",
        "At 50",
        "Channel 1 Thru 8 At Full",
        "Clear",
        "Cue 3 CueFade 1.5",
    ]


def test_feedback_receiver_captures_messages():
    receiver = Ma3OscFeedbackReceiver()

    receiver._handle_message("/feedback", "ok", 1)

    assert len(receiver.messages) == 1
    assert receiver.messages[0].index == 0
    assert receiver.messages[0].address == "/feedback"
    assert receiver.messages[0].args == ("ok", 1)
    assert receiver.messages[0].as_dict()["args"] == ["ok", 1]
