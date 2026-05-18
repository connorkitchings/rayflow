# -*- coding: utf-8 -*-
"""Rig definition CLI commands."""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rayflow._cli_shared import console, list_yaml_files

rig_app = typer.Typer(help="Rig definition management")


def _rig_dir_path(dir: str) -> Path:
    return Path(dir)


def _rig_path(name: str, directory: Path) -> Path:
    return directory / f"{name}.yaml"


@rig_app.command("create")
def rig_create(
    name: str = typer.Argument(..., help="Rig name"),
    venue: str = typer.Option(..., "--venue", help="Venue name"),
    dimensions: str = typer.Option(
        ..., "--dimensions", help="Venue dimensions W,D,H (meters)"
    ),
    template: bool = typer.Option(
        False, "--template", help="Mark as reusable template"
    ),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
) -> None:
    """Create a new minimal rig definition."""
    from rayflow.shows.models import Rig, Venue
    from rayflow.shows.serializers import save_rig

    try:
        parts = dimensions.split(",")
        if len(parts) != 3:
            raise ValueError("Dimensions must be W,D,H")
        dims = (float(parts[0]), float(parts[1]), float(parts[2]))
        v = Venue(name=venue, dimensions=dims)
        rig = Rig(name=name, venue=v, template=template)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    target = _rig_path(name, _rig_dir_path(rig_dir))
    saved = save_rig(rig, target)
    console.print(f"[green]Rig created:[/green] {saved}")
    console.print(f"  Venue: {venue} ({dimensions}m)")
    if template:
        console.print("  Template: yes")


@rig_app.command("list")
def rig_list(
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
    templates_only: bool = typer.Option(
        False, "--templates-only", help="Show only template rigs"
    ),
) -> None:
    """List all rig definitions."""
    from rayflow.shows.serializers import load_rig

    directory = _rig_dir_path(rig_dir)
    files = list_yaml_files(directory)
    if not files:
        console.print("[dim]No rigs found[/dim]")
        return

    table = Table(title=f"Rigs ({len(files)})")
    table.add_column("Name", style="cyan")
    table.add_column("Venue", style="green")
    table.add_column("Fixtures", justify="right")
    table.add_column("Presets", justify="right")
    table.add_column("Template", justify="center")

    for f in files:
        try:
            rig = load_rig(f)
            if templates_only and not rig.template:
                continue
            table.add_row(
                rig.name,
                rig.venue.name,
                str(len(rig.fixtures)),
                str(len(rig.presets)),
                "yes" if rig.template else "",
            )
        except Exception as e:
            table.add_row(f.name, "[red]error[/red]", "", "", str(e))

    console.print(table)


@rig_app.command("info")
def rig_info(
    name: str = typer.Argument(..., help="Rig name"),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show rig details."""
    from rayflow.shows.serializers import load_rig

    path = _rig_path(name, _rig_dir_path(rig_dir))
    if not path.exists():
        typer.echo(f"Error: Rig not found: {name}", err=True)
        raise typer.Exit(code=1)

    rig = load_rig(path)

    if json_output:
        console.print(json_module.dumps(rig.as_dict(), indent=2))
        return

    console.print(f"[bold]{rig.name}[/bold]")
    if rig.template:
        console.print("[dim]Template[/dim]")
    w, d, h = rig.venue.width, rig.venue.depth, rig.venue.height
    console.print(f"Venue: {rig.venue.name} ({w}x{d}x{h}m)")
    if rig.notes:
        console.print(f"Notes: {rig.notes}")

    if rig.fixtures:
        table = Table(title=f"Fixtures ({len(rig.fixtures)})")
        table.add_column("Label", style="cyan")
        table.add_column("Fixture", style="green")
        table.add_column("Mode")
        table.add_column("Universe", justify="right")
        table.add_column("Address", justify="right")
        for slot in rig.fixtures:
            table.add_row(
                slot.label,
                slot.fixture_name,
                slot.mode,
                str(slot.universe),
                str(slot.start_address),
            )
        console.print(table)
    else:
        console.print("[dim]No fixtures[/dim]")

    if rig.presets:
        table = Table(title=f"Presets ({len(rig.presets)})")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Attributes")
        for pname, preset in rig.presets.items():
            attrs = ", ".join(f"{k}={v}" for k, v in preset.attributes.items())
            table.add_row(pname, preset.description, attrs)
        console.print(table)
    else:
        console.print("[dim]No presets[/dim]")


@rig_app.command("copy")
def rig_copy(
    source: str = typer.Argument(..., help="Source rig name"),
    dest: str = typer.Argument(..., help="Destination rig name"),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
) -> None:
    """Copy a rig to create a variant."""
    from rayflow.shows.serializers import load_rig, save_rig

    src_path = _rig_path(source, _rig_dir_path(rig_dir))
    if not src_path.exists():
        typer.echo(f"Error: Source rig not found: {source}", err=True)
        raise typer.Exit(code=1)

    rig = load_rig(src_path)
    rig.name = dest
    rig.template = False
    dest_path = _rig_path(dest, _rig_dir_path(rig_dir))
    saved = save_rig(rig, dest_path)
    console.print(f"[green]Copied[/green] {source} -> {dest}")
    console.print(f"  Saved to: {saved}")


@rig_app.command("add-fixture")
def rig_add_fixture(
    rig_name: str = typer.Argument(..., help="Rig name"),
    fixture: str = typer.Option(..., "--fixture", help="GDTF fixture name"),
    mode: str = typer.Option(..., "--mode", help="DMX mode name"),
    address: int = typer.Option(..., "--address", "-a", help="DMX start address"),
    label: str = typer.Option(..., "--label", help="Fixture label"),
    position: Optional[str] = typer.Option(
        None, "--position", help='Position JSON: {"x":0,"y":4,"z":0,"pan":0,"tilt":0}'
    ),
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--fixture-dir", help="Fixture directory"
    ),
    no_validate: bool = typer.Option(
        False, "--no-validate", help="Skip GDTF fixture validation"
    ),
) -> None:
    """Add a fixture slot to a rig."""
    import json as _json

    from rayflow.shows.models import FixtureSlot, Position3D
    from rayflow.shows.serializers import load_rig, save_rig

    path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    if not no_validate:
        from rayflow.fixtures.library import FixtureLibrary

        try:
            library = FixtureLibrary(fixture_dir)
            library.load()
            found = library.get(fixture)
            if found is None:
                typer.echo(f"Error: Fixture not found: {fixture}", err=True)
                raise typer.Exit(code=1)
            mode_names = found.mode_names()
            if mode not in mode_names:
                typer.echo(
                    f"Error: Mode '{mode}' not found. Available: {mode_names}",
                    err=True,
                )
                raise typer.Exit(code=1)
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

    pos = Position3D()
    if position:
        try:
            pos_data = _json.loads(position)
            pos = Position3D(
                x=pos_data.get("x", 0),
                y=pos_data.get("y", 0),
                z=pos_data.get("z", 0),
                pan=pos_data.get("pan", 0),
                tilt=pos_data.get("tilt", 0),
            )
        except json_module.JSONDecodeError as e:
            typer.echo(f"Error: Invalid position JSON: {e}", err=True)
            raise typer.Exit(code=1)

    rig = load_rig(path)
    slot = FixtureSlot(
        fixture_name=fixture,
        mode=mode,
        label=label,
        universe=0,
        start_address=address,
        position=pos,
        channels=channels,
    )
    rig.add_fixture(slot)
    save_rig(rig, path)
    console.print(f"[green]Added fixture[/green] {label} to {rig_name}")


@rig_app.command("add-preset")
def rig_add_preset(
    rig_name: str = typer.Argument(..., help="Rig name"),
    name: str = typer.Argument(..., help="Preset name"),
    description: str = typer.Option(..., "--description", help="Preset description"),
    attributes: str = typer.Option(
        ..., "--attributes", help='Attributes JSON: {"dimmer":"80","color":"Warm"}'
    ),
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    tags: Optional[str] = typer.Option(
        None, "--tags", help='Tags JSON: ["warm","wash"]'
    ),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
) -> None:
    """Add a preset to a rig."""
    from rayflow.shows.models import Preset
    from rayflow.shows.serializers import load_rig, save_rig

    path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    try:
        attrs = json_module.loads(attributes)
    except json_module.JSONDecodeError as e:
        typer.echo(f"Error: Invalid attributes JSON: {e}", err=True)
        raise typer.Exit(code=1)

    tag_list: list[str] = []
    if tags:
        try:
            tag_list = json_module.loads(tags)
        except json_module.JSONDecodeError as e:
            typer.echo(f"Error: Invalid tags JSON: {e}", err=True)
            raise typer.Exit(code=1)

    preset = Preset(
        name=name,
        description=description,
        attributes=attrs,
        channels=channels,
        tags=tag_list,
    )

    rig = load_rig(path)
    rig.add_preset(preset)
    save_rig(rig, path)
    console.print(f"[green]Added preset[/green] {name} to {rig_name}")


@rig_app.command("export-mvr")
def rig_export_mvr(
    rig_name: str = typer.Argument(..., help="Rig name"),
    output: Path = typer.Option(..., "--output", "-o", help="Output MVR file path"),
    rig_dir: str = typer.Option("data/rigs", "--dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--fixture-dir", help="Fixture directory"
    ),
) -> None:
    """Export a rig as an MVR file for MA3 import."""
    from rayflow.fixtures.library import FixtureLibrary
    from rayflow.fixtures.mvr_export import (
        FixturePosition,
        build_patch_entry,
    )
    from rayflow.fixtures.mvr_export import (
        export_mvr as _export_mvr,
    )
    from rayflow.shows.serializers import load_rig

    path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    rig = load_rig(path)

    try:
        library = FixtureLibrary(fixture_dir)
        library.load()
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error loading fixtures: {e}", err=True)
        raise typer.Exit(code=1)

    patches = []
    address = 1
    for slot in rig.fixtures:
        parser = library.get(slot.fixture_name)
        if parser is None:
            typer.echo(
                f"Warning: Fixture not found: {slot.fixture_name}, skipping",
                err=True,
            )
            continue

        mode_idx = 0
        mode_names = parser.mode_names()
        if slot.mode in mode_names:
            mode_idx = mode_names.index(slot.mode)

        channel_count = parser.get_channel_count(mode_idx)
        pos = FixturePosition(
            name=slot.label,
            x=slot.position.x,
            y=slot.position.y,
            z=slot.position.z,
            pan=slot.position.pan,
            tilt=slot.position.tilt,
        )
        gdtf_file = getattr(parser, "path", None)
        patches.append(
            build_patch_entry(
                name=slot.label,
                manufacturer=parser.manufacturer,
                fixture_type=f"{parser.manufacturer}@{parser.name}",
                dmx_mode=slot.mode,
                universe=slot.universe,
                address=address,
                position=pos,
                gdtf_file=gdtf_file,
            )
        )
        address += channel_count

    if not patches:
        typer.echo("Error: No valid fixtures to export", err=True)
        raise typer.Exit(code=1)

    saved = _export_mvr(patches, output, scene_name=rig.name)
    console.print(f"[green]MVR exported[/green] to {saved}")
    console.print(f"  Fixtures: {len(patches)}")
    console.print(f"  Scene: {rig.name}")
