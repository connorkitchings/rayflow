"""DMX backend adapters for rendered cue frames."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from rayflow.rendering import DmxFrame, RenderedCue

EvidenceMode = Literal["dry-run", "apply"]


@dataclass(frozen=True)
class BackendCapabilities:
    """Static capability declaration for a backend adapter."""

    backend: str
    attributes: tuple[str, ...]
    operations: tuple[str, ...]
    evidence_types: tuple[str, ...]
    requires_execute: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "attributes": list(self.attributes),
            "operations": list(self.operations),
            "evidence_types": list(self.evidence_types),
            "requires_execute": self.requires_execute,
        }


@dataclass(frozen=True)
class BackendEvidence:
    """Structured proof for a backend operation."""

    backend: str
    operation: str
    mode: EvidenceMode
    target: str
    frames: list[dict[str, Any]]
    commands: list[str] = field(default_factory=list)
    observed: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds")
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend,
            "operation": self.operation,
            "mode": self.mode,
            "target": self.target,
            "frames": self.frames,
            "commands": list(self.commands),
            "observed": dict(self.observed),
            "warnings": list(self.warnings),
            "timestamp": self.timestamp,
        }


class ArtNetDmxBackend:
    """Art-Net adapter for rendered DMX frames."""

    capabilities = BackendCapabilities(
        backend="artnet",
        attributes=("dimmer", "color"),
        operations=("dry-run", "apply"),
        evidence_types=("frame-plan", "send-call", "receiver-buffer"),
    )

    def __init__(self, target_ip: str = "127.0.0.1"):
        self.target_ip = target_ip

    def dry_run(self, rendered: RenderedCue) -> BackendEvidence:
        return BackendEvidence(
            backend="artnet",
            operation="send-frame",
            mode="dry-run",
            target=f"{self.target_ip}:6454",
            frames=_frames_as_dicts(rendered.frames),
            commands=[
                f"ArtDMX universe {frame.universe} -> {self.target_ip}:6454"
                for frame in rendered.frames
            ],
            warnings=_render_warnings(rendered),
            observed={"status": "not-applied"},
        )

    def apply(
        self,
        rendered: RenderedCue,
        *,
        capture_evidence: bool = False,
        evidence_timeout: float = 0.25,
    ) -> BackendEvidence:
        from rayflow.bridge.artnet import ArtNetReceiver, ArtNetSender

        sent_universes: list[int] = []
        for frame in rendered.frames:
            sender = ArtNetSender(target_ip=self.target_ip, universe=frame.universe)
            sender.set_universe(_expand_frame(frame))
            sent_universes.append(frame.universe)

        warnings = _render_warnings(rendered)
        observed: dict[str, Any] = {
            "status": "sent",
            "universes": sent_universes,
            "evidence_quality": "send-call-only",
        }
        if capture_evidence:
            captures = []
            for frame in rendered.frames:
                receiver = ArtNetReceiver(universe=frame.universe)
                buffer = _read_artnet_buffer(receiver, frame, evidence_timeout)
                captures.append(_artnet_capture(frame, buffer))
            observed["receiver_captures"] = captures
            if captures and all(capture["matches_rendered"] for capture in captures):
                observed["evidence_quality"] = "receiver-buffer"
            else:
                observed["evidence_quality"] = "receiver-buffer-mismatch"
                warnings.append("Art-Net receiver buffer did not match rendered frame.")
        else:
            warnings.append("No receiver or packet-capture proof was captured.")

        return BackendEvidence(
            backend="artnet",
            operation="send-frame",
            mode="apply",
            target=f"{self.target_ip}:6454",
            frames=_frames_as_dicts(rendered.frames),
            commands=[
                f"ArtDMX universe {frame.universe} -> {self.target_ip}:6454"
                for frame in rendered.frames
            ],
            observed=observed,
            warnings=warnings,
        )


class SacnDmxBackend:
    """sACN/E1.31 adapter for rendered DMX frames."""

    capabilities = BackendCapabilities(
        backend="sacn",
        attributes=("dimmer", "color"),
        operations=("dry-run", "apply"),
        evidence_types=("frame-plan", "send-call", "receiver-state"),
    )

    def __init__(
        self,
        *,
        multicast: bool = True,
        universe_offset: int = 1,
        source_name: str = "RayFlow",
    ):
        self.multicast = multicast
        self.universe_offset = universe_offset
        self.source_name = source_name

    def dry_run(self, rendered: RenderedCue) -> BackendEvidence:
        mappings = [
            _sacn_mapping(frame, self.universe_offset) for frame in rendered.frames
        ]
        target = "sACN multicast" if self.multicast else "sACN unicast"
        return BackendEvidence(
            backend="sacn",
            operation="send-frame",
            mode="dry-run",
            target=target,
            frames=_frames_as_dicts(rendered.frames, sacn_offset=self.universe_offset),
            commands=[
                f"sACN RayFlow universe {item['rayflow_universe']} "
                f"-> E1.31 universe {item['sacn_universe']}"
                for item in mappings
            ],
            observed={"status": "not-applied", "universe_mapping": mappings},
            warnings=_render_warnings(rendered),
        )

    def apply(
        self,
        rendered: RenderedCue,
        *,
        capture_evidence: bool = False,
        evidence_timeout: float = 0.25,
    ) -> BackendEvidence:
        from rayflow.bridge.sacn_bridge import SacnReceiver, SacnSender

        mappings = [
            _sacn_mapping(frame, self.universe_offset) for frame in rendered.frames
        ]
        for frame in rendered.frames:
            sacn_universe = frame.universe + self.universe_offset
            sender = SacnSender(
                universe=sacn_universe,
                multicast=self.multicast,
                source_name=self.source_name,
            )
            sender.set_universe(tuple(_expand_frame(frame)))
            sender.flush()
            sender.stop()

        warnings = _render_warnings(rendered)
        observed: dict[str, Any] = {
            "status": "sent",
            "universe_mapping": mappings,
            "evidence_quality": "send-call-only",
        }
        if capture_evidence:
            sacn_universes = [item["sacn_universe"] for item in mappings]
            receiver = (
                SacnReceiver(universe=sacn_universes[0]) if sacn_universes else None
            )
            possible = (
                _read_sacn_universes(receiver, sacn_universes, evidence_timeout)
                if receiver
                else ()
            )
            if receiver and self.multicast:
                receiver.join_multicast()
            if receiver:
                receiver.stop()
            observed["possible_universes"] = list(possible)
            all_universes_seen = all(
                universe in possible for universe in sacn_universes
            )
            if sacn_universes and all_universes_seen:
                observed["evidence_quality"] = "receiver-state"
            else:
                observed["evidence_quality"] = "receiver-state-mismatch"
                warnings.append("sACN receiver did not observe all expected universes.")
        else:
            warnings.append("No receiver or packet-capture proof was captured.")

        target = "sACN multicast" if self.multicast else "sACN unicast"
        return BackendEvidence(
            backend="sacn",
            operation="send-frame",
            mode="apply",
            target=target,
            frames=_frames_as_dicts(rendered.frames, sacn_offset=self.universe_offset),
            commands=[
                f"sACN RayFlow universe {item['rayflow_universe']} "
                f"-> E1.31 universe {item['sacn_universe']}"
                for item in mappings
            ],
            observed=observed,
            warnings=warnings,
        )


def _expand_frame(frame: DmxFrame) -> list[int]:
    data = [0] * 512
    for channel, value in frame.channels.items():
        if not 1 <= channel <= 512:
            raise ValueError(f"DMX channel must be 1-512, got {channel}")
        if not 0 <= value <= 255:
            raise ValueError(f"DMX value must be 0-255, got {value}")
        data[channel - 1] = value
    return data


def _frames_as_dicts(
    frames: list[DmxFrame], *, sacn_offset: int | None = None
) -> list[dict[str, Any]]:
    result = []
    for frame in frames:
        data = frame.as_dict()
        if sacn_offset is not None:
            data["rayflow_universe"] = frame.universe
            data["sacn_universe"] = frame.universe + sacn_offset
        result.append(data)
    return result


def _render_warnings(rendered: RenderedCue) -> list[str]:
    return [
        f"Cue {warning.cue} fixture {warning.fixture}: {warning.message}"
        for warning in rendered.warnings
    ]


def _sacn_mapping(frame: DmxFrame, universe_offset: int) -> dict[str, int]:
    return {
        "rayflow_universe": frame.universe,
        "sacn_universe": frame.universe + universe_offset,
    }


def _artnet_capture(frame: DmxFrame, buffer: list[int]) -> dict[str, Any]:
    observed_values = {
        channel: buffer[channel - 1] if channel - 1 < len(buffer) else None
        for channel in sorted(frame.channels)
    }
    mismatches = {
        channel: {
            "expected": expected,
            "observed": observed_values[channel],
        }
        for channel, expected in sorted(frame.channels.items())
        if observed_values[channel] != expected
    }
    return {
        "universe": frame.universe,
        "observed_values": observed_values,
        "mismatches": mismatches,
        "matches_rendered": not mismatches,
    }


def _read_artnet_buffer(receiver: Any, frame: DmxFrame, timeout: float) -> list[int]:
    deadline = time.monotonic() + max(0.0, timeout)
    latest = receiver.get_buffer()
    while time.monotonic() < deadline:
        if _artnet_capture(frame, latest)["matches_rendered"]:
            break
        time.sleep(0.02)
        latest = receiver.get_buffer()
    return latest


def _read_sacn_universes(
    receiver: Any, expected_universes: list[int], timeout: float
) -> tuple[int, ...]:
    deadline = time.monotonic() + max(0.0, timeout)
    latest = tuple(receiver.get_possible_universes())
    while time.monotonic() < deadline:
        all_universes_seen = all(universe in latest for universe in expected_universes)
        if expected_universes and all_universes_seen:
            break
        time.sleep(0.02)
        latest = tuple(receiver.get_possible_universes())
    return latest
