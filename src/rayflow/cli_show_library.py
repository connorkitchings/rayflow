# -*- coding: utf-8 -*-
"""Show library CLI commands."""

from __future__ import annotations

from typing import Optional

import typer
from rich.table import Table

from rayflow._cli_shared import console
from rayflow.cli_show_paths import show_dir_path, show_path


def register_show_library_commands(show_app: typer.Typer) -> None:
    """Register show library commands on the provided show Typer app."""

    @show_app.command("save")
    def show_save_version(
        show_name: str = typer.Argument(..., help="Show name"),
        message: Optional[str] = typer.Option(
            None, "--message", "-m", help="Version note"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        library_dir: str = typer.Option(
            "data/show_library", "--library-dir", help="Show library directory"
        ),
    ) -> None:
        """Save a versioned snapshot of a show."""
        from rayflow.shows.library import save_show_version

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        try:
            saved = save_show_version(
                path,
                library_dir=library_dir,
                message=message,
            )
        except (FileExistsError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        console.print(f"[green]Saved show version[/green] {saved.metadata.version_id}")
        console.print(f"  Show: {saved.metadata.show_name}")
        console.print(f"  Snapshot: {saved.show_path}")
        console.print(f"  Metadata: {saved.metadata_path}")

    @show_app.command("versions")
    def show_versions(
        show_name: str = typer.Argument(..., help="Show name"),
        library_dir: str = typer.Option(
            "data/show_library", "--library-dir", help="Show library directory"
        ),
    ) -> None:
        """List saved versions for a show."""
        from rayflow.shows.library import list_show_versions

        versions = list_show_versions(show_name, library_dir=library_dir)
        if not versions:
            console.print(f"[dim]No saved versions for {show_name}[/dim]")
            return

        table = Table(title=f"Show Versions: {show_name}")
        table.add_column("Version", style="cyan")
        table.add_column("Created")
        table.add_column("Cues", justify="right")
        table.add_column("Message")
        for version in versions:
            table.add_row(
                version.version_id,
                version.created_at,
                str(version.cue_count),
                version.message or "",
            )
        console.print(table)

    @show_app.command("restore")
    def show_restore_version(
        show_name: str = typer.Argument(..., help="Show name"),
        version: str = typer.Option(..., "--version", help="Version ID to restore"),
        force: bool = typer.Option(
            False, "--force", help="Overwrite changed show file"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        library_dir: str = typer.Option(
            "data/show_library", "--library-dir", help="Show library directory"
        ),
    ) -> None:
        """Restore a saved show version."""
        from rayflow.shows.library import restore_show_version

        target = show_path(show_name, show_dir_path(show_dir))
        try:
            restored = restore_show_version(
                show_name,
                version,
                target_path=target,
                library_dir=library_dir,
                force=force,
            )
        except (FileNotFoundError, FileExistsError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        console.print(f"[green]Restored show version[/green] {version}")
        console.print(f"  Show: {show_name}")
        console.print(f"  Path: {restored}")

    @show_app.command("diff")
    def show_diff_version(
        show_name: str = typer.Argument(..., help="Show name"),
        version: str = typer.Option(..., "--version", help="Version ID to diff from"),
        other_version: Optional[str] = typer.Option(
            None, "--other-version", help="Optional second saved version"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
        library_dir: str = typer.Option(
            "data/show_library", "--library-dir", help="Show library directory"
        ),
    ) -> None:
        """Show a unified YAML diff against a saved show version."""
        from rayflow.shows.library import diff_show_version

        current_path = (
            None if other_version else show_path(show_name, show_dir_path(show_dir))
        )
        try:
            diff = diff_show_version(
                show_name,
                version,
                current_path=current_path,
                other_version_id=other_version,
                library_dir=library_dir,
            )
        except (FileNotFoundError, ValueError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        if diff:
            typer.echo(diff, nl=False)
        else:
            console.print("[dim]No differences[/dim]")
