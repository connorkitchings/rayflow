"""Safety helpers for grandMA3 live control probes."""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from rayflow.fixtures.mvr_export import FixturePosition, build_patch_entry, export_mvr

REQUIRED_TARGET_SHOW = "rayflow_control_probe"
MA3_VERSION = "2.3.2.0"
DEFAULT_SHOWS_DIR = Path.home() / "MALightingTechnology/gma3_2.3.2/shared/shows"
DEFAULT_RESEARCH_DIR = Path("docs/research")
DEFAULT_PROBE_MVR = Path("data/ma3_exports/probes/rayflow_control_probe.mvr")


@dataclass(frozen=True)
class ExpectedExport:
    """One expected file produced by an MA3 export command."""

    label: str
    path: Path
    required_substrings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProbePlan:
    """Serializable MA3 probe plan."""

    name: str
    target_show: str
    commands: list[str]
    expected_exports: list[ExpectedExport] = field(default_factory=list)
    notes: str = ""


@dataclass(frozen=True)
class CommandLog:
    """A command sent or previewed during a probe."""

    command: str
    sent: bool
    timestamp: float


@dataclass(frozen=True)
class ExportCheck:
    """Observed state for one expected export file."""

    label: str
    path: Path
    exists: bool
    missing_substrings: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.exists and not self.missing_substrings


@dataclass(frozen=True)
class ProbeResult:
    """Result of running or dry-running a probe plan."""

    name: str
    target_show: str
    ma3_version: str
    osc_endpoint: str
    executed: bool
    passed: bool
    commands: list[CommandLog]
    exports: list[ExportCheck]
    pre_show_mtimes: dict[str, float]
    post_show_mtimes: dict[str, float]
    status: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "target_show": self.target_show,
            "ma3_version": self.ma3_version,
            "osc_endpoint": self.osc_endpoint,
            "executed": self.executed,
            "passed": self.passed,
            "status": self.status,
            "commands": [
                {"command": c.command, "sent": c.sent, "timestamp": c.timestamp}
                for c in self.commands
            ],
            "exports": [
                {
                    "label": e.label,
                    "path": str(e.path),
                    "exists": e.exists,
                    "missing_substrings": list(e.missing_substrings),
                    "passed": e.passed,
                }
                for e in self.exports
            ],
            "pre_show_mtimes": dict(self.pre_show_mtimes),
            "post_show_mtimes": dict(self.post_show_mtimes),
        }


def load_probe_plan(path: str | Path) -> ProbePlan:
    """Load a probe plan JSON file."""
    payload = json.loads(Path(path).read_text())
    expected = [
        ExpectedExport(
            label=str(item["label"]),
            path=Path(item["path"]).expanduser(),
            required_substrings=[
                str(value) for value in item.get("required_substrings", [])
            ],
        )
        for item in payload.get("expected_exports", [])
    ]
    return ProbePlan(
        name=str(payload["name"]),
        target_show=str(payload["target_show"]),
        commands=[str(command) for command in payload.get("commands", [])],
        expected_exports=expected,
        notes=str(payload.get("notes", "")),
    )


def validate_target_show(target_show: str) -> None:
    """Reject mutating probes unless the disposable target show is explicit."""
    if target_show != REQUIRED_TARGET_SHOW:
        raise ValueError(
            f"target_show must be {REQUIRED_TARGET_SHOW!r} for live MA3 probes"
        )


def snapshot_show_mtimes(shows_dir: str | Path = DEFAULT_SHOWS_DIR) -> dict[str, float]:
    """Return mtimes for MA3 show files in a directory."""
    root = Path(shows_dir).expanduser()
    if not root.exists():
        return {}
    return {path.name: path.stat().st_mtime for path in sorted(root.glob("*.show"))}


def changed_show_files(
    before: dict[str, float], after: dict[str, float]
) -> dict[str, tuple[float | None, float]]:
    """Return added or modified show files."""
    changed: dict[str, tuple[float | None, float]] = {}
    for name, mtime in after.items():
        previous = before.get(name)
        if previous is None or mtime > previous:
            changed[name] = (previous, mtime)
    return changed


def show_isolation_passed(
    *,
    target_show: str,
    before: dict[str, float],
    after: dict[str, float],
) -> bool:
    """True when the target show was created/updated and no other show changed."""
    changed = changed_show_files(before, after)
    target_name = f"{target_show}.show"
    return bool(changed) and set(changed) == {target_name}


def check_osc_udp_listener(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Best-effort local UDP port availability check.

    UDP does not expose connection state, so this only proves another process has
    bound the port on this host.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
    except OSError:
        return True
    finally:
        sock.close()
    return False


def check_expected_exports(expected: list[ExpectedExport]) -> list[ExportCheck]:
    """Validate expected export files and required content markers."""
    checks: list[ExportCheck] = []
    for item in expected:
        path = item.path.expanduser()
        if not path.exists():
            checks.append(ExportCheck(label=item.label, path=path, exists=False))
            continue
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        missing = [marker for marker in item.required_substrings if marker not in text]
        checks.append(
            ExportCheck(
                label=item.label,
                path=path,
                exists=True,
                missing_substrings=missing,
            )
        )
    return checks


def run_probe_plan(
    plan: ProbePlan,
    *,
    ip: str = "127.0.0.1",
    port: int = 8000,
    execute: bool = False,
    delay: float = 0.25,
    shows_dir: str | Path = DEFAULT_SHOWS_DIR,
    client: Any | None = None,
) -> ProbeResult:
    """Run or dry-run a probe plan."""
    if execute:
        validate_target_show(plan.target_show)
    pre = snapshot_show_mtimes(shows_dir)
    command_logs: list[CommandLog] = []
    if execute and client is None:
        from rayflow.console.osc import Ma3OscClient

        client = Ma3OscClient(ip=ip, port=port)

    for command in plan.commands:
        if execute:
            client.send(command)
        command_logs.append(
            CommandLog(command=command, sent=execute, timestamp=time.time())
        )
        if execute and delay > 0:
            time.sleep(delay)

    post = snapshot_show_mtimes(shows_dir)
    exports = check_expected_exports(plan.expected_exports)
    passed = all(item.passed for item in exports)
    if execute and plan.name == "show-isolation":
        passed = passed and show_isolation_passed(
            target_show=plan.target_show, before=pre, after=post
        )
    status = "passed" if passed else "failed"
    if not execute:
        status = "dry-run"
    return ProbeResult(
        name=plan.name,
        target_show=plan.target_show,
        ma3_version=MA3_VERSION,
        osc_endpoint=f"{ip}:{port}",
        executed=execute,
        passed=passed if execute else False,
        commands=command_logs,
        exports=exports,
        pre_show_mtimes=pre,
        post_show_mtimes=post,
        status=status,
    )


def show_isolation_plan(target_show: str = REQUIRED_TARGET_SHOW) -> ProbePlan:
    """Build the standard disposable show isolation plan."""
    return ProbePlan(
        name="show-isolation",
        target_show=target_show,
        commands=[
            f'NewShow "{target_show}"',
            "SaveShow",
        ],
        notes="Pass only when the target .show file is the only changed show file.",
    )


def build_fixture_probe_mvr(output: str | Path = DEFAULT_PROBE_MVR) -> Path:
    """Build the dedicated sample-fixture MVR for MA3 import probes."""
    root = Path("data/fixtures/samples")
    patches = [
        build_patch_entry(
            name="Probe LED PAR 1",
            manufacturer="BlenderDMX",
            fixture_type="LED PAR 64 RGBW",
            dmx_mode="Default",
            universe=0,
            address=1,
            position=FixturePosition(name="Probe LED PAR 1", x=-2, y=3, z=0),
            gdtf_file=root / "BlenderDMX_LED_PAR_64_RGBW.gdtf",
        ),
        build_patch_entry(
            name="Probe MMX Blade 1",
            manufacturer="Robe Lighting",
            fixture_type="Robin MMX Blade",
            dmx_mode="Mode 1 - Standard",
            universe=0,
            address=20,
            position=FixturePosition(
                name="Probe MMX Blade 1", x=2, y=3, z=2.5, tilt=45
            ),
            gdtf_file=root / "Robe_Robin_MMX_Blade.gdtf",
        ),
    ]
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return export_mvr(patches, output_path, scene_name="RayFlow Control Probe")


def write_result_json(result: ProbeResult, output: str | Path) -> Path:
    """Write a probe result JSON artifact."""
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.as_dict(), indent=2) + "\n")
    return path


def write_research_note_template(
    path: str | Path = DEFAULT_RESEARCH_DIR
    / "ma3_disposable_show_and_fixture_probe_2_3_2.md",
) -> Path:
    """Write the research note template for the safe probe slice."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        """# MA3 Disposable Show And Fixture Probe

**Date:** TBD
**grandMA3 onPC version:** 2.3.2.0
**Target show:** `rayflow_control_probe`

## Commands

TBD

## Filesystem Evidence

TBD

## Fixture Import / Patch Evidence

TBD

## Capability Updates

TBD
"""
    )
    return target
