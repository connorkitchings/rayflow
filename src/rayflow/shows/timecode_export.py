"""MA3 Timecode XML export.

Generates a grandMA3 2.3.2.0-compatible GMA3 Timecode XML document from a
RayFlow Show.  Each cue in the show maps to one timecode event that fires a
"Go+" on the target sequence at the cue's timestamp.

.. warning::
    The event schema is inferred from the MA3 2.3.2.0 Timecode track skeleton
    captured on 2026-05-19 plus MA3 documentation patterns.  The generated XML
    **must be validated against a running grandMA3 onPC instance** before the
    timecode blocker is considered fully resolved.  See:
    data/ma3_exports/samples/rayflow_minimal_timecode_track_skeleton_2_3_2.xml
"""

from __future__ import annotations

import uuid
from xml.etree.ElementTree import (
    Element,
    SubElement,
    indent,
    tostring,
)

from rayflow.shows.models import Cue, Show

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def export_timecode_xml(
    show: Show,
    *,
    sequence: int = 1,
    frame_rate: float = 30.0,
) -> str:
    """Generate a GMA3-format Timecode XML string for *show*.

    Parameters
    ----------
    show:
        The RayFlow show whose cues drive the timecode events.
    sequence:
        The MA3 sequence (executor) number that receives Go+ events.
        Defaults to 1.
    frame_rate:
        Frames per second used for the timecode display.  Defaults to 30.

    Returns
    -------
    str
        A UTF-8 XML string ready to write to a ``.xml`` file and import into
        grandMA3 via *Import → Timecode Pool*.
    """
    if sequence <= 0:
        raise ValueError(f"sequence must be > 0, got {sequence}")
    if frame_rate <= 0:
        raise ValueError(f"frame_rate must be > 0, got {frame_rate}")

    # Sort cues by timestamp so the XML is ordered correctly.
    cues: list[Cue] = sorted(show.cues, key=lambda c: c.timestamp)

    root = _build_root(show, cues, sequence=sequence, frame_rate=frame_rate)
    indent(root, space="    ")
    xml_bytes = tostring(root, encoding="unicode", xml_declaration=False)
    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    return header + xml_bytes + "\n"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _new_guid() -> str:
    """Return a GUID in MA3's space-separated hex format.

    MA3 stores GUIDs as 16 uppercase hex bytes separated by single spaces,
    e.g. ``FE CB 11 D4 C1 7F 73 5B BC 0F 4B 8A 49 AD 38 46``.
    """
    raw = uuid.uuid4().bytes
    return " ".join(f"{b:02X}" for b in raw)


def _seconds_to_tc(seconds: float) -> str:
    """Convert a float seconds value to MA3 HH:MM:SS.mmm format.

    Examples
    --------
    >>> _seconds_to_tc(0.0)
    '00:00:00.000'
    >>> _seconds_to_tc(90.5)
    '00:01:30.500'
    >>> _seconds_to_tc(3661.25)
    '01:01:01.250'
    """
    if seconds < 0:
        raise ValueError(f"seconds must be >= 0, got {seconds}")
    total_ms = round(seconds * 1000)
    ms = total_ms % 1000
    total_s = total_ms // 1000
    secs = total_s % 60
    total_m = total_s // 60
    mins = total_m % 60
    hours = total_m // 60
    return f"{hours:02d}:{mins:02d}:{secs:02d}.{ms:03d}"


def _build_root(
    show: Show,
    cues: list[Cue],
    *,
    sequence: int,
    frame_rate: float,
) -> Element:
    """Build the full GMA3 XML element tree."""
    root = Element("GMA3", {"DataVersion": "2.3.2.0"})

    # Duration: use song duration; MA3 accepts decimal seconds.
    duration = f"{show.song.duration:.2f}"
    name = show.name[:64]  # MA3 pool name length limit (observed: ~64 chars)

    timecode = SubElement(
        root,
        "Timecode",
        {
            "Name": name,
            "Guid": _new_guid(),
            "Duration": duration,
            "LoopCount": "0",
            "TCSlot": "-1",
            "AutoStop": "No",
            "SwitchOff": "Keep Playbacks",
            "TimeDisplayFormat": "Default",
            "FrameReadout": "Default",
        },
    )

    track_group = SubElement(timecode, "TrackGroup", {"Play": "", "Rec": ""})

    # Marker track — always present (empty in skeleton).
    SubElement(
        track_group,
        "MarkerTrack",
        {"Name": "Marker", "Guid": _new_guid()},
    )

    # Cue-trigger track — one Track per sequence target.
    # Based on MA3 pattern: a single Track holds all events for one executor.
    _build_cue_track(track_group, cues, sequence=sequence, duration=show.song.duration)

    return root


def _build_cue_track(
    track_group: Element,
    cues: list[Cue],
    *,
    sequence: int,
    duration: float,
) -> None:
    """Add a Track element with one Event per cue."""
    track = SubElement(
        track_group,
        "Track",
        {
            "Guid": _new_guid(),
            "Play": "",
            "Rec": "",
        },
    )

    # A TimeRange wraps the full song so all events are active.
    time_range = SubElement(
        track,
        "TimeRange",
        {
            "Guid": _new_guid(),
            # "Duration" is the length of this range; "To End" covers the song.
            "Duration": "To End",
            "Play": "",
            "Rec": "",
        },
    )

    # One Event per cue.  MA3 event attributes (inferred from MA3 2.3 docs):
    #   Time     — timecode position in HH:MM:SS.mmm
    #   Action   — "Go+" fires the next cue in the sequence
    #   Executor — executor number (= sequence number in default page layout)
    #
    # NOTE: This schema is inferred.  Validate by importing into MA3 and
    # checking that the Timecode Viewer shows events at the correct times.
    for cue in cues:
        SubElement(
            time_range,
            "Event",
            {
                "Guid": _new_guid(),
                "Time": _seconds_to_tc(cue.timestamp),
                "Action": "Go+",
                "Executor": str(sequence),
                "CueName": cue.label,
            },
        )
