"""RayFlow configuration — loads settings from environment variables."""

import os
from dataclasses import dataclass


@dataclass
class Ma3Config:
    """grandMA3 onPC connection settings."""

    ip: str = "127.0.0.1"
    osc_port: int = 8000


@dataclass
class ArtnetConfig:
    """Art-Net protocol settings."""

    target_ip: str = "127.0.0.1"
    port: int = 6454
    universe: int = 0


@dataclass
class SacnConfig:
    """sACN/E1.31 protocol settings."""

    universe: int = 1
    multicast: bool = True


@dataclass
class FixtureConfig:
    """Fixture library settings."""

    fixture_dir: str = "data/fixtures"


@dataclass
class Settings:
    """All RayFlow settings loaded from environment."""

    ma3: Ma3Config
    artnet: ArtnetConfig
    sacn: SacnConfig
    fixtures: FixtureConfig

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            ma3=Ma3Config(
                ip=os.getenv("MA3_IP", "127.0.0.1"),
                osc_port=int(os.getenv("MA3_OSC_PORT", "8000")),
            ),
            artnet=ArtnetConfig(
                target_ip=os.getenv("ARTNET_TARGET", "127.0.0.1"),
                port=int(os.getenv("ARTNET_PORT", "6454")),
                universe=int(os.getenv("ARTNET_UNIVERSE", "0")),
            ),
            sacn=SacnConfig(
                universe=int(os.getenv("SACN_UNIVERSE", "1")),
                multicast=os.getenv("SACN_MULTICAST", "true").lower() == "true",
            ),
            fixtures=FixtureConfig(
                fixture_dir=os.getenv("FIXTURE_DIR", "data/fixtures"),
            ),
        )
