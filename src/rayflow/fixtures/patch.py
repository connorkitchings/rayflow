"""DMX universe and fixture patching."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from rayflow.fixtures.channel_map import ChannelMap, ChannelMapEntry
    from rayflow.fixtures.parser import FixtureSummary, GdtfParser


@dataclass
class FixturePatch:
    """A fixture patched to a DMX address."""

    name: str
    start_address: int
    channel_count: int
    universe: int = 0
    manufacturer: str | None = None
    mode_name: str | None = None
    channel_map: "ChannelMap | None" = None

    @property
    def end_address(self) -> int:
        return self.start_address + self.channel_count - 1

    @property
    def channel_entries(self) -> list["ChannelMapEntry"]:
        if self.channel_map is None:
            return []
        return self.channel_map.entries

    def overlaps(self, other: "FixturePatch") -> bool:
        if self.universe != other.universe:
            return False
        return not (
            self.end_address < other.start_address
            or other.end_address < self.start_address
        )

    def as_dict(self) -> dict[str, Any]:
        """Return a CLI/docs-friendly representation of the patch."""
        return {
            "name": self.name,
            "manufacturer": self.manufacturer,
            "mode_name": self.mode_name,
            "universe": self.universe,
            "start_address": self.start_address,
            "end_address": self.end_address,
            "channel_count": self.channel_count,
            "channels": [entry.as_dict() for entry in self.channel_entries],
        }


class DmxUniverse:
    """Manage a single DMX universe (512 channels).

    Tracks patched fixtures and validates address assignments.
    """

    MAX_CHANNELS = 512

    def __init__(self, universe_number: int = 0):
        self.universe_number = universe_number
        self._patches: list[FixturePatch] = []

    def patch(self, name: str, start_address: int, channel_count: int) -> FixturePatch:
        """Patch a fixture to a DMX address.

        Raises ValueError if the address range is invalid or overlaps.
        """
        new_patch = self._build_patch(
            name=name,
            start_address=start_address,
            channel_count=channel_count,
        )
        self._patches.append(new_patch)
        return new_patch

    def patch_fixture(
        self,
        fixture: "GdtfParser | FixtureSummary",
        start_address: int,
        mode_index: int = 0,
        mode_name: str | None = None,
        name: str | None = None,
    ) -> FixturePatch:
        """Patch a parsed GDTF fixture mode to this universe."""
        from rayflow.fixtures.channel_map import build_channel_map

        channel_map = build_channel_map(
            fixture,
            mode_index=mode_index,
            mode_name=mode_name,
            start_address=start_address,
            universe=self.universe_number,
        )
        fixture_name = name or channel_map.fixture_name
        patch = self._build_patch(
            name=fixture_name,
            start_address=start_address,
            channel_count=channel_map.channel_count,
            manufacturer=fixture.manufacturer,
            mode_name=channel_map.mode_name,
            channel_map=channel_map,
        )
        self._patches.append(patch)
        return patch

    def unpatch(self, name: str) -> bool:
        """Remove a fixture patch by name."""
        for i, patch in enumerate(self._patches):
            if patch.name == name:
                self._patches.pop(i)
                return True
        return False

    @property
    def used_channels(self) -> int:
        return sum(p.channel_count for p in self._patches)

    @property
    def patches(self) -> list[FixturePatch]:
        return list(self._patches)

    def get_patch(self, name: str) -> FixturePatch | None:
        for patch in self._patches:
            if patch.name == name:
                return patch
        return None

    def _build_patch(
        self,
        *,
        name: str,
        start_address: int,
        channel_count: int,
        manufacturer: str | None = None,
        mode_name: str | None = None,
        channel_map: "ChannelMap | None" = None,
    ) -> FixturePatch:
        self._validate_range(start_address, channel_count)
        new_patch = FixturePatch(
            name=name,
            start_address=start_address,
            channel_count=channel_count,
            universe=self.universe_number,
            manufacturer=manufacturer,
            mode_name=mode_name,
            channel_map=channel_map,
        )
        self._validate_no_overlap(new_patch)
        return new_patch

    def _validate_range(self, start_address: int, channel_count: int) -> None:
        if start_address < 1:
            raise ValueError(f"Address must be >= 1, got {start_address}")
        if start_address + channel_count - 1 > self.MAX_CHANNELS:
            raise ValueError(
                f"Fixture exceeds universe bounds: "
                f"address {start_address} + {channel_count} channels "
                f"= {start_address + channel_count - 1} > {self.MAX_CHANNELS}"
            )

    def _validate_no_overlap(self, new_patch: FixturePatch) -> None:
        for existing in self._patches:
            if new_patch.overlaps(existing):
                raise ValueError(
                    f"Address conflict: {new_patch.name} "
                    f"({new_patch.start_address}-{new_patch.end_address}) "
                    f"overlaps with {existing.name} "
                    f"({existing.start_address}-{existing.end_address})"
                )
