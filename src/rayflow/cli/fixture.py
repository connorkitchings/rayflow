# -*- coding: utf-8 -*-
"""GDTF fixture CLI commands."""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rayflow.cli._shared import console

fixture_app = typer.Typer(help="GDTF fixture management")


@fixture_app.command("list")
def list_fixtures(
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
) -> None:
    """List loaded GDTF fixtures."""
    from rayflow.engine.fixtures.library import FixtureLibrary

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    table = Table(title=f"GDTF Fixtures ({library.count})")
    table.add_column("Manufacturer", style="cyan")
    table.add_column("Fixture", style="green")
    table.add_column("Modes", justify="right")
    table.add_column("Channels", justify="right")

    for summary in library.summaries():
        channel_counts = ", ".join(str(mode.channel_count) for mode in summary.modes)
        table.add_row(
            summary.manufacturer,
            summary.name,
            str(summary.mode_count),
            channel_counts,
        )

    console.print(table)


@fixture_app.command("info")
def fixture_info(
    name: str = typer.Argument(..., help="Fixture name to look up"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
) -> None:
    """Show details about a GDTF fixture."""
    from rayflow.engine.fixtures.library import FixtureLibrary

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    parser = library.get(name)
    if parser is None:
        typer.echo(f"Error: Fixture not found: {name}", err=True)
        raise typer.Exit(code=1)

    summary = parser.get_summary()
    console.print(f"[bold]{summary.manufacturer} — {summary.name}[/bold]")

    table = Table(title="DMX Modes")
    table.add_column("Mode", style="cyan")
    table.add_column("Channels", justify="right")
    table.add_column("Attributes", style="green")

    for mode in summary.modes:
        attributes = ", ".join(
            str(channel["attribute"])
            for channel in mode.channels
            if channel.get("attribute")
        )
        table.add_row(mode.name, str(mode.channel_count), attributes)

    console.print(table)


@fixture_app.command("patch")
def patch_fixture(
    fixture_name: str = typer.Argument(..., help="Fixture name to patch"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
    mode: Optional[str] = typer.Option(None, "--mode", help="DMX mode name"),
    mode_index: int = typer.Option(0, "--mode-index", help="DMX mode index"),
    universe: int = typer.Option(0, "--universe", "-u", help="DMX universe number"),
    address: int = typer.Option(1, "--address", "-a", help="DMX start address"),
    patch_name: Optional[str] = typer.Option(
        None, "--name", help="Optional patched fixture name"
    ),
) -> None:
    """Preview patching a GDTF fixture into a DMX universe."""
    from rayflow.engine.fixtures.library import FixtureLibrary
    from rayflow.engine.fixtures.patch import DmxUniverse

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
        parser = library.get(fixture_name)
        if parser is None:
            typer.echo(f"Error: Fixture not found: {fixture_name}", err=True)
            raise typer.Exit(code=1)

        dmx_universe = DmxUniverse(universe_number=universe)
        patch = dmx_universe.patch_fixture(
            parser,
            start_address=address,
            mode_index=mode_index,
            mode_name=mode,
            name=patch_name,
        )
    except (FileNotFoundError, ValueError, IndexError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    console.print(
        f"[bold]{patch.manufacturer or ''} — {patch.name}[/bold]\n"
        f"Mode: {patch.mode_name or ''} | Universe: {patch.universe} | "
        f"Address: {patch.start_address}-{patch.end_address} | "
        f"Channels: {patch.channel_count}"
    )

    table = Table(title="Channel Map")
    table.add_column("DMX", justify="right", style="cyan")
    table.add_column("Rel", justify="right")
    table.add_column("Attribute", style="green")
    table.add_column("Family")
    table.add_column("Geometry")
    table.add_column("Res", justify="right")

    for entry in patch.channel_entries:
        table.add_row(
            str(entry.dmx_address),
            str(entry.relative_channel),
            entry.attribute,
            entry.family,
            entry.geometry or "",
            str(entry.resolution),
        )

    console.print(table)


@fixture_app.command("compare-ma3")
def compare_fixture_ma3(
    fixture_name: str = typer.Argument(..., help="Fixture name to compare"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
    mode: Optional[str] = typer.Option(None, "--mode", help="DMX mode name"),
    mode_index: int = typer.Option(0, "--mode-index", help="DMX mode index"),
    universe: int = typer.Option(0, "--universe", "-u", help="DMX universe number"),
    address: int = typer.Option(1, "--address", "-a", help="DMX start address"),
    ma3_json: Optional[Path] = typer.Option(
        None, "--ma3-json", help="Manually captured MA3 observation JSON"
    ),
    capture: Optional[Path] = typer.Option(
        None,
        "--capture",
        help="Generate and save observation JSON to the given directory",
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Print machine-readable JSON output"
    ),
) -> None:
    """Build or compare a RayFlow patch report for grandMA3 validation."""
    from rayflow.engine.fixtures.library import FixtureLibrary
    from rayflow.engine.fixtures.ma3_compare import (
        build_library_patch_report,
        compare_ma3_observation,
        discover_observation,
        generate_observation_file,
        load_ma3_observation,
    )

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
        parser = library.get(fixture_name)
        if parser is None:
            typer.echo(f"Error: Fixture not found: {fixture_name}", err=True)
            raise typer.Exit(code=1)

        report = build_library_patch_report(
            fixture_name,
            fixture_dir=fixture_dir,
            mode_index=mode_index,
            mode_name=mode,
            universe=universe,
            start_address=address,
        )
        comparison = None

        if capture is not None:
            saved = generate_observation_file(
                parser,
                capture,
                mode_index=mode_index,
                mode_name=mode,
                universe=universe,
                start_address=address,
            )
            console.print(f"[green]Observation saved to {saved}[/green]")
        elif ma3_json is not None:
            observation = load_ma3_observation(ma3_json)
            comparison = compare_ma3_observation(report, observation)
        else:
            obs_path = discover_observation(
                fixture_dir,
                parser.name,
                mode_name=report.mode,
            )
            if obs_path is not None:
                observation = load_ma3_observation(obs_path)
                comparison = compare_ma3_observation(report, observation)
    except (
        FileNotFoundError,
        ValueError,
        IndexError,
        json_module.JSONDecodeError,
    ) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if json_output:
        payload = comparison.as_dict() if comparison else report.as_dict()
        console.print(json_module.dumps(payload, indent=2))
    else:
        _print_patch_report(report)
        if comparison is not None:
            if comparison.matches:
                console.print("[bold green]MA3 comparison matched[/bold green]")
            else:
                console.print("[bold red]MA3 comparison mismatched[/bold red]")
                for mismatch in comparison.mismatches:
                    console.print(f"- {mismatch}")

    if comparison is not None and not comparison.matches:
        raise typer.Exit(code=1)


@fixture_app.command("compare-all")
def compare_all_fixtures(
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
    universe: int = typer.Option(0, "--universe", "-u", help="DMX universe number"),
    address: int = typer.Option(1, "--address", "-a", help="DMX start address"),
    json_output: bool = typer.Option(
        False, "--json", help="Print machine-readable JSON output"
    ),
) -> None:
    """Compare all sample fixtures against grandMA3 observation files."""
    from rayflow.engine.fixtures.ma3_compare import compare_all_samples

    try:
        results = compare_all_samples(
            fixture_dir,
            universe=universe,
            start_address=address,
        )
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if json_output:
        console.print(json_module.dumps([r.as_dict() for r in results], indent=2))
    else:
        _print_compare_all_results(results)

    if any(not r.matches for r in results):
        raise typer.Exit(code=1)


def _print_compare_all_results(
    results: list,
) -> None:
    table = Table(title="Sample Fixture Comparison Results")
    table.add_column("Fixture", style="cyan")
    table.add_column("Mode")
    table.add_column("Channels", justify="right")
    table.add_column("Observation", style="green")
    table.add_column("Result", style="bold")

    for result in results:
        obs_status = "found" if result.ma3 else "missing"
        result_text = "[green]PASS[/green]" if result.matches else "[red]FAIL[/red]"
        table.add_row(
            result.rayflow.fixture,
            result.rayflow.mode,
            str(result.rayflow.channel_count),
            obs_status,
            result_text,
        )

    console.print(table)

    failed = [r for r in results if not r.matches]
    if failed:
        console.print("\n[bold red]Mismatches:[/bold red]")
        for result in failed:
            console.print(
                f"[bold]{result.rayflow.fixture} — {result.rayflow.mode}[/bold]"
            )
            for mismatch in result.mismatches:
                console.print(f"  - {mismatch}")


def _print_patch_report(report) -> None:
    console.print(
        f"[bold]{report.manufacturer} — {report.fixture}[/bold]\n"
        f"Mode: {report.mode} | Universe: {report.universe} | "
        f"Address: {report.start_address}-{report.end_address} | "
        f"Channels: {report.channel_count}"
    )

    table = Table(title="RayFlow Expected Attributes")
    table.add_column("Attribute", style="green")
    for attribute in report.attributes:
        table.add_row(attribute)
    console.print(table)


@fixture_app.command("export-mvr")
def export_mvr(
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
    output: Path = typer.Option(
        ..., "--output", "-o", help="Output MVR file path (.mvr)"
    ),
    scene_name: str = typer.Option(
        "RayFlow Rig", "--scene", help="Scene name in MVR file"
    ),
    universe: int = typer.Option(0, "--universe", "-u", help="DMX universe number"),
    positions_json: Optional[Path] = typer.Option(
        None, "--positions", help="JSON file with fixture positions"
    ),
) -> None:
    """Export patched fixtures from the library as an MVR file.

    Patches all fixtures loaded from the fixture directory into a single
    MVR file that can be imported into grandMA3 onPC.

    Optional --positions JSON format:
    [{"name": "Fixture Name", "x": 0, "y": 2, "z": 0, "pan": 0, "tilt": 0}]
    """
    from rayflow.engine.fixtures.library import FixtureLibrary
    from rayflow.engine.fixtures.mvr_export import (
        FixturePosition,
        build_patch_entry,
    )
    from rayflow.engine.fixtures.mvr_export import (
        export_mvr as _export_mvr,
    )

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    positions: dict[str, FixturePosition] = {}
    if positions_json is not None:
        raw = json_module.loads(positions_json.read_text())
        for entry in raw:
            pos = FixturePosition(
                name=entry["name"],
                x=entry.get("x", 0),
                y=entry.get("y", 0),
                z=entry.get("z", 0),
                pan=entry.get("pan", 0),
                tilt=entry.get("tilt", 0),
            )
            positions[pos.name] = pos

    patches = []
    address = 1
    for key in library.list_fixtures():
        parser = library.get_exact(*_parse_fixture_key(key))
        if parser is None:
            continue
        gdtf_file = getattr(parser, "path", None)
        for mode_idx in range(parser.mode_count):
            mode_name = parser.mode_names()[mode_idx]
            channel_count = parser.get_channel_count(mode_idx)
            pos = positions.get(parser.name, FixturePosition(name=parser.name))
            patches.append(
                build_patch_entry(
                    name=parser.name,
                    manufacturer=parser.manufacturer,
                    fixture_type=f"{parser.manufacturer}@{parser.name}",
                    dmx_mode=mode_name,
                    universe=universe,
                    address=address,
                    position=pos,
                    gdtf_file=gdtf_file,
                )
            )
            address += channel_count
            if address > 512:
                typer.echo(
                    "Warning: fixture patch exceeds 512 channels in universe", err=True
                )
                break

    if not patches:
        typer.echo("Error: No fixtures found to export", err=True)
        raise typer.Exit(code=1)

    saved = _export_mvr(patches, output, scene_name=scene_name)

    console.print(f"[green]MVR file exported to {saved}[/green]")
    console.print(f"  Fixtures: {len(patches)}")
    console.print(f"  Scene: {scene_name}")
    console.print(f"  Universe: {universe}")
    console.print(f"  Address range: 1-{address - 1}")


def _parse_fixture_key(key: str) -> tuple[str, str]:
    if "@" in key:
        manufacturer, name = key.split("@", 1)
        return manufacturer, name
    return "", key
