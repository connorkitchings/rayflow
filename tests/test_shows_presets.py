"""Tests for preset validation helpers."""

from unittest.mock import MagicMock

from rayflow.shows.presets import (
    ATTRIBUTE_FAMILIES,
    fixture_supports_attribute,
    validate_preset_against_fixture,
    validate_preset_attributes,
)


class TestValidatePresetAttributes:
    def test_valid_attributes(self) -> None:
        errors = validate_preset_attributes({"dimmer": "80", "color": "Red"})
        assert errors == []

    def test_unknown_attribute(self) -> None:
        errors = validate_preset_attributes({"dimmer": "80", "bogus": "X"})
        assert len(errors) == 1
        assert "bogus" in errors[0]

    def test_all_families_valid(self) -> None:
        attrs = {family: "50" for family in ATTRIBUTE_FAMILIES}
        errors = validate_preset_attributes(attrs)
        assert errors == []

    def test_empty_attributes(self) -> None:
        errors = validate_preset_attributes({})
        assert errors == []


class TestFixtureSupportsAttribute:
    def _make_parser(self, channel_attributes: list[str]) -> MagicMock:
        parser = MagicMock()
        parser.name = "TestFixture"
        parser.get_mode.return_value = {"name": "Mode 1"}
        channels = [{"attribute": a} for a in channel_attributes]
        parser.get_channels_as_dict.return_value = channels
        return parser

    def test_supports_dimmer(self) -> None:
        parser = self._make_parser(["Dimmer", "Pan"])
        assert fixture_supports_attribute(parser, 0, "dimmer") is True

    def test_supports_multiple_color_synonyms(self) -> None:
        parser = self._make_parser(["ColorRGB"])
        assert fixture_supports_attribute(parser, 0, "color") is True

    def test_does_not_support_missing(self) -> None:
        parser = self._make_parser(["Dimmer"])
        assert fixture_supports_attribute(parser, 0, "gobo") is False

    def test_invalid_mode_index_returns_false(self) -> None:
        parser = self._make_parser(["Dimmer"])
        parser.get_mode.side_effect = IndexError
        assert fixture_supports_attribute(parser, 99, "dimmer") is False

    def test_attribute_error_on_get_mode(self) -> None:
        parser = self._make_parser(["Dimmer"])
        parser.get_mode.side_effect = AttributeError
        assert fixture_supports_attribute(parser, 0, "dimmer") is False

    def test_supports_position(self) -> None:
        parser = self._make_parser(["Pan", "Tilt"])
        assert fixture_supports_attribute(parser, 0, "position") is True

    def test_supports_partial_position(self) -> None:
        parser = self._make_parser(["Pan"])
        assert fixture_supports_attribute(parser, 0, "position") is True

    def test_supports_beam(self) -> None:
        parser = self._make_parser(["Zoom", "Iris"])
        assert fixture_supports_attribute(parser, 0, "beam") is True


class TestValidatePresetAgainstFixture:
    def _make_parser(self, channel_attributes: list[str]) -> MagicMock:
        parser = MagicMock()
        parser.name = "TestFixture"
        parser.get_mode.return_value = {"name": "Mode 1"}
        channels = [{"attribute": a} for a in channel_attributes]
        parser.get_channels_as_dict.return_value = channels
        return parser

    def test_all_supported(self) -> None:
        parser = self._make_parser(["Dimmer", "ColorRGB", "Pan"])
        errors = validate_preset_against_fixture(
            {"dimmer": "80", "color": "Red"}, parser, 0
        )
        assert errors == []

    def test_partially_unsupported(self) -> None:
        parser = self._make_parser(["Dimmer"])
        errors = validate_preset_against_fixture(
            {"dimmer": "80", "gobo": "1"}, parser, 0
        )
        assert len(errors) == 1
        assert "gobo" in errors[0]

    def test_empty_attributes(self) -> None:
        parser = self._make_parser(["Dimmer"])
        errors = validate_preset_against_fixture({}, parser, 0)
        assert errors == []
