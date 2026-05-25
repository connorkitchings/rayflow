"""Experimental QLC+ WebSocket adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rayflow.backends.dmx import BackendCapabilities, BackendEvidence


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
    """Experimental QLC+ WebSocket command/query adapter."""

    capabilities = BackendCapabilities(
        backend="qlcplus",
        attributes=("query", "function-status", "channel-values"),
        operations=("dry-run", "query", "apply"),
        evidence_types=("websocket-response", "unavailable"),
    )

    def __init__(self, endpoint: str = "ws://127.0.0.1:9999/qlcplusWS"):
        self.endpoint = endpoint

    def spike(
        self,
        *,
        execute: bool = False,
        function_id: int | None = None,
        function_status: int = 1,
        universe: int = 0,
        start_channel: int = 1,
        channel_count: int = 8,
        timeout: float = 1.0,
    ) -> BackendEvidence:
        commands = [
            "QLC+API|getFunctionsList",
            f"QLC+API|getChannelsValues|{universe}|{start_channel}|{channel_count}",
        ]
        if execute and function_id is not None:
            commands.append(
                f"QLC+API|setFunctionStatus|{function_id}|{function_status}"
            )

        if not execute:
            return BackendEvidence(
                backend="qlcplus",
                operation="query-state",
                mode="dry-run",
                target=self.endpoint,
                frames=[],
                commands=commands,
                observed={"status": "not-applied"},
                warnings=[
                    "QLC+ adapter is experimental until local query proof exists."
                ],
            )

        try:
            results = self._execute_commands(commands, timeout=timeout)
        except Exception as exc:
            return BackendEvidence(
                backend="qlcplus",
                operation="query-state",
                mode="apply",
                target=self.endpoint,
                frames=[],
                commands=commands,
                observed={"status": "unavailable", "error": str(exc)},
                warnings=["QLC+ WebSocket endpoint was unavailable."],
            )

        return BackendEvidence(
            backend="qlcplus",
            operation="query-state",
            mode="apply",
            target=self.endpoint,
            frames=[],
            commands=commands,
            observed={
                "status": "queried",
                "responses": [result.as_dict() for result in results],
                "evidence_quality": "websocket-response",
            },
            warnings=["QLC+ adapter remains experimental pending live workflow proof."],
        )

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
