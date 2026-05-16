"""Fixture library — manage loaded GDTF fixtures."""

from pathlib import Path

from rayflow.fixtures.parser import FixtureSummary, GdtfParser


class FixtureLibrary:
    """Catalog of loaded GDTF fixtures.

    Loads fixtures from a directory and provides search/retrieval by name
    or manufacturer.
    """

    def __init__(self, fixture_dir: str | Path = "data/fixtures"):
        self.fixture_dir = Path(fixture_dir)
        self._fixtures: dict[str, GdtfParser] = {}

    def load(self, path: str | Path | None = None) -> int:
        """Load fixtures from a path (file or directory)."""
        target = Path(path) if path else self.fixture_dir
        if not target.exists():
            raise FileNotFoundError(f"Fixture path not found: {target}")

        before = self.count
        if target.is_file() and self._is_gdtf_file(target):
            self._load_file(target)
        elif target.is_dir():
            for gdtf_file in sorted(target.iterdir()):
                if not self._is_gdtf_file(gdtf_file):
                    continue
                self._load_file(gdtf_file)
        elif target.is_file():
            raise ValueError(f"Unsupported fixture file type: {target}")
        return self.count - before

    @staticmethod
    def _is_gdtf_file(path: Path) -> bool:
        return path.suffix == ".gdtf" or path.suffixes[-2:] == [".gdtf", ".zip"]

    def _load_file(self, path: Path) -> None:
        parser = GdtfParser(path)
        key = self._key(parser)
        self._fixtures[key] = parser

    @staticmethod
    def _key(parser: GdtfParser) -> str:
        return f"{parser.manufacturer}@{parser.name}"

    def get(self, name: str) -> GdtfParser | None:
        """Get a fixture by name (partial match)."""
        for key, parser in self._fixtures.items():
            if name.lower() in key.lower():
                return parser
        return None

    def get_exact(self, manufacturer: str, name: str) -> GdtfParser | None:
        """Get a fixture by exact manufacturer/name key."""
        return self._fixtures.get(f"{manufacturer}@{name}")

    def list_fixtures(self) -> list[str]:
        """List all loaded fixture names."""
        return sorted(self._fixtures.keys())

    def search(self, query: str) -> list[str]:
        """Search fixtures by name or manufacturer."""
        query_lower = query.lower()
        return sorted(key for key in self._fixtures if query_lower in key.lower())

    def manufacturers(self) -> list[str]:
        """List manufacturers represented in the library."""
        return sorted({parser.manufacturer for parser in self._fixtures.values()})

    def by_manufacturer(self, manufacturer: str) -> list[str]:
        """List fixture keys for one manufacturer."""
        manufacturer_lower = manufacturer.lower()
        return sorted(
            key
            for key, parser in self._fixtures.items()
            if parser.manufacturer.lower() == manufacturer_lower
        )

    def summaries(self) -> list[FixtureSummary]:
        """Return summaries for all loaded fixtures."""
        return [self._fixtures[key].get_summary() for key in self.list_fixtures()]

    @property
    def count(self) -> int:
        return len(self._fixtures)
