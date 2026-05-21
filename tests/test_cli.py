"""CLI integration tests for bridge commands."""

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rayflow.cli import app

runner = CliRunner()


class TestBridgeSend:
    """Tests for `rayflow bridge send` command."""

    @patch("rayflow.bridge.artnet.ArtNetSender")
    def test_send_artnet_basic(self, mock_sender_cls):
        mock_sender = MagicMock()
        mock_sender_cls.return_value = mock_sender

        result = runner.invoke(
            app, ["bridge", "send", "--channel", "1", "--value", "255"]
        )

        assert result.exit_code == 0
        assert "Sending" in result.output
        assert "channel 1 = 255" in result.output
        assert "via artnet" in result.output
        mock_sender_cls.assert_called_once_with(target_ip="127.0.0.1", universe=0)
        mock_sender.set_channel.assert_called_once_with(1, 255)

    @patch("rayflow.bridge.artnet.ArtNetSender")
    def test_send_artnet_custom_target(self, mock_sender_cls):
        mock_sender = MagicMock()
        mock_sender_cls.return_value = mock_sender

        result = runner.invoke(
            app,
            [
                "bridge",
                "send",
                "--channel",
                "1",
                "--value",
                "128",
                "--target",
                "192.168.1.50",
                "--universe",
                "3",
            ],
        )

        assert result.exit_code == 0
        assert "Target: 192.168.1.50:6454" in result.output
        mock_sender_cls.assert_called_once_with(target_ip="192.168.1.50", universe=3)

    @patch("rayflow.bridge.sacn_bridge.SacnSender")
    def test_send_sacn(self, mock_sender_cls):
        mock_sender = MagicMock()
        mock_sender_cls.return_value = mock_sender

        result = runner.invoke(
            app,
            [
                "bridge",
                "send",
                "--protocol",
                "sacn",
                "--universe",
                "1",
                "--channel",
                "5",
                "--value",
                "64",
            ],
        )

        assert result.exit_code == 0
        assert "via sacn" in result.output
        mock_sender_cls.assert_called_once_with(universe=1, multicast=False)
        mock_sender.set_channels.assert_called_once()
        mock_sender.flush.assert_called_once()
        mock_sender.stop.assert_called_once()

    @patch("rayflow.bridge.sacn_bridge.SacnSender")
    def test_send_sacn_multicast(self, mock_sender_cls):
        mock_sender = MagicMock()
        mock_sender_cls.return_value = mock_sender

        result = runner.invoke(
            app,
            [
                "bridge",
                "send",
                "--protocol",
                "sacn",
                "--universe",
                "1",
                "--channel",
                "5",
                "--value",
                "64",
                "--multicast",
            ],
        )

        assert result.exit_code == 0
        mock_sender_cls.assert_called_once_with(universe=1, multicast=True)

    def test_send_channel_below_1(self):
        result = runner.invoke(
            app, ["bridge", "send", "--channel", "0", "--value", "128"]
        )
        assert result.exit_code == 2
        assert "Channel must be 1-512" in result.output

    def test_send_channel_above_512(self):
        result = runner.invoke(
            app, ["bridge", "send", "--channel", "513", "--value", "128"]
        )
        assert result.exit_code == 2
        assert "Channel must be 1-512" in result.output

    def test_send_value_negative(self):
        result = runner.invoke(
            app, ["bridge", "send", "--channel", "1", "--value", "-1"]
        )
        assert result.exit_code == 2
        assert "Value must be 0-255" in result.output

    def test_send_value_above_255(self):
        result = runner.invoke(
            app, ["bridge", "send", "--channel", "1", "--value", "300"]
        )
        assert result.exit_code == 2
        assert "Value must be 0-255" in result.output

    def test_send_unknown_protocol(self):
        result = runner.invoke(
            app,
            ["bridge", "send", "--protocol", "foo", "--channel", "1", "--value", "128"],
        )
        assert result.exit_code == 2
        assert "Unknown protocol" in result.output

    @patch("rayflow.bridge.artnet.ArtNetSender")
    def test_bridge_error_propagates(self, mock_sender_cls):
        from rayflow.bridge.exceptions import NetworkError

        mock_sender_cls.side_effect = NetworkError("Host down")
        result = runner.invoke(
            app, ["bridge", "send", "--channel", "1", "--value", "128"]
        )
        assert result.exit_code == 1
        assert "Host down" in result.output


class TestBridgeRecv:
    """Tests for `rayflow bridge recv` command."""

    @patch("rayflow.bridge.artnet.ArtNetReceiver")
    def test_recv_artnet(self, mock_receiver_cls):
        mock_receiver = MagicMock()
        mock_receiver.get_buffer.return_value = [0] * 512
        mock_receiver_cls.return_value = mock_receiver

        result = runner.invoke(
            app, ["bridge", "recv", "--protocol", "artnet", "--duration", "1"]
        )

        assert result.exit_code == 0
        assert "Listening" in result.output
        assert "via artnet" in result.output
        mock_receiver_cls.assert_called_once_with(universe=0)

    @patch("rayflow.bridge.sacn_bridge.SacnReceiver")
    def test_recv_sacn(self, mock_receiver_cls):
        mock_receiver = MagicMock()
        mock_receiver_cls.return_value = mock_receiver

        result = runner.invoke(
            app, ["bridge", "recv", "--protocol", "sacn", "--duration", "1"]
        )

        assert result.exit_code == 0
        assert "via sacn" in result.output
        mock_receiver_cls.assert_called_once_with(universe=0)
        mock_receiver.join_multicast.assert_called_once()

    @patch("rayflow.bridge.artnet.ArtNetReceiver")
    def test_recv_shows_non_zero_channels(self, mock_receiver_cls):
        mock_receiver = MagicMock()
        buffer = [0] * 512
        buffer[0] = 255
        buffer[4] = 128
        mock_receiver.get_buffer.return_value = buffer
        mock_receiver_cls.return_value = mock_receiver

        result = runner.invoke(
            app, ["bridge", "recv", "--protocol", "artnet", "--duration", "1"]
        )

        assert result.exit_code == 0
        assert "Listening" in result.output

    def test_recv_unknown_protocol(self):
        result = runner.invoke(app, ["bridge", "recv", "--protocol", "foo"])
        assert result.exit_code == 2
        assert "Unknown protocol" in result.output


class TestBridgeStatus:
    """Tests for `rayflow bridge status` command."""

    def test_status_shows_config(self):
        result = runner.invoke(app, ["bridge", "status"])

        assert result.exit_code == 0
        assert "RayFlow Bridge Status" in result.output
        assert "Art-Net" in result.output
        assert "127.0.0.1" in result.output
        assert "6454" in result.output
        assert "sACN" in result.output
        assert "Ready" in result.output


class TestFixtureCommands:
    """Tests for fixture subcommands."""

    def test_fixture_list(self, sample_gdtf_library):
        result = runner.invoke(
            app, ["fixture", "list", "--dir", str(sample_gdtf_library)]
        )
        assert result.exit_code == 0
        assert "GDTF Fixtures" in result.output
        assert "RayFlow" in result.output
        assert "Sample Dimmer" in result.output

    def test_fixture_info(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            ["fixture", "info", "Sample", "--dir", str(sample_gdtf_library)],
        )
        assert result.exit_code == 0
        assert "RayFlow" in result.output
        assert "Sample Dimmer" in result.output
        assert "Basic" in result.output
        assert "Dimmer" in result.output

    def test_fixture_info_missing(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            ["fixture", "info", "Missing", "--dir", str(sample_gdtf_library)],
        )
        assert result.exit_code == 1
        assert "Fixture not found" in result.output

    def test_fixture_patch(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            [
                "fixture",
                "patch",
                "Sample",
                "--dir",
                str(sample_gdtf_library),
                "--address",
                "10",
            ],
        )

        assert result.exit_code == 0
        assert "RayFlow" in result.output
        assert "Sample Dimmer" in result.output
        assert "Mode: Basic" in result.output
        assert "Address: 10-10" in result.output
        assert "Dimmer" in result.output

    def test_fixture_patch_missing(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            [
                "fixture",
                "patch",
                "Missing",
                "--dir",
                str(sample_gdtf_library),
            ],
        )

        assert result.exit_code == 1
        assert "Fixture not found" in result.output

    def test_fixture_compare_ma3_text_report(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            [
                "fixture",
                "compare-ma3",
                "Sample",
                "--dir",
                str(sample_gdtf_library),
                "--address",
                "10",
            ],
        )

        assert result.exit_code == 0
        assert "Sample Dimmer" in result.output
        assert "Mode: Basic" in result.output
        assert "Address: 10-10" in result.output
        assert "Dimmer" in result.output

    def test_fixture_compare_ma3_json_report(self, sample_gdtf_library):
        result = runner.invoke(
            app,
            [
                "fixture",
                "compare-ma3",
                "Sample",
                "--dir",
                str(sample_gdtf_library),
                "--json",
            ],
        )

        assert result.exit_code == 0
        payload = json.loads(result.output)
        assert payload["fixture"] == "Sample Dimmer"
        assert payload["mode"] == "Basic"

    def test_fixture_compare_ma3_observation_mismatch(
        self, sample_gdtf_library, tmp_path
    ):
        observation = {
            "manufacturer": "RayFlow",
            "fixture": "Sample Dimmer",
            "mode": "Wrong",
            "universe": 0,
            "start_address": 1,
            "end_address": 1,
            "channel_count": 1,
            "required_attributes": ["Dimmer"],
        }
        observation_path = tmp_path / "ma3-observation.json"
        observation_path.write_text(json.dumps(observation))

        result = runner.invoke(
            app,
            [
                "fixture",
                "compare-ma3",
                "Sample",
                "--dir",
                str(sample_gdtf_library),
                "--ma3-json",
                str(observation_path),
            ],
        )

        assert result.exit_code == 1
        assert "mismatched" in result.output
        assert "mode" in result.output


class TestConsoleCommands:
    """Tests for console subcommands."""

    def test_console_connect(self):
        result = runner.invoke(app, ["console", "connect"])
        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "About" in result.output
        assert "--execute" in result.output

    def test_console_cmd(self):
        result = runner.invoke(app, ["console", "cmd", "Store Cue 1"])
        assert result.exit_code == 0
        assert "Store Cue 1" in result.output
        assert "Dry run" in result.output

    @patch("rayflow.console.osc.Ma3OscClient")
    def test_console_connect_executes_about(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        result = runner.invoke(app, ["console", "connect", "--execute"])

        assert result.exit_code == 0
        mock_client_cls.assert_called_once_with(ip="127.0.0.1", port=8000)
        mock_client.send.assert_called_once_with("About")
        assert "Sent" in result.output

    @patch("rayflow.console.osc.Ma3OscClient")
    def test_console_cmd_executes_only_with_execute(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        dry_run = runner.invoke(app, ["console", "cmd", "Store Cue 1"])
        sent = runner.invoke(app, ["console", "cmd", "Store Cue 1", "--execute"])

        assert dry_run.exit_code == 0
        assert sent.exit_code == 0
        mock_client.send.assert_called_once_with("Store Cue 1")

    def test_console_cmd_rejects_empty_command(self):
        result = runner.invoke(app, ["console", "cmd", "   ", "--execute"])

        assert result.exit_code == 1
        assert "must not be empty" in result.output

    @patch("rayflow.console.osc.Ma3OscFeedbackReceiver")
    def test_console_listen(self, mock_receiver_cls):
        mock_receiver = MagicMock()
        mock_receiver.listen.return_value = []
        mock_receiver_cls.return_value = mock_receiver

        result = runner.invoke(app, ["console", "listen", "--duration", "0"])

        assert result.exit_code == 0
        mock_receiver_cls.assert_called_once_with(host="127.0.0.1", port=8001)
        mock_receiver.listen.assert_called_once_with(duration=0.0)
        assert "No OSC feedback received" in result.output

    def test_console_cue_store_dry_run(self):
        result = runner.invoke(app, ["console", "cue", "store", "1", "--fade", "2.5"])

        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "Store Cue 1" in result.output
        assert "Cue 1 CueFade 2.5" in result.output

    @patch("rayflow.console.osc.Ma3OscClient")
    def test_console_cue_store_execute(self, mock_client_cls):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        result = runner.invoke(
            app,
            ["console", "cue", "store", "1", "--fade", "2.5", "--execute"],
        )

        assert result.exit_code == 0
        assert [call.args[0] for call in mock_client.send.call_args_list] == [
            "Store Cue 1 /Overwrite /NoConfirmation",
            "Cue 1 CueFade 2.5",
        ]

    def test_console_sequence_go_dry_run(self):
        result = runner.invoke(app, ["console", "sequence", "go", "1"])

        assert result.exit_code == 0
        assert "Go Sequence 1" in result.output

    def test_console_channel_at_dry_run(self):
        result = runner.invoke(app, ["console", "channel", "at", "1 Thru 8", "Full"])

        assert result.exit_code == 0
        assert "Channel 1 Thru 8 At Full" in result.output

    def test_console_clear_dry_run(self):
        result = runner.invoke(app, ["console", "clear"])

        assert result.exit_code == 0
        assert "Clear" in result.output

    def test_console_cue_stack_run_dry_run(self, tmp_path):
        stack_path = tmp_path / "stack.json"
        stack_path.write_text(
            json.dumps(
                {
                    "sequence": 1,
                    "name": "Demo Stack",
                    "cues": [
                        {
                            "cue": 1,
                            "channels": "1 Thru 8",
                            "at": "Full",
                            "fade": 2.5,
                            "clear_after": True,
                        }
                    ],
                }
            )
        )

        result = runner.invoke(app, ["console", "cue-stack", "run", str(stack_path)])

        assert result.exit_code == 0
        assert "Demo Stack" in result.output
        assert "Channel 1 Thru 8 At Full" in result.output
        assert "Store Cue 1" in result.output
        assert "Cue 1 CueFade 2.5" in result.output
        assert "Clear" in result.output

    @patch("rayflow.console.osc.Ma3OscClient")
    def test_console_cue_stack_run_execute(self, mock_client_cls, tmp_path):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        stack_path = tmp_path / "stack.json"
        stack_path.write_text(
            json.dumps(
                {
                    "sequence": 1,
                    "name": "Demo Stack",
                    "cues": [
                        {
                            "cue": 1,
                            "channels": "1",
                            "at": "Full",
                            "clear_after": True,
                        },
                        {
                            "cue": 2,
                            "channels": "2",
                            "at": "50",
                        },
                    ],
                }
            )
        )

        result = runner.invoke(
            app,
            ["console", "cue-stack", "run", str(stack_path), "--execute"],
        )

        assert result.exit_code == 0
        assert [call.args[0] for call in mock_client.send.call_args_list] == [
            "Channel 1 At Full",
            "Store Cue 1 /Overwrite /NoConfirmation",
            "Clear",
            "Channel 2 At 50",
            "Store Cue 2 /Overwrite /NoConfirmation",
        ]

    def test_console_cue_stack_rejects_bad_json(self, tmp_path):
        stack_path = tmp_path / "stack.json"
        stack_path.write_text("{")

        result = runner.invoke(app, ["console", "cue-stack", "run", str(stack_path)])

        assert result.exit_code == 1
        assert "Invalid cue stack JSON" in result.output
