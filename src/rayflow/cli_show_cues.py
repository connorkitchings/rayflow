# -*- coding: utf-8 -*-
"""Show cue editing CLI commands."""

from __future__ import annotations

import json as json_module
from typing import Optional

import typer

from rayflow._cli_shared import console
from rayflow.cli_show_paths import show_dir_path, show_path


def register_show_cue_commands(show_app: typer.Typer) -> None:
    """Register cue editing commands on the provided show Typer app."""

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
        channels: Optional[str] = typer.Option(
            None, "--channels", help="MA3 channel spec"
        ),
        fade: float = typer.Option(0.0, "--fade", help="Fade time (seconds)"),
        follow: Optional[float] = typer.Option(
            None, "--follow", help="Follow time (seconds)"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Add a cue to a show."""
        from rayflow.shows.models import Cue
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
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

    @show_app.command("update-cue")
    def show_update_cue(
        show_name: str = typer.Argument(..., help="Show name"),
        number: int = typer.Option(..., "--number", help="Cue number to update"),
        label: Optional[str] = typer.Option(None, "--label", help="New label"),
        timestamp: Optional[float] = typer.Option(
            None, "--timestamp", help="New timestamp (seconds)"
        ),
        preset: Optional[str] = typer.Option(None, "--preset", help="New preset name"),
        section: Optional[str] = typer.Option(
            None, "--section", help="New section name"
        ),
        attributes: Optional[str] = typer.Option(
            None, "--attributes", help='Attributes JSON: {"dimmer":"80"}'
        ),
        channels: Optional[str] = typer.Option(
            None, "--channels", help="MA3 channel spec"
        ),
        fade: Optional[float] = typer.Option(
            None, "--fade", help="New fade time (seconds)"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Update an existing cue's fields."""
        from rayflow.shows.cue_generator import update_cue
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        attrs: dict[str, str] | None = None
        if attributes:
            try:
                attrs = json_module.loads(attributes)
            except json_module.JSONDecodeError as e:
                typer.echo(f"Error: Invalid attributes JSON: {e}", err=True)
                raise typer.Exit(code=1)

        try:
            show = load_show(path)
            update_cue(
                show,
                number,
                label=label,
                timestamp=timestamp,
                preset=preset,
                channels=channels,
                attributes=attrs,
                fade_time=fade,
                section=section,
            )
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        save_show(show, path)
        console.print(f"[green]Updated cue[/green] #{number} in {show_name}")

    @show_app.command("delete-cue")
    def show_delete_cue(
        show_name: str = typer.Argument(..., help="Show name"),
        number: int = typer.Option(..., "--number", help="Cue number to delete"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Delete a cue and renumber remaining cues."""
        from rayflow.shows.cue_generator import remove_cue
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        try:
            show = load_show(path)
            removed = remove_cue(show, number)
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        from rayflow.shows.cue_generator import auto_number_cues

        auto_number_cues(show)
        save_show(show, path)
        console.print(
            f"[green]Deleted cue[/green] #{number} ({removed.label}) from {show_name}"
        )

    @show_app.command("renumber")
    def show_renumber(
        show_name: str = typer.Argument(..., help="Show name"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Renumber all cues sequentially starting from 1."""
        from rayflow.shows.cue_generator import auto_number_cues
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        auto_number_cues(show)
        save_show(show, path)
        console.print(f"[green]Renumbered[/green] {len(show.cues)} cues in {show_name}")

    @show_app.command("generate-cues")
    def show_generate_cues(
        show_name: str = typer.Argument(..., help="Show name"),
        section: str = typer.Option(..., "--section", help="Song section name"),
        preset: Optional[str] = typer.Option(None, "--preset", help="Preset name"),
        count: int = typer.Option(4, "--count", "-n", help="Number of cues"),
        spacing: float = typer.Option(
            5.0, "--spacing", "-s", help="Spacing between cues (seconds)"
        ),
        fade: float = typer.Option(0.0, "--fade", help="Fade time (seconds)"),
        attributes: Optional[str] = typer.Option(
            None, "--attributes", help='Attributes JSON: {"dimmer":"80"}'
        ),
        channels: Optional[str] = typer.Option(
            None, "--channels", help="MA3 channel spec"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Generate evenly spaced cues for a song section."""
        from rayflow.shows.cue_generator import generate_cues_for_section
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        attrs: dict[str, str] | None = None
        if attributes:
            try:
                attrs = json_module.loads(attributes)
            except json_module.JSONDecodeError as e:
                typer.echo(f"Error: Invalid attributes JSON: {e}", err=True)
                raise typer.Exit(code=1)

        try:
            show = load_show(path)
            generated = generate_cues_for_section(
                show,
                section,
                preset=preset,
                count=count,
                spacing=spacing,
                attributes=attrs,
                channels=channels,
                fade_time=fade,
            )
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        for cue in generated:
            show.add_cue(cue)

        from rayflow.shows.cue_generator import auto_number_cues

        auto_number_cues(show)
        save_show(show, path)
        console.print(
            f"[green]Generated[/green] {len(generated)} cues "
            f"for section {section} in {show_name}"
        )
        for cue in generated:
            console.print(f"  #{cue.number}: {cue.label} at {cue.timestamp:.1f}s")

    @show_app.command("batch-update-cues")
    def show_batch_update_cues(
        show_name: str = typer.Argument(..., help="Show name"),
        section: Optional[str] = typer.Option(
            None, "--section", help="Limit to cues in this section"
        ),
        attributes: Optional[str] = typer.Option(
            None, "--attributes", help='Attributes JSON: {"dimmer":"Full"}'
        ),
        set_fade: Optional[float] = typer.Option(
            None, "--set-fade", help="Set fade time on matching cues"
        ),
        set_preset: Optional[str] = typer.Option(
            None, "--set-preset", help="Set preset on matching cues"
        ),
        delete: bool = typer.Option(
            False, "--delete", help="Delete matching cues instead of updating"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Batch update or delete cues matching a filter."""
        from rayflow.shows.cue_generator import batch_update_cues
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        attrs: dict[str, str] | None = None
        if attributes:
            try:
                attrs = json_module.loads(attributes)
            except json_module.JSONDecodeError as e:
                typer.echo(f"Error: Invalid attributes JSON: {e}", err=True)
                raise typer.Exit(code=1)

        try:
            show = load_show(path)
            affected = batch_update_cues(
                show,
                section=section,
                attributes=attrs,
                set_fade=set_fade,
                set_preset=set_preset,
                delete=delete,
            )
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        save_show(show, path)
        action = "Deleted" if delete else "Updated"
        section_str = f" in section '{section}'" if section else ""
        console.print(
            f"[green]{action}[/green] {affected} cues{section_str} in {show_name}"
        )
