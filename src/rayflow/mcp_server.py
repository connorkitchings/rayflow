from mcp.server.fastmcp import FastMCP
from rayflow.cli._paths import show_dir_path, show_path
from rayflow.cli.rig import _rig_dir_path, _rig_path
from rayflow.design.serializers import load_rig, load_show

mcp = FastMCP("RayFlow")


@mcp.tool()
def list_shows() -> list[str]:
    """List all available show names in the configured show directory."""
    dir_path = show_dir_path("data/shows")
    shows = []
    if dir_path.exists():
        for file in dir_path.glob("*.json"):
            shows.append(file.stem)
    return sorted(shows)


@mcp.tool()
def get_show_context(show_name: str) -> dict:
    """Get the full JSON context of a given show."""
    dir_path = show_dir_path("data/shows")
    path = show_path(show_name, dir_path)
    if not path.exists():
        return {"error": f"Show not found: {show_name}"}
    return load_show(path).as_dict()


@mcp.tool()
def list_rigs() -> list[str]:
    """List all available rig names in the configured rig directory."""
    dir_path = _rig_dir_path("data/rigs")
    rigs = []
    if dir_path.exists():
        for file in dir_path.glob("*.json"):
            rigs.append(file.stem)
    return sorted(rigs)


@mcp.tool()
def get_rig_context(rig_name: str) -> dict:
    """Get the full JSON context of a given rig."""
    dir_path = _rig_dir_path("data/rigs")
    path = _rig_path(rig_name, dir_path)
    if not path.exists():
        return {"error": f"Rig not found: {rig_name}"}
    return load_rig(path).as_dict()


@mcp.tool()
def generate_cues(
    show_name: str,
    section_name: str,
    preset: str,
    style: str,
    cue_count: int,
    step_duration: float,
    vibe: str | None = None,
) -> str:
    """
    Generate and append a sequence of cues to a show section based on a preset.
    Returns a success message or an error.
    """
    from rayflow.design.cue_generator import generate_cues_for_section
    from rayflow.design.serializers import save_show

    dir_path = show_dir_path("data/shows")
    path = show_path(show_name, dir_path)
    if not path.exists():
        return f"Error: Show not found: {show_name}"

    show = load_show(path)
    section = show.get_section(section_name)
    if not section:
        return f"Error: Section not found: {section_name}"

    cues = generate_cues_for_section(
        show,
        section.name,
        preset=preset,
        count=cue_count,
        spacing=step_duration,
        # ignore style/vibe for now or pass as attributes if implemented
    )

    section.cues.extend(cues)
    save_show(show, path)
    return f"Successfully generated {len(cues)} cues in section '{section_name}'."
