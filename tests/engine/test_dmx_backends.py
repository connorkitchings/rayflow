"""Tests for DMX backend evidence adapters."""

from unittest.mock import patch

from rayflow.engine.backends import ArtNetDmxBackend, SacnDmxBackend
from rayflow.engine.rendering import DmxFrame, RenderedCue


def _rendered() -> RenderedCue:
    return RenderedCue(
        cue_number=1,
        cue_label="Hit",
        section="Intro",
        timestamp=0,
        frames=[DmxFrame(universe=0, channels={1: 255, 13: 128})],
    )


def test_artnet_dry_run_returns_frame_plan_and_commands() -> None:
    evidence = ArtNetDmxBackend(target_ip="192.0.2.10").dry_run(_rendered())

    assert evidence.backend == "artnet"
    assert evidence.mode == "dry-run"
    assert evidence.target == "192.0.2.10:6454"
    assert evidence.frames[0]["channels"] == {1: 255, 13: 128}
    assert evidence.observed == {"status": "not-applied"}
    assert "ArtDMX universe 0" in evidence.commands[0]


def test_artnet_apply_expands_sparse_frame_to_universe_buffer() -> None:
    sender_instance = patch("rayflow.engine.bridge.artnet.ArtNetSender").start()
    try:
        evidence = ArtNetDmxBackend(target_ip="192.0.2.10").apply(_rendered())
    finally:
        patch.stopall()

    sender_instance.assert_called_once_with(target_ip="192.0.2.10", universe=0)
    buffer = sender_instance.return_value.set_universe.call_args.args[0]
    assert len(buffer) == 512
    assert buffer[0] == 255
    assert buffer[12] == 128
    assert evidence.mode == "apply"
    assert evidence.observed["evidence_quality"] == "send-call-only"
    assert any("No receiver" in warning for warning in evidence.warnings)


def test_artnet_apply_can_capture_receiver_buffer_evidence() -> None:
    sender_class = patch("rayflow.engine.bridge.artnet.ArtNetSender").start()
    receiver_class = patch("rayflow.engine.bridge.artnet.ArtNetReceiver").start()
    buffer = [0] * 512
    buffer[0] = 255
    buffer[12] = 128
    receiver_class.return_value.get_buffer.return_value = buffer
    try:
        evidence = ArtNetDmxBackend(target_ip="192.0.2.10").apply(
            _rendered(),
            capture_evidence=True,
        )
    finally:
        patch.stopall()

    sender_class.assert_called_once_with(target_ip="192.0.2.10", universe=0)
    receiver_class.assert_called_once_with(universe=0)
    receiver_class.return_value.stop.assert_called_once()
    assert evidence.observed["evidence_quality"] == "receiver-buffer"
    capture = evidence.observed["receiver_captures"][0]
    assert capture["observed_values"] == {1: 255, 13: 128}
    assert capture["matches_rendered"] is True


def test_artnet_capture_reports_exact_mismatches() -> None:
    patch("rayflow.engine.bridge.artnet.ArtNetSender").start()
    receiver_class = patch("rayflow.engine.bridge.artnet.ArtNetReceiver").start()
    receiver_class.return_value.get_buffer.return_value = [0] * 512
    try:
        evidence = ArtNetDmxBackend(target_ip="192.0.2.10").apply(
            _rendered(),
            capture_evidence=True,
            evidence_timeout=0,
        )
    finally:
        patch.stopall()

    assert evidence.observed["evidence_quality"] == "receiver-buffer-mismatch"
    receiver_class.return_value.stop.assert_called_once()
    capture = evidence.observed["receiver_captures"][0]
    assert capture["mismatches"] == {
        1: {"expected": 255, "observed": 0},
        13: {"expected": 128, "observed": 0},
    }


def test_sacn_dry_run_records_universe_mapping() -> None:
    evidence = SacnDmxBackend(universe_offset=1).dry_run(_rendered())

    assert evidence.backend == "sacn"
    assert evidence.mode == "dry-run"
    assert evidence.frames[0]["rayflow_universe"] == 0
    assert evidence.frames[0]["sacn_universe"] == 1
    assert evidence.observed["universe_mapping"] == [
        {"rayflow_universe": 0, "sacn_universe": 1}
    ]


def test_sacn_apply_expands_sparse_frame_and_stops_sender() -> None:
    sender_class = patch("rayflow.engine.bridge.sacn_bridge.SacnSender").start()
    try:
        evidence = SacnDmxBackend(multicast=False, universe_offset=1).apply(_rendered())
    finally:
        patch.stopall()

    sender_class.assert_called_once_with(
        universe=1,
        multicast=False,
        source_name="RayFlow",
    )
    sender = sender_class.return_value
    buffer = sender.set_universe.call_args.args[0]
    assert isinstance(buffer, tuple)
    assert len(buffer) == 512
    assert buffer[0] == 255
    assert buffer[12] == 128
    sender.flush.assert_called_once()
    sender.stop.assert_called_once()
    assert evidence.mode == "apply"
    assert evidence.observed["evidence_quality"] == "send-call-only"


def test_sacn_apply_can_capture_receiver_universe_state() -> None:
    sender_class = patch("rayflow.engine.bridge.sacn_bridge.SacnSender").start()
    receiver_class = patch("rayflow.engine.bridge.sacn_bridge.SacnReceiver").start()
    receiver_class.return_value.get_possible_universes.return_value = (1,)
    try:
        evidence = SacnDmxBackend(multicast=True, universe_offset=1).apply(
            _rendered(),
            capture_evidence=True,
        )
    finally:
        patch.stopall()

    sender_class.assert_called_once()
    receiver_class.assert_called_once_with(universe=1)
    receiver = receiver_class.return_value
    receiver.join_multicast.assert_called_once()
    receiver.stop.assert_called_once()
    assert evidence.observed["evidence_quality"] == "receiver-state"
    assert evidence.observed["possible_universes"] == [1]


def test_sacn_capture_reports_universe_mismatch() -> None:
    patch("rayflow.engine.bridge.sacn_bridge.SacnSender").start()
    receiver_class = patch("rayflow.engine.bridge.sacn_bridge.SacnReceiver").start()
    receiver_class.return_value.get_possible_universes.return_value = ()
    try:
        evidence = SacnDmxBackend(multicast=False, universe_offset=1).apply(
            _rendered(),
            capture_evidence=True,
            evidence_timeout=0,
        )
    finally:
        patch.stopall()

    assert evidence.observed["evidence_quality"] == "receiver-state-mismatch"
    assert any("did not observe" in warning for warning in evidence.warnings)
