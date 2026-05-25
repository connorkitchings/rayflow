"""Test fixtures and utilities for RayFlow bridge tests."""

from pathlib import Path
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import pytest


@pytest.fixture
def mock_artnet_lib():
    """Mock the stupidArtnet library for testing ArtNetSender."""
    with (
        patch("rayflow.engine.bridge.artnet.StupidArtnet") as mock_sender,
        patch("rayflow.engine.bridge.artnet.StupidArtnetServer") as mock_server,
    ):
        mock_sender_instance = MagicMock()
        mock_sender.return_value = mock_sender_instance
        mock_server_instance = MagicMock()
        mock_server.return_value = mock_server_instance
        yield {
            "sender_class": mock_sender,
            "sender_instance": mock_sender_instance,
            "server_class": mock_server,
            "server_instance": mock_server_instance,
        }


@pytest.fixture
def mock_sacn_lib():
    """Mock the sacn library for testing SacnSender."""
    with patch("rayflow.engine.bridge.sacn_bridge.sacn") as mock_sacn:
        mock_sender = MagicMock()
        mock_sacn.sACNsender.return_value = mock_sender
        mock_receiver = MagicMock()
        mock_sacn.sACNreceiver.return_value = mock_receiver
        yield {
            "sacn": mock_sacn,
            "sender": mock_sender,
            "receiver": mock_receiver,
        }


@pytest.fixture
def temp_dir(tmp_path: Path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_gdtf_file(tmp_path: Path) -> Path:
    """Create a small valid GDTF archive for parser/library tests."""
    gdtf_path = tmp_path / "rayflow_sample_dimmer.gdtf.zip"
    description_xml = """<?xml version="1.0" encoding="UTF-8"?>
<GDTF DataVersion="1.2">
  <FixtureType
    Manufacturer="RayFlow"
    Name="Sample Dimmer"
    ShortName="Dimmer"
    LongName="RayFlow Sample Dimmer"
    Description="Minimal test dimmer"
    FixtureTypeID="11111111-1111-1111-1111-111111111111"
    RefFT=""
    Thumbnail="">
    <AttributeDefinitions>
      <FeatureGroups>
        <FeatureGroup Name="Dimmer" Pretty="Dimmer">
          <Feature Name="Dimmer" Pretty="Dimmer" />
        </FeatureGroup>
      </FeatureGroups>
      <Attributes>
        <Attribute Name="Dimmer" Pretty="Dimmer" Feature="Dimmer.Dimmer" />
      </Attributes>
    </AttributeDefinitions>
    <Geometries>
      <Geometry Name="Body" Model="Body" />
    </Geometries>
    <DMXModes>
      <DMXMode Name="Basic" Geometry="Body">
        <DMXChannels>
          <DMXChannel DMXBreak="1" Offset="1" Geometry="Body">
            <LogicalChannel Attribute="Dimmer">
              <ChannelFunction
                Name="Dimmer"
                Attribute="Dimmer"
                DMXFrom="0/1"
                PhysicalFrom="0"
                PhysicalTo="100" />
            </LogicalChannel>
          </DMXChannel>
        </DMXChannels>
      </DMXMode>
    </DMXModes>
  </FixtureType>
</GDTF>
"""
    with ZipFile(gdtf_path, "w") as archive:
        archive.writestr("description.xml", description_xml)
    return gdtf_path


@pytest.fixture
def sample_gdtf_library(tmp_path: Path, sample_gdtf_file: Path) -> Path:
    """Create a directory containing a sample GDTF file."""
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    target = fixture_dir / sample_gdtf_file.name
    target.write_bytes(sample_gdtf_file.read_bytes())
    return fixture_dir
