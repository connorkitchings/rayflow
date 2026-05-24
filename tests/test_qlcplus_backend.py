"""Tests for experimental QLC+ WebSocket adapter."""

import sys
import types

from rayflow.backends import QlcPlusBackend


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


def test_qlcplus_dry_run_does_not_connect() -> None:
    evidence = QlcPlusBackend().spike()

    assert evidence.backend == "qlcplus"
    assert evidence.mode == "dry-run"
    assert evidence.observed == {"status": "not-applied"}
    assert "QLC+API|getFunctionsList" in evidence.commands


def test_qlcplus_execute_records_websocket_responses(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS").spike(
        execute=True,
        function_id=7,
        function_status=1,
        universe=0,
        start_channel=1,
        channel_count=4,
    )

    assert evidence.mode == "apply"
    assert evidence.observed["status"] == "queried"
    assert evidence.observed["evidence_quality"] == "websocket-response"
    assert fake_ws.closed is True
    assert fake_ws.sent[-1] == "QLC+API|setFunctionStatus|7|1"


def test_qlcplus_unavailable_returns_structured_evidence(monkeypatch) -> None:
    def fail_connection(*args, **kwargs):
        raise OSError("connection refused")

    fake_module = types.SimpleNamespace(create_connection=fail_connection)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend().spike(execute=True)

    assert evidence.observed["status"] == "unavailable"
    assert "connection refused" in evidence.observed["error"]
    assert evidence.warnings == ["QLC+ WebSocket endpoint was unavailable."]
