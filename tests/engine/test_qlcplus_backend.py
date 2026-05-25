"""Tests for experimental QLC+ WebSocket adapter."""

import sys
import types

from rayflow.engine.backends import QlcPlusBackend
from rayflow.engine.rendering import DmxFrame, RenderedCue


class FakeWebSocket:
    def __init__(self):
        self.sent: list[str] = []
        self.closed = False

    def send(self, command: str) -> None:
        self.sent.append(command)

    def recv(self) -> str:
        return f"response:{self.sent[-1]}"

    def close(self) -> None:
        self.closed = True


def _rendered_cue() -> RenderedCue:
    return RenderedCue(
        cue_number=1.0,
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
    assert fake_ws.closed is True
    assert fake_ws.sent[-1] == "QLC+API|setChannelsValues|1|1|255|2|128"


def test_qlcplus_unavailable_returns_structured_evidence(monkeypatch) -> None:
    def fail_connection(*args, **kwargs):
        raise OSError("connection refused")

    fake_module = types.SimpleNamespace(create_connection=fail_connection)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend().apply(_rendered_cue())

    assert evidence.observed["status"] == "unavailable"
    assert "connection refused" in evidence.observed["error"]
    assert evidence.warnings == ["QLC+ WebSocket endpoint was unavailable."]
