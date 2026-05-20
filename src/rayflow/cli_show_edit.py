# -*- coding: utf-8 -*-
"""Show metadata, section, vibe, and preset override CLI commands."""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Optional

import typer

from rayflow._cli_shared import console
from rayflow.cli_show_paths import show_dir_path, show_path


def register_show_edit_commands(show_app: typer.Typer) -> None:
    """Register show editing commands on the provided show Typer app."""

    @show_app.command("set-vibe")
    def show_set_vibe(
        show_name: str = typer.Argument(..., help="Show name"),
        vibe_json: Optional[Path] = typer.Option(
            None, "--vibe-json", help="Vibe JSON file"
        ),
        palette_name: Optional[str] = typer.Option(
            None, "--palette-name", help="Color palette name"
        ),
        colors: Optional[str] = typer.Option(
            None, "--colors", help='Colors JSON: ["#FF6600","#3366FF"]'
        ),
        palette_desc: Optional[str] = typer.Option(
            None, "--palette-desc", help="Color palette description"
        ),
        intensity_curve: Optional[str] = typer.Option(
            None, "--intensity", help='Intensity curve, e.g. "low -> medium -> high"'
        ),
        movement_style: Optional[str] = typer.Option(
            None, "--movement", help='Movement style, e.g. "slow sweep"'
        ),
        beam_style: Optional[str] = typer.Option(
            None, "--beam", help='Beam style, e.g. "tight beams"'
        ),
        mood_keywords: Optional[str] = typer.Option(
            None,
            "--mood-keywords",
            help='Mood keywords JSON: ["cinematic","building"]',
        ),
        description: Optional[str] = typer.Option(
            None, "--description", help="Vibe description"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Set or update the vibe for a show."""
        from rayflow.shows.models import Vibe
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        try:
            if vibe_json is not None:
                if not vibe_json.exists():
                    typer.echo(f"Error: Vibe JSON not found: {vibe_json}", err=True)
                    raise typer.Exit(code=1)
                data = json_module.loads(vibe_json.read_text(encoding="utf-8"))
                vibe = Vibe.from_dict(data)
            else:
                if palette_name is None or colors is None:
                    typer.echo(
                        "Error: --palette-name and --colors are required "
                        "when not using --vibe-json",
                        err=True,
                    )
                    raise typer.Exit(code=1)
                color_list = json_module.loads(colors)
                mood_list: list[str] = []
                if mood_keywords:
                    mood_list = json_module.loads(mood_keywords)
                vibe = Vibe.from_dict(
                    {
                        "palette": {
                            "name": palette_name,
                            "colors": color_list,
                            "description": palette_desc or "",
                        },
                        "intensity_curve": intensity_curve or "medium",
                        "movement_style": movement_style or "static",
                        "beam_style": beam_style,
                        "mood_keywords": mood_list,
                        "description": description or "",
                    }
                )
        except (ValueError, json_module.JSONDecodeError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        show.vibe = vibe
        save_show(show, path)
        console.print(f"[green]Vibe set[/green] on {show_name}")
        console.print(f"  Palette: {vibe.palette.name}")
        console.print(f"  Colors: {', '.join(vibe.palette.colors)}")
        console.print(f"  Intensity: {vibe.intensity_curve}")
        console.print(f"  Movement: {vibe.movement_style}")
        if vibe.beam_style:
            console.print(f"  Beam: {vibe.beam_style}")

    @show_app.command("set-song-meta")
    def show_set_song_meta(
        show_name: str = typer.Argument(..., help="Show name"),
        title: Optional[str] = typer.Option(None, "--title", help="New song title"),
        artist: Optional[str] = typer.Option(None, "--artist", help="New song artist"),
        duration: Optional[float] = typer.Option(
            None, "--duration", help="New song duration (seconds)"
        ),
        bpm: Optional[float] = typer.Option(None, "--bpm", help="New song BPM"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Update song metadata on a show."""
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        try:
            show = load_show(path)
            if title is not None:
                if not title.strip():
                    raise ValueError("Song title must not be empty")
                show.song.title = title
            if artist is not None:
                if not artist.strip():
                    raise ValueError("Song artist must not be empty")
                show.song.artist = artist
            if duration is not None:
                if duration <= 0:
                    raise ValueError(f"Song duration must be > 0, got {duration}")
                show.song.duration = duration
            if bpm is not None:
                if bpm <= 0:
                    raise ValueError(f"BPM must be > 0, got {bpm}")
                show.song.bpm = bpm
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        save_show(show, path)
        console.print(f"[green]Updated song meta[/green] for {show_name}")
        console.print(f"  Title: {show.song.title}")
        console.print(f"  Artist: {show.song.artist}")
        console.print(f"  Duration: {show.song.duration}s")
        if show.song.bpm:
            console.print(f"  BPM: {show.song.bpm}")

    @show_app.command("update-section")
    def show_update_section(
        show_name: str = typer.Argument(..., help="Show name"),
        name: str = typer.Option(..., "--name", help="Section name to update"),
        start: Optional[float] = typer.Option(
            None, "--start", help="New start time (seconds)"
        ),
        end: Optional[float] = typer.Option(
            None, "--end", help="New end time (seconds)"
        ),
        energy: Optional[float] = typer.Option(
            None, "--energy", help="New energy level (0-1)"
        ),
        mood: Optional[str] = typer.Option(None, "--mood", help="New mood descriptor"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Update a song section's fields."""
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        section = None
        for s in show.song.sections:
            if s.name == name:
                section = s
                break
        if section is None:
            typer.echo(f"Error: Section not found: {name}", err=True)
            raise typer.Exit(code=1)

        try:
            if start is not None:
                if start < 0:
                    raise ValueError(f"Section start must be >= 0, got {start}")
                if start >= section.end:
                    raise ValueError(f"Start ({start}) must be < end ({section.end})")
                section.start = start
            if end is not None:
                if end <= section.start:
                    raise ValueError(f"End ({end}) must be > start ({section.start})")
                section.end = end
            if energy is not None:
                if not (0 <= energy <= 1):
                    raise ValueError(f"Energy must be 0-1, got {energy}")
                section.energy = energy
            if mood is not None:
                section.mood = mood if mood.strip() else None
        except ValueError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        save_show(show, path)
        console.print(f"[green]Updated section[/green] {name} in {show_name}")

    @show_app.command("delete-section")
    def show_delete_section(
        show_name: str = typer.Argument(..., help="Show name"),
        name: str = typer.Option(..., "--name", help="Section name to delete"),
        delete_cues: bool = typer.Option(
            False, "--delete-cues", help="Also delete cues belonging to this section"
        ),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Remove a song section from a show."""
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        show = load_show(path)
        section = None
        for s in show.song.sections:
            if s.name == name:
                section = s
                break
        if section is None:
            typer.echo(f"Error: Section not found: {name}", err=True)
            raise typer.Exit(code=1)

        show.song.sections = [s for s in show.song.sections if s.name != name]

        if delete_cues:
            from rayflow.shows.cue_generator import delete_cues_for_section

            removed = delete_cues_for_section(show, name)
            console.print(f"  Also deleted {removed} cues")

        save_show(show, path)
        console.print(f"[green]Deleted section[/green] {name} from {show_name}")

    @show_app.command("add-section")
    def show_add_section(
        show_name: str = typer.Argument(..., help="Show name"),
        name: str = typer.Option(..., "--name", help="Section name"),
        start: float = typer.Option(..., "--start", help="Start time (seconds)"),
        end: float = typer.Option(..., "--end", help="End time (seconds)"),
        energy: Optional[float] = typer.Option(
            None, "--energy", help="Energy level (0-1)"
        ),
        mood: Optional[str] = typer.Option(None, "--mood", help="Mood descriptor"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Add a song section to a show."""
        from rayflow.shows.models import Section
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
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

    @show_app.command("import-sections")
    def show_import_sections(
        show_name: str = typer.Argument(..., help="Show name"),
        json_file: Path = typer.Argument(..., help="Section import JSON file"),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Import song sections from an audio analysis JSON file."""
        from rayflow.shows.section_import import import_sections_to_song
        from rayflow.shows.serializers import load_show, save_show

        if not json_file.exists():
            typer.echo(f"Error: File not found: {json_file}", err=True)
            raise typer.Exit(code=1)

        path = show_path(show_name, show_dir_path(show_dir))
        if not path.exists():
            typer.echo(f"Error: Show not found: {show_name}", err=True)
            raise typer.Exit(code=1)

        try:
            show = load_show(path)
            import_sections_to_song(json_file, song=show.song)
        except (ValueError, json_module.JSONDecodeError) as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(code=1)

        save_show(show, path)
        section_count = len(show.song.sections)
        console.print(
            f"[green]Imported sections[/green] from {json_file.name} to {show_name}"
        )
        console.print(f"  Song: {show.song.title} by {show.song.artist}")
        console.print(f"  Duration: {show.song.duration}s")
        if show.song.bpm:
            console.print(f"  BPM: {show.song.bpm}")
        console.print(f"  Sections: {section_count}")
        for sec in show.song.sections:
            energy_str = f", energy={sec.energy:.2f}" if sec.energy is not None else ""
            mood_str = f", mood={sec.mood}" if sec.mood else ""
            console.print(
                f"    {sec.name}: {sec.start:.1f}s-{sec.end:.1f}s{energy_str}{mood_str}"
            )

    @show_app.command("add-preset-override")
    def show_add_preset_override(
        show_name: str = typer.Argument(..., help="Show name"),
        name: str = typer.Argument(..., help="Preset name"),
        description: str = typer.Option(..., "--description", help="Description"),
        attributes: str = typer.Option(
            ..., "--attributes", help='Attributes JSON: {"dimmer":"80"}'
        ),
        channels: Optional[str] = typer.Option(
            None, "--channels", help="MA3 channel spec"
        ),
        tags: Optional[str] = typer.Option(None, "--tags", help='Tags JSON: ["warm"]'),
        show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    ) -> None:
        """Add a show-specific preset override."""
        from rayflow.shows.models import Preset
        from rayflow.shows.serializers import load_show, save_show

        path = show_path(show_name, show_dir_path(show_dir))
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
