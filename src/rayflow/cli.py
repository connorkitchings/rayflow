"""RayFlow CLI entry point."""

import json as json_module
import time
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from rayflow.bridge.exceptions import BridgeError
from rayflow.config import Settings

app = typer.Typer(
    name="rayflow",
    help="Concert lighting design toolkit",
    add_completion=False,
)
console = Console()


def _get_settings() -> Settings:
    try:
        return Settings.from_env()
    except Exception as e:
        typer.echo(f"Error loading config: {e}", err=True)
        raise typer.Exit(code=1)


bridge_app = typer.Typer(help="Art-Net / sACN bridge commands")
app.add_typer(bridge_app, name="bridge")


def _validate_channel(channel: int) -> None:
    if not 1 <= channel <= 512:
        typer.echo(f"Error: Channel must be 1-512, got {channel}", err=True)
        raise typer.Exit(code=2)


def _validate_value(value: int) -> None:
    if not 0 <= value <= 255:
        typer.echo(f"Error: Value must be 0-255, got {value}", err=True)
        raise typer.Exit(code=2)


def _validate_protocol(protocol: str) -> str:
    protocol = protocol.lower()
    if protocol not in ("artnet", "sacn"):
        typer.echo(
            f"Error: Unknown protocol '{protocol}'. Use artnet or sacn.", err=True
        )
        raise typer.Exit(code=2)
    return protocol


@bridge_app.command("send")
def send_dmx(
    universe: int = typer.Option(0, "--universe", "-u", help="DMX universe number"),
    channel: int = typer.Option(1, "--channel", "-c", help="DMX channel (1-512)"),
    value: int = typer.Option(0, "--value", "-v", help="DMX value (0-255)"),
    protocol: str = typer.Option(
        "artnet", "--protocol", "-p", help="Protocol: artnet or sacn"
    ),
    target: Optional[str] = typer.Option(
        None, "--target", "-t", help="Target IP address"
    ),
    multicast: bool = typer.Option(
        False, "--multicast/--no-multicast", help="Use multicast (sACN only)"
    ),
) -> None:
    """Send a DMX value to a channel."""
    _validate_channel(channel)
    _validate_value(value)
    protocol = _validate_protocol(protocol)
    settings = _get_settings()

    try:
        if protocol == "artnet":
            ip = target or settings.artnet.target_ip
            from rayflow.bridge.artnet import ArtNetSender

            sender = ArtNetSender(target_ip=ip, universe=universe)
            sender.set_channel(channel, value)
            target_str = f"{ip}:6454"

        elif protocol == "sacn":
            from rayflow.bridge.sacn_bridge import SacnSender

            sender = SacnSender(
                universe=universe,
                multicast=multicast,
            )
            sender.set_channels({channel - 1: value})
            sender.flush()
            sender.stop()
            target_str = "multicast" if multicast else "127.0.0.1 (unicast)"

        console.print(
            f"[bold green]Sending[/bold green] channel {channel} = {value} "
            f"on universe {universe} via {protocol}"
        )
        console.print(f"Target: {target_str}")
        console.print("[dim]Packet sent successfully[/dim]")

    except BridgeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@bridge_app.command("recv")
def recv_dmx(
    universe: int = typer.Option(
        0, "--universe", "-u", help="DMX universe to listen on"
    ),
    protocol: str = typer.Option(
        "artnet", "--protocol", "-p", help="Protocol: artnet or sacn"
    ),
    duration: int = typer.Option(10, "--duration", "-d", help="Seconds to listen"),
) -> None:
    """Listen for incoming DMX values."""
    protocol = _validate_protocol(protocol)

    try:
        if protocol == "artnet":
            from rayflow.bridge.artnet import ArtNetReceiver

            receiver = ArtNetReceiver(universe=universe)
            port = 6454
        elif protocol == "sacn":
            from rayflow.bridge.sacn_bridge import SacnReceiver

            receiver = SacnReceiver(universe=universe)
            receiver.join_multicast()
            port = 5568

        console.print(
            f"[bold]Listening[/bold] on universe {universe} via {protocol} "
            f"(port {port}) for {duration} seconds..."
        )
        start_time = time.time()
        last_frame = 0

        while time.time() - start_time < duration:
            if protocol == "artnet":
                buffer = receiver.get_buffer()
                if buffer and sum(buffer) > 0 and hash(bytes(buffer)) != last_frame:
                    last_frame = hash(bytes(buffer))
                    table = Table(title=f"Universe {universe} — Non-Zero Channels")
                    table.add_column("Channel", style="cyan")
                    table.add_column("Value", style="green")
                    for i, v in enumerate(buffer):
                        if v > 0:
                            table.add_row(str(i + 1), str(v))
                    console.print(table)
            elif protocol == "sacn":
                time.sleep(0.1)
            time.sleep(0.1)

        console.print(f"[dim]Listening ended after {duration}s[/dim]")

    except BridgeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)


@bridge_app.command("status")
def bridge_status() -> None:
    """Show bridge configuration and status."""
    settings = _get_settings()

    table = Table(title="RayFlow Bridge Status")
    table.add_column("Protocol", style="cyan")
    table.add_column("Setting", style="dim")
    table.add_column("Value", style="green")

    table.add_row("Art-Net", "Target", settings.artnet.target_ip)
    table.add_row("Art-Net", "Port", str(settings.artnet.port))
    table.add_row("Art-Net", "Universe", str(settings.artnet.universe))
    table.add_row("Art-Net", "Status", "[green]Ready[/green]")
    table.add_section()
    table.add_row("sACN", "Universe", str(settings.sacn.universe))
    table.add_row(
        "sACN",
        "Multicast",
        "[green]on[/green]" if settings.sacn.multicast else "[dim]off[/dim]",
    )
    table.add_row("sACN", "Status", "[green]Ready[/green]")

    console.print(table)


fixture_app = typer.Typer(help="GDTF fixture management")
app.add_typer(fixture_app, name="fixture")


@fixture_app.command("list")
def list_fixtures(
    fixture_dir: str = typer.Option(
        "data/fixtures", "--dir", "-d", help="Fixture directory"
    ),
) -> None:
    """List loaded GDTF fixtures."""
    from rayflow.fixtures.library import FixtureLibrary

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
    from rayflow.fixtures.library import FixtureLibrary

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
    from rayflow.fixtures.library import FixtureLibrary
    from rayflow.fixtures.patch import DmxUniverse

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
    json_output: bool = typer.Option(
        False, "--json", help="Print machine-readable JSON output"
    ),
) -> None:
    """Build or compare a RayFlow patch report for grandMA3 validation."""
    from rayflow.fixtures.ma3_compare import (
        build_library_patch_report,
        compare_ma3_observation,
        load_ma3_observation,
    )

    try:
        report = build_library_patch_report(
            fixture_name,
            fixture_dir=fixture_dir,
            mode_index=mode_index,
            mode_name=mode,
            universe=universe,
            start_address=address,
        )
        comparison = None
        if ma3_json is not None:
            observation = load_ma3_observation(ma3_json)
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


console_app = typer.Typer(help="grandMA3 onPC console control")
app.add_typer(console_app, name="console")
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


if __name__ == "__main__":
    app()
