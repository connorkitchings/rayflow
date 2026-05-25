"""Tests for CLI shared utilities."""

from pathlib import Path

from rayflow.cli._shared import list_yaml_files


class TestListYamlFiles:
    def test_empty_directory(self, tmp_path: Path) -> None:
        result = list_yaml_files(tmp_path)
        assert result == []

    def test_non_existent_directory(self) -> None:
        result = list_yaml_files(Path("/nonexistent/path"))
        assert result == []

    def test_lists_yaml_files(self, tmp_path: Path) -> None:
        (tmp_path / "a.yaml").touch()
        (tmp_path / "b.yaml").touch()
        (tmp_path / "not_yaml.txt").touch()
        result = list_yaml_files(tmp_path)
        assert [p.name for p in result] == ["a.yaml", "b.yaml"]
