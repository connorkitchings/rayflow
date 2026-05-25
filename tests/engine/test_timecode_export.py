"""Tests for shows/timecode_export.py."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from rayflow.design.models import Cue, Show, Song
from rayflow.engine.console.timecode_export import export_timecode_xml

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_show(
    cues: list[Cue] | None = None,
    duration: float = 120.0,
    name: str = "Test Show",
) -> Show:
    song = Song(title="Test Song", artist="Test Artist", duration=duration)
    return Show(name=name, rig_name="Test Rig", song=song, cues=cues or [])


def _parse(xml_str: str) -> ET.Element:
    """Parse XML string and return root element."""
    return ET.fromstring(xml_str)


# ---------------------------------------------------------------------------
# export_timecode_xml — basic validity
# ---------------------------------------------------------------------------


class TestExportTimecodeXmlBasic:
    def test_returns_string(self):
        show = _make_show()
        result = export_timecode_xml(show)
        assert isinstance(result, str)

    def test_has_xml_declaration(self):
        show = _make_show()
        result = export_timecode_xml(show)
        assert result.startswith('<?xml version="1.0" encoding="UTF-8"?>')

    def test_is_well_formed_xml(self):
        show = _make_show()
        result = export_timecode_xml(show)
        root = _parse(result)
        assert root is not None

    def test_root_element_is_gma3(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        assert root.tag == "GMA3"

    def test_data_version_attribute(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        assert root.attrib["DataVersion"] == "2.3.2.0"


# ---------------------------------------------------------------------------
# export_timecode_xml — Timecode element
# ---------------------------------------------------------------------------


class TestTimecodeElement:
    def test_timecode_element_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert tc is not None

    def test_timecode_name_matches_show(self):
        show = _make_show(name="My Rock Show")
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert tc.attrib["Name"] == "My Rock Show"

    def test_timecode_duration_matches_song(self):
        show = _make_show(duration=180.0)
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert float(tc.attrib["Duration"]) == pytest.approx(180.0)

    def test_timecode_guid_is_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        guid = tc.attrib.get("Guid", "")
        # GUID format: 16 uppercase hex bytes separated by spaces
        parts = guid.split()
        assert len(parts) == 16
        for part in parts:
            int(part, 16)  # raises ValueError if not hex

    def test_timecode_loop_count(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert tc.attrib["LoopCount"] == "0"


# ---------------------------------------------------------------------------
# export_timecode_xml — TrackGroup / Track structure
# ---------------------------------------------------------------------------


class TestTrackStructure:
    def test_track_group_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tg = root.find(".//TrackGroup")
        assert tg is not None

    def test_marker_track_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        mt = root.find(".//MarkerTrack")
        assert mt is not None
        assert mt.attrib["Name"] == "Marker"

    def test_cue_track_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tracks = root.findall(".//Track")
        assert len(tracks) >= 1

    def test_time_range_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        tr = root.find(".//TimeRange")
        assert tr is not None
        assert tr.attrib["Duration"] == "To End"

    def test_cmd_sub_track_present(self):
        show = _make_show()
        root = _parse(export_timecode_xml(show))
        assert root.find(".//CmdSubTrack") is not None


# ---------------------------------------------------------------------------
# export_timecode_xml — Events (cue mapping)
# ---------------------------------------------------------------------------


class TestTimecodeEvents:
    def test_empty_show_has_no_events(self):
        show = _make_show(cues=[])
        root = _parse(export_timecode_xml(show))
        events = root.findall(".//CmdEvent")
        assert len(events) == 0

    def test_single_cue_produces_one_event(self):
        cue = Cue(number=1, label="Intro", section="Intro", timestamp=10.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show))
        events = root.findall(".//CmdEvent")
        assert len(events) == 1

    def test_three_cues_produce_three_events(self):
        cues = [
            Cue(number=1, label="A", section="S", timestamp=0.0),
            Cue(number=2, label="B", section="S", timestamp=30.0),
            Cue(number=3, label="C", section="S", timestamp=60.0),
        ]
        show = _make_show(cues=cues)
        root = _parse(export_timecode_xml(show))
        events = root.findall(".//CmdEvent")
        assert len(events) == 3

    def test_event_times_match_cue_timestamps(self):
        cues = [
            Cue(number=1, label="A", section="S", timestamp=0.0),
            Cue(number=2, label="B", section="S", timestamp=75.0),
            Cue(number=3, label="C", section="S", timestamp=90.5),
        ]
        show = _make_show(cues=cues)
        root = _parse(export_timecode_xml(show))
        events = root.findall(".//CmdEvent")
        times = {e.attrib["Time"] for e in events}
        assert "0.000" in times
        assert "75.000" in times
        assert "90.500" in times

    def test_events_are_sorted_by_timestamp(self):
        # Pass cues out of order; XML events should be sorted.
        cues = [
            Cue(number=2, label="B", section="S", timestamp=60.0),
            Cue(number=1, label="A", section="S", timestamp=0.0),
            Cue(number=3, label="C", section="S", timestamp=30.0),
        ]
        show = _make_show(cues=cues)
        root = _parse(export_timecode_xml(show))
        events = root.findall(".//CmdEvent")
        times = [float(e.attrib["Time"]) for e in events]
        assert times == sorted(times)

    def test_event_action_is_goto(self):
        cue = Cue(number=1, label="Hit", section="S", timestamp=5.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show))
        event = root.find(".//CmdEvent")
        assert event.attrib["Name"] == "Goto"
        assert event.attrib["CueDestination"] == "Cue 1"

    def test_event_has_captured_realtime_command_shape(self):
        cue = Cue(number=2, label="Hit", section="S", timestamp=5.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show))
        realtime_cmd = root.find(".//CmdEvent/RealtimeCmd")
        assert realtime_cmd is not None
        assert realtime_cmd.attrib == {
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
            "ValCueDestination": "0.5.0.2000",
        }

    def test_event_executor_matches_sequence(self):
        cue = Cue(number=1, label="Hit", section="S", timestamp=5.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show, sequence=3))
        track = root.find(".//Track")
        assert track.attrib["Target"] == "ShowData.DataPools.Default.Sequences.3"


# ---------------------------------------------------------------------------
# export_timecode_xml — sequence / parameter validation
# ---------------------------------------------------------------------------


class TestExportTimecodeXmlValidation:
    def test_invalid_sequence_zero_raises(self):
        show = _make_show()
        with pytest.raises(ValueError, match="sequence must be > 0"):
            export_timecode_xml(show, sequence=0)

    def test_invalid_sequence_negative_raises(self):
        show = _make_show()
        with pytest.raises(ValueError, match="sequence must be > 0"):
            export_timecode_xml(show, sequence=-1)

    def test_invalid_frame_rate_raises(self):
        show = _make_show()
        with pytest.raises(ValueError, match="frame_rate must be > 0"):
            export_timecode_xml(show, frame_rate=0.0)

    def test_default_sequence_is_1(self):
        cue = Cue(number=1, label="Hit", section="S", timestamp=5.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show))
        track = root.find(".//Track")
        assert track.attrib["Target"] == "ShowData.DataPools.Default.Sequences.1"

    def test_sequence_5_in_executor(self):
        cue = Cue(number=1, label="Hit", section="S", timestamp=5.0)
        show = _make_show(cues=[cue])
        root = _parse(export_timecode_xml(show, sequence=5))
        track = root.find(".//Track")
        assert track.attrib["Target"] == "ShowData.DataPools.Default.Sequences.5"

    def test_show_name_truncated_to_64_chars(self):
        long_name = "A" * 100
        show = _make_show(name=long_name)
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert len(tc.attrib["Name"]) == 64

    def test_show_name_short_not_truncated(self):
        show = _make_show(name="Short")
        root = _parse(export_timecode_xml(show))
        tc = root.find("Timecode")
        assert tc.attrib["Name"] == "Short"


# ---------------------------------------------------------------------------
# export_timecode_xml — all GUIDs unique across document
# ---------------------------------------------------------------------------


class TestAllGuidsUnique:
    def test_all_guids_unique_in_document(self):
        cues = [
            Cue(number=i, label=f"Cue {i}", section="S", timestamp=float(i * 5))
            for i in range(1, 6)
        ]
        show = _make_show(cues=cues)
        xml_str = export_timecode_xml(show)
        root = _parse(xml_str)

        guids = []
        for elem in root.iter():
            g = elem.attrib.get("Guid")
            if g:
                guids.append(g)

        assert len(guids) == len(set(guids)), "Found duplicate GUIDs in document"
