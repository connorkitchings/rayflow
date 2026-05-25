from unittest.mock import patch

import pytest

from rayflow.design.models import Cue, FixtureSlot, Rig, Show, Song, Venue
from rayflow.design.serializers import save_rig, save_show
from rayflow.mcp_server import (
    generate_cues,
    get_rig_context,
    get_show_context,
    list_rigs,
    list_shows,
    plan_show_cues,
    render_cue_dmx,
    render_show_dmx,
)


@pytest.fixture
def temp_data_dirs(tmp_path):
    shows_dir = tmp_path / "shows"
    shows_dir.mkdir()
    rigs_dir = tmp_path / "rigs"
    rigs_dir.mkdir()

    # Create dummy show
    show = Show(
        name="test_show",
        rig_name="test_rig",
        song=Song(title="Song", artist="Artist", duration=120),
        cues=[Cue(number=1, label="Cue 1", section="Intro", timestamp=0.0)],
    )
    # Create dummy rig
    rig = Rig(
        name="test_rig",
        venue=Venue("Venue", (10, 10, 5)),
        fixtures=[
            FixtureSlot("LED PAR 64 RGBW", "Default", "PAR 1", 0, 1, channels="1")
        ],
    )

    save_show(show, shows_dir / "test_show.yaml")
    save_rig(rig, rigs_dir / "test_rig.yaml")

    return shows_dir, rigs_dir


def test_list_shows(temp_data_dirs):
    shows_dir, _ = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        shows = list_shows()
        assert shows == ["test_show"]


def test_get_show_context(temp_data_dirs):
    shows_dir, _ = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        context = get_show_context("test_show")
        assert context["name"] == "test_show"

        err = get_show_context("non_existent")
        assert "error" in err


def test_list_rigs(temp_data_dirs):
    _, rigs_dir = temp_data_dirs
    with patch("rayflow.mcp_server._rig_dir_path", return_value=rigs_dir):
        rigs = list_rigs()
        assert rigs == ["test_rig"]


def test_get_rig_context(temp_data_dirs):
    _, rigs_dir = temp_data_dirs
    with patch("rayflow.mcp_server._rig_dir_path", return_value=rigs_dir):
        context = get_rig_context("test_rig")
        assert context["name"] == "test_rig"

        err = get_rig_context("non_existent")
        assert "error" in err


def test_generate_cues(temp_data_dirs):
    shows_dir, _ = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        from rayflow.design.serializers import load_show

        show_path = shows_dir / "test_show.yaml"
        show = load_show(show_path)
        from rayflow.design.models import Section

        show.song.sections.append(Section(name="Chorus", start=30, end=60))
        save_show(show, show_path)

        res = generate_cues("test_show", "Chorus", "all_white", 2, 4.0)
        assert "Successfully generated" in res

        err1 = generate_cues("non_existent", "Chorus", "all_white", 2, 4.0)
        assert "Error: Show not found" in err1

        err2 = generate_cues("test_show", "Intro", "all_white", 2, 4.0)
        assert "Error: Section not found" in err2


def test_plan_show_cues(temp_data_dirs):
    shows_dir, rigs_dir = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        with patch("rayflow.mcp_server._rig_dir_path", return_value=rigs_dir):
            from rayflow.design.serializers import load_show

            show_path = shows_dir / "test_show.yaml"
            show = load_show(show_path)
            from rayflow.design.models import Section

            show.song.sections.append(Section(name="Intro", start=0, end=30))
            save_show(show, show_path)

            res = plan_show_cues(
                "test_show", "test_rig", section_name="Intro", apply=True
            )
            assert res["show"] == "test_show"

            err1 = plan_show_cues("non_existent", "test_rig")
            assert "error" in err1

            err2 = plan_show_cues("test_show", "non_existent")
            assert "error" in err2


def test_render_cue_dmx(temp_data_dirs):
    shows_dir, rigs_dir = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        with patch("rayflow.mcp_server._rig_dir_path", return_value=rigs_dir):
            res = render_cue_dmx("test_show", "test_rig", 1)
            assert res["cue"]["number"] == 1

            err1 = render_cue_dmx("non_existent", "test_rig", 1)
            assert "error" in err1

            err2 = render_cue_dmx("test_show", "non_existent", 1)
            assert "error" in err2

            err3 = render_cue_dmx("test_show", "test_rig", 999)
            assert "error" in err3


def test_render_show_dmx(temp_data_dirs):
    shows_dir, rigs_dir = temp_data_dirs
    with patch("rayflow.mcp_server.show_dir_path", return_value=shows_dir):
        with patch("rayflow.mcp_server._rig_dir_path", return_value=rigs_dir):
            res = render_show_dmx("test_show", "test_rig")
            assert res["scope"] == "show:test_show"

            err1 = render_show_dmx("non_existent", "test_rig")
            assert "error" in err1

            err2 = render_show_dmx("test_show", "non_existent")
            assert "error" in err2
