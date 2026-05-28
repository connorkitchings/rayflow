"""Generate simple 2D rig plot artifacts from RayFlow rig coordinates."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path

from rayflow.design.models import FixtureSlot, Rig


@dataclass(frozen=True)
class RigPlotArtifact:
    """Generated rig plot artifact paths."""

    top_svg: Path
    front_svg: Path
    manifest: Path

    def as_dict(self) -> dict[str, str]:
        return {
            "top_svg": str(self.top_svg),
            "front_svg": str(self.front_svg),
            "manifest": str(self.manifest),
        }


@dataclass(frozen=True)
class RigFrontVisualizationArtifact:
    """Generated front-view visualizer artifact path."""

    front_svg: Path

    def as_dict(self) -> dict[str, str]:
        return {"front_svg": str(self.front_svg)}


def write_rig_plot_artifacts(rig: Rig, output_dir: str | Path) -> RigPlotArtifact:
    """Write top/front SVG plots and a Markdown summary for a rig."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    slug = _slugify(rig.name)
    top_svg = target / f"{slug}_top.svg"
    front_svg = target / f"{slug}_front.svg"
    manifest = target / f"{slug}_plots.md"

    top_svg.write_text(_render_svg(rig, view="top"), encoding="utf-8")
    front_svg.write_text(_render_svg(rig, view="front"), encoding="utf-8")
    manifest.write_text(_render_manifest(rig, top_svg, front_svg), encoding="utf-8")

    return RigPlotArtifact(top_svg=top_svg, front_svg=front_svg, manifest=manifest)


def write_front_visualization(
    rig: Rig,
    output_dir: str | Path,
    *,
    look: str = "highlight",
) -> RigFrontVisualizationArtifact:
    """Write a simple front-view lights-on SVG visualizer for a rig."""
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    slug = _slugify(rig.name)
    front_svg = target / f"{slug}_front_lights_on.svg"
    front_svg.write_text(_render_front_visualizer_svg(rig, look=look), encoding="utf-8")
    return RigFrontVisualizationArtifact(front_svg=front_svg)


def _slugify(value: str) -> str:
    chars = [char.lower() if char.isalnum() else "-" for char in value.strip()]
    slug = "".join(chars).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "rig"


def _fixture_role(slot: FixtureSlot) -> str:
    text = f"{slot.label} {slot.fixture_name}".lower()
    if "par" in text or "front" in text or "side" in text:
        return "wash"
    if "blade" in text or "texture" in text or "gobo" in text:
        return "texture"
    if "spiider" in text or "back" in text:
        return "back"
    return "other"


def _role_color(role: str) -> str:
    return {
        "wash": "#f59e0b",
        "back": "#2563eb",
        "texture": "#7c3aed",
        "other": "#64748b",
    }[role]


def _role_label(role: str) -> str:
    return {
        "wash": "front/side wash",
        "back": "back wash",
        "texture": "texture/profile",
        "other": "other",
    }[role]


def _project(slot: FixtureSlot, view: str) -> tuple[float, float]:
    position = slot.position
    if view == "top":
        return position.x, position.y
    if view == "front":
        return position.x, position.z
    raise ValueError(f"unknown plot view: {view}")


def _axis_labels(view: str) -> tuple[str, str, str]:
    if view == "top":
        return ("Top Plot", "X: stage left/right", "Y: downstage/upstage")
    if view == "front":
        return ("Front Plot", "X: stage left/right", "Z: trim height")
    raise ValueError(f"unknown plot view: {view}")


def _bounds(rig: Rig, view: str) -> tuple[float, float, float, float]:
    width, depth, height = rig.venue.dimensions
    if view == "top":
        return (-width / 2, width / 2, 0.0, depth)
    if view == "front":
        return (-width / 2, width / 2, 0.0, height)
    raise ValueError(f"unknown plot view: {view}")


def _scale(
    value: float,
    source_min: float,
    source_max: float,
    target_min: float,
    target_max: float,
) -> float:
    if source_max == source_min:
        return (target_min + target_max) / 2
    ratio = (value - source_min) / (source_max - source_min)
    return target_min + ratio * (target_max - target_min)


def _svg_tag(
    name: str,
    attrs: dict[str, str],
    content: str = "",
    *,
    indent: int = 0,
    close: bool = True,
    self_close: bool = False,
) -> str:
    prefix = " " * indent
    attr_text = " ".join(f'{key}="{escape(value)}"' for key, value in attrs.items())
    if self_close:
        return f"{prefix}<{name} {attr_text}/>"
    if not close:
        return f"{prefix}<{name} {attr_text}>"
    return f"{prefix}<{name} {attr_text}>{content}</{name}>"


def _render_svg(rig: Rig, view: str) -> str:
    title, x_label, y_label = _axis_labels(view)
    min_x, max_x, min_y, max_y = _bounds(rig, view)
    width = 960
    height = 620
    margin_left = 84
    margin_right = 220
    margin_top = 82
    margin_bottom = 82
    plot_left = margin_left
    plot_right = width - margin_right
    plot_top = margin_top
    plot_bottom = height - margin_bottom

    def sx(value: float) -> float:
        return _scale(value, min_x, max_x, plot_left, plot_right)

    def sy(value: float) -> float:
        return _scale(value, min_y, max_y, plot_bottom, plot_top)

    fixture_marks = []
    for index, slot in enumerate(rig.fixtures, start=1):
        x_value, y_value = _project(slot, view)
        x = sx(x_value)
        y = sy(y_value)
        role = _fixture_role(slot)
        color = _role_color(role)
        label = escape(slot.label)
        fixture_marks.append(
            f'<g><circle cx="{x:.1f}" cy="{y:.1f}" r="10" fill="{color}" '
            f'stroke="#111827" stroke-width="1.5"><title>{label}</title></circle>'
            f'<text x="{x:.1f}" y="{y + 4:.1f}" text-anchor="middle" '
            f'font-size="9" fill="#ffffff">{index}</text></g>'
        )

    x_ticks = _ticks(min_x, max_x)
    y_ticks = _ticks(min_y, max_y)
    x_tick_marks = "\n".join(
        f'<g><line x1="{sx(value):.1f}" y1="{plot_top}" x2="{sx(value):.1f}" '
        f'y2="{plot_bottom}" stroke="#d1d5db" stroke-width="1"/>'
        f'<text x="{sx(value):.1f}" y="{plot_bottom + 24}" '
        f'text-anchor="middle" font-size="12" fill="#374151">{value:g}</text></g>'
        for value in x_ticks
    )
    y_tick_marks = "\n".join(
        f'<g><line x1="{plot_left}" y1="{sy(value):.1f}" x2="{plot_right}" '
        f'y2="{sy(value):.1f}" stroke="#d1d5db" stroke-width="1"/>'
        f'<text x="{plot_left - 16}" y="{sy(value) + 4:.1f}" '
        f'text-anchor="end" font-size="12" fill="#374151">{value:g}</text></g>'
        for value in y_ticks
    )
    legend = _render_legend(rig, width - margin_right + 36, plot_top)
    fixture_table = _render_fixture_table(
        rig, width - margin_right + 36, plot_top + 150
    )
    subtitle = (
        f"{escape(rig.venue.name)} | {len(rig.fixtures)} fixtures | "
        f"dimensions {rig.venue.width:g}m W x {rig.venue.depth:g}m D x "
        f"{rig.venue.height:g}m H"
    )
    x_axis_center = (plot_left + plot_right) / 2
    y_axis_center = (plot_top + plot_bottom) / 2

    lines = [
        _svg_tag(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": str(width),
                "height": str(height),
                "viewBox": f"0 0 {width} {height}",
                "role": "img",
                "aria-labelledby": "title desc",
            },
            close=False,
        ),
        f'  <title id="title">{escape(rig.name)} - {title}</title>',
        (
            f'  <desc id="desc">2D {title.lower()} showing fixture positions '
            "and roles.</desc>"
        ),
        '  <rect width="100%" height="100%" fill="#f8fafc"/>',
        _svg_tag(
            "text",
            {
                "x": str(margin_left),
                "y": "36",
                "font-size": "24",
                "font-weight": "700",
                "fill": "#111827",
            },
            f"{escape(rig.name)} - {title}",
            indent=2,
        ),
        _svg_tag(
            "text",
            {
                "x": str(margin_left),
                "y": "60",
                "font-size": "13",
                "fill": "#4b5563",
            },
            subtitle,
            indent=2,
        ),
        _svg_tag(
            "rect",
            {
                "x": str(plot_left),
                "y": str(plot_top),
                "width": str(plot_right - plot_left),
                "height": str(plot_bottom - plot_top),
                "fill": "#ffffff",
                "stroke": "#111827",
                "stroke-width": "2",
            },
            indent=2,
            self_close=True,
        ),
        x_tick_marks,
        y_tick_marks,
        _svg_tag(
            "text",
            {
                "x": f"{x_axis_center:.1f}",
                "y": str(height - 24),
                "text-anchor": "middle",
                "font-size": "14",
                "fill": "#111827",
            },
            x_label,
            indent=2,
        ),
        _svg_tag(
            "text",
            {
                "x": "22",
                "y": f"{y_axis_center:.1f}",
                "text-anchor": "middle",
                "font-size": "14",
                "fill": "#111827",
                "transform": f"rotate(-90 22 {y_axis_center:.1f})",
            },
            y_label,
            indent=2,
        ),
        _svg_tag(
            "text",
            {
                "x": str(plot_left),
                "y": str(plot_top - 12),
                "font-size": "12",
                "fill": "#6b7280",
            },
            "stage left",
            indent=2,
        ),
        _svg_tag(
            "text",
            {
                "x": str(plot_right),
                "y": str(plot_top - 12),
                "text-anchor": "end",
                "font-size": "12",
                "fill": "#6b7280",
            },
            "stage right",
            indent=2,
        ),
        "".join(fixture_marks),
        legend,
        fixture_table,
        "</svg>",
        "",
    ]
    return "\n".join(lines)


def _render_front_visualizer_svg(rig: Rig, *, look: str) -> str:
    min_x, max_x, min_z, max_z = _bounds(rig, "front")
    width = 1280
    height = 760
    plot_left = 90
    plot_right = width - 90
    plot_top = 80
    plot_bottom = height - 92
    stage_y = plot_bottom
    band_floor = plot_bottom - 26

    def sx(value: float) -> float:
        return _scale(value, min_x, max_x, plot_left, plot_right)

    def sz(value: float) -> float:
        return _scale(value, min_z, max_z, plot_bottom, plot_top)

    defs = """
  <defs>
    <filter id="beamGlow" x="-35%" y="-35%" width="170%" height="170%">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <radialGradient id="fixtureGlow">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="1"/>
      <stop offset="70%" stop-color="#fef3c7" stop-opacity="0.72"/>
      <stop offset="100%" stop-color="#fef3c7" stop-opacity="0"/>
    </radialGradient>
  </defs>"""
    beams = []
    fixture_marks = []
    for index, slot in enumerate(rig.fixtures, start=1):
        x = sx(slot.position.x)
        z = sz(slot.position.z)
        role = _fixture_role(slot)
        target_x, target_y, spread, color, opacity = _visual_beam_for_slot(
            slot, index, sx, stage_y, band_floor, look
        )
        points = [
            f"{x:.1f},{z:.1f}",
            f"{target_x - spread:.1f},{target_y:.1f}",
            f"{target_x + spread:.1f},{target_y:.1f}",
        ]
        beams.append(
            f'<polygon points="{" ".join(points)}" fill="{color}" '
            f'opacity="{opacity}" filter="url(#beamGlow)"/>'
        )
        beams.append(
            f'<line x1="{x:.1f}" y1="{z:.1f}" x2="{target_x:.1f}" '
            f'y2="{target_y:.1f}" stroke="#ffffff" stroke-width="2.5" '
            'opacity="0.75"/>'
        )
        fixture_marks.append(
            f'<g><circle cx="{x:.1f}" cy="{z:.1f}" r="13" '
            'fill="url(#fixtureGlow)"/>'
            f'<circle cx="{x:.1f}" cy="{z:.1f}" r="6" fill="#ffffff" '
            f'stroke="{_role_color(role)}" stroke-width="2"/>'
            f'<text x="{x:.1f}" y="{z - 16:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#e5e7eb">{index}</text></g>'
        )

    performer_marks = _render_performers(sx, band_floor)
    rig_title = escape(rig.name)
    subtitle = (
        f"{escape(rig.venue.name)} | front view | all fixtures in {escape(look)} look"
    )
    lines = [
        _svg_tag(
            "svg",
            {
                "xmlns": "http://www.w3.org/2000/svg",
                "width": str(width),
                "height": str(height),
                "viewBox": f"0 0 {width} {height}",
                "role": "img",
                "aria-labelledby": "title desc",
            },
            close=False,
        ),
        f'  <title id="title">{rig_title} - Front Lights On</title>',
        '  <desc id="desc">Front-view visualizer with lights on.</desc>',
        defs,
        '  <rect width="100%" height="100%" fill="#020617"/>',
        _svg_tag(
            "rect",
            {
                "x": str(plot_left),
                "y": str(plot_top),
                "width": str(plot_right - plot_left),
                "height": str(plot_bottom - plot_top),
                "fill": "#08111f",
                "stroke": "#334155",
                "stroke-width": "2",
            },
            indent=2,
            self_close=True,
        ),
        _svg_tag(
            "text",
            {
                "x": str(plot_left),
                "y": "38",
                "font-size": "26",
                "font-weight": "700",
                "fill": "#f8fafc",
            },
            f"{rig_title} - Front Lights On",
            indent=2,
        ),
        _svg_tag(
            "text",
            {
                "x": str(plot_left),
                "y": "62",
                "font-size": "14",
                "fill": "#cbd5e1",
            },
            subtitle,
            indent=2,
        ),
        _svg_tag(
            "line",
            {
                "x1": str(plot_left),
                "y1": str(stage_y),
                "x2": str(plot_right),
                "y2": str(stage_y),
                "stroke": "#64748b",
                "stroke-width": "3",
            },
            indent=2,
            self_close=True,
        ),
        _svg_tag(
            "rect",
            {
                "x": str(plot_left),
                "y": str(stage_y),
                "width": str(plot_right - plot_left),
                "height": "38",
                "fill": "#111827",
            },
            indent=2,
            self_close=True,
        ),
        "".join(beams),
        performer_marks,
        "".join(fixture_marks),
        _svg_tag(
            "text",
            {
                "x": str(plot_left),
                "y": str(height - 24),
                "font-size": "13",
                "fill": "#94a3b8",
            },
            "White/highlight visualization for spatial readiness only.",
            indent=2,
        ),
        "</svg>",
        "",
    ]
    return "\n".join(lines)


def _visual_beam_for_slot(
    slot: FixtureSlot,
    index: int,
    sx,
    stage_y: float,
    band_floor: float,
    look: str,
) -> tuple[float, float, float, str, str]:
    role = _fixture_role(slot)
    if look == "white":
        color = "#f8fafc"
    elif role == "wash":
        color = "#fef3c7"
    elif role == "back":
        color = "#bfdbfe"
    else:
        color = "#f5f3ff"
    if role == "wash":
        target_x = sx(slot.position.x * 0.78)
        return target_x, band_floor, 58.0, color, "0.32"
    if role == "back":
        target_x = sx((-1) ** index * 1.2 + slot.position.x * 0.22)
        return target_x, band_floor - 180, 74.0, color, "0.42"
    target_x = sx(slot.position.x * -0.34)
    return target_x, band_floor - 210, 42.0, color, "0.5"


def _render_performers(sx, floor_y: float) -> str:
    performers = [
        (-5.4, "guitar"),
        (-2.0, "bass"),
        (0.0, "drums"),
        (2.2, "lead"),
        (5.2, "keys"),
    ]
    marks = []
    for x_value, label in performers:
        x = sx(x_value)
        marks.append(
            f'<g><circle cx="{x:.1f}" cy="{floor_y - 54:.1f}" r="12" '
            'fill="#0f172a" stroke="#94a3b8" stroke-width="1.5"/>'
            f'<rect x="{x - 9:.1f}" y="{floor_y - 42:.1f}" width="18" '
            'height="38" rx="7" fill="#0f172a" stroke="#94a3b8" '
            'stroke-width="1.5"/>'
            f'<text x="{x:.1f}" y="{floor_y + 18:.1f}" text-anchor="middle" '
            f'font-size="11" fill="#cbd5e1">{label}</text></g>'
        )
    return "".join(marks)


def _ticks(min_value: float, max_value: float) -> list[float]:
    span = max_value - min_value
    step = 2.0 if span <= 16 else 5.0
    first = int(min_value // step) * step
    values: list[float] = []
    current = first
    while current <= max_value:
        if current >= min_value:
            values.append(float(current))
        current += step
    if min_value not in values:
        values.insert(0, min_value)
    if max_value not in values:
        values.append(max_value)
    return values


def _render_legend(rig: Rig, x: float, y: float) -> str:
    roles = []
    seen = set()
    for slot in rig.fixtures:
        role = _fixture_role(slot)
        if role not in seen:
            roles.append(role)
            seen.add(role)
    rows = []
    for offset, role in enumerate(roles):
        row_y = y + 32 + offset * 24
        rows.append(
            f'<circle cx="{x}" cy="{row_y}" r="7" fill="{_role_color(role)}" '
            f'stroke="#111827" stroke-width="1"/>'
            f'<text x="{x + 16}" y="{row_y + 4}" font-size="12" '
            f'fill="#111827">{escape(_role_label(role))}</text>'
        )
    return (
        f'<text x="{x}" y="{y}" font-size="15" font-weight="700" '
        f'fill="#111827">Legend</text>{"".join(rows)}'
    )


def _render_fixture_table(rig: Rig, x: float, y: float) -> str:
    rows = []
    for index, slot in enumerate(rig.fixtures, start=1):
        row_y = y + index * 21
        text = f"{index}. {slot.label} (U{slot.universe}, A{slot.start_address})"
        rows.append(
            f'<text x="{x}" y="{row_y}" font-size="10.5" '
            f'fill="#374151">{escape(text)}</text>'
        )
    return (
        f'<text x="{x}" y="{y}" font-size="15" font-weight="700" '
        f'fill="#111827">Fixture Index</text>{"".join(rows)}'
    )


def _render_manifest(rig: Rig, top_svg: Path, front_svg: Path) -> str:
    fixture_rows = "\n".join(
        "| "
        + " | ".join(
            [
                str(index),
                slot.label,
                slot.fixture_name,
                _role_label(_fixture_role(slot)),
                f"({slot.position.x:g}, {slot.position.y:g}, {slot.position.z:g})",
                f"U{slot.universe} A{slot.start_address}",
            ]
        )
        + " |"
        for index, slot in enumerate(rig.fixtures, start=1)
    )
    dimensions = (
        f"{rig.venue.width:g}m wide x {rig.venue.depth:g}m deep x "
        f"{rig.venue.height:g}m high"
    )
    return f"""# {rig.name} - Rig Plots

Generated context artifacts for reviewing fixture placement before cue authoring.

- Top plot: [{top_svg.name}]({top_svg.name})
- Front plot: [{front_svg.name}]({front_svg.name})
- Venue: {rig.venue.name}
- Dimensions: {dimensions}

## Fixture Index

| # | Label | Fixture | Role | Position x/y/z | Patch |
|---|-------|---------|------|----------------|-------|
{fixture_rows}
"""
