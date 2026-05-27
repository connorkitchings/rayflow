"""QLC+ workspace (.qxw) exporter.

Generates a QLC+ workspace XML file from a RayFlow rig configuration.
The exported file can be loaded directly into QLC+ to configure universes
and patch all fixtures in one step.

QLC+ workspace format reference:
- Root element: <Workspace>
- <Creator> metadata block
- <Engine> containing <InputOutputMap> (universes) and <Fixture> entries
- Universe and Address are 0-based in QLC+ (RayFlow uses 0-based universes,
  1-based addresses)
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from rayflow.engine.rendering import RenderedCue

# QLC+ workspace format version
QXW_VERSION = "4.12.4"
QXW_ENGINE_VERSION = "2"

# Universe limit for the InputOutputMap
_MAX_UNIVERSES = 4


@dataclass(frozen=True)
class QlcFixturePatch:
    """Patch data for a single fixture in a QLC+ workspace."""

    fixture_id: int
    name: str
    manufacturer: str
    model: str
    mode: str
    universe: int
    address: int  # 1-based (RayFlow convention)
    channel_count: int

    @property
    def qlc_address(self) -> int:
        """QLC+ uses 0-based addresses."""
        return self.address - 1

    @property
    def qlc_universe(self) -> int:
        """QLC+ uses 0-based universes."""
        return self.universe

    def as_dict(self) -> dict[str, Any]:
        return {
            "fixture_id": self.fixture_id,
            "name": self.name,
            "manufacturer": self.manufacturer,
            "model": self.model,
            "mode": self.mode,
            "universe": self.universe,
            "address": self.address,
            "channel_count": self.channel_count,
        }


@dataclass(frozen=True)
class QlcSceneFunction:
    """Export-only QLC+ Scene function data."""

    function_id: int
    name: str
    fixture_values: dict[int, list[int]]
    cue_number: int | None = None
    cue_label: str | None = None
    fade_ms: int = 0
    duration_ms: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "function_id": self.function_id,
            "name": self.name,
            "fixture_values": {
                str(fixture_id): list(values)
                for fixture_id, values in self.fixture_values.items()
            },
            "cue_number": self.cue_number,
            "cue_label": self.cue_label,
            "fade_ms": self.fade_ms,
            "duration_ms": self.duration_ms,
        }


@dataclass(frozen=True)
class QlcWorkspaceValidationReport:
    """Static validation report for a generated QLC+ workspace."""

    path: str
    fixture_count: int
    scene_function_count: int
    virtual_console_button_count: int
    linked_button_count: int
    missing_function_links: list[str] = field(default_factory=list)
    missing_fixture_definitions: list[str] = field(default_factory=list)
    live_function_count: int | None = None
    live_function_names: list[str] = field(default_factory=list)
    live_missing_scene_names: list[str] = field(default_factory=list)
    live_trigger_results: list[dict[str, Any]] = field(default_factory=list)
    live_observed_matches: bool | None = None
    live_warnings: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return not (
            self.missing_function_links
            or self.missing_fixture_definitions
            or self.live_missing_scene_names
            or self.live_observed_matches is False
            or self.live_warnings
            or self.warnings
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "fixture_count": self.fixture_count,
            "scene_function_count": self.scene_function_count,
            "virtual_console_button_count": self.virtual_console_button_count,
            "linked_button_count": self.linked_button_count,
            "missing_function_links": list(self.missing_function_links),
            "missing_fixture_definitions": list(self.missing_fixture_definitions),
            "live": {
                "function_count": self.live_function_count,
                "function_names": list(self.live_function_names),
                "missing_scene_names": list(self.live_missing_scene_names),
                "trigger_results": list(self.live_trigger_results),
                "observed_matches": self.live_observed_matches,
                "warnings": list(self.live_warnings),
            },
            "warnings": list(self.warnings),
            "readiness": {
                "status": "ready" if self.ready else "warnings",
                "summary": _validation_summary(self),
            },
        }


@dataclass(frozen=True)
class QxfWorkspaceCopyResult:
    """QXF copy result for direct QLC+ workspace opening."""

    source: Path
    destination: Path
    copied: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": str(self.source),
            "destination": str(self.destination),
            "copied": self.copied,
        }


def build_qlcplus_workspace(
    patches: list[QlcFixturePatch],
    *,
    functions: list[QlcSceneFunction] | None = None,
    virtual_console: bool = True,
    author: str = "RayFlow",
) -> ET.Element:
    """Build a QLC+ workspace XML element tree.

    Args:
        patches: List of QlcFixturePatch objects representing patched fixtures.
        functions: Optional QLC+ Scene functions to include in the Engine block.
        virtual_console: Add a basic playback surface for exported functions.
        author: Author name to embed in the workspace Creator block.

    Returns:
        The root XML element of the workspace.
    """
    root = ET.Element("Workspace")
    root.set("xmlns", "http://www.qlcplus.org/Workspace")
    root.set("CurrentWindow", "FixtureManager")

    _add_creator(root, author=author)
    engine = ET.SubElement(root, "Engine")
    _add_input_output_map(engine, patches)

    for patch in patches:
        _add_fixture(engine, patch)

    for function in functions or []:
        _add_scene_function(engine, function)

    if virtual_console and functions:
        _add_virtual_console(root, functions)

    return root


def export_qlcplus_workspace(
    patches: list[QlcFixturePatch],
    output_path: str | Path,
    *,
    functions: list[QlcSceneFunction] | None = None,
    virtual_console: bool = True,
    author: str = "RayFlow",
) -> Path:
    """Export a QLC+ workspace file (.qxw) from a fixture patch list.

    Args:
        patches: List of QlcFixturePatch objects representing patched fixtures.
        output_path: Destination path for the .qxw file.
        functions: Optional QLC+ Scene functions to include in the workspace.
        virtual_console: Add a basic playback surface for exported functions.
        author: Author name embedded in the workspace Creator block.

    Returns:
        The resolved output path.
    """
    output_path = Path(output_path)
    root = build_qlcplus_workspace(
        patches,
        functions=functions,
        virtual_console=virtual_console,
        author=author,
    )
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")

    with output_path.open("wb") as fh:
        fh.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
        fh.write(b"<!DOCTYPE Workspace>\n")
        tree.write(fh, encoding="UTF-8", xml_declaration=False)

    return output_path


def validate_qlcplus_workspace(
    workspace_path: str | Path,
    *,
    qxf_dir: str | Path | None = None,
    live_functions: list[dict[str, Any]] | None = None,
    live_trigger_results: list[dict[str, Any]] | None = None,
) -> QlcWorkspaceValidationReport:
    """Inspect a generated QLC+ workspace for import-readiness."""
    workspace_path = Path(workspace_path)
    try:
        root = ET.parse(workspace_path).getroot()
    except ET.ParseError as exc:
        return QlcWorkspaceValidationReport(
            path=str(workspace_path),
            fixture_count=0,
            scene_function_count=0,
            virtual_console_button_count=0,
            linked_button_count=0,
            warnings=[f"Malformed QXW XML: {exc}"],
        )
    except OSError as exc:
        return QlcWorkspaceValidationReport(
            path=str(workspace_path),
            fixture_count=0,
            scene_function_count=0,
            virtual_console_button_count=0,
            linked_button_count=0,
            warnings=[str(exc)],
        )

    fixtures = _children(root, "Fixture")
    scenes = [
        function
        for function in _children(root, "Function")
        if function.get("Type") == "Scene"
    ]
    scene_ids = {scene.get("ID") for scene in scenes if scene.get("ID") is not None}
    buttons = _children(root, "Button")

    missing_links: list[str] = []
    linked_count = 0
    for button in buttons:
        function_id = _child_text(button, "Function")
        caption = button.get("Caption") or button.get("ID") or "<unnamed>"
        if function_id in scene_ids:
            linked_count += 1
        else:
            missing_links.append(f"{caption} -> {function_id or '<missing>'}")

    warnings: list[str] = []
    if fixtures and not scenes:
        warnings.append("Workspace has fixtures but no Scene functions.")
    if scenes and not buttons:
        warnings.append("Workspace has Scene functions but no Virtual Console buttons.")

    missing_fixture_definitions = _missing_qxf_definitions(fixtures, qxf_dir)
    live_function_count = None
    live_function_names: list[str] = []
    live_missing_scene_names: list[str] = []
    trigger_results = list(live_trigger_results or [])
    live_observed_matches = None
    live_warnings: list[str] = []
    if live_functions is not None:
        live_function_names = [
            str(item.get("name", "")) for item in live_functions if item.get("name")
        ]
        live_function_count = len(live_function_names)
        scene_names = [scene.get("Name") or "" for scene in scenes]
        live_missing_scene_names = [
            scene_name
            for scene_name in scene_names
            if scene_name not in live_function_names
        ]
        if live_function_count < len(scenes):
            live_warnings.append(
                "Live QLC+ function count is lower than exported Scene function count."
            )
    if live_trigger_results is not None:
        if trigger_results:
            live_observed_matches = all(
                item.get("observed_matches") is True for item in trigger_results
            )
        else:
            live_observed_matches = False
            live_warnings.append("Live QLC+ trigger proof produced no results.")
        for item in trigger_results:
            if item.get("observed_matches") is not True:
                live_warnings.append(
                    "Live QLC+ function trigger evidence did not match expectation."
                )
                break

    return QlcWorkspaceValidationReport(
        path=str(workspace_path),
        fixture_count=len(fixtures),
        scene_function_count=len(scenes),
        virtual_console_button_count=len(buttons),
        linked_button_count=linked_count,
        missing_function_links=missing_links,
        missing_fixture_definitions=missing_fixture_definitions,
        live_function_count=live_function_count,
        live_function_names=live_function_names,
        live_missing_scene_names=live_missing_scene_names,
        live_trigger_results=trigger_results,
        live_observed_matches=live_observed_matches,
        live_warnings=live_warnings,
        warnings=warnings,
    )


def qlc_scene_functions_from_workspace(
    workspace_path: str | Path,
) -> list[dict[str, str | int]]:
    """Return exported QLC+ Scene IDs and names from a workspace."""
    root = ET.parse(workspace_path).getroot()
    scenes: list[dict[str, str | int]] = []
    for function in _children(root, "Function"):
        if function.get("Type") != "Scene":
            continue
        raw_id = function.get("ID")
        if raw_id is None:
            continue
        try:
            function_id: str | int = int(raw_id)
        except ValueError:
            function_id = raw_id
        scenes.append(
            {
                "id": function_id,
                "name": function.get("Name") or "",
            }
        )
    return scenes


def copy_qxf_files_for_workspace(
    qxf_results: list[Any],
    workspace_path: str | Path,
) -> list[QxfWorkspaceCopyResult]:
    """Copy generated QXF files beside a QXW for direct QLC+ opening."""
    workspace_dir = Path(workspace_path).parent
    workspace_dir.mkdir(parents=True, exist_ok=True)
    copied: list[QxfWorkspaceCopyResult] = []
    for result in qxf_results:
        source = Path(result.path)
        destination = workspace_dir / source.name
        if source.resolve() == destination.resolve():
            copied.append(
                QxfWorkspaceCopyResult(
                    source=source, destination=destination, copied=False
                )
            )
            continue
        shutil.copy2(source, destination)
        copied.append(
            QxfWorkspaceCopyResult(source=source, destination=destination, copied=True)
        )
    return copied


def build_qlc_scene_function(
    *,
    function_id: int,
    name: str,
    fixture_values: dict[int, list[int]],
    cue_number: int | None = None,
    cue_label: str | None = None,
    fade_ms: int = 0,
    duration_ms: int = 0,
) -> QlcSceneFunction:
    """Convenience constructor for a QLC+ Scene function."""
    return QlcSceneFunction(
        function_id=function_id,
        name=name,
        fixture_values={
            fixture_id: [max(0, min(255, int(value))) for value in values]
            for fixture_id, values in fixture_values.items()
        },
        cue_number=cue_number,
        cue_label=cue_label,
        fade_ms=max(0, int(fade_ms)),
        duration_ms=max(0, int(duration_ms)),
    )


def build_qlc_scene_from_rendered_cue(
    rendered: RenderedCue,
    patches: list[QlcFixturePatch],
    *,
    function_id: int,
) -> QlcSceneFunction:
    """Build one QLC+ Scene function from a rendered RayFlow cue."""
    frames_by_universe = {frame.universe: frame.channels for frame in rendered.frames}
    fixture_values: dict[int, list[int]] = {}
    for patch in patches:
        channels = frames_by_universe.get(patch.universe, {})
        values = [
            channels.get(address, 0)
            for address in range(patch.address, patch.address + patch.channel_count)
        ]
        fixture_values[patch.fixture_id] = values

    label = rendered.cue_label or f"Cue {rendered.cue_number}"
    return build_qlc_scene_function(
        function_id=function_id,
        name=f"{rendered.cue_number:g} {label}",
        fixture_values=fixture_values,
        cue_number=rendered.cue_number,
        cue_label=rendered.cue_label,
    )


def build_qlc_patch(
    *,
    fixture_id: int,
    name: str,
    manufacturer: str,
    model: str,
    mode: str,
    universe: int,
    address: int,
    channel_count: int,
) -> QlcFixturePatch:
    """Convenience constructor for a QlcFixturePatch."""
    return QlcFixturePatch(
        fixture_id=fixture_id,
        name=name,
        manufacturer=manufacturer,
        model=model,
        mode=mode,
        universe=universe,
        address=address,
        channel_count=channel_count,
    )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _add_creator(root: ET.Element, *, author: str) -> None:
    creator = ET.SubElement(root, "Creator")
    ET.SubElement(creator, "Name").text = "Q Light Controller Plus"
    ET.SubElement(creator, "Version").text = QXW_VERSION
    ET.SubElement(creator, "Author").text = author


def _add_input_output_map(engine: ET.Element, patches: list[QlcFixturePatch]) -> None:
    """Add the InputOutputMap section with universe entries.

    QLC+ requires at least the universes that are in use to be declared here,
    otherwise imported fixtures may not map correctly.
    """
    universes_used = sorted({p.qlc_universe for p in patches})
    io_map = ET.SubElement(engine, "InputOutputMap")

    for uni_idx in universes_used:
        universe = ET.SubElement(io_map, "Universe")
        universe.set("ID", str(uni_idx))
        universe.set("Name", f"Universe {uni_idx + 1}")


def _add_fixture(engine: ET.Element, patch: QlcFixturePatch) -> None:
    """Add a single Fixture element to the Engine block."""
    fixture = ET.SubElement(engine, "Fixture")
    ET.SubElement(fixture, "Manufacturer").text = patch.manufacturer
    ET.SubElement(fixture, "Model").text = patch.model
    ET.SubElement(fixture, "Mode").text = patch.mode
    ET.SubElement(fixture, "Name").text = patch.name
    ET.SubElement(fixture, "Universe").text = str(patch.qlc_universe)
    ET.SubElement(fixture, "Address").text = str(patch.qlc_address)
    ET.SubElement(fixture, "ID").text = str(patch.fixture_id)
    ET.SubElement(fixture, "Channels").text = str(patch.channel_count)


def _add_scene_function(engine: ET.Element, function: QlcSceneFunction) -> None:
    """Add a QLC+ Scene function to the Engine block."""
    scene = ET.SubElement(engine, "Function")
    scene.set("ID", str(function.function_id))
    scene.set("Type", "Scene")
    scene.set("Name", function.name)

    speed = ET.SubElement(scene, "Speed")
    speed.set("FadeIn", str(function.fade_ms))
    speed.set("FadeOut", str(function.fade_ms))
    speed.set("Duration", str(function.duration_ms))

    for fixture_id, values in sorted(function.fixture_values.items()):
        fixture_val = ET.SubElement(scene, "FixtureVal")
        fixture_val.set("ID", str(fixture_id))
        fixture_val.text = ",".join(
            str(max(0, min(255, int(value)))) for value in values
        )


def _add_virtual_console(
    root: ET.Element,
    functions: list[QlcSceneFunction],
) -> None:
    """Add a simple QLC+ Virtual Console button grid for exported scenes."""
    virtual_console = ET.SubElement(root, "VirtualConsole")
    virtual_console.set("Width", "800")
    virtual_console.set("Height", "480")
    virtual_console.set("Properties", "0")

    frame = ET.SubElement(virtual_console, "Frame")
    frame.set("Caption", "RayFlow Scenes")
    frame.set("ID", "0")
    frame.set("X", "0")
    frame.set("Y", "0")
    frame.set("Width", "800")
    frame.set("Height", "480")

    button_width = 150
    button_height = 48
    gap = 10
    columns = 4
    for index, function in enumerate(functions):
        row = index // columns
        column = index % columns
        button = ET.SubElement(frame, "Button")
        button.set("Caption", function.name)
        button.set("ID", str(index + 1))
        button.set("X", str(gap + column * (button_width + gap)))
        button.set("Y", str(gap + row * (button_height + gap)))
        button.set("Width", str(button_width))
        button.set("Height", str(button_height))
        button.set("Action", "Toggle")
        ET.SubElement(button, "Function").text = str(function.function_id)


def _children(root: ET.Element, tag: str) -> list[ET.Element]:
    return [element for element in root.iter() if _local_name(element.tag) == tag]


def _child_text(element: ET.Element, tag: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == tag:
            return child.text
    return None


def _local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag


def _missing_qxf_definitions(
    fixtures: list[ET.Element],
    qxf_dir: str | Path | None,
) -> list[str]:
    if qxf_dir is None:
        return []
    qxf_path = Path(qxf_dir)
    existing = (
        {path.name for path in qxf_path.glob("*.qxf")} if qxf_path.exists() else set()
    )
    missing: list[str] = []
    for fixture in fixtures:
        manufacturer = _child_text(fixture, "Manufacturer") or "Unknown"
        model = _child_text(fixture, "Model") or "Unknown"
        expected = f"{_filename_part(manufacturer)}-{_filename_part(model)}.qxf"
        if expected not in existing:
            missing.append(expected)
    return sorted(set(missing))


def _filename_part(value: str) -> str:
    import re

    value = re.sub(r"[^A-Za-z0-9]+", "-", value.strip())
    return value.strip("-") or "Fixture"


def _validation_summary(report: QlcWorkspaceValidationReport) -> str:
    if report.ready:
        return (
            "QXW has fixtures, Scene functions, and Virtual Console buttons with "
            "valid function links."
        )
    issues = (
        len(report.missing_function_links)
        + len(report.missing_fixture_definitions)
        + len(report.warnings)
    )
    return f"QXW validation found {issues} issue(s)."
