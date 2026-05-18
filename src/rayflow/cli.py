"""RayFlow CLI entry point."""

from __future__ import annotations

import typer

from rayflow.cli_bridge import bridge_app
from rayflow.cli_console import console_app
from rayflow.cli_fixture import fixture_app
from rayflow.cli_rig import rig_app
from rayflow.cli_show import show_app

app = typer.Typer(
    name="rayflow",
    help="Concert lighting design toolkit",
    add_completion=False,
)

app.add_typer(bridge_app, name="bridge")
app.add_typer(fixture_app, name="fixture")
app.add_typer(console_app, name="console")
app.add_typer(rig_app, name="rig")
app.add_typer(show_app, name="show")

if __name__ == "__main__":
    app()
