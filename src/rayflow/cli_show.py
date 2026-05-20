# -*- coding: utf-8 -*-
"""Show definition CLI commands."""

from __future__ import annotations

import json as json_module
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from rayflow._cli_shared import console, list_yaml_files
from rayflow.cli_rig import _rig_dir_path, _rig_path

show_app = typer.Typer(help="Show definition management")


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


@show_app.command("save")
def show_save_version(
    show_name: str = typer.Argument(..., help="Show name"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Version note"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    library_dir: str = typer.Option(
        "data/show_library", "--library-dir", help="Show library directory"
    ),
) -> None:
    """Save a versioned snapshot of a show."""
    from rayflow.shows.library import save_show_version

    show_path = _show_path(show_name, _show_dir_path(show_dir))
    if not show_path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    try:
        saved = save_show_version(
            show_path,
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
    force: bool = typer.Option(False, "--force", help="Overwrite changed show file"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    library_dir: str = typer.Option(
        "data/show_library", "--library-dir", help="Show library directory"
    ),
) -> None:
    """Restore a saved show version."""
    from rayflow.shows.library import restore_show_version

    target = _show_path(show_name, _show_dir_path(show_dir))
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
        None if other_version else _show_path(show_name, _show_dir_path(show_dir))
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
        None, "--mood-keywords", help='Mood keywords JSON: ["cinematic","building"]'
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Vibe description"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Set or update the vibe for a show.

    Can load from a JSON file or specify inline. The vibe defines the
    creative direction: color palette, intensity curve, movement style,
    and beam choices.

    Vibe JSON format:
    {
      "palette": {
        "name": "Warm to Cool",
        "colors": ["#FF6600", "#FF3366", "#3366FF", "#00CCFF"],
        "description": "Start warm, transition to cool blues"
      },
      "intensity_curve": "low -> medium -> high",
      "movement_style": "slow sweep",
      "beam_style": "tight beams",
      "mood_keywords": ["cinematic", "building"],
      "description": "Cinematic build from warm amber to cool blue energy"
    }
    """
    from rayflow.shows.models import Vibe
    from rayflow.shows.serializers import load_show, save_show

    show_path = _show_path(show_name, _show_dir_path(show_dir))
    if not show_path.exists():
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

    show = load_show(show_path)
    show.vibe = vibe
    save_show(show, show_path)
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

    path = _show_path(show_name, _show_dir_path(show_dir))
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
    end: Optional[float] = typer.Option(None, "--end", help="New end time (seconds)"),
    energy: Optional[float] = typer.Option(
        None, "--energy", help="New energy level (0-1)"
    ),
    mood: Optional[str] = typer.Option(None, "--mood", help="New mood descriptor"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Update a song section's fields."""
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
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

    path = _show_path(show_name, _show_dir_path(show_dir))
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


@show_app.command("import-sections")
def show_import_sections(
    show_name: str = typer.Argument(..., help="Show name"),
    json_file: Path = typer.Argument(..., help="Section import JSON file"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Import song sections from an audio analysis JSON file.

    The JSON format is LLM-agnostic and supports Mixed In Key, rekordbox,
    Ableton, and other audio analysis tools:

    {
      "title": "Song Title",
      "artist": "Artist Name",
      "duration": 245.0,
      "bpm": 120.0,
      "sections": [
        {"name": "Intro", "start": 0.0, "end": 15.0, "energy": 0.3, "mood": "ambient"},
        {"name": "Verse 1", "start": 15.0, "end": 45.0, "energy": 0.5}
      ]
    }
    """
    from rayflow.shows.section_import import import_sections_to_song
    from rayflow.shows.serializers import load_show, save_show

    if not json_file.exists():
        typer.echo(f"Error: File not found: {json_file}", err=True)
        raise typer.Exit(code=1)

    show_path = _show_path(show_name, _show_dir_path(show_dir))
    if not show_path.exists():
        typer.echo(f"Error: Show not found: {show_name}", err=True)
        raise typer.Exit(code=1)

    try:
        show = load_show(show_path)
        import_sections_to_song(json_file, song=show.song)
    except (ValueError, json_module.JSONDecodeError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    save_show(show, show_path)
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


@show_app.command("update-cue")
def show_update_cue(
    show_name: str = typer.Argument(..., help="Show name"),
    number: int = typer.Option(..., "--number", help="Cue number to update"),
    label: Optional[str] = typer.Option(None, "--label", help="New label"),
    timestamp: Optional[float] = typer.Option(
        None, "--timestamp", help="New timestamp (seconds)"
    ),
    preset: Optional[str] = typer.Option(None, "--preset", help="New preset name"),
    section: Optional[str] = typer.Option(None, "--section", help="New section name"),
    attributes: Optional[str] = typer.Option(
        None, "--attributes", help='Attributes JSON: {"dimmer":"80"}'
    ),
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    fade: Optional[float] = typer.Option(
        None, "--fade", help="New fade time (seconds)"
    ),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Update an existing cue's fields."""
    from rayflow.shows.cue_generator import update_cue
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
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

    path = _show_path(show_name, _show_dir_path(show_dir))
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

    path = _show_path(show_name, _show_dir_path(show_dir))
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
    channels: Optional[str] = typer.Option(None, "--channels", help="MA3 channel spec"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
) -> None:
    """Generate evenly spaced cues for a song section."""
    from rayflow.shows.cue_generator import generate_cues_for_section
    from rayflow.shows.serializers import load_show, save_show

    path = _show_path(show_name, _show_dir_path(show_dir))
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

    path = _show_path(show_name, _show_dir_path(show_dir))
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


@show_app.command("push-to-ma3")
def show_push_to_ma3(
    show_name: str = typer.Argument(..., help="Show name"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send OSC commands to MA3"
    ),
    sequence: int = typer.Option(1, "--sequence", help="Target MA3 sequence number"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
) -> None:
    """Push all show cues to grandMA3 onPC via OSC.

    Generates OSC commands from the show's cues and presets.
    By default, runs as a dry-run showing the commands that would be sent.
    Use --execute to actually send them.
    """
    from rayflow.shows.models import resolve_presets
    from rayflow.shows.push import commands_for_show
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
    presets = resolve_presets(rig, show)
    commands = commands_for_show(show, presets, sequence=sequence)

    seq_label = show.song.title
    if not commands:
        console.print(f"[dim]Show {show_name} has no cues to push[/dim]")
        return

    if not execute:
        console.print(
            f"[bold yellow]Dry run[/bold yellow] — {len(commands)} OSC commands "
            f"for {show_name}:"
        )
        console.print(f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")')
        for cmd in commands:
            console.print(f"  {cmd.command}")
        console.print(
            f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
        )
        return

    from rayflow.console.osc import Ma3OscClient

    client = Ma3OscClient(ip=ip, port=port)
    for cmd in commands:
        client.send(cmd.command)
    console.print(
        f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
        f"to Sequence {sequence} on {ip}:{port}"
    )


@show_app.command("push-section")
def show_push_section(
    show_name: str = typer.Argument(..., help="Show name"),
    section: str = typer.Option(..., "--section", help="Section name to push"),
    execute: bool = typer.Option(
        False, "--execute", help="Actually send OSC commands to MA3"
    ),
    sequence: int = typer.Option(1, "--sequence", help="Target MA3 sequence number"),
    ip: str = typer.Option("127.0.0.1", "--ip", help="grandMA3 onPC IP"),
    port: int = typer.Option(8000, "--port", "-p", help="OSC port"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
) -> None:
    """Push cues for a single section to grandMA3 onPC."""
    from rayflow.shows.models import resolve_presets
    from rayflow.shows.push import commands_for_show
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
    presets = resolve_presets(rig, show)
    commands = commands_for_show(show, presets, section=section, sequence=sequence)

    seq_label = show.song.title
    if not commands:
        console.print(f"[dim]Show {show_name} has no cues in section '{section}'[/dim]")
        return

    if not execute:
        console.print(
            f"[bold yellow]Dry run[/bold yellow] — {len(commands)} OSC commands "
            f"for section '{section}' in {show_name}:"
        )
        console.print(f'  [bold]Target:[/bold] Sequence {sequence} ("{seq_label}")')
        for cmd in commands:
            console.print(f"  {cmd.command}")
        console.print(
            f"\n[dim]Pass --execute to send {len(commands)} commands to MA3[/dim]"
        )
        return

    from rayflow.console.osc import Ma3OscClient

    client = Ma3OscClient(ip=ip, port=port)
    for cmd in commands:
        client.send(cmd.command)
    console.print(
        f"[bold green]Sent[/bold green] {len(commands)} OSC commands "
        f"to Sequence {sequence} on {ip}:{port}"
    )


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


@show_app.command("export")
def show_export(
    show_name: str = typer.Argument(..., help="Show name"),
    output_dir: Path = typer.Option(
        ..., "--output-dir", "-o", help="Output bundle directory"
    ),
    sequence: int = typer.Option(1, "--sequence", help="Target MA3 sequence number"),
    show_dir: str = typer.Option("data/shows", "--dir", help="Show directory"),
    rig_dir: str = typer.Option("data/rigs", "--rig-dir", help="Rig directory"),
    fixture_dir: str = typer.Option(
        "data/fixtures", "--fixture-dir", help="Fixture directory"
    ),
) -> None:
    """Export a dry-run-safe MA3 bundle for a show."""
    from rayflow.shows.export_bundle import export_show_bundle
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
        bundle = export_show_bundle(
            show,
            rig,
            output_dir=output_dir,
            fixture_dir=fixture_dir,
            sequence=sequence,
        )
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

    console.print(f"[green]MA3 show export created[/green] at {bundle.output_dir}")
    console.print(f"  MVR: {bundle.mvr_path}")
    console.print(f"  Commands: {bundle.commands_path}")
    console.print(f"  README: {bundle.readme_path}")
    console.print(f"  Metadata: {bundle.metadata_path}")
    console.print(f"  Sequence: {sequence}")
    console.print(f"  Fixtures: {bundle.fixture_count}")
    console.print(f"  OSC commands: {bundle.command_count}")


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
    from rayflow.fixtures.mvr_export import (
        export_mvr as _export_mvr,
    )
    from rayflow.shows.export_bundle import build_mvr_patches
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
        patches = build_mvr_patches(rig, fixture_dir)
    except (FileNotFoundError, ValueError) as e:
        typer.echo(f"Error loading fixtures: {e}", err=True)
        raise typer.Exit(code=1)

    if not patches:
        typer.echo("Error: No valid fixtures to export", err=True)
        raise typer.Exit(code=1)

    saved = _export_mvr(patches, output, scene_name=rig.name)
    console.print(f"[green]MVR exported[/green] to {saved}")
    console.print(f"  Fixtures: {len(patches)}")
    console.print(f"  Scene: {rig.name}")
