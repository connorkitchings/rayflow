# -*- coding: utf-8 -*-
"""grandMA3 onPC console CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rayflow.cli._shared import console

console_app = typer.Typer(help="grandMA3 onPC console control")
cue_app = typer.Typer(help="Cue commands")
sequence_app = typer.Typer(help="Sequence commands")
channel_app = typer.Typer(help="Channel commands")
cue_stack_app = typer.Typer(help="Cue stack commands")
probe_app = typer.Typer(help="Safe grandMA3 live probe commands")
console_app.add_typer(cue_app, name="cue")
console_app.add_typer(sequence_app, name="sequence")
console_app.add_typer(channel_app, name="channel")
console_app.add_typer(cue_stack_app, name="cue-stack")
console_app.add_typer(probe_app, name="probe")


@console_app.command("connect")
def connect_ma3(
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send the OSC About command"
    ),
    feedback_port: Optional[int] = typer.Option(
        None, "--feedback-port", help="Optional local OSC feedback port"
    ),
    timeout: float = typer.Option(2.0, "--timeout", help="Feedback listen timeout"),
) -> None:
    """Test connection to grandMA3 onPC."""
    command = "About"
    _send_console_command(
        command,
        ip=ip,
        port=port,
        execute=execute,
        feedback_port=feedback_port,
        timeout=timeout,
    )


@console_app.command("cmd")
def send_command(
    command: str = typer.Argument(..., help="MA3 command string"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send the OSC command"
    ),
    feedback_port: Optional[int] = typer.Option(
        None, "--feedback-port", help="Optional local OSC feedback port"
    ),
    timeout: float = typer.Option(2.0, "--timeout", help="Feedback listen timeout"),
) -> None:
    """Send a command to grandMA3 onPC."""
    _send_console_command(
        command,
        ip=ip,
        port=port,
        execute=execute,
        feedback_port=feedback_port,
        timeout=timeout,
    )


@console_app.command("listen")
def listen_console_feedback(
    host: str = typer.Option("127.0.0.1", "--host", help="Local OSC listen host"),
    port: int = typer.Option(8001, "--port", "-p", help="Local OSC listen port"),
    duration: float = typer.Option(10.0, "--duration", "-d", help="Seconds to listen"),
) -> None:
    """Listen for grandMA3 OSC feedback without sending a command."""
    from rayflow.engine.console.osc import Ma3OscFeedbackReceiver

    console.print(f"[bold]Listening[/bold] for OSC feedback on {host}:{port}")
    receiver = Ma3OscFeedbackReceiver(host=host, port=port)
    messages = receiver.listen(duration=duration)
    _print_feedback_messages(messages)


@probe_app.command("show-isolation")
def probe_show_isolation(
    target_show: str = typer.Option(
        "rayflow_control_probe", "--target-show", help="Disposable MA3 show name"
    ),
    execute: bool = typer.Option(False, "--execute", help="Send OSC commands"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    delay: float = typer.Option(0.25, "--delay", help="Delay between commands"),
    shows_dir: Path = typer.Option(
        Path.home() / "MALightingTechnology/gma3_2.3.2/shared/shows",
        "--shows-dir",
        help="MA3 show file directory",
    ),
    result_json: Optional[Path] = typer.Option(
        None, "--result-json", help="Optional probe result JSON path"
    ),
    assume_disposable: bool = typer.Option(
        False,
        "--assume-disposable",
        help="Record user-confirmed disposable show if file isolation cannot prove it",
    ),
) -> None:
    """Verify MA3 disposable show isolation before live mutation probes."""
    from rayflow.engine.console.probe import (
        assumed_disposable_show_plan,
        run_probe_plan,
        show_isolation_passed,
        show_isolation_plan,
        validate_target_show,
        write_result_json,
    )

    try:
        if execute:
            validate_target_show(target_show)
        plan = (
            assumed_disposable_show_plan(target_show)
            if assume_disposable
            else show_isolation_plan(target_show)
        )
        result = run_probe_plan(
            plan,
            ip=ip,
            port=port,
            execute=execute,
            delay=delay,
            shows_dir=shows_dir,
            assume_disposable=assume_disposable,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    _print_probe_result(result)
    if execute and not (
        show_isolation_passed(
            target_show=target_show,
            before=result.pre_show_mtimes,
            after=result.post_show_mtimes,
        )
        or assume_disposable
    ):
        typer.echo("Error: disposable show isolation failed", err=True)
        if result_json is not None:
            write_result_json(result, result_json)
        raise typer.Exit(code=1)
    if result_json is not None:
        saved = write_result_json(result, result_json)
        console.print(f"[green]Wrote probe result[/green] {saved}")


@probe_app.command("command-acceptance")
def probe_command_acceptance(
    target_show: str = typer.Option(
        "rayflow_control_probe", "--target-show", help="Disposable MA3 show name"
    ),
    execute: bool = typer.Option(False, "--execute", help="Send OSC commands"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    delay: float = typer.Option(0.25, "--delay", help="Delay between commands"),
    shows_dir: Path = typer.Option(
        Path.home() / "MALightingTechnology/gma3_2.3.2/shared/shows",
        "--shows-dir",
        help="MA3 show file directory",
    ),
    export_path: Path = typer.Option(
        Path.home()
        / "MALightingTechnology/gma3_library/datapools/sequences"
        / "rayflow_command_acceptance_probe_sequence.xml",
        "--export-path",
        help="Expected MA3 export file written by the acceptance command",
    ),
    result_json: Optional[Path] = typer.Option(
        None, "--result-json", help="Optional probe result JSON path"
    ),
) -> None:
    """Verify OSC /cmd acceptance using an observable MA3 export."""
    from rayflow.engine.console.probe import (
        command_acceptance_plan,
        run_probe_plan,
        validate_target_show,
        write_result_json,
    )

    try:
        if execute:
            validate_target_show(target_show)
        result = run_probe_plan(
            command_acceptance_plan(target_show, export_path),
            ip=ip,
            port=port,
            execute=execute,
            delay=delay,
            shows_dir=shows_dir,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    _print_probe_result(result)
    if result_json is not None:
        saved = write_result_json(result, result_json)
        console.print(f"[green]Wrote probe result[/green] {saved}")
    if execute and not result.passed:
        raise typer.Exit(code=1)


@probe_app.command("live-osc-proof")
def probe_live_osc_proof(
    target_show: str = typer.Option(
        "rayflow_control_probe", "--target-show", help="Disposable MA3 show name"
    ),
    execute: bool = typer.Option(False, "--execute", help="Send OSC commands"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    delay: float = typer.Option(0.25, "--delay", help="Delay between commands"),
    shows_dir: Path = typer.Option(
        Path.home() / "MALightingTechnology/gma3_2.3.2/shared/shows",
        "--shows-dir",
        help="MA3 show file directory",
    ),
    export_path: Path = typer.Option(
        Path.home()
        / "MALightingTechnology/gma3_library/datapools/sequences"
        / "rayflow_command_acceptance_probe_sequence.xml",
        "--export-path",
        help="Expected MA3 export file written by the acceptance command",
    ),
    result_json: Optional[Path] = typer.Option(
        None, "--result-json", help="Optional probe result JSON path"
    ),
) -> None:
    """Prove live MA3 OSC /cmd acceptance against the disposable probe show only."""
    from rayflow.engine.console.probe import (
        command_acceptance_plan,
        run_probe_plan,
        validate_target_show,
        write_result_json,
    )

    try:
        validate_target_show(target_show)
        result = run_probe_plan(
            command_acceptance_plan(target_show, export_path),
            ip=ip,
            port=port,
            execute=execute,
            delay=delay,
            shows_dir=shows_dir,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    result.metadata["proof_type"] = "disposable-command-acceptance"
    result.metadata["live_mutation_scope"] = "rayflow_control_probe_only"
    _print_probe_result(result)
    if result_json is not None:
        saved = write_result_json(result, result_json)
        console.print(f"[green]Wrote probe result[/green] {saved}")
    if execute and not result.passed:
        raise typer.Exit(code=1)


@probe_app.command("fixture-import")
def probe_fixture_import(
    mvr: Path = typer.Option(
        Path("data/ma3_exports/probes/rayflow_control_probe.mvr"),
        "--mvr",
        help="Probe MVR output path",
    ),
    target_show: str = typer.Option(
        "rayflow_control_probe", "--target-show", help="Disposable MA3 show name"
    ),
    execute: bool = typer.Option(
        False,
        "--execute",
        help="Build the MVR after validating the disposable target show name",
    ),
    import_method: str = typer.Option(
        "none",
        "--import-method",
        help="Import evidence mode: none, cli, or ui-assisted",
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    assume_disposable: bool = typer.Option(
        False,
        "--assume-disposable",
        help="Record user-confirmed disposable show for import/patch verification",
    ),
    result_json: Optional[Path] = typer.Option(
        None, "--result-json", help="Optional probe result JSON path"
    ),
    write_note: bool = typer.Option(
        False, "--write-note", help="Write research note template"
    ),
) -> None:
    """Build the dedicated sample-fixture MVR for MA3 import proof."""
    from rayflow.engine.console.probe import (
        MA3_VERSION,
        ProbeResult,
        build_fixture_probe_mvr,
        fixture_probe_mvr_entries,
        require_disposable_confirmation,
        validate_target_show,
        write_research_note_template,
        write_result_json,
    )

    import_method = import_method.lower()
    if import_method not in {"none", "cli", "ui-assisted"}:
        typer.echo("Error: --import-method must be none, cli, or ui-assisted", err=True)
        raise typer.Exit(code=1)

    try:
        if execute:
            validate_target_show(target_show)
            if import_method != "none":
                require_disposable_confirmation(
                    target_show=target_show,
                    assume_disposable=assume_disposable,
                )
            saved = build_fixture_probe_mvr(mvr)
            entries = fixture_probe_mvr_entries(saved)
            console.print(f"[green]Probe MVR exported[/green] {saved}")
            metadata = {
                "mvr_path": str(saved),
                "mvr_entries": entries,
                "import_method": import_method,
                "assume_disposable": assume_disposable,
            }
            if import_method == "cli":
                import time

                from rayflow.engine.console.osc import Ma3OscClient
                from rayflow.engine.console.probe import CommandLog

                import_command = f'Import MVR "{saved.expanduser().resolve()}"'
                Ma3OscClient(ip=ip, port=port).send(import_command)
                commands = [
                    CommandLog(command=import_command, sent=True, timestamp=time.time())
                ]
                metadata["import_command"] = import_command
                console.print(
                    "[yellow]CLI import is not verified; use the recorded "
                    "command as probe evidence only.[/yellow]"
                )
            elif import_method == "ui-assisted":
                commands = []
                metadata["ui_instruction"] = (
                    "Import the generated MVR into the active disposable MA3 show, "
                    "then capture verification evidence."
                )
            else:
                commands = []
            passed = import_method == "none"
            status = "passed" if passed else "pending-verification"
            result = ProbeResult(
                name="fixture-import",
                target_show=target_show,
                ma3_version=MA3_VERSION,
                osc_endpoint=f"{ip}:{port}" if import_method == "cli" else "not-used",
                executed=True,
                passed=passed,
                commands=commands,
                exports=[],
                pre_show_mtimes={},
                post_show_mtimes={},
                status=status,
                metadata=metadata,
            )
        else:
            console.print("[bold yellow]Dry run[/bold yellow] fixture import probe")
            console.print(f"Would build probe MVR: {mvr}")
            console.print("[dim]Pass --execute to write the MVR artifact.[/dim]")
            result = None
        if write_note:
            note = write_research_note_template()
            console.print(f"[green]Wrote research note template[/green] {note}")
        if result_json is not None and result is not None:
            saved_json = write_result_json(result, result_json)
            console.print(f"[green]Wrote probe result[/green] {saved_json}")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@probe_app.command("run")
def probe_run(
    plan: Path = typer.Option(..., "--plan", help="Probe plan JSON path"),
    target_show: str = typer.Option(
        "rayflow_control_probe", "--target-show", help="Disposable MA3 show name"
    ),
    execute: bool = typer.Option(False, "--execute", help="Send OSC commands"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    delay: float = typer.Option(0.25, "--delay", help="Delay between commands"),
    shows_dir: Path = typer.Option(
        Path.home() / "MALightingTechnology/gma3_2.3.2/shared/shows",
        "--shows-dir",
        help="MA3 show file directory",
    ),
    result_json: Optional[Path] = typer.Option(
        None, "--result-json", help="Optional probe result JSON path"
    ),
    assume_disposable: bool = typer.Option(
        False,
        "--assume-disposable",
        help="Record user-confirmed disposable show for live generic probes",
    ),
) -> None:
    """Run or dry-run a JSON MA3 probe plan."""
    from rayflow.engine.console.probe import (
        load_probe_plan,
        run_probe_plan,
        validate_target_show,
        write_result_json,
    )

    try:
        probe_plan = load_probe_plan(plan)
        if probe_plan.target_show != target_show:
            raise ValueError("plan target_show must match --target-show")
        if execute:
            validate_target_show(target_show)
        result = run_probe_plan(
            probe_plan,
            ip=ip,
            port=port,
            execute=execute,
            delay=delay,
            shows_dir=shows_dir,
            assume_disposable=assume_disposable,
        )
    except (FileNotFoundError, KeyError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    _print_probe_result(result)
    if result_json is not None:
        saved = write_result_json(result, result_json)
        console.print(f"[green]Wrote probe result[/green] {saved}")
    if execute and not result.passed:
        raise typer.Exit(code=1)


@cue_app.command("store")
def store_cue_command(
    cue: int = typer.Argument(..., help="Cue number"),
    fade: Optional[float] = typer.Option(None, "--fade", help="Optional fade time"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send generated OSC commands"
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
) -> None:
    """Store a cue, optionally setting its fade time."""
    from rayflow.engine.console.cue import set_cue_time, store_cue

    try:
        commands = [store_cue(cue)]
        if fade is not None:
            commands.append(set_cue_time(cue, fade))
        _send_ma3_commands(commands, ip=ip, port=port, execute=execute)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@sequence_app.command("go")
def go_sequence_command(
    sequence: int = typer.Argument(..., help="Sequence number"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send generated OSC commands"
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
) -> None:
    """Run a sequence."""
    from rayflow.engine.console.cue import go_sequence

    try:
        _send_ma3_commands([go_sequence(sequence)], ip=ip, port=port, execute=execute)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@channel_app.command("at")
def channel_at_command(
    channels: str = typer.Argument(..., help='Channel spec, e.g. "1 Thru 8"'),
    value: str = typer.Argument(..., help='Value, e.g. "Full" or "50"'),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send generated OSC commands"
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
) -> None:
    """Set channel intensity."""
    from rayflow.engine.console.cue import channel_at

    try:
        _send_ma3_commands(
            [channel_at(channels, value)], ip=ip, port=port, execute=execute
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@console_app.command("clear")
def clear_console_command(
    execute: bool = typer.Option(
        False, "--execute", help="Actually send generated OSC commands"
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
) -> None:
    """Clear the grandMA3 programmer."""
    from rayflow.engine.console.cue import clear_programmer

    _send_ma3_commands([clear_programmer()], ip=ip, port=port, execute=execute)


@cue_stack_app.command("run")
def run_cue_stack_command(
    path: Path = typer.Argument(..., help="Cue stack JSON file"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send generated OSC commands"
    ),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    feedback_port: Optional[int] = typer.Option(
        None, "--feedback-port", help="Optional local OSC feedback port"
    ),
    timeout: float = typer.Option(2.0, "--timeout", help="Feedback listen timeout"),
) -> None:
    """Generate or send commands for a cue stack JSON file."""
    from rayflow.engine.console.cue import commands_for_cue_stack, load_cue_stack
    from rayflow.engine.console.osc import Ma3OscFeedbackReceiver

    try:
        stack = load_cue_stack(path)
        commands = commands_for_cue_stack(stack)
        console.print(f"[bold]Cue stack:[/bold] {stack.name or path.name}")
        _send_ma3_commands(commands, ip=ip, port=port, execute=execute)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    if execute and feedback_port is not None:
        receiver = Ma3OscFeedbackReceiver(port=feedback_port)
        messages = receiver.listen(duration=timeout)
        _print_feedback_messages(messages)


def _send_console_command(
    command: str,
    *,
    ip: str,
    port: int,
    execute: bool,
    feedback_port: int | None,
    timeout: float,
) -> None:
    from rayflow.engine.console.osc import Ma3OscClient, Ma3OscFeedbackReceiver

    try:
        if not command.strip():
            raise ValueError("OSC command must not be empty")
        if not execute:
            console.print(
                f"[bold yellow]Dry run[/bold yellow] OSC /cmd to {ip}:{port}: {command}"
            )
            console.print("[dim]Pass --execute to send this command.[/dim]")
            return

        client = Ma3OscClient(ip=ip, port=port)
        client.send(command)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    console.print(f"[bold green]Sent[/bold green] OSC /cmd to {ip}:{port}: {command}")
    if feedback_port is not None:
        receiver = Ma3OscFeedbackReceiver(port=feedback_port)
        messages = receiver.listen(duration=timeout)
        _print_feedback_messages(messages)


def _send_ma3_commands(commands, *, ip: str, port: int, execute: bool) -> None:
    from rayflow.engine.console.osc import Ma3OscClient

    if not execute:
        console.print(f"[bold yellow]Dry run[/bold yellow] OSC /cmd to {ip}:{port}")
        for command in commands:
            console.print(command.command)
        console.print("[dim]Pass --execute to send these commands.[/dim]")
        return

    client = Ma3OscClient(ip=ip, port=port)
    for command in commands:
        client.send(command.command)
        console.print(f"[bold green]Sent[/bold green] {command.command}")


def _print_feedback_messages(messages) -> None:
    if not messages:
        console.print("[dim]No OSC feedback received[/dim]")
        return

    table = Table(title="OSC Feedback")
    table.add_column("#", justify="right")
    table.add_column("Address", style="cyan")
    table.add_column("Args", style="green")
    for message in messages:
        table.add_row(
            str(message.index),
            message.address,
            ", ".join(str(arg) for arg in message.args),
        )
    console.print(table)


def _print_probe_result(result) -> None:
    """Print a compact MA3 probe result."""
    console.print(f"[bold]Probe:[/bold] {result.name}")
    console.print(f"  Status: {result.status}")
    console.print(f"  Target show: {result.target_show}")
    console.print(f"  OSC: {result.osc_endpoint}")
    if result.commands:
        table = Table(title="Commands")
        table.add_column("#", justify="right")
        table.add_column("Sent")
        table.add_column("Command")
        for index, command in enumerate(result.commands, start=1):
            table.add_row(str(index), "yes" if command.sent else "no", command.command)
        console.print(table)
    if result.exports:
        table = Table(title="Expected Exports")
        table.add_column("Label")
        table.add_column("Exists")
        table.add_column("Missing markers")
        for item in result.exports:
            table.add_row(
                item.label,
                "yes" if item.exists else "no",
                ", ".join(item.missing_substrings) or "-",
            )
        console.print(table)


# ---------------------------------------------------------------------------
# Rig management
# ---------------------------------------------------------------------------
