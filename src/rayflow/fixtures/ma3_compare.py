"""Compare RayFlow fixture patches with manually captured grandMA3 observations."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rayflow.fixtures.library import FixtureLibrary
from rayflow.fixtures.parser import FixtureSummary, GdtfParser
from rayflow.fixtures.patch import DmxUniverse


@dataclass(frozen=True)
class RayflowPatchReport:
    """Expected fixture patch data produced by RayFlow."""

    manufacturer: str
    fixture: str
    mode: str
    universe: int
    start_address: int
    end_address: int
    channel_count: int
    attributes: list[str]
    channels: list[dict[str, Any]]

    def as_dict(self) -> dict[str, Any]:
        return {
            "manufacturer": self.manufacturer,
            "fixture": self.fixture,
            "mode": self.mode,
            "universe": self.universe,
            "start_address": self.start_address,
            "end_address": self.end_address,
            "channel_count": self.channel_count,
            "attributes": self.attributes,
            "channels": self.channels,
        }


@dataclass(frozen=True)
class Ma3ComparisonResult:
    """Result of comparing RayFlow data with a grandMA3 observation."""

    rayflow: RayflowPatchReport
    ma3: dict[str, Any]
    mismatches: list[str]

    @property
    def matches(self) -> bool:
        return not self.mismatches

    def as_dict(self) -> dict[str, Any]:
        return {
            "matches": self.matches,
            "mismatches": self.mismatches,
            "rayflow": self.rayflow.as_dict(),
            "ma3": self.ma3,
        }


def build_library_patch_report(
    fixture_name: str,
    *,
    fixture_dir: str | Path = "data/fixtures",
    mode_index: int = 0,
    mode_name: str | None = None,
    universe: int = 0,
    start_address: int = 1,
) -> RayflowPatchReport:
    """Build a RayFlow patch report from a fixture library lookup."""
    library = FixtureLibrary(fixture_dir)
    library.load()
    fixture = library.get(fixture_name)
    if fixture is None:
        raise ValueError(f"Fixture not found: {fixture_name}")
    return build_patch_report(
        fixture,
        mode_index=mode_index,
        mode_name=mode_name,
        universe=universe,
        start_address=start_address,
    )


def build_patch_report(
    fixture: GdtfParser | FixtureSummary,
    *,
    mode_index: int = 0,
    mode_name: str | None = None,
    universe: int = 0,
    start_address: int = 1,
) -> RayflowPatchReport:
    """Build the RayFlow expected patch report for one fixture mode."""
    dmx_universe = DmxUniverse(universe_number=universe)
    patch = dmx_universe.patch_fixture(
        fixture,
        start_address=start_address,
        mode_index=mode_index,
        mode_name=mode_name,
    )
    channels = [entry.as_dict() for entry in patch.channel_entries]
    attributes = sorted(
        {str(channel["attribute"]) for channel in channels if channel.get("attribute")}
    )
    return RayflowPatchReport(
        manufacturer=patch.manufacturer or "",
        fixture=patch.name,
        mode=patch.mode_name or "",
        universe=patch.universe,
        start_address=patch.start_address,
        end_address=patch.end_address,
        channel_count=patch.channel_count,
        attributes=attributes,
        channels=channels,
    )


def load_ma3_observation(path: str | Path) -> dict[str, Any]:
    """Load a manually captured grandMA3 patch observation."""
    return json.loads(Path(path).read_text())


def compare_ma3_observation(
    rayflow: RayflowPatchReport, ma3: dict[str, Any]
) -> Ma3ComparisonResult:
    """Compare a RayFlow patch report with a grandMA3 observation."""
    mismatches: list[str] = []
    for key in (
        "manufacturer",
        "fixture",
        "mode",
        "universe",
        "start_address",
        "end_address",
        "channel_count",
    ):
        expected = getattr(rayflow, key)
        observed = ma3.get(key)
        if observed != expected:
            mismatches.append(f"{key}: RayFlow={expected!r}, MA3={observed!r}")

    expected_attributes = {
        attribute.lstrip("+").lower() for attribute in rayflow.attributes
    }
    for attribute in ma3.get("required_attributes", []):
        normalized = str(attribute).lstrip("+").lower()
        if normalized not in expected_attributes:
            mismatches.append(f"required attribute missing: {attribute}")

    return Ma3ComparisonResult(
        rayflow=rayflow,
        ma3=ma3,
        mismatches=mismatches,
    )
