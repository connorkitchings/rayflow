"""QLC+ WebSocket backend adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rayflow.engine.backends.dmx import (
    BackendCapabilities,
    BackendEvidence,
    _frames_as_dicts,
    _render_warnings,
)
from rayflow.engine.rendering import RenderedCue


@dataclass(frozen=True)
class QlcPlusCommandResult:
    """Plain-text QLC+ command result."""

    command: str
    response: str | None
    ok: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "response": self.response,
            "ok": self.ok,
        }


class QlcPlusBackend:
    """QLC+ WebSocket command/query adapter."""

    capabilities = BackendCapabilities(
        backend="qlcplus",
        attributes=(
            "dimmer",
            "color",
            "pan",
            "tilt",
            "zoom",
            "focus",
            "shutter",
            "gobo",
        ),
        operations=("dry-run", "apply", "query-functions", "trigger-function"),
        evidence_types=("websocket-response", "unavailable"),
    )

    def __init__(self, endpoint: str = "ws://127.0.0.1:9999/qlcplusWS"):
        self.endpoint = endpoint

    def dry_run(self, rendered: RenderedCue) -> BackendEvidence:
        commands = self._generate_commands(rendered)
        return BackendEvidence(
            backend="qlcplus",
            operation="send-frame",
            mode="dry-run",
            target=self.endpoint,
            frames=_frames_as_dicts(rendered.frames),
            commands=commands,
            observed={"status": "not-applied"},
        )

    def apply(
        self,
        rendered: RenderedCue,
        *,
        capture_evidence: bool = False,
        evidence_timeout: float = 1.0,
    ) -> BackendEvidence:
        commands = self._generate_commands(rendered)
        warnings = _render_warnings(rendered)

        try:
            results = self._execute_commands(commands, timeout=evidence_timeout)
        except Exception as exc:
            return BackendEvidence(
                backend="qlcplus",
                operation="send-frame",
                mode="apply",
                target=self.endpoint,
                frames=_frames_as_dicts(rendered.frames),
                commands=commands,
                observed={"status": "unavailable", "error": str(exc)},
                warnings=["QLC+ WebSocket endpoint was unavailable."],
            )

        responses = [result.as_dict() for result in results]
        observed_matches = True

        if capture_evidence:
            try:
                for frame in rendered.frames:
                    if not frame.channels:
                        continue
                    min_ch = min(frame.channels.keys())
                    max_ch = max(frame.channels.keys())
                    count = max_ch - min_ch + 1
                    queried_vals = self.query_channels(
                        frame.universe, min_ch, count, timeout=evidence_timeout
                    )
                    for ch, expected in frame.channels.items():
                        offset = ch - min_ch
                        if offset < len(queried_vals):
                            actual = queried_vals[offset]
                            if actual != expected:
                                observed_matches = False
                        else:
                            observed_matches = False
                    responses.append(
                        {
                            "universe": frame.universe,
                            "queried_channels": {
                                min_ch + i: val for i, val in enumerate(queried_vals)
                            },
                        }
                    )
            except Exception as exc:
                observed_matches = False
                warnings.append(f"Failed to capture query evidence: {exc}")

        return BackendEvidence(
            backend="qlcplus",
            operation="send-frame",
            mode="apply",
            target=self.endpoint,
            frames=_frames_as_dicts(rendered.frames),
            commands=commands,
            observed={
                "status": "queried" if capture_evidence else "sent",
                "responses": responses,
                "evidence_quality": "websocket-response"
                if capture_evidence
                else "send-call-only",
                "observed_matches": observed_matches if capture_evidence else None,
            },
            warnings=warnings,
        )

    def query_channels(
        self, universe: int, start_address: int, count: int, timeout: float = 1.0
    ) -> list[int]:
        """Query channel values from QLC+ over WebSocket.

        Returns a list of integer values (0-255) for the requested range.
        """
        try:
            from websocket import create_connection
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "websocket-client is not installed. Run: uv sync --extra lighting"
            ) from exc

        qlc_universe = universe + 1
        command = f"QLC+API|getChannelsValues|{qlc_universe}|{start_address}|{count}"
        ws = create_connection(self.endpoint, timeout=timeout)
        try:
            ws.send(command)
            response = ws.recv()
            if not response or not response.startswith("QLC+API|getChannelsValues|"):
                raise ValueError(f"Unexpected response from QLC+: {response}")
            return _parse_channel_values(response)
        finally:
            ws.close()

    def query_functions(self, timeout: float = 1.0) -> BackendEvidence:
        """Query QLC+ functions/scenes over WebSocket."""
        command = "QLC+API|getFunctionsList"
        try:
            result = self._execute_commands([command], timeout=timeout)[0]
            functions = _parse_functions_list(result.response)
        except Exception as exc:
            return BackendEvidence(
                backend="qlcplus",
                operation="query-functions",
                mode="query",
                target=self.endpoint,
                frames=[],
                commands=[command],
                observed={"status": "unavailable", "error": str(exc)},
                warnings=["QLC+ WebSocket endpoint was unavailable."],
            )

        return BackendEvidence(
            backend="qlcplus",
            operation="query-functions",
            mode="query",
            target=self.endpoint,
            frames=[],
            commands=[command],
            observed={
                "status": "queried",
                "responses": [result.as_dict()],
                "functions": functions,
                "function_count": len(functions),
            },
        )

    def query_function_status(
        self, function_id: int, timeout: float = 1.0
    ) -> BackendEvidence:
        """Query one QLC+ function status."""
        command = f"QLC+API|getFunctionStatus|{function_id}"
        try:
            result = self._execute_commands([command], timeout=timeout)[0]
            status = _parse_function_status(result.response)
        except Exception as exc:
            return BackendEvidence(
                backend="qlcplus",
                operation="query-function-status",
                mode="query",
                target=self.endpoint,
                frames=[],
                commands=[command],
                observed={"status": "unavailable", "error": str(exc)},
                warnings=["QLC+ WebSocket endpoint was unavailable."],
            )

        return BackendEvidence(
            backend="qlcplus",
            operation="query-function-status",
            mode="query",
            target=self.endpoint,
            frames=[],
            commands=[command],
            observed={
                "status": "queried",
                "responses": [result.as_dict()],
                "function_id": function_id,
                "active": status,
            },
        )

    def set_function_status(
        self,
        function_id: int,
        active: bool,
        *,
        execute: bool = False,
        timeout: float = 1.0,
    ) -> BackendEvidence:
        """Dry-run or set one QLC+ function/scene status."""
        value = 1 if active else 0
        command = f"QLC+API|setFunctionStatus|{function_id}|{value}"
        if not execute:
            return BackendEvidence(
                backend="qlcplus",
                operation="trigger-function",
                mode="dry-run",
                target=self.endpoint,
                frames=[],
                commands=[command],
                observed={
                    "status": "not-applied",
                    "function_id": function_id,
                    "requested_active": active,
                },
            )

        warnings: list[str] = []
        try:
            result = self._execute_commands([command], timeout=timeout)[0]
            status_evidence = self.query_function_status(function_id, timeout=timeout)
        except Exception as exc:
            return BackendEvidence(
                backend="qlcplus",
                operation="trigger-function",
                mode="apply",
                target=self.endpoint,
                frames=[],
                commands=[command],
                observed={"status": "unavailable", "error": str(exc)},
                warnings=["QLC+ WebSocket endpoint was unavailable."],
            )

        observed_active = status_evidence.observed.get("active")
        if observed_active is not None and observed_active != active:
            warnings.append("QLC+ function status query did not match requested state.")

        return BackendEvidence(
            backend="qlcplus",
            operation="trigger-function",
            mode="apply",
            target=self.endpoint,
            frames=[],
            commands=[command],
            observed={
                "status": "queried",
                "responses": [result.as_dict()],
                "function_id": function_id,
                "requested_active": active,
                "observed_active": observed_active,
                "observed_matches": observed_active == active
                if observed_active is not None
                else None,
            },
            warnings=warnings,
        )

    def _generate_commands(self, rendered: RenderedCue) -> list[str]:
        commands = []
        for frame in rendered.frames:
            # API: QLC+API|setChannelsValues|<universe>|<ch1>|<val1>...
            # QLC+ Web API universes are 1-based; RayFlow universes are 0-based.
            parts = [f"QLC+API|setChannelsValues|{frame.universe + 1}"]
            for channel, value in sorted(frame.channels.items()):
                # QLC+ API is 1-based matching our channels
                parts.append(str(channel))
                parts.append(str(value))
            if len(parts) > 1:
                commands.append("|".join(parts))
        return commands

    def _execute_commands(
        self, commands: list[str], *, timeout: float
    ) -> list[QlcPlusCommandResult]:
        try:
            from websocket import create_connection
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "websocket-client is not installed. Run: uv sync --extra lighting"
            ) from exc

        ws = create_connection(self.endpoint, timeout=timeout)
        try:
            results = []
            for command in commands:
                ws.send(command)
                response = ws.recv()
                results.append(
                    QlcPlusCommandResult(
                        command=command,
                        response=response,
                        ok=response is not None,
                    )
                )
            return results
        finally:
            ws.close()


def _parse_functions_list(response: str | None) -> list[dict[str, Any]]:
    if not response:
        return []
    if response == "QLC+API|getFunctionsList":
        return []
    if not response.startswith("QLC+API|getFunctionsList|"):
        raise ValueError(f"Unexpected response from QLC+: {response}")
    parts = response.split("|")[2:]
    stride = 3 if len(parts) % 3 == 0 else 2
    functions: list[dict[str, Any]] = []
    for index in range(0, len(parts), stride):
        chunk = parts[index : index + stride]
        if len(chunk) < 2:
            continue
        function_id, name = chunk[:2]
        function_type = chunk[2] if len(chunk) > 2 else None
        try:
            parsed_id = int(function_id)
        except ValueError:
            continue
        item = {"id": parsed_id, "name": name}
        if function_type:
            item["type"] = function_type
        functions.append(item)
    return functions


def _parse_channel_values(response: str) -> list[int]:
    parts = response.split("|")[2:]
    if not parts:
        return []
    stride = 4 if len(parts) % 4 == 0 else 3
    values: list[int] = []
    for index in range(0, len(parts), stride):
        chunk = parts[index : index + stride]
        if len(chunk) < 2:
            continue
        try:
            values.append(int(chunk[1]))
        except ValueError:
            values.append(0)
    return values


def _parse_function_status(response: str | None) -> bool | None:
    if not response:
        return None
    if not response.startswith("QLC+API|getFunctionStatus|"):
        raise ValueError(f"Unexpected response from QLC+: {response}")
    parts = response.split("|")
    if len(parts) < 3:
        return None
    status = parts[-1].strip().lower()
    if status in {"1", "true", "on", "running"}:
        return True
    if status in {"0", "false", "off", "stopped"}:
        return False
    return None
