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
        self.functions: dict[int, dict[str, object]] = {
            10: {"name": "Verse Look", "type": "Scene", "active": False},
            11: {"name": "Chorus Chase", "type": "Chaser", "active": True},
        }

    def send(self, command: str) -> None:
        self.sent.append(command)
        if command.startswith("QLC+API|setChannelsValues|"):
            parts = command.split("|")[2:]
            universe = int(parts[0])
            for i in range(1, len(parts), 2):
                ch = int(parts[i])
                val = int(parts[i + 1])
                self.channels[(universe, ch)] = val
        if command.startswith("QLC+API|setFunctionStatus|"):
            parts = command.split("|")
            function_id = int(parts[2])
            active = parts[3] == "1"
            self.functions.setdefault(
                function_id,
                {"name": f"Function {function_id}", "type": "Scene", "active": False},
            )
            self.functions[function_id]["active"] = active

    def recv(self) -> str:
        last = self.sent[-1]
        if last.startswith("QLC+API|getChannelsValues|"):
            parts = last.split("|")[2:]
            universe = int(parts[0])
            start = int(parts[1])
            count = int(parts[2])
            vals = []
            for ch in range(start, start + count):
                vals.extend([str(ch), str(self.channels.get((universe, ch), 0)), ""])
            return "QLC+API|getChannelsValues|" + "|".join(vals)
        if last == "QLC+API|getFunctionsList":
            parts = []
            for function_id, function in self.functions.items():
                parts.extend(
                    [
                        str(function_id),
                        str(function["name"]),
                        str(function["type"]),
                    ]
                )
            return "QLC+API|getFunctionsList|" + "|".join(parts)
        if last.startswith("QLC+API|getFunctionStatus|"):
            function_id = int(last.split("|")[2])
            active = self.functions.get(function_id, {}).get("active", False)
            return f"QLC+API|getFunctionStatus|{1 if active else 0}"
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
    assert "QLC+API|setChannelsValues|2|1|255|2|128" in evidence.commands


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
    assert fake_ws.sent[0] == "QLC+API|setChannelsValues|2|1|255|2|128"
    assert fake_ws.sent[1] == "QLC+API|getChannelsValues|2|1|2"


def test_qlcplus_query_channels_direct(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    # Pre-populate fake channel values
    fake_ws.channels[(2, 10)] = 200
    fake_ws.channels[(2, 11)] = 100

    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    backend = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS")
    vals = backend.query_channels(universe=1, start_address=10, count=2)
    assert vals == [200, 100]
    assert fake_ws.sent[-1] == "QLC+API|getChannelsValues|2|10|2"


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


def test_qlcplus_query_functions(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS").query_functions()

    assert evidence.operation == "query-functions"
    assert evidence.observed["status"] == "queried"
    assert evidence.observed["function_count"] == 2
    assert evidence.observed["functions"][0] == {
        "id": 10,
        "name": "Verse Look",
        "type": "Scene",
    }


def test_qlcplus_query_functions_empty_list(monkeypatch) -> None:
    class EmptyFunctionsWebSocket(FakeWebSocket):
        def recv(self) -> str:
            return "QLC+API|getFunctionsList"

    fake_ws = EmptyFunctionsWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS").query_functions()

    assert evidence.observed["status"] == "queried"
    assert evidence.observed["function_count"] == 0
    assert evidence.observed["functions"] == []


def test_qlcplus_query_functions_pair_response(monkeypatch) -> None:
    class PairFunctionsWebSocket(FakeWebSocket):
        def recv(self) -> str:
            return "QLC+API|getFunctionsList|0|RayFlow Validation Scene"

    fake_ws = PairFunctionsWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(endpoint="ws://example.test/qlcplusWS").query_functions()

    assert evidence.observed["function_count"] == 1
    assert evidence.observed["functions"] == [
        {"id": 0, "name": "RayFlow Validation Scene"}
    ]


def test_qlcplus_query_function_status(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(
        endpoint="ws://example.test/qlcplusWS"
    ).query_function_status(11)

    assert evidence.operation == "query-function-status"
    assert evidence.observed["function_id"] == 11
    assert evidence.observed["active"] is True


def test_qlcplus_set_function_status_dry_run_does_not_connect() -> None:
    evidence = QlcPlusBackend().set_function_status(10, True)

    assert evidence.mode == "dry-run"
    assert evidence.commands == ["QLC+API|setFunctionStatus|10|1"]
    assert evidence.observed["status"] == "not-applied"


def test_qlcplus_set_function_status_execute_queries_state(monkeypatch) -> None:
    fake_ws = FakeWebSocket()
    fake_module = types.SimpleNamespace(create_connection=lambda *a, **k: fake_ws)
    monkeypatch.setitem(sys.modules, "websocket", fake_module)

    evidence = QlcPlusBackend(
        endpoint="ws://example.test/qlcplusWS"
    ).set_function_status(10, True, execute=True)

    assert evidence.mode == "apply"
    assert evidence.observed["function_id"] == 10
    assert evidence.observed["observed_active"] is True
    assert evidence.observed["observed_matches"] is True
    assert "QLC+API|setFunctionStatus|10|1" in fake_ws.sent
    assert "QLC+API|getFunctionStatus|10" in fake_ws.sent
