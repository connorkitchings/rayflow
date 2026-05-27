# -*- coding: utf-8 -*-
"""Show definition CLI commands."""

from __future__ import annotations

import json as json_module
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import typer
from rich.table import Table

from rayflow.cli._paths import show_dir_path, show_path
from rayflow.cli._shared import console, list_yaml_files, resolve_show_name
from rayflow.cli.rig import _rig_dir_path, _rig_path
from rayflow.cli.show.cues import register_show_cue_commands
from rayflow.cli.show.edit import register_show_edit_commands
from rayflow.cli.show.export import register_show_export_commands
from rayflow.cli.show.library import register_show_library_commands

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
    from rayflow.design.models import Show, Song
    from rayflow.design.serializers import save_show

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
    from rayflow.design.serializers import load_show

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
    from rayflow.design.serializers import load_show

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
    show_name: str | None = typer.Argument(None, help="Show name"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
) -> None:
    """Output the full AI context bundle for a show as JSON."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.context import build_context_bundle
    from rayflow.design.serializers import load_rig, load_show

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


@show_app.command("switch")
def switch_show(
    show_name: str = typer.Argument(..., help="Show name"),
) -> None:
    """Set the active workspace show."""
    from rayflow.config import config

    dir_path = show_dir_path(config.show_dir)
    target = show_path(show_name, dir_path)
    if not target.exists():
        console.print(f"[red]Show '{show_name}' does not exist.[/red]")
        raise typer.Exit(1)

    config.workspace.active_show = show_name
    config.workspace.save()
    console.print(f"[green]Switched active show to '{show_name}'.[/green]")


@show_app.command("render-cue")
def show_render_cue(
    show_name: str | None = typer.Argument(None, help="Show name"),
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
    show_name = resolve_show_name(show_name)
    from rayflow.design.serializers import load_rig, load_show
    from rayflow.engine.rendering import render_cue_to_dmx

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
    show_name: str | None = typer.Argument(None, help="Show name"),
    cue_number: int = typer.Argument(..., help="Cue number to output"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    backend: str = typer.Option("artnet", "--backend", help="Backend: artnet or sacn"),
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
    show_name = resolve_show_name(show_name)
    from rayflow.design.serializers import load_rig, load_show
    from rayflow.engine.backends import ArtNetDmxBackend, SacnDmxBackend
    from rayflow.engine.rendering import render_cue_to_dmx

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
        typer.echo(f"Error: Unknown backend '{backend}'. Use artnet or sacn.", err=True)
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
    show_name: str | None = typer.Argument(None, help="Show name"),
    section_name: str = typer.Argument(..., help="Section name to output"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    backend: str = typer.Option("artnet", "--backend", help="Backend: artnet or sacn"),
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
    show_name = resolve_show_name(show_name)
    from rayflow.design.serializers import load_rig, load_show
    from rayflow.engine.backends import ArtNetDmxBackend, SacnDmxBackend
    from rayflow.engine.rendering import render_section_to_dmx

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
        typer.echo(f"Error: Unknown backend '{backend}'. Use artnet or sacn.", err=True)
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


@show_app.command("qlc-function")
def show_qlc_function(
    function_id: int | None = typer.Argument(
        None, help="QLC+ function ID for status or trigger actions"
    ),
    action: str = typer.Option(
        "list", "--action", help="Action: list, status, start, or stop"
    ),
    endpoint: str = typer.Option(
        "ws://127.0.0.1:9999/qlcplusWS", "--endpoint", help="QLC+ WebSocket endpoint"
    ),
    execute: bool = typer.Option(
        False, "--execute", help="Apply start/stop actions to QLC+"
    ),
    timeout: float = typer.Option(1.0, "--timeout", help="WebSocket timeout seconds"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """List, query, or trigger QLC+ functions/scenes over WebSocket."""
    from rayflow.engine.backends import QlcPlusBackend

    adapter = QlcPlusBackend(endpoint=endpoint)
    action_name = action.lower()
    if action_name == "list":
        evidence = adapter.query_functions(timeout=timeout)
    elif action_name == "status":
        if function_id is None:
            typer.echo("Error: function_id is required for status", err=True)
            raise typer.Exit(code=2)
        evidence = adapter.query_function_status(function_id, timeout=timeout)
    elif action_name in {"start", "stop"}:
        if function_id is None:
            typer.echo(f"Error: function_id is required for {action_name}", err=True)
            raise typer.Exit(code=2)
        evidence = adapter.set_function_status(
            function_id,
            active=action_name == "start",
            execute=execute,
            timeout=timeout,
        )
    else:
        typer.echo(
            f"Error: Unknown QLC+ function action '{action}'. "
            "Use list, status, start, or stop.",
            err=True,
        )
        raise typer.Exit(code=2)

    payload = evidence.as_dict()
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]qlcplus {evidence.operation}[/bold] {evidence.mode}")
    console.print(f"Target: {evidence.target}")
    console.print(f"Status: {evidence.observed.get('status')}")
    if evidence.warnings:
        console.print(f"[yellow]Warnings: {len(evidence.warnings)}[/yellow]")


@show_app.command("plan-practice-cues")
def show_plan_practice_cues(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    section: str = typer.Option(
        "all", "--section", help="Section name to plan, or all"
    ),
    style: str = typer.Option(
        "energy-arc",
        "--style",
        help="Practice style: energy-arc, warm-cool, or front-back",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write proposed practice cues to the show YAML"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Plan or apply deterministic renderer-safe practice cues."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.practice_authoring import plan_practice_cues
    from rayflow.design.serializers import load_rig, load_show, save_show

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
    try:
        plan = plan_practice_cues(
            show,
            rig,
            section_name=section,
            style=style,
            apply=apply,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if apply:
        save_show(show, path)

    payload = plan.as_dict()
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]Practice cue {payload['mode']}[/bold] {show.name}")
    console.print(f"Style: {plan.style}")
    console.print(f"Section: {plan.section}")
    console.print(f"Cues: {len(plan.proposed_cues)}")
    console.print(f"Next: {plan.next_command}")


@show_app.command("plan-cues")
def show_plan_cues(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    section: str = typer.Option(
        "all", "--section", help="Section name to plan, or all"
    ),
    style: str = typer.Option(
        "energy-arc",
        "--style",
        help="Authoring style: energy-arc, warm-cool, front-back, or vibe-palette",
    ),
    cues_per_section: int = typer.Option(
        2,
        "--cues-per-section",
        "-n",
        help="Number of proposed cues per selected section",
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write proposed cues to the show YAML"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Plan or apply deterministic renderer-safe cues for any show."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.authoring import plan_cues
    from rayflow.design.serializers import load_rig, load_show, save_show

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
    try:
        plan = plan_cues(
            show,
            rig,
            section_name=section,
            style=style,
            cues_per_section=cues_per_section,
            fixture_dir=fixture_dir,
            apply=apply,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if apply:
        save_show(show, path)

    payload = plan.as_dict()
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]Cue {payload['mode']}[/bold] {show.name}")
    console.print(f"Style: {plan.style}")
    console.print(f"Section: {plan.section}")
    console.print(f"Cues: {len(plan.proposed_cues)}")
    console.print(f"Next: {plan.next_command}")


@show_app.command("refine-cues")
def show_refine_cues(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    critique: str = typer.Option(
        ...,
        "--critique",
        help=(
            "Refinement critique: too-busy, less-movement, "
            "more-psychedelic, bigger-chorus"
        ),
    ),
    section: str = typer.Option(
        "all", "--section", help="Section name to refine, or all"
    ),
    apply: bool = typer.Option(
        False, "--apply", help="Write proposed cue refinements to the show YAML"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Plan or apply targeted cue edits from a user critique."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.authoring import refine_cues
    from rayflow.design.serializers import load_rig, load_show, save_show

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
    try:
        plan = refine_cues(
            show,
            rig,
            section_name=section,
            critique=critique,
            fixture_dir=fixture_dir,
            apply=apply,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if apply:
        save_show(show, path)

    payload = plan.as_dict()
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]Cue refinement {payload['mode']}[/bold] {show.name}")
    console.print(f"Critique: {plan.critique}")
    console.print(f"Section: {plan.section}")
    console.print(f"Cues: {len(plan.proposed_cues)}")
    console.print(f"Next: {plan.next_command}")


@show_app.command("plan-palettes")
def show_plan_palettes(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    apply: bool = typer.Option(
        False, "--apply", help="Write generated palettes to show overrides"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Plan or apply generated show-specific palette overrides."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.palette_generator import plan_show_palettes
    from rayflow.design.serializers import load_rig, load_show, save_show

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
    plan = plan_show_palettes(
        show,
        rig,
        fixture_dir=fixture_dir,
        apply=apply,
    )

    if apply:
        save_show(show, path)

    payload = plan.as_dict()
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    console.print(f"[bold]Palette {payload['mode']}[/bold] {show.name}")
    console.print(f"Presets: {len(plan.proposed_presets)}")
    if plan.replaced_override_names:
        console.print(f"Replacing generated: {len(plan.replaced_override_names)}")
    if plan.warnings:
        console.print(f"[yellow]Warnings: {len(plan.warnings)}[/yellow]")
    console.print(f"Next: {plan.next_command}")


@show_app.command("preview")
def show_preview(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    section: str = typer.Option(
        "all", "--section", help="Section name to preview, or all"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures/samples", "--fixture-dir", help="Fixture directory"
    ),
    output: Path | None = typer.Option(
        None, "--output", help="Write preview packet JSON to this path"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Build a dry-run preview packet for critique."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.preview import build_preview_packet
    from rayflow.design.serializers import load_rig, load_show

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
    try:
        packet = build_preview_packet(
            show,
            rig,
            fixture_dir=fixture_dir,
            section_name=section,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    payload = packet.as_dict()
    packet_text = json_module.dumps(payload, indent=2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(packet_text + "\n", encoding="utf-8")

    if json_output:
        typer.echo(packet_text)
        return

    console.print(f"[bold]Preview packet[/bold] {show.name}")
    console.print(f"Scope: {payload['scope']}")
    console.print(f"Readiness: {payload['readiness']['status']}")
    console.print(f"Cues: {len(packet.selected_cues)}")
    if output is not None:
        console.print(f"Written: {output}")


@show_app.command("validate-qxw")
def show_validate_qxw(
    workspace: Path = typer.Argument(..., help="Generated QLC+ .qxw workspace"),
    qxf_dir: Path | None = typer.Option(
        None,
        "--qxf-dir",
        help="Optional QLC+ fixture definition directory to check",
    ),
    live: bool = typer.Option(
        False,
        "--live",
        help="Also query a running QLC+ WebSocket endpoint for imported functions",
    ),
    trigger_functions: bool = typer.Option(
        False,
        "--trigger-functions",
        help="With --live, trigger exported Scene functions and record proof evidence",
    ),
    endpoint: str = typer.Option(
        "ws://127.0.0.1:9999/qlcplusWS", "--endpoint", help="QLC+ WebSocket endpoint"
    ),
    timeout: float = typer.Option(1.0, "--timeout", help="WebSocket timeout seconds"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Validate a generated QLC+ show workspace."""
    from rayflow.engine.fixtures.qlcplus_export import (
        qlc_scene_functions_from_workspace,
        validate_qlcplus_workspace,
    )

    if trigger_functions and not live:
        typer.echo("Error: --trigger-functions requires --live", err=True)
        raise typer.Exit(code=1)

    live_functions = None
    live_trigger_results = None
    if live:
        from rayflow.engine.backends import QlcPlusBackend

        backend = QlcPlusBackend(endpoint=endpoint)
        evidence = backend.query_functions(timeout=timeout)
        live_functions = evidence.observed.get("functions")
        if not isinstance(live_functions, list):
            live_functions = []
        if trigger_functions:
            live_by_name = {
                str(item.get("name")): item
                for item in live_functions
                if item.get("name") is not None
            }
            live_trigger_results = []
            for scene in qlc_scene_functions_from_workspace(workspace):
                live_function = live_by_name.get(str(scene["name"]))
                function_id = live_function.get("id") if live_function else scene["id"]
                try:
                    function_id_int = int(function_id)
                except (TypeError, ValueError):
                    live_trigger_results.append(
                        {
                            "scene": scene["name"],
                            "function_id": function_id,
                            "observed_matches": False,
                            "error": "Function ID is not numeric.",
                        }
                    )
                    continue
                trigger_evidence = backend.set_function_status(
                    function_id_int,
                    True,
                    execute=True,
                    timeout=timeout,
                )
                backend.set_function_status(
                    function_id_int,
                    False,
                    execute=True,
                    timeout=timeout,
                )
                live_trigger_results.append(
                    {
                        "scene": scene["name"],
                        "function_id": function_id_int,
                        "observed_matches": trigger_evidence.observed.get(
                            "observed_matches"
                        ),
                        "evidence": trigger_evidence.as_dict(),
                    }
                )

    report = validate_qlcplus_workspace(
        workspace,
        qxf_dir=qxf_dir,
        live_functions=live_functions,
        live_trigger_results=live_trigger_results,
    )
    payload = report.as_dict()
    if live:
        payload["live"]["endpoint"] = endpoint
        payload["live"]["triggered"] = trigger_functions
    if json_output:
        typer.echo(json_module.dumps(payload, indent=2))
        return

    status = payload["readiness"]["status"]
    color = "green" if status == "ready" else "yellow"
    console.print(f"[bold {color}]QXW validation {status}[/bold {color}] {workspace}")
    console.print(f"Fixtures: {report.fixture_count}")
    console.print(f"Scene functions: {report.scene_function_count}")
    console.print(f"Virtual Console buttons: {report.virtual_console_button_count}")
    console.print(f"Linked buttons: {report.linked_button_count}")
    if live:
        console.print(f"Live functions: {report.live_function_count}")
        if trigger_functions:
            console.print(f"Triggered functions: {len(report.live_trigger_results)}")
    if report.missing_function_links:
        console.print(
            f"[yellow]Missing links: {len(report.missing_function_links)}[/yellow]"
        )
    if report.missing_fixture_definitions:
        console.print(
            f"[yellow]Missing QXF definitions: "
            f"{len(report.missing_fixture_definitions)}[/yellow]"
        )
    if report.warnings:
        console.print(f"[yellow]Warnings: {len(report.warnings)}[/yellow]")
    if report.live_warnings:
        console.print(f"[yellow]Live warnings: {len(report.live_warnings)}[/yellow]")


@show_app.command("workflow-report")
def show_workflow_report(
    show_name: str | None = typer.Argument(None, help="Show name"),
    rig_name: str = typer.Option(..., "--rig", help="Rig name"),
    backend: str = typer.Option("artnet", "--backend", help="Backend: artnet or sacn"),
    section: str = typer.Option(
        "all", "--section", help="Section name to report, or all"
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
    output: Path | None = typer.Option(
        None, "--output", help="Write report JSON to this path"
    ),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
) -> None:
    """Build a dry-run practice workflow report for rendered backend output."""
    show_name = resolve_show_name(show_name)
    from rayflow.design.serializers import load_rig, load_show
    from rayflow.engine.backends import ArtNetDmxBackend, SacnDmxBackend
    from rayflow.engine.rendering import render_section_to_dmx, render_show_to_dmx

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
    section_name = section.strip()
    if section_name.lower() == "all":
        rendered_group = render_show_to_dmx(show, rig, fixture_dir)
        selected_section: str | None = None
    elif show.cues_for_section(section_name):
        rendered_group = render_section_to_dmx(show, rig, section_name, fixture_dir)
        selected_section = section_name
    else:
        typer.echo(f"Error: Section has no cues: {section_name}", err=True)
        raise typer.Exit(code=1)

    backend_name = backend.lower()
    if backend_name == "artnet":
        adapter = ArtNetDmxBackend(target_ip=target)
    elif backend_name == "sacn":
        adapter = SacnDmxBackend(
            multicast=multicast,
            universe_offset=sacn_universe_offset,
        )
    else:
        typer.echo(f"Error: Unknown backend '{backend}'. Use artnet or sacn.", err=True)
        raise typer.Exit(code=2)

    payload = _workflow_report_payload(
        show_name=show.name,
        rig_name=rig.name,
        backend_name=backend_name,
        selected_section=selected_section,
        rendered_group=rendered_group,
        mode="apply" if execute else "dry-run",
        evidence=[
            adapter.apply(
                rendered,
                capture_evidence=capture_evidence,
                evidence_timeout=evidence_timeout,
            )
            if execute
            else adapter.dry_run(rendered)
            for rendered in rendered_group.rendered_cues
        ],
    )
    report_text = json_module.dumps(payload, indent=2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report_text + "\n", encoding="utf-8")

    if json_output:
        typer.echo(report_text)
        return

    console.print(f"[bold]Workflow report[/bold] {show.name}")
    console.print(f"Rig: {rig.name}")
    console.print(f"Backend: {backend_name} {payload['mode']}")
    console.print(f"Readiness: {payload['readiness']['status']}")
    console.print(f"Cues: {payload['cue_count']}")
    if output is not None:
        console.print(f"Written: {output}")


def _workflow_report_payload(
    *,
    show_name: str,
    rig_name: str,
    backend_name: str,
    selected_section: str | None,
    rendered_group: Any,
    mode: str,
    evidence: list[Any],
) -> dict[str, Any]:
    rendered_cues = rendered_group.rendered_cues
    warnings = [
        warning.as_dict() for rendered in rendered_cues for warning in rendered.warnings
    ]
    evidence_dicts = [item.as_dict() for item in evidence]
    backend_warnings = [
        warning for item in evidence_dicts for warning in item.get("warnings", [])
    ]
    frame_count = sum(len(rendered.frames) for rendered in rendered_cues)
    status = "ready"
    if not rendered_cues or frame_count == 0:
        status = "blocked"
    elif warnings or backend_warnings:
        status = "warnings"

    return {
        "show": show_name,
        "rig": rig_name,
        "backend": backend_name,
        "mode": mode,
        "scope": rendered_group.scope,
        "section": selected_section or "all",
        "cue_count": len(rendered_cues),
        "frame_count": frame_count,
        "rendered": rendered_group.as_dict(),
        "evidence": evidence_dicts,
        "warnings": {
            "render": warnings,
            "backend": backend_warnings,
        },
        "readiness": {
            "status": status,
            "summary": _readiness_summary(status, len(warnings), len(backend_warnings)),
        },
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
    }


def _readiness_summary(
    status: str, render_warning_count: int, backend_warning_count: int
) -> str:
    if status == "ready":
        return "All selected cues rendered and produced backend evidence."
    if status == "blocked":
        return "No rendered backend frames were produced for the selected scope."
    return (
        "Workflow produced backend evidence with "
        f"{render_warning_count} render warnings and "
        f"{backend_warning_count} backend warnings."
    )
