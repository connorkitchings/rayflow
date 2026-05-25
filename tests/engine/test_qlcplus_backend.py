"""Tests for QLC+ WebSocket adapter."""

from __future__ import annotations

import sys
import types

import pytest

from rayflow.engine.backends import QlcPlusBackend
from rayflow.engine.rendering import DmxFrame, RenderedCue


class FakeWebSocket:
    def __init__(self):
        self.sent: list[str] = []
        self.closed = False
        self.channels: dict[tuple[int, int], int] = {}

    def send(self, command: str) -> None:
        self.sent.append(command)
        if command.startswith("QLC+API|setChannelsValues|"):
            parts = command.split("|")[2:]
            universe = int(parts[0])
            for i in range(1, len(parts), 2):
                ch = int(parts[i])
                val = int(parts[i + 1])
                self.channels[(universe, ch)] = val

    def recv(self) -> str:
        last = self.sent[-1]
        if last.startswith("QLC+API|getChannelsValues|"):
            parts = last.split("|")[2:]
            universe = int(parts[0])
            start = int(parts[1])
            count = int(parts[2])
            vals = []
            for ch in range(start, start + count):
                vals.append(str(self.channels.get((universe, ch), 0)))
            return "QLC+API|getChannelsValues|" + "|".join(vals)
        return f"response:{last}"

    def close(self) -> None:
        self.closed = True


def _rendered_cue() -> RenderedCue:
    return RenderedCue(
        cue_number=1,
        cue_label="Test",
        section="Chorus",
        timestamp=0.0,
        frames=[DmxFrame(universe=1, channels={1: 255, 2: 128})],
        warnings=[],
    )


def test_qlcplus_dry_run_does_not_connect() -> None:
    evidence = QlcPlusBackend().dry_run(_rendered_cue())

    assert evidence.backend == "qlcplus"
    assert evidence.mode == "dry-run"
    assert evidence.observed == {"status": "not-applied"}
    assert "QLC+API|setChannelsValues|1|1|255|2|128" in evidence.commands


def test_qlcplus_execute_records_websocket_responses(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS").apply(
        _rendered_cue(), capture_evidence=True
    )

    assert evidence.mode == "apply"
    assert evidence.observed["status"] == "queried"
    assert evidence.observed["evidence_quality"] == "websocket-response"
    assert evidence.observed["observed_matches"] is True
    assert fake_ws.closed is True
    assert fake_ws.sent[0] == "QLC+API|setChannelsValues|1|1|255|2|128"
    assert fake_ws.sent[1] == "QLC+API|getChannelsValues|1|1|2"


def test_qlcplus_query_channels_direct(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    # Pre-populate fake channel values
    fake_ws.channels[(1, 10)] = 200
    fake_ws.channels[(1, 11)] = 100

    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    backend = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS")
    vals = backend.query_channels(universe=1, start_address=10, count=2)
    assert vals == [200, 100]
    assert fake_ws.sent[-1] == "QLC+API|getChannelsValues|1|10|2"


def test_qlcplus_query_channels_invalid_response(monkeypatch) -> None:
    class BadWebSocket(FakeWebSocket):
        def recv(self) -> str:
            return "BadResponse"

    fake_ws = BadWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    backend = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS")
    with pytest.raises(ValueError, match="Unexpected response"):
        backend.query_channels(universe=1, start_address=10, count=2)


def test_qlcplus_unavailable_returns_structured_evidence(monkeypatch) -> None:
    def fail_connection(*args, **kwargs):
        raise OSError("connection refused")

    fake_module = types.SimpleNamespace(create_connection=fail_connection)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend().apply(_rendered_cue())

    assert evidence.observed["status"] == "unavailable"
    assert "connection refused" in evidence.observed["error"]
    assert evidence.warnings == ["QLC+ WebSocket endpoint was unavailable."]
