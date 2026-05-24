# -*- coding: utf-8 -*-
"""Show definition CLI commands."""

from __future__ import annotations

import json as json_module

import typer
from rich.table import Table

from rayflow._cli_shared import console, list_yaml_files
from rayflow.cli_rig import _rig_dir_path, _rig_path
from rayflow.cli_show_cues import register_show_cue_commands
from rayflow.cli_show_edit import register_show_edit_commands
from rayflow.cli_show_export import register_show_export_commands
from rayflow.cli_show_library import register_show_library_commands
from rayflow.cli_show_paths import show_dir_path, show_path

show_app = typer.Typer(help="Show definition management")


register_show_cue_commands(show_app)
register_show_edit_commands(show_app)
register_show_library_commands(show_app)
register_show_export_commands(show_app)


@show_app.command("create")
def show_create(
    name: str = typer.Argument(..., help="Show name"),
    rig: str = typer.Option(..., "--rig", help="Rig name"),
    title: str = typer.Option(..., "--title", help="Song title"),
    artist: str = typer.Option(..., "--artist", help="Song artist"),
    duration: float = typer.Option(..., "--duration", help="Song duration (seconds)"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Create a new show definition."""
    from rayflow.shows.models import Show, Song
    from rayflow.shows.serializers import save_show

    try:
        song = Song(title=title, artist=artist, duration=duration)
        show = Show(name=name, rig_name=rig, song=song)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    target = show_path(name, show_dir_path(show_dir))
    saved = save_show(show, target)
    console.print(f"[green]Show created:[/green] {saved}")
    console.print(f"  Rig: {rig}")
    console.print(f"  Song: {title} by {artist} ({duration}s)")


@show_app.command("list")
def show_list(
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """List all show definitions."""
    from rayflow.shows.serializers import load_show

    directory = show_dir_path(show_dir)
    files = list_yaml_files(directory)
    if not files:
        console.print("[dim]No shows found[/dim]")
        return

    table = Table(title=f"Shows ({len(files)})")
    table.add_column("Name", style="cyan")
    table.add_column("Rig", style="green")
    table.add_column("Song")
    table.add_column("Cues", justify="right")

    for f in files:
        try:
            show = load_show(f)
            table.add_row(
                show.name,
                show.rig_name,
                f"{show.song.title} by {show.song.artist}",
                str(len(show.cues)),
            )
        except Exception as e:
            table.add_row(f.name, "[red]error[/red]", "", str(e))

    console.print(table)


@show_app.command("info")
def show_info(
    name: str = typer.Argument(..., help="Show name"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Show show details."""
    from rayflow.shows.serializers import load_show

    path = show_path(name, show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {name}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)

    if json_output:
        console.print(json_module.dumps(show.as_dict(), indent=2))
        return

    console.print(f"[bold]{show.name}[/bold]")
    console.print(f"Rig: {show.rig_name}")
    console.print(
        f"Song: {show.song.title} by {show.song.artist} ({show.song.duration}s)"
    )
    if show.song.bpm:
        console.print(f"BPM: {show.song.bpm}")

    if show.vibe:
        console.print(f"\n[bold]Vibe:[/bold] {show.vibe.description}")
        console.print(f"  Palette: {show.vibe.palette.name}")
        console.print(f"  Intensity: {show.vibe.intensity_curve}")
        console.print(f"  Movement: {show.vibe.movement_style}")

    if show.song.sections:
        table = Table(title=f"Sections ({len(show.song.sections)})")
        table.add_column("Name", style="cyan")
        table.add_column("Start", justify="right")
        table.add_column("End", justify="right")
        table.add_column("Energy", justify="right")
        table.add_column("Mood")
        for sec in show.song.sections:
            table.add_row(
                sec.name,
                f"{sec.start:.1f}s",
                f"{sec.end:.1f}s",
                f"{sec.energy:.2f}" if sec.energy is not None else "",
                sec.mood or "",
            )
        console.print(table)

    if show.cues:
        table = Table(title=f"Cues ({len(show.cues)})")
        table.add_column("#", justify="right", style="cyan")
        table.add_column("Label", style="green")
        table.add_column("Section")
        table.add_column("Time", justify="right")
        table.add_column("Fade", justify="right")
        for cue in show.cues:
            table.add_row(
                str(cue.number),
                cue.label,
                cue.section,
                f"{cue.timestamp:.1f}s",
                f"{cue.fade_time:.1f}s" if cue.fade_time else "",
            )
        console.print(table)
    else:
        console.print("\n[dim]No cues[/dim]")

    if show.preset_overrides:
        n = len(show.preset_overrides)
        console.print(f"\n[bold]Preset Overrides ({n}):[/bold]")
        for pname, preset in show.preset_overrides.items():
            attrs = ", ".join(f"{k}={v}" for k, v in preset.attributes.items())
            console.print(f"  {pname}: {attrs}")


@show_app.command("context")
def show_context(
    show_name: str = typer.Argument(..., help="Show name"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
) -> None:
    """Output the full AI context bundle for a show as JSON."""
    from rayflow.shows.context import build_context_bundle
    from rayflow.shows.serializers import load_rig, load_show

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

    bundle = build_context_bundle(show, rig, fixture_dir)
    typer.echo(json_module.dumps(bundle, indent=2))


@show_app.command("render-cue")
def show_render_cue(
    show_name: str = typer.Argument(..., help="Show name"),
    cue_number: int = typer.Argument(..., help="Cue number to render"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Dry-run render one show cue to fixture-aware DMX frames."""
    from rayflow.rendering import render_cue_to_dmx
    from rayflow.shows.serializers import load_rig, load_show

    path = show_path(show_name, show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    rig_path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not rig_path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)
    rig = load_rig(rig_path)
    cue = show.get_cue(cue_number)
    if cue is None:
        typer.echo(f"Error: Cue not found: {cue_number}", err=True)
        raise typer.Exit(code=1)

    rendered = render_cue_to_dmx(show, rig, cue, fixture_dir=fixture_dir)

    if json_output:
        typer.echo(json_module.dumps(rendered.as_dict(), indent=2))
        return

    console.print(f"[bold]Cue {cue.number}: {cue.label}[/bold]")
    for frame in rendered.frames:
        channel_count = len(frame.channels)
        console.print(f"Universe {frame.universe}: {channel_count} channels")
    if rendered.warnings:
        console.print(f"[yellow]Warnings: {len(rendered.warnings)}[/yellow]")


@show_app.command("output-cue")
def show_output_cue(
    show_name: str = typer.Argument(..., help="Show name"),
    cue_number: int = typer.Argument(..., help="Cue number to output"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    backend: str = typer.Option(
        "artnet", "--backend", help="Backend: artnet or sacn"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    target: str = typer.Option("127.0.0.1", "--target", help="Art-Net target IP"),
    multicast: bool = typer.Option(
        True, "--multicast/--no-multicast", help="Use sACN multicast"
    ),
    sacn_universe_offset: int = typer.Option(
        1,
        "--sacn-universe-offset",
        help="Offset from RayFlow universe to E1.31 universe",
    ),
    execute: bool = typer.Option(
        False, "--execute", help="Apply output to the selected backend"
    ),
    capture_evidence: bool = typer.Option(
        False,
        "--capture-evidence",
        help="Attempt receiver-side evidence capture after --execute",
    ),
    evidence_timeout: float = typer.Option(
        0.25,
        "--evidence-timeout",
        help="Seconds to wait for receiver evidence",
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Dry-run or apply one rendered cue through a backend adapter."""
    from rayflow.backends import ArtNetDmxBackend, SacnDmxBackend
    from rayflow.rendering import render_cue_to_dmx
    from rayflow.shows.serializers import load_rig, load_show

    path = show_path(show_name, show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    rig_path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not rig_path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)
    rig = load_rig(rig_path)
    cue = show.get_cue(cue_number)
    if cue is None:
        typer.echo(f"Error: Cue not found: {cue_number}", err=True)
        raise typer.Exit(code=1)

    rendered = render_cue_to_dmx(show, rig, cue, fixture_dir=fixture_dir)
    backend_name = backend.lower()
    if backend_name == "artnet":
        adapter = ArtNetDmxBackend(target_ip=target)
    elif backend_name == "sacn":
        adapter = SacnDmxBackend(
            multicast=multicast,
            universe_offset=sacn_universe_offset,
        )
    else:
        typer.echo(
            f"Error: Unknown backend '{backend}'. Use artnet or sacn.", err=True
        )
        raise typer.Exit(code=2)

    evidence = (
        adapter.apply(
            rendered,
            capture_evidence=capture_evidence,
            evidence_timeout=evidence_timeout,
        )
        if execute
        else adapter.dry_run(rendered)
    )

    if json_output:
        typer.echo(json_module.dumps(evidence.as_dict(), indent=2))
        return

    mode = "apply" if execute else "dry-run"
    console.print(f"[bold]{backend_name} {mode}[/bold] cue {cue.number}: {cue.label}")
    console.print(f"Target: {evidence.target}")
    console.print(f"Frames: {len(evidence.frames)}")
    if evidence.warnings:
        console.print(f"[yellow]Warnings: {len(evidence.warnings)}[/yellow]")


@show_app.command("output-section")
def show_output_section(
    show_name: str = typer.Argument(..., help="Show name"),
    section_name: str = typer.Argument(..., help="Section name to output"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    backend: str = typer.Option(
        "artnet", "--backend", help="Backend: artnet or sacn"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    target: str = typer.Option("127.0.0.1", "--target", help="Art-Net target IP"),
    multicast: bool = typer.Option(
        True, "--multicast/--no-multicast", help="Use sACN multicast"
    ),
    sacn_universe_offset: int = typer.Option(
        1,
        "--sacn-universe-offset",
        help="Offset from RayFlow universe to E1.31 universe",
    ),
    execute: bool = typer.Option(
        False, "--execute", help="Apply output to the selected backend"
    ),
    capture_evidence: bool = typer.Option(
        False,
        "--capture-evidence",
        help="Attempt receiver-side evidence capture after --execute",
    ),
    evidence_timeout: float = typer.Option(
        0.25,
        "--evidence-timeout",
        help="Seconds to wait for receiver evidence",
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Dry-run or apply all rendered cues in one section."""
    from rayflow.backends import ArtNetDmxBackend, SacnDmxBackend
    from rayflow.rendering import render_section_to_dmx
    from rayflow.shows.serializers import load_rig, load_show

    path = show_path(show_name, show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    rig_path = _rig_path(rig_name, _rig_dir_path(rig_dir))
    if not rig_path.exists():
        typer.echo(f"Error: Rig not found: {rig_name}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)
    rig = load_rig(rig_path)
    if not show.cues_for_section(section_name):
        typer.echo(f"Error: Section has no cues: {section_name}", err=True)
        raise typer.Exit(code=1)

    rendered_group = render_section_to_dmx(show, rig, section_name, fixture_dir)
    backend_name = backend.lower()
    if backend_name == "artnet":
        adapter = ArtNetDmxBackend(target_ip=target)
    elif backend_name == "sacn":
        adapter = SacnDmxBackend(
            multicast=multicast,
            universe_offset=sacn_universe_offset,
        )
    else:
        typer.echo(
            f"Error: Unknown backend '{backend}'. Use artnet or sacn.", err=True
        )
        raise typer.Exit(code=2)

    evidence = []
    for rendered in rendered_group.rendered_cues:
        item = (
            adapter.apply(
                rendered,
                capture_evidence=capture_evidence,
                evidence_timeout=evidence_timeout,
            )
            if execute
            else adapter.dry_run(rendered)
        )
        evidence.append(item.as_dict())

    payload = {
        "scope": rendered_group.scope,
        "backend": backend_name,
        "mode": "apply" if execute else "dry-run",
        "cues": evidence,
    }
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]{backend_name} {payload['mode']}[/bold] {section_name}")
    console.print(f"Cues: {len(evidence)}")


@show_app.command("qlc-spike")
def show_qlc_spike(
    endpoint: str = typer.Option(
        "ws://127.0.0.1:9999/qlcplusWS",
        "--endpoint",
        help="QLC+ WebSocket endpoint",
    ),
    universe: int = typer.Option(0, "--universe", help="QLC+ universe to query"),
    start_channel: int = typer.Option(
        1, "--start-channel", help="First channel to query"
    ),
    channel_count: int = typer.Option(
        8, "--channel-count", help="Number of channels to query"
    ),
    function_id: int | None = typer.Option(
        None, "--function-id", help="Function ID for gated status set"
    ),
    function_status: int = typer.Option(
        1, "--function-status", help="Function status for gated status set"
    ),
    timeout: float = typer.Option(1.0, "--timeout", help="WebSocket timeout"),
    execute: bool = typer.Option(
        False, "--execute", help="Connect to QLC+ and run the spike"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Experimental QLC+ WebSocket command/query spike."""
    from rayflow.backends import QlcPlusBackend

    evidence = QlcPlusBackend(endpoint=endpoint).spike(
        execute=execute,
        function_id=function_id,
        function_status=function_status,
        universe=universe,
        start_channel=start_channel,
        channel_count=channel_count,
        timeout=timeout,
    )

    if json_output:
        typer.echo(json_module.dumps(evidence.as_dict(), indent=2))
        return

    console.print(f"[bold]QLC+ {evidence.mode}[/bold] {endpoint}")
    console.print(f"Status: {evidence.observed.get('status', 'unknown')}")
    if evidence.warnings:
        console.print(f"[yellow]Warnings: {len(evidence.warnings)}[/yellow]")
