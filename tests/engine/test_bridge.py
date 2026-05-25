"""Functional tests for Art-Net and sACN bridge classes."""

from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest

from rayflow.engine.bridge.artnet import ArtNetReceiver, ArtNetSender
from rayflow.engine.bridge.exceptions import (
    InvalidChannelError,
    InvalidUniverseError,
    InvalidValueError,
    NetworkError,
)
from rayflow.engine.bridge.sacn_bridge import SacnReceiver, SacnSender
from rayflow.engine.fixtures.parser import GdtfParser
from rayflow.engine.fixtures.patch import DmxUniverse, FixturePatch

SAMPLES_DIR = Path("data/fixtures/samples")


def _artdmx_packet(universe: int, values: list[int]) -> bytes:
    header = bytearray(b"Art-Net\x00\x00P\x00\x0e")
    header.extend((0, 0))
    header.extend(universe.to_bytes(2, "little"))
    header.extend(len(values).to_bytes(2, "big"))
    return bytes(header + bytearray(values))


class TestArtNetSender:
    """Tests for ArtNetSender with mocked stupidArtnet library."""

    def test_set_single_channel(self, mock_artnet_lib):
        sender = ArtNetSender(target_ip="127.0.0.1", universe=0)
        sender.set_channel(1, 128)

        mock_artnet_lib["sender_class"].assert_called_once_with(
            target_ip="127.0.0.1", universe=0
        )
        mock_artnet_lib["sender_instance"].set_single_value.assert_called_with(1, 128)
        mock_artnet_lib["sender_instance"].show.assert_called_once()

    def test_set_multiple_channels(self, mock_artnet_lib):
        sender = ArtNetSender(target_ip="127.0.0.1", universe=0)
        sender.set_channels({1: 255, 10: 64, 512: 0})

        expected = [call(1, 255), call(10, 64), call(512, 0)]
        mock_artnet_lib["sender_instance"].set_single_value.assert_has_calls(
            expected, any_order=False
        )
        assert mock_artnet_lib["sender_instance"].set_single_value.call_count == 3
        mock_artnet_lib["sender_instance"].show.assert_called_once()

    def test_set_universe(self, mock_artnet_lib):
        sender = ArtNetSender(target_ip="127.0.0.1", universe=0)
        data = [0] * 512
        data[0] = 255
        sender.set_universe(data)

        mock_artnet_lib["sender_instance"].set.assert_called_with(data)
        mock_artnet_lib["sender_instance"].show.assert_called_once()

    def test_start_stop_thread(self, mock_artnet_lib):
        sender = ArtNetSender(target_ip="127.0.0.1", universe=0)

        sender.start_thread()
        mock_artnet_lib["sender_instance"].start.assert_called_once()

        sender.stop_thread()
        mock_artnet_lib["sender_instance"].stop.assert_called_once()

    def test_default_values(self, mock_artnet_lib):
        sender = ArtNetSender()
        assert sender.target_ip == "127.0.0.1"
        assert sender.universe == 0

    def test_custom_target_and_universe(self, mock_artnet_lib):
        sender = ArtNetSender(target_ip="192.168.1.100", universe=3)
        assert sender.target_ip == "192.168.1.100"
        assert sender.universe == 3

    def test_channel_below_range(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidChannelError, match="Channel must be 1-512"):
            sender.set_channel(0, 128)

    def test_channel_above_range(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidChannelError, match="Channel must be 1-512"):
            sender.set_channel(513, 128)

    def test_value_below_range(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidValueError, match="Value must be 0-255"):
            sender.set_channel(1, -1)

    def test_value_above_range(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidValueError, match="Value must be 0-255"):
            sender.set_channel(1, 256)

    def test_value_255_is_valid(self, mock_artnet_lib):
        sender = ArtNetSender()
        sender.set_channel(1, 255)
        mock_artnet_lib["sender_instance"].set_single_value.assert_called_with(1, 255)

    def test_value_0_is_valid(self, mock_artnet_lib):
        sender = ArtNetSender()
        sender.set_channel(1, 0)
        mock_artnet_lib["sender_instance"].set_single_value.assert_called_with(1, 0)

    def test_set_channels_with_invalid_channel(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidChannelError):
            sender.set_channels({0: 128, 1: 255})

    def test_set_channels_with_invalid_value(self, mock_artnet_lib):
        sender = ArtNetSender()
        with pytest.raises(InvalidValueError):
            sender.set_channels({1: 300, 2: 255})

    def test_invalid_universe_raises(self, mock_artnet_lib):
        with pytest.raises(InvalidUniverseError, match="0-15"):
            ArtNetSender(universe=16)

    def test_negative_universe_raises(self, mock_artnet_lib):
        with pytest.raises(InvalidUniverseError, match="0-15"):
            ArtNetSender(universe=-1)

    def test_network_error_on_init_failure(self):
        with patch("rayflow.engine.bridge.artnet.StupidArtnet") as mock_lib:
            mock_lib.side_effect = OSError("Network unreachable")
            with pytest.raises(NetworkError, match="Network unreachable"):
                ArtNetSender(target_ip="192.168.1.100")


class TestArtNetReceiver:
    """Tests for the native Art-Net receiver."""

    def test_get_buffer(self):
        expected_buffer = [0] * 512
        expected_buffer[0] = 255

        receiver = ArtNetReceiver(universe=0, port=0)
        try:
            receiver._handle_packet(_artdmx_packet(0, expected_buffer))
            buffer = receiver.get_buffer()
        finally:
            receiver.stop()

        assert buffer == expected_buffer

    def test_receiver_with_callback(self):
        cb = MagicMock()

        receiver = ArtNetReceiver(universe=1, callback=cb, port=0)
        try:
            receiver._handle_packet(_artdmx_packet(1, [128] * 512))
        finally:
            receiver.stop()

        cb.assert_called_once_with([128] * 512)


class TestSacnSender:
    """Tests for SacnSender with mocked sacn library."""

    def test_set_channels(self, mock_sacn_lib):
        mock_sender = mock_sacn_lib["sender"]
        fake_data = [0] * 512
        mock_sender.__getitem__.return_value.dmx_data = tuple(fake_data)
        mock_sender.__getitem__.return_value.multicast = True

        sender = SacnSender(universe=1, multicast=True)

        # Reset mock state after init calls
        mock_sender.__getitem__.return_value.dmx_data = tuple(fake_data)

        sender.set_channels({1: 128, 5: 255})
        expected = [0] * 512
        expected[0] = 128
        expected[4] = 255
        assert mock_sender.__getitem__.return_value.dmx_data == tuple(expected)

    def test_default_multicast_flag(self, mock_sacn_lib):
        sender = SacnSender()
        assert sender.multicast is True
        assert sender.universe == 1

    def test_channel_out_of_range(self, mock_sacn_lib):
        sender = SacnSender()
        with pytest.raises(InvalidChannelError, match="Channel must be 1-512"):
            sender.set_channels({0: 128})

    def test_channel_above_512(self, mock_sacn_lib):
        sender = SacnSender()
        with pytest.raises(InvalidChannelError, match="Channel must be 1-512"):
            sender.set_channels({513: 128})

    def test_value_negative(self, mock_sacn_lib):
        sender = SacnSender()
        with pytest.raises(InvalidValueError, match="Value must be 0-255"):
            sender.set_channels({1: -5})

    def test_value_above_255(self, mock_sacn_lib):
        sender = SacnSender()
        with pytest.raises(InvalidValueError, match="Value must be 0-255"):
            sender.set_channels({1: 300})

    def test_set_universe(self, mock_sacn_lib):
        sender = SacnSender()
        data = tuple([0] * 512)
        sender.set_universe(data)
        mock_sacn_lib["sender"].__getitem__.return_value.dmx_data == data

    def test_flush(self, mock_sacn_lib):
        sender = SacnSender()
        sender.flush()
        mock_sacn_lib["sender"].flush.assert_called_once()

    def test_stop(self, mock_sacn_lib):
        sender = SacnSender()
        sender.stop()
        mock_sacn_lib["sender"].stop.assert_called_once()

    def test_network_error_on_init_failure(self):
        with patch("rayflow.engine.bridge.sacn_bridge.sacn") as mock_sacn:
            mock_sender = MagicMock()
            mock_sacn.sACNsender.return_value = mock_sender
            mock_sender.start.side_effect = OSError("Cannot bind port")
            with pytest.raises(NetworkError, match="Cannot bind port"):
                SacnSender()


class TestSacnReceiver:
    """Tests for SacnReceiver with mocked sacn library."""

    def test_receiver_creation(self, mock_sacn_lib):
        SacnReceiver(universe=1)
        mock_sacn_lib["sacn"].sACNreceiver.assert_called_once()
        mock_sacn_lib["receiver"].start.assert_called_once()

    def test_join_multicast(self, mock_sacn_lib):
        receiver = SacnReceiver(universe=1)
        receiver.join_multicast()
        mock_sacn_lib["receiver"].join_multicast.assert_called_with(1)

    def test_receiver_with_callback(self, mock_sacn_lib):
        def _cb(data):
            pass

        SacnReceiver(universe=1, callback=_cb)
        mock_sacn_lib["receiver"].listen_on.assert_called_once()

    def test_get_possible_universes(self, mock_sacn_lib):
        receiver = SacnReceiver(universe=1)
        receiver.get_possible_universes()
        mock_sacn_lib["receiver"].get_possible_universes.assert_called_once()

    def test_stop(self, mock_sacn_lib):
        receiver = SacnReceiver(universe=1)
        receiver.stop()
        mock_sacn_lib["receiver"].stop.assert_called_once()


class TestDmxUniverse:
    """Tests for DMX universe and fixture patching."""

    def test_patch_single_fixture(self):
        universe = DmxUniverse(universe_number=0)
        patch = universe.patch("Dimmer Wash", 1, 10)

        assert patch.name == "Dimmer Wash"
        assert patch.start_address == 1
        assert patch.channel_count == 10
        assert patch.end_address == 10
        assert patch.universe == 0
        assert patch.manufacturer is None
        assert patch.mode_name is None
        assert patch.channel_entries == []
        assert universe.used_channels == 10

    def test_patch_fixture_from_gdtf_parser(self, sample_gdtf_file):
        universe = DmxUniverse(universe_number=2)
        parser = GdtfParser(sample_gdtf_file)

        patch = universe.patch_fixture(parser, start_address=10)

        assert patch.name == "Sample Dimmer"
        assert patch.manufacturer == "RayFlow"
        assert patch.mode_name == "Basic"
        assert patch.start_address == 10
        assert patch.end_address == 10
        assert patch.channel_count == 1
        assert patch.universe == 2
        assert patch.channel_map is not None
        assert patch.channel_entries[0].attribute == "Dimmer"
        assert patch.channel_entries[0].dmx_address == 10
        assert patch.as_dict()["channels"][0]["attribute"] == "Dimmer"

    def test_patch_fixture_supports_summary_and_custom_name(self, sample_gdtf_file):
        universe = DmxUniverse(universe_number=4)
        summary = GdtfParser(sample_gdtf_file).get_summary()

        patch = universe.patch_fixture(
            summary,
            start_address=101,
            mode_name="Basic",
            name="Front Dimmer",
        )

        assert patch.name == "Front Dimmer"
        assert patch.manufacturer == "RayFlow"
        assert patch.mode_name == "Basic"
        assert patch.channel_entries[0].universe == 4
        assert patch.channel_entries[0].dmx_address == 101

    def test_patch_fixture_rejects_invalid_mode(self, sample_gdtf_file):
        universe = DmxUniverse()
        parser = GdtfParser(sample_gdtf_file)

        with pytest.raises(ValueError, match="DMX mode not found"):
            universe.patch_fixture(parser, start_address=1, mode_name="Missing")

    def test_patch_multiple_fixtures(self):
        universe = DmxUniverse(universe_number=1)
        universe.patch("Fixture A", 1, 10)
        universe.patch("Fixture B", 11, 5)
        universe.patch("Fixture C", 21, 8)

        assert universe.used_channels == 23
        assert len(universe.patches) == 3

    def test_patch_overlap_detection(self):
        universe = DmxUniverse()
        universe.patch("Fixture A", 1, 20)
        with pytest.raises(ValueError, match="Address conflict"):
            universe.patch("Fixture B", 15, 10)

        universe.patch("Fixture B", 21, 10)

    def test_patch_fixture_detects_overlap_with_raw_patch(self):
        universe = DmxUniverse()
        universe.patch("Reserved", 1, 25)
        parser = GdtfParser(SAMPLES_DIR / "BlenderDMX_LED_PAR_64_RGBW.gdtf")

        with pytest.raises(ValueError, match="Address conflict"):
            universe.patch_fixture(parser, start_address=20)

    def test_patch_beyond_512_raises(self):
        universe = DmxUniverse()
        with pytest.raises(ValueError, match="exceeds universe bounds"):
            universe.patch("Too Big", 510, 10)

    def test_patch_fixture_beyond_512_uses_real_channel_count(self):
        universe = DmxUniverse()
        parser = GdtfParser(SAMPLES_DIR / "BlenderDMX_LED_PAR_64_RGBW.gdtf")

        with pytest.raises(ValueError, match="exceeds universe bounds"):
            universe.patch_fixture(parser, start_address=509)

    def test_patch_real_led_par_sample(self):
        universe = DmxUniverse(universe_number=1)
        parser = GdtfParser(SAMPLES_DIR / "BlenderDMX_LED_PAR_64_RGBW.gdtf")

        patch = universe.patch_fixture(parser, start_address=20)
        attributes = {entry.attribute for entry in patch.channel_entries}

        assert patch.start_address == 20
        assert patch.end_address == 24
        assert patch.channel_count == 5
        assert {"Dimmer", "ColorAdd_R", "ColorAdd_G", "ColorAdd_B", "ColorAdd_W"} <= (
            attributes
        )

    def test_patch_real_mmx_blade_sample(self):
        universe = DmxUniverse(universe_number=3)
        parser = GdtfParser(SAMPLES_DIR / "Robe_Robin_MMX_Blade.gdtf")

        patch = universe.patch_fixture(
            parser,
            start_address=1,
            mode_name="Mode 1 - Standard",
        )
        families = {entry.family for entry in patch.channel_entries}

        assert patch.mode_name == "Mode 1 - Standard"
        assert patch.channel_count == 45
        assert patch.end_address == 45
        assert {"position", "gobo", "color"} <= families

    def test_patch_address_zero_raises(self):
        universe = DmxUniverse()
        with pytest.raises(ValueError, match="must be >= 1"):
            universe.patch("Bad Address", 0, 5)

    def test_unpatch_fixture(self):
        universe = DmxUniverse()
        universe.patch("Fixture A", 1, 10)
        universe.patch("Fixture B", 11, 5)

        assert universe.unpatch("Fixture A") is True
        assert universe.used_channels == 5
        assert len(universe.patches) == 1

    def test_unpatch_nonexistent(self):
        universe = DmxUniverse()
        universe.patch("Fixture A", 1, 10)
        assert universe.unpatch("No Such Fixture") is False

    def test_get_patch_by_name(self):
        universe = DmxUniverse()
        universe.patch("Moving Head", 1, 20)
        patch = universe.get_patch("Moving Head")
        assert patch is not None
        assert patch.channel_count == 20

    def test_get_patch_nonexistent(self):
        universe = DmxUniverse()
        assert universe.get_patch("nope") is None

    def test_overlap_across_universes(self):
        universe_0 = DmxUniverse(universe_number=0)
        universe_1 = DmxUniverse(universe_number=1)

        universe_0.patch("Fixture A U0", 1, 10)
        universe_1.patch("Fixture B U1", 1, 10)

        assert universe_0.used_channels == 10
        assert universe_1.used_channels == 10

    def test_end_address_calculation(self):
        patch = FixturePatch(name="Test", start_address=5, channel_count=3)
        assert patch.end_address == 7

    def test_overlap_no_overlap(self):
        a = FixturePatch(name="A", start_address=1, channel_count=10)
        b = FixturePatch(name="B", start_address=11, channel_count=5)
        assert not a.overlaps(b)
        assert not b.overlaps(a)

    def test_overlap_detected(self):
        a = FixturePatch(name="A", start_address=1, channel_count=10)
        b = FixturePatch(name="B", start_address=5, channel_count=5)
        assert a.overlaps(b)
        assert b.overlaps(a)

    def test_overlap_same_start(self):
        a = FixturePatch(name="A", start_address=1, channel_count=5)
        b = FixturePatch(name="B", start_address=1, channel_count=5)
        assert a.overlaps(b)

    def test_overlap_different_universe(self):
        a = FixturePatch(name="A", start_address=1, channel_count=5, universe=0)
        b = FixturePatch(name="B", start_address=1, channel_count=5, universe=1)
        assert not a.overlaps(b)
