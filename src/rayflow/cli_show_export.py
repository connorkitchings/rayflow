# -*- coding: utf-8 -*-
"""Show MA3 push and export CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from rayflow._cli_shared import console
from rayflow.cli_rig import _rig_dir_path, _rig_path


def _show_dir_path(dir: str) -> Path:
    return Path(dir)


def _show_path(name: str, directory: Path) -> Path:
    return directory / f"{name}.yaml"


def register_show_export_commands(show_app: typer.Typer) -> None:
    """Register show MA3 push and export commands."""

    @show_app.command("push-to-ma3")
    def show_push_to_ma3(
        show_name: str = typer.Argument(..., help="Show name"),
        execute: bool = typer.Option(
            False, "--execute", help="Actually send OSC commands to MA3"
        ),
        sequence: int = typer.Option(
            1, "--sequence", help="Target MA3 sequence number"
        ),
        ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
        port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    ) -> None:
        """Push all show cues to grandMA3 onPC via OSC.

        Generates OSC commands from the show's cues and presets.
        By default, runs as a dry-run showing the commands that would be sent.
        Use --execute to actually send them.
        """
        from rayflow.shows.models import resolve_presets
        from rayflow.shows.push import commands_for_show
        from rayflow.shows.serializers import load_rig, load_show

        show_path = _show_path(show_name, _show_dir_path(show_dir))
        if not show_path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(show_path)
        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)
        presets = resolve_presets(rig, show)
        commands = commands_for_show(show, presets, sequence=sequence)

        seq_label = show.song.title
        if not commands:
            console.print(f"[dim]Show {show_name} has no cues to push[/dim]")
            return

        if not execute:
            console.print(
                f"[bold yellow]Dry run[/bold yellow] — {len(commands)} OSC commands "
                f"for {show_name}:"
            )
            console.print(
                f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")'
            )
            for cmd in commands:
                console.print(f"  {cmd.command}")
            console.print(
                f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
            )
            return

        from rayflow.console.osc import Ma3OscClient

        client = Ma3OscClient(ip=ip, port=port)
        for cmd in commands:
            client.send(cmd.command)
        console.print(
            f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
            f"to Sequence {sequence} on {ip}:{port}"
        )

    @show_app.command("push-section")
    def show_push_section(
        show_name: str = typer.Argument(..., help="Show name"),
        section: str = typer.Option(..., "--section", help="Section name to push"),
        execute: bool = typer.Option(
            False, "--execute", help="Actually send OSC commands to MA3"
        ),
        sequence: int = typer.Option(
            1, "--sequence", help="Target MA3 sequence number"
        ),
        ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
        port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    ) -> None:
        """Push cues for a single section to grandMA3 onPC."""
        from rayflow.shows.models import resolve_presets
        from rayflow.shows.push import commands_for_show
        from rayflow.shows.serializers import load_rig, load_show

        show_path = _show_path(show_name, _show_dir_path(show_dir))
        if not show_path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(show_path)
        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)
        presets = resolve_presets(rig, show)
        commands = commands_for_show(show, presets, section=section, sequence=sequence)

        seq_label = show.song.title
        if not commands:
            console.print(
                f"[dim]Show {show_name} has no cues in section '{section}'[/dim]"
            )
            return

        if not execute:
            console.print(
                f"[bold yellow]Dry run[/bold yellow] — {len(commands)} OSC commands "
                f"for section '{section}' in {show_name}:"
            )
            console.print(
                f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")'
            )
            for cmd in commands:
                console.print(f"  {cmd.command}")
            console.print(
                f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
            )
            return

        from rayflow.console.osc import Ma3OscClient

        client = Ma3OscClient(ip=ip, port=port)
        for cmd in commands:
            client.send(cmd.command)
        console.print(
            f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
            f"to Sequence {sequence} on {ip}:{port}"
        )

    @show_app.command("export")
    def show_export(
        show_name: str = typer.Argument(..., help="Show name"),
        output_dir: Path = typer.Option(
            ..., "--output-dir", "-o", help="Output bundle directory"
        ),
        sequence: int = typer.Option(
            1, "--sequence", help="Target MA3 sequence number"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
    ) -> None:
        """Export a dry-run-safe MA3 bundle for a show."""
        from rayflow.shows.export_bundle import export_show_bundle
        from rayflow.shows.serializers import load_rig, load_show

        show_path = _show_path(show_name, _show_dir_path(show_dir))
        if not show_path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(show_path)

        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)

        try:
            bundle = export_show_bundle(
                show,
                rig,
                output_dir=output_dir,
                fixture_dir=fixture_dir,
                sequence=sequence,
            )
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        console.print(f"[green]MA3 show export created[/green] at {bundle.output_dir}")
        console.print(f"  MVR: {bundle.mvr_path}")
        console.print(f"  Commands: {bundle.commands_path}")
        console.print(f"  README: {bundle.readme_path}")
        console.print(f"  Metadata: {bundle.metadata_path}")
        console.print(f"  Sequence: {sequence}")
        console.print(f"  Fixtures: {bundle.fixture_count}")
        console.print(f"  OSC commands: {bundle.command_count}")

    @show_app.command("export-mvr")
    def show_export_mvr(
        show_name: str = typer.Argument(..., help="Show name"),
        output: Path = typer.Option(
            ..., "--output", "-o", help="Output MVR file path"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
    ) -> None:
        """Export a show's rig as an MVR file."""
        from rayflow.fixtures.mvr_export import (
            export_mvr as _export_mvr,
        )
        from rayflow.shows.export_bundle import build_mvr_patches
        from rayflow.shows.serializers import load_rig, load_show

        show_path = _show_path(show_name, _show_dir_path(show_dir))
        if not show_path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(show_path)

        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)

        try:
            patches = build_mvr_patches(rig, fixture_dir)
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error loading fixtures: {e}", err=True)
            raise typer.Exit(code=1)

        if not patches:
            typer.echo("Error: No valid fixtures to export", err=True)
            raise typer.Exit(code=1)

        saved = _export_mvr(patches, output, scene_name=rig.name)
        console.print(f"[green]MVR exported[/green] to {saved}")
        console.print(f"  Fixtures: {len(patches)}")
        console.print(f"  Scene: {rig.name}")
