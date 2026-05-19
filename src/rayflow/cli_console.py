# -*- coding: utf-8 -*-
"""grandMA3 onPC console CLI commands."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rayflow._cli_shared import console

console_app = typer.Typer(help="grandMA3 onPC console control")
cue_app = typer.Typer(help="Cue commands")
sequence_app = typer.Typer(help="Sequence commands")
channel_app = typer.Typer(help="Channel commands")
cue_stack_app = typer.Typer(help="Cue stack commands")
console_app.add_typer(cue_app, name="cue")
console_app.add_typer(sequence_app, name="sequence")
console_app.add_typer(channel_app, name="channel")
console_app.add_typer(cue_stack_app, name="cue-stack")


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
    from rayflow.console.osc import Ma3OscFeedbackReceiver

    console.print(f"[bold]Listening[/bold] for OSC feedback on {host}:{port}")
    receiver = Ma3OscFeedbackReceiver(host=host, port=port)
    messages = receiver.listen(duration=duration)
    _print_feedback_messages(messages)


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
    from rayflow.console.cue import set_cue_time, store_cue

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
    from rayflow.console.cue import go_sequence

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
    from rayflow.console.cue import channel_at

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
    from rayflow.console.cue import clear_programmer

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
    from rayflow.console.cue import commands_for_cue_stack, load_cue_stack
    from rayflow.console.osc import Ma3OscFeedbackReceiver

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
    from rayflow.console.osc import Ma3OscClient, Ma3OscFeedbackReceiver

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
    from rayflow.console.osc import Ma3OscClient

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


# ---------------------------------------------------------------------------
# Rig management
# ---------------------------------------------------------------------------
