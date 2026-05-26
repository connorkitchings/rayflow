"""MA3 show export bundle generation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from rayflow import __version__
from rayflow.design.models import Rig, Show, resolve_presets
from rayflow.engine.console.push import commands_for_show
from rayflow.engine.console.timecode_export import export_timecode_xml
from rayflow.engine.fixtures.library import FixtureLibrary
from rayflow.engine.fixtures.mvr_export import FixturePosition, build_patch_entry
from rayflow.engine.fixtures.mvr_export import export_mvr as write_mvr


@dataclass(frozen=True)
class ShowExportBundle:
    """Files generated for an MA3 show export bundle."""

    output_dir: Path
    mvr_path: Path
    commands_path: Path
    readme_path: Path
    metadata_path: Path
    timecode_path: Path
    command_count: int
    fixture_count: int


def export_show_bundle(
    show: Show,
    rig: Rig,
    *,
    output_dir: str | Path,
    fixture_dir: str | Path,
    sequence: int = 1,
) -> ShowExportBundle:
    """Export a dry-run-safe MA3 bundle for a RayFlow show."""
    if sequence <= 0:
        raise ValueError("sequence must be > 0")

    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    patches = build_mvr_patches(rig, fixture_dir)
    if not patches:
        raise ValueError("No valid fixtures to export")

    mvr_path = target_dir / "rig.mvr"
    write_mvr(patches, mvr_path, scene_name=rig.name)

    presets = resolve_presets(rig, show)
    commands = commands_for_show(show, presets, sequence=sequence)
    commands_path = target_dir / "ma3_push_commands.txt"
    commands_path.write_text(
        "\n".join(command.command for command in commands) + "\n",
        encoding="utf-8",
    )

    timecode_path = target_dir / "timecode.xml"
    timecode_xml = export_timecode_xml(show, sequence=sequence)
    timecode_path.write_text(timecode_xml, encoding="utf-8-sig")

    readme_path = target_dir / "README.md"
    readme_path.write_text(
        _bundle_readme(
            show, rig, sequence, commands_path.name, mvr_path.name, timecode_path.name
        ),
        encoding="utf-8",
    )

    metadata_path = target_dir / "metadata.json"
    metadata = {
        "rayflow_version": __version__,
        "show": show.name,
        "song": {
            "title": show.song.title,
            "artist": show.song.artist,
            "duration": show.song.duration,
        },
        "rig": rig.name,
        "sequence": sequence,
        "cue_count": len(show.cues),
        "command_count": len(commands),
        "fixture_count": len(patches),
        "files": {
            "mvr": mvr_path.name,
            "commands": commands_path.name,
            "timecode": timecode_path.name,
            "readme": readme_path.name,
        },
        "format_notes": {
            "native_show_file": "not_generated",
            "native_show_file_reason": (
                "grandMA3 .show.gz generation remains out of scope until the "
                "binary format is proven writable."
            ),
            "timecode_xml_source": "captured grandMA3 onPC 2.3.2.0 event exports",
            "import_validation_required": True,
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    return ShowExportBundle(
        output_dir=target_dir,
        mvr_path=mvr_path,
        commands_path=commands_path,
        readme_path=readme_path,
        metadata_path=metadata_path,
        timecode_path=timecode_path,
        command_count=len(commands),
        fixture_count=len(patches),
    )


def build_mvr_patches(rig: Rig, fixture_dir: str | Path):
    """Build MVR patch entries for a rig using the fixture library."""
    library = FixtureLibrary(fixture_dir)
    library.load()

    patches = []
    address = 1
    for slot in rig.fixtures:
        parser = library.get(slot.fixture_name)
        if parser is None:
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

    return patches


def _bundle_readme(
    show: Show,
    rig: Rig,
    sequence: int,
    commands_filename: str,
    mvr_filename: str,
    timecode_filename: str,
) -> str:
    return f"""# RayFlow MA3 Show Export: {show.name}

Generated for grandMA3 onPC 2.3.2.0.

## Contents

- `{mvr_filename}` — MVR rig export for MA3 patch and 3D import.
- `{commands_filename}` — dry-run OSC command list for Sequence {sequence}.
- `{timecode_filename}` — MA3 Timecode XML based on captured MA3 2.3.2.0
  event exports; validate import/playback before use.
- `metadata.json` — bundle metadata for automation and review.

## Verified Boundaries

RayFlow does not generate a native `.show.gz` file in this bundle. The MA3
native show format is treated as opaque until a writable format is verified.
This bundle uses inspectable artifacts instead: MVR, OSC command text, and
captured-export-shaped Timecode XML.

## Import Workflow

1. Import `{mvr_filename}` into grandMA3 to create the rig/patch for `{rig.name}`.
2. Review `{commands_filename}` before sending anything to MA3.
3. Dry-run the same command path with:

   `rayflow show push-to-ma3 "{show.name}" --sequence {sequence}`

4. When the rig and command list look correct, send the cues with:

   `rayflow show push-to-ma3 "{show.name}" --sequence {sequence} --execute`

5. Import `{timecode_filename}` into grandMA3 via *Import → Timecode Pool*
   and validate the events against the Timecode Viewer.

> **Note:** The Timecode XML follows captured MA3 2.3.2.0 event exports. Verify
> import/playback in MA3 before relying on it for show playback.
"""
