"""GDTF fixture parsing and management."""

from rayflow.fixtures.channel_map import (
    ChannelMap,
    ChannelMapEntry,
    build_channel_map,
    classify_attribute,
    normalize_attribute,
)
from rayflow.fixtures.parser import DmxModeSummary, FixtureSummary, GdtfParser

__all__ = [
    "ChannelMap",
    "ChannelMapEntry",
    "DmxModeSummary",
    "FixtureSummary",
    "GdtfParser",
    "build_channel_map",
    "classify_attribute",
    "normalize_attribute",
]
