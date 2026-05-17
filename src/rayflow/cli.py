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
    from rayflow.fixtures.library import FixtureLibrary
    from rayflow.fixtures.ma3_compare import (
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
    from rayflow.fixtures.ma3_compare import compare_all_samples

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
    from rayflow.fixtures.library import FixtureLibrary
    from rayflow.fixtures.mvr_export import (
        FixturePosition,
        build_patch_entry,
    )
    from rayflow.fixtures.mvr_export import (
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


# ---------------------------------------------------------------------------
# Rig management
# ---------------------------------------------------------------------------

rig_app = typer.Typer(help="Rig definition management")
app.add_typer(rig_app, name="rig")


def _rig_dir_path(dir: str) -> Path:
    return Path(dir)


def _list_yaml_files(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*.yaml"))


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
    files = _list_yaml_files(directory)
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


# ---------------------------------------------------------------------------
# Show management
# ---------------------------------------------------------------------------

show_app = typer.Typer(help="Show definition management")
app.add_typer(show_app, name="show")


def _show_dir_path(dir: str) -> Path:
    return Path(dir)


def _show_path(name: str, directory: Path) -> Path:
    return directory / f"{name}.yaml"


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

    target = _show_path(name, _show_dir_path(show_dir))
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

    directory = _show_dir_path(show_dir)
    files = _list_yaml_files(directory)
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

    path = _show_path(name, _show_dir_path(show_dir))
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


@show_app.command("add-section")
def show_add_section(
    show_name: str = typer.Argument(..., help="Show name"),
    name: str = typer.Option(..., "--name", help="Section name"),
    start: float = typer.Option(..., "--start", help="Start time (seconds)"),
    end: float = typer.Option(..., "--end", help="End time (seconds)"),
    energy: Optional[float] = typer.Option(None, "--energy", help="Energy level (0-1)"),
    mood: Optional[str] = typer.Option(None, "--mood", help="Mood descriptor"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Add a song section to a show."""
    from rayflow.shows.models import Section
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    try:
        section = Section(name=name, start=start, end=end, energy=energy, mood=mood)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)
    show.song.add_section(section)
    save_show(show, path)
    console.print(
        f"[green]Added section[/green] {name} ({start}s-{end}s) to {show_name}"
    )


@show_app.command("add-cue")
def show_add_cue(
    show_name: str = typer.Argument(..., help="Show name"),
    number: int = typer.Option(..., "--number", help="Cue number"),
    label: str = typer.Option(..., "--label", help="Cue label"),
    section: str = typer.Option(..., "--section", help="Song section name"),
    timestamp: float = typer.Option(..., "--timestamp", help="Timecode (seconds)"),
    preset: Optional[str] = typer.Option(None, "--preset", help="Preset name"),
    attributes: Optional[str] = typer.Option(
        None, "--attributes", help='Attributes JSON: {"dimmer":"80"}'
    ),
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    fade: float = typer.Option(0.0, "--fade", help="Fade time (seconds)"),
    follow: Optional[float] = typer.Option(
        None, "--follow", help="Follow time (seconds)"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Add a cue to a show."""
    from rayflow.shows.models import Cue
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    attrs: dict[str, str] = {}
    if attributes:
        try:
            attrs = json_module.loads(attributes)
        except json_module.JSONDecodeError as e:
            typer.echo(f"Error: Invalid attributes JSON: {e}", err=True)
            raise typer.Exit(code=1)

    try:
        cue = Cue(
            number=number,
            label=label,
            section=section,
            timestamp=timestamp,
            preset=preset,
            channels=channels,
            attributes=attrs,
            fade_time=fade,
            follow_time=follow,
        )
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    show = load_show(path)
    show.add_cue(cue)
    save_show(show, path)
    console.print(f"[green]Added cue[/green] #{number} {label} to {show_name}")


@show_app.command("add-preset-override")
def show_add_preset_override(
    show_name: str = typer.Argument(..., help="Show name"),
    name: str = typer.Argument(..., help="Preset name"),
    description: str = typer.Option(..., "--description", help="Description"),
    attributes: str = typer.Option(
        ..., "--attributes", help='Attributes JSON: {"dimmer":"80"}'
    ),
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    tags: Optional[str] = typer.Option(None, "--tags", help='Tags JSON: ["warm"]'),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Add a show-specific preset override."""
    from rayflow.shows.models import Preset
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
    if not path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
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

    show = load_show(path)
    show.preset_overrides[name] = preset
    save_show(show, path)
    console.print(f"[green]Added preset override[/green] {name} to {show_name}")


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

    bundle = build_context_bundle(show, rig, fixture_dir)
    typer.echo(json_module.dumps(bundle, indent=2))


@show_app.command("export-mvr")
def show_export_mvr(
    show_name: str = typer.Argument(..., help="Show name"),
    output: Path = typer.Option(..., "--output", "-o", help="Output MVR file path"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--fixture-dir", help="Fixture directory"
    ),
) -> None:
    """Export a show's rig as an MVR file."""
    from rayflow.fixtures.library import FixtureLibrary
    from rayflow.fixtures.mvr_export import (
        FixturePosition,
        build_patch_entry,
    )
    from rayflow.fixtures.mvr_export import (
        export_mvr as _export_mvr,
    )
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


if __name__ == "__main__":
    app()
