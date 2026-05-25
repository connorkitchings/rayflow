"""Compare RayFlow fixture patches with manually captured grandMA3 observations."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from rayflow.engine.fixtures.library import FixtureLibrary
from rayflow.engine.fixtures.parser import FixtureSummary, GdtfParser
from rayflow.engine.fixtures.patch import DmxUniverse


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


def generate_observation(
    fixture: GdtfParser,
    *,
    mode_index: int = 0,
    mode_name: str | None = None,
    universe: int = 0,
    start_address: int = 1,
) -> dict[str, Any]:
    """Generate an observation JSON dict from a parsed fixture.

    Represents RayFlow's expected view of the fixture data in grandMA3 format.


    This produces the same shape as a manually captured grandMA3 observation,
    serving as a template for real MA3 capture or as expected-ground-truth data.
    """
    report = build_patch_report(
        fixture,
        mode_index=mode_index,
        mode_name=mode_name,
        universe=universe,
        start_address=start_address,
    )
    observation: dict[str, Any] = {
        "source": "generated-from-rayflow",
        "description": (
            f"RayFlow generated observation for {report.fixture} "
            f"mode {report.mode} at address {report.start_address}. "
            "Replace with real grandMA3 capture when MA3 is running."
        ),
        "manufacturer": report.manufacturer,
        "fixture": report.fixture,
        "mode": report.mode,
        "universe": report.universe,
        "start_address": report.start_address,
        "end_address": report.end_address,
        "channel_count": report.channel_count,
        "required_attributes": report.attributes,
    }
    return observation


def generate_observation_file(
    fixture: GdtfParser,
    output_dir: str | Path,
    *,
    mode_index: int = 0,
    mode_name: str | None = None,
    universe: int = 0,
    start_address: int = 1,
) -> Path:
    """Generate and save an observation JSON file for a fixture."""
    observation = generate_observation(
        fixture,
        mode_index=mode_index,
        mode_name=mode_name,
        universe=universe,
        start_address=start_address,
    )
    safe_name = _observation_filename(
        observation["manufacturer"],
        observation["fixture"],
        observation["mode"],
    )
    output_path = Path(output_dir) / f"{safe_name}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(observation, indent=2) + "\n")
    return output_path


def discover_observation(
    fixture_dir: str | Path,
    fixture_name: str,
    *,
    mode_name: str | None = None,
) -> Path | None:
    """Discover an observation JSON file for a fixture in the observations directory."""
    observations_dir = Path(fixture_dir) / "samples" / "observations"
    if not observations_dir.exists():
        return None

    fixture_slug = _slugify(fixture_name).lower()
    for obs_file in sorted(observations_dir.iterdir()):
        if not obs_file.suffix == ".json":
            continue
        if fixture_slug not in _slugify(obs_file.stem).lower():
            continue
        if mode_name:
            mode_slug = _slugify(mode_name).lower()
            if mode_slug not in _slugify(obs_file.stem).lower():
                continue
        return obs_file
    return None


def compare_all_samples(
    fixture_dir: str | Path,
    *,
    universe: int = 0,
    start_address: int = 1,
) -> list[Ma3ComparisonResult]:
    """Compare all sample fixtures against discovered observation files.

    Loads all fixtures from the samples directory, builds patch reports,
    discovers matching observation files, and returns comparison results.
    """
    results: list[Ma3ComparisonResult] = []
    samples_dir = Path(fixture_dir) / "samples"

    library = FixtureLibrary(samples_dir)
    library.load()

    for key in library.list_fixtures():
        fixture = library.get_exact(*_parse_key(key))
        if fixture is None:
            continue

        for mode_idx in range(fixture.mode_count):
            mode_name = fixture.mode_names()[mode_idx]
            report = build_patch_report(
                fixture,
                mode_index=mode_idx,
                universe=universe,
                start_address=start_address,
            )

            obs_path = discover_observation(
                fixture_dir,
                fixture.name,
                mode_name=mode_name,
            )

            if obs_path is None:
                result = Ma3ComparisonResult(
                    rayflow=report,
                    ma3={},
                    mismatches=["no observation file found"],
                )
            else:
                observation = load_ma3_observation(obs_path)
                result = compare_ma3_observation(report, observation)

            results.append(result)

    return results


def _observation_filename(manufacturer: str, fixture: str, mode: str) -> str:
    return f"{_slugify(manufacturer)}_{_slugify(fixture)}_{_slugify(mode)}"


def _slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "", value.replace(" ", ""))


def _parse_key(key: str) -> tuple[str, str]:
    if "@" in key:
        manufacturer, name = key.split("@", 1)
        return manufacturer, name
    return "", key
