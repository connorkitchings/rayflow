# -*- coding: utf-8 -*-
"""Show MA3 push and export CLI commands."""

from __future__ import annotations

from pathlib import Path

import typer

from rayflow.cli._paths import show_dir_path, show_path
from rayflow.cli._shared import console, resolve_show_name
from rayflow.cli.rig import _rig_dir_path, _rig_path


def register_show_export_commands(show_app: typer.Typer) -> None:
    """Register show MA3 push and export commands."""

    @show_app.command("push-to-ma3")
    def show_push_to_ma3(
        show_name: str | None = typer.Argument(None, help="Show name"),
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
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
    ) -> None:
        """Push all show cues to grandMA3 onPC via OSC.

        Generates OSC commands from the show's cues and presets.
        By default, runs as a dry-run showing the commands that would be sent.
        Use --execute to actually send them.
        """
        show_name = resolve_show_name(show_name)
        from rayflow.design.models import resolve_presets
        from rayflow.design.serializers import load_rig, load_show
        from rayflow.engine.console.push import commands_for_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)
        presets = resolve_presets(rig, show)
        commands = commands_for_show(
            show,
            presets,
            sequence=sequence,
            rig=rig,
            fixture_dir=fixture_dir,
        )

        seq_label = show.song.title
        if not commands:
            console.print(f"[dim]Show {show_name} has no cues to push[/dim]")
            return

        if not execute:
            console.print(
                f"[bold yellow]Dry run[/bold yellow] — {len(commands)} OSC commands "
                f"for {show_name}:"
            )
            console.print(f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")')
            for cmd in commands:
                console.print(f"  {cmd.command}")
            console.print(
                f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
            )
            return

        from rayflow.engine.console.osc import Ma3OscClient

        client = Ma3OscClient(ip=ip, port=port)
        for cmd in commands:
            client.send(cmd.command)
        console.print(
            f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
            f"to Sequence {sequence} on {ip}:{port}"
        )

    @show_app.command("push-section")
    def show_push_section(
        show_name: str | None = typer.Argument(None, help="Show name"),
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
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
    ) -> None:
        """Push cues for a single section to grandMA3 onPC."""
        show_name = resolve_show_name(show_name)
        from rayflow.design.models import resolve_presets
        from rayflow.design.serializers import load_rig, load_show
        from rayflow.engine.console.push import commands_for_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)
        presets = resolve_presets(rig, show)
        commands = commands_for_show(
            show,
            presets,
            section=section,
            sequence=sequence,
            rig=rig,
            fixture_dir=fixture_dir,
        )

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
            console.print(f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")')
            for cmd in commands:
                console.print(f"  {cmd.command}")
            console.print(
                f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
            )
            return

        from rayflow.engine.console.osc import Ma3OscClient

        client = Ma3OscClient(ip=ip, port=port)
        for cmd in commands:
            client.send(cmd.command)
        console.print(
            f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
            f"to Sequence {sequence} on {ip}:{port}"
        )

    @show_app.command("export")
    def show_export(
        show_name: str | None = typer.Argument(None, help="Show name"),
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
        show_name = resolve_show_name(show_name)
        from rayflow.design.serializers import load_rig, load_show
        from rayflow.engine.console.export_bundle import export_show_bundle

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)

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
        console.print(f"  Timecode: {bundle.timecode_path}")
        console.print(f"  README: {bundle.readme_path}")
        console.print(f"  Metadata: {bundle.metadata_path}")
        console.print(f"  Sequence: {sequence}")
        console.print(f"  Fixtures: {bundle.fixture_count}")
        console.print(f"  OSC commands: {bundle.command_count}")

    @show_app.command("export-mvr")
    def show_export_mvr(
        show_name: str | None = typer.Argument(None, help="Show name"),
        output: Path = typer.Option(..., "--output", "-o", help="Output MVR file path"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
    ) -> None:
        """Export a show's rig as an MVR file."""
        show_name = resolve_show_name(show_name)
        from rayflow.design.serializers import load_rig, load_show
        from rayflow.engine.console.export_bundle import build_mvr_patches
        from rayflow.engine.fixtures.mvr_export import (
            export_mvr as _export_mvr,
        )

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)

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

    @show_app.command("export-qxw")
    def show_export_qxw(
        show_name: str | None = typer.Argument(None, help="Show name"),
        output: Path = typer.Option(..., "--output", "-o", help="Output QXW file path"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
        fixture_dir: str = typer.Option(
            "data/fixtures", "--fixture-dir", help="Fixture directory"
        ),
        author: str = typer.Option(
            "RayFlow", "--author", help="Author name for workspace"
        ),
        qxf_dir: Path | None = typer.Option(
            None,
            "--qxf-dir",
            help="Also export QLC+ fixture definitions for the workspace",
        ),
    ) -> None:
        """Export a QLC+ workspace with fixtures and cue Scene functions."""
        show_name = resolve_show_name(show_name)
        from rayflow.design.serializers import load_rig, load_show
        from rayflow.engine.fixtures.library import FixtureLibrary
        from rayflow.engine.fixtures.qlcplus_export import (
            build_qlc_patch,
            build_qlc_scene_from_rendered_cue,
            copy_qxf_files_for_workspace,
            export_qlcplus_workspace,
        )
        from rayflow.engine.fixtures.qlcplus_qxf import (
            export_qlcplus_fixture_definitions,
        )
        from rayflow.engine.rendering import render_show_to_dmx

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        rig_path = _rig_path(show.rig_name, _rig_dir_path(rig_dir))
        if not rig_path.exists():
            typer.echo(f"Error: Rig not found: {show.rig_name}", err=True)
            raise typer.Exit(code=1)

        rig = load_rig(rig_path)
        library = FixtureLibrary(fixture_dir)
        library.load()

        patches = []
        parsers = []
        for fixture_id, slot in enumerate(rig.fixtures):
            parser = library.get(slot.fixture_name)
            if parser is None:
                typer.echo(
                    f"Warning: Fixture not found: {slot.fixture_name}, skipping",
                    err=True,
                )
                continue
            parsers.append(parser)
            mode_idx = 0
            mode_names = parser.mode_names()
            if slot.mode in mode_names:
                mode_idx = mode_names.index(slot.mode)
            patches.append(
                build_qlc_patch(
                    fixture_id=fixture_id,
                    name=slot.label,
                    manufacturer=parser.manufacturer,
                    model=parser.name,
                    mode=slot.mode,
                    universe=slot.universe,
                    address=slot.start_address,
                    channel_count=parser.get_channel_count(mode_idx),
                )
            )

        if not patches:
            typer.echo("Error: No valid fixtures to export", err=True)
            raise typer.Exit(code=1)

        rendered_show = render_show_to_dmx(show, rig, fixture_dir)
        functions = [
            build_qlc_scene_from_rendered_cue(
                rendered,
                patches,
                function_id=index,
            )
            for index, rendered in enumerate(rendered_show.rendered_cues)
        ]

        qxf_results = []
        qxf_copies = []
        if qxf_dir is not None:
            qxf_results = export_qlcplus_fixture_definitions(parsers, qxf_dir)
            qxf_copies = copy_qxf_files_for_workspace(qxf_results, output)

        saved = export_qlcplus_workspace(
            patches,
            output,
            functions=functions,
            author=author,
        )
        console.print(f"[green]QXW show exported[/green] to {saved}")
        console.print(f"  Show: {show.name}")
        console.print(f"  Rig: {rig.name}")
        console.print(f"  Fixtures: {len(patches)}")
        console.print(f"  Scene functions: {len(functions)}")
        if qxf_dir is not None:
            console.print(f"  QXF definitions: {len(qxf_results)} in {qxf_dir}")
            copied_count = sum(1 for result in qxf_copies if result.copied)
            if copied_count:
                console.print(
                    f"  QXF workspace copies: {copied_count} in {output.parent}"
                )

    @show_app.command("export-timecode")
    def show_export_timecode(
        show_name: str | None = typer.Argument(None, help="Show name"),
        output: Path = typer.Option(
            ..., "--output", "-o", help="Output timecode XML file path"
        ),
        sequence: int = typer.Option(
            1, "--sequence", help="Target MA3 sequence / executor number"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Export a MA3 Timecode XML for the show's cue timestamps.

        Generates a GMA3-format Timecode XML where each cue fires a Goto event
        on the target sequence at the cue's timestamp.  Import into grandMA3 via
        Import -> Timecode Pool.

        WARNING: The event schema is based on captured MA3 2.3.2.0 exports.
        Validate imported event playback before relying on it for a show.
        """
        show_name = resolve_show_name(show_name)
        from rayflow.design.serializers import load_show
        from rayflow.engine.console.timecode_export import export_timecode_xml

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)

        try:
            xml_str = export_timecode_xml(show, sequence=sequence)
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)
        output.parent.mkdir(parents=True, exist_ok=True)
        # MA3 strictly requires a UTF-8 BOM, which utf-8-sig provides
        output.write_text(xml_str, encoding="utf-8-sig")

        cue_count = len(show.cues)
        console.print(f"[green]Timecode XML exported[/green] to {output}")
        console.print(f"  Show: {show_name}")
        console.print(f"  Sequence/Executor: {sequence}")
        console.print(f"  Cue events: {cue_count}")
        console.print("  [yellow]Validate import/playback in MA3 before use[/yellow]")
