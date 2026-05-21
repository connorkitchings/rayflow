"""MA3 Timecode XML export.

Generates a grandMA3 2.3.2.0-compatible GMA3 Timecode XML document from a
RayFlow Show.  Each cue in the show maps to one timecode event that performs
a ``Goto`` on the target sequence at the cue's timestamp.

.. warning::
    The event schema is based on local grandMA3 onPC 2.3.2.0 exports captured
    from ``~/MALightingTechnology/gma3_library/datapools/timecodes/findme2.xml``.
    The generated XML still needs import/playback validation in MA3 before the
    Phase 7 timecode milestone is considered fully closed.
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
        Reserved for future frame-display support.  MA3 stores event times as
        decimal seconds in exported Timecode XML.

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


def _build_root(
    show: Show,
    cues: list[Cue],
    *,
    sequence: int,
    frame_rate: float,
) -> Element:
    """Build the full GMA3 XML element tree."""
    root = Element("GMA3", {"DataVersion": "2.3.2.0"})

    # Duration and event times are exported by MA3 as decimal seconds.
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

    _build_cue_track(track_group, cues, sequence=sequence, duration=show.song.duration)

    return root


def _build_cue_track(
    track_group: Element,
    cues: list[Cue],
    *,
    sequence: int,
    duration: float,
) -> None:
    """Add a Sequence-targeted Track element with one CmdEvent per cue."""
    track = SubElement(
        track_group,
        "Track",
        {
            "Guid": _new_guid(),
            "Target": f"ShowData.DataPools.Default.Sequences.{sequence}",
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

    cmd_sub_track = SubElement(time_range, "CmdSubTrack")

    # Captured MA3 event exports use CmdEvent + RealtimeCmd records with
    # decimal-second Time values and cue destinations encoded in thousandths.
    for cue in cues:
        cmd_event = SubElement(
            cmd_sub_track,
            "CmdEvent",
            {
                "Name": "Goto",
                "Time": f"{cue.timestamp:.3f}",
                "CueDestination": f"Cue {cue.number}",
            },
        )
        SubElement(
            cmd_event,
            "RealtimeCmd",
            {
                "Type": "Key",
                "Source": "Original",
                "UserProfile": "0",
                "User": "0",
                "Status": "On",
                "IsRealtime": "0",
                "IsXFade": "0",
                "IgnoreFollow": "0",
                "IgnoreCommand": "0",
                "Assert": "0",
                "IgnoreNetwork": "0",
                "FromTriggerNode": "0",
                "IgnoreExecTime": "0",
                "IssuedByTimecode": "0",
                "FromLocalHardwareFader": "1",
                "IgnoreExecXFade": "0",
                "IsExecXFade": "0",
                "ExecToken": "Goto",
                "ValCueDestination": f"0.5.0.{cue.number * 1000}",
            },
        )
