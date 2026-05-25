"""Test that all lighting library dependencies can be imported."""


def test_import_stupidartnet():
    import stupidArtnet  # noqa: F401


def test_import_sacn():
    import sacn  # noqa: F401


def test_import_python_osc():
    from pythonosc import udp_client  # noqa: F401


def test_import_pygdtf():
    import pygdtf  # noqa: F401


def test_import_numpy():
    import numpy  # noqa: F401


def test_import_rayflow():
    import rayflow  # noqa: F401

    assert rayflow.__version__ == "0.1.0"


def test_import_config():
    from rayflow.config import ArtnetConfig, Ma3Config, Settings

    assert Settings is not None
    assert Ma3Config is not None
    assert ArtnetConfig is not None


def test_import_bridge():
    from rayflow.engine.bridge.artnet import ArtNetSender
    from rayflow.engine.bridge.sacn_bridge import SacnSender

    assert ArtNetSender is not None
    assert SacnSender is not None


def test_import_fixtures():
    from rayflow.engine.fixtures.library import FixtureLibrary
    from rayflow.engine.fixtures.parser import GdtfParser
    from rayflow.engine.fixtures.patch import DmxUniverse

    assert GdtfParser is not None
    assert FixtureLibrary is not None
    assert DmxUniverse is not None


def test_import_console():
    from rayflow.engine.console.cue import CueStack, CueStep, Ma3Command
    from rayflow.engine.console.osc import Ma3OscClient

    assert Ma3OscClient is not None
    assert Ma3Command is not None
    assert CueStep is not None
    assert CueStack is not None


def test_import_design():
    from rayflow.design.authoring import plan_cues
    from rayflow.design.models import Cue, Rig, Show, Song, Venue, Vibe

    assert Cue is not None
    assert Rig is not None
    assert Show is not None
    assert Song is not None
    assert Venue is not None
    assert Vibe is not None
    assert plan_cues is not None
