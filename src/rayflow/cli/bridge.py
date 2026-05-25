# -*- coding: utf-8 -*-
"""Art-Net / sACN bridge CLI commands."""

from __future__ import annotations

import time
from typing import Optional

import typer
from rich.table import Table

from rayflow.cli._shared import console
from rayflow.config import Settings
from rayflow.engine.bridge.exceptions import BridgeError


def _get_settings() -> Settings:
    try:
        return Settings.from_env()
    except Exception as e:
        typer.echo(f"Error loading config: {e}", err=True)
        raise typer.Exit(code=1)


bridge_app = typer.Typer(help="Art-Net / sACN bridge commands")


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
            from rayflow.engine.bridge.artnet import ArtNetSender

            sender = ArtNetSender(target_ip=ip, universe=universe)
            sender.set_channel(channel, value)
            target_str = f"{ip}:6454"

        elif protocol == "sacn":
            from rayflow.engine.bridge.sacn_bridge import SacnSender

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
            from rayflow.engine.bridge.artnet import ArtNetReceiver

            receiver = ArtNetReceiver(universe=universe)
            port = 6454
        elif protocol == "sacn":
            from rayflow.engine.bridge.sacn_bridge import SacnReceiver

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
