"""GDTF fixture parser."""

import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import pygdtf

if TYPE_CHECKING:
    from rayflow.fixtures.channel_map import ChannelMap


@dataclass(frozen=True)
class DmxModeSummary:
    """Small, stable view of a GDTF DMX mode."""

    name: str
    channel_count: int
    channels: list[dict]


@dataclass(frozen=True)
class FixtureSummary:
    """Small, stable view of a GDTF fixture profile."""

    manufacturer: str
    name: str
    mode_count: int
    modes: list[DmxModeSummary]


class GdtfParser:
    """Parse GDTF fixture files (.gdtf.zip).

    Wraps pygdtf.FixtureType for reading fixture definitions including
    DMX modes, channels, geometry, and wheel data.
    """

    def __init__(self, gdtf_path: str | Path):
        self.path = Path(gdtf_path)
        self._validate_path()
        self._fixture = pygdtf.FixtureType(str(self.path))

    def _validate_path(self) -> None:
        if not self.path.exists():
            raise FileNotFoundError(f"GDTF file not found: {self.path}")
        if not self.path.is_file():
            raise ValueError(f"GDTF path is not a file: {self.path}")
        if not zipfile.is_zipfile(self.path):
            raise ValueError(f"GDTF file is not a valid ZIP archive: {self.path}")

        with zipfile.ZipFile(self.path) as archive:
            if "description.xml" not in archive.namelist():
                raise ValueError(
                    f"GDTF file is missing required description.xml: {self.path}"
                )

    @property
    def name(self) -> str:
        return self._fixture.name or ""

    @property
    def manufacturer(self) -> str:
        return self._fixture.manufacturer or ""

    @property
    def dmx_modes(self) -> list:
        return self._fixture.dmx_modes

    @property
    def mode_count(self) -> int:
        return len(self._fixture.dmx_modes)

    def mode_names(self) -> list[str]:
        """Return DMX mode names in fixture order."""
        return [mode.name or "" for mode in self._fixture.dmx_modes]

    def get_mode(self, index: int = 0):
        """Get a DMX mode by index."""
        if index < 0 or index >= self.mode_count:
            raise IndexError(
                f"DMX mode index {index} out of range for {self.mode_count} modes"
            )
        return self._fixture.dmx_modes[index]

    def get_channel_count(self, mode_index: int = 0) -> int:
        """Get the number of DMX channels for a mode."""
        return self.get_mode(mode_index).dmx_channels_count

    def get_channels(self, mode_index: int = 0) -> list:
        """Get DMX channel definitions for a mode."""
        return self.get_mode(mode_index).dmx_channels

    def get_channels_as_dict(self, mode_index: int = 0) -> list[dict]:
        """Get DMX channels as a list of dictionaries."""
        return list(self.get_mode(mode_index).dmx_channels.as_dict())

    def get_mode_summary(self, mode_index: int = 0) -> DmxModeSummary:
        """Return a stable summary for a DMX mode."""
        mode = self.get_mode(mode_index)
        return DmxModeSummary(
            name=mode.name or "",
            channel_count=mode.dmx_channels_count,
            channels=self.get_channels_as_dict(mode_index),
        )

    def get_summary(self) -> FixtureSummary:
        """Return a stable summary for the fixture."""
        return FixtureSummary(
            manufacturer=self.manufacturer,
            name=self.name,
            mode_count=self.mode_count,
            modes=[self.get_mode_summary(i) for i in range(self.mode_count)],
        )

    def get_geometry_tree(self, mode_index: int = 0):
        """Get the geometry tree with expanded references."""
        mode_name = self.get_mode(mode_index).name
        return self._fixture.geometries.get_geometry_tree(
            fixture_type=self._fixture,
            mode_name=mode_name,
        )

    def get_channel_map(
        self,
        mode_index: int = 0,
        start_address: int = 1,
        universe: int = 0,
        mode_name: str | None = None,
    ) -> "ChannelMap":
        """Build a concrete DMX channel map for a fixture mode."""
        from rayflow.fixtures.channel_map import build_channel_map

        return build_channel_map(
            self,
            mode_index=mode_index,
            mode_name=mode_name,
            start_address=start_address,
            universe=universe,
        )
