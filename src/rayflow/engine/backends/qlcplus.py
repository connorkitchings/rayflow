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
        operations=("dry-run", "apply"),
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

        command = f"QLC+API|getChannelsValues|{universe}|{start_address}|{count}"
        ws = create_connection(self.endpoint, timeout=timeout)
        try:
            ws.send(command)
            response = ws.recv()
            if not response or not response.startswith("QLC+API|getChannelsValues|"):
                raise ValueError(f"Unexpected response from QLC+: {response}")
            parts = response.split("|")[2:]
            return [int(val) for val in parts if val.strip().isdigit()]
        finally:
            ws.close()

    def _generate_commands(self, rendered: RenderedCue) -> list[str]:
        commands = []
        for frame in rendered.frames:
            # API: QLC+API|setChannelsValues|<universe>|<ch1>|<val1>...
            parts = [f"QLC+API|setChannelsValues|{frame.universe}"]
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
