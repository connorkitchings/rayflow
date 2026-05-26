"""Tests for MA3 export bundle helpers."""

from rayflow.design.models import FixtureSlot, Position3D, Rig, Venue
from rayflow.engine.console.export_bundle import build_mvr_patches

SAMPLE_FIXTURE_DIR = "data/fixtures/samples"


def test_build_mvr_patches_preserves_rig_dmx_addresses() -> None:
    rig = Rig(
        name="Addressed Rig",
        venue=Venue(name="Test", dimensions=(10, 5, 3)),
        fixtures=[
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 1",
                universe=0,
                start_address=37,
                position=Position3D(x=-1, y=2, z=3),
            ),
            FixtureSlot(
                fixture_name="LED PAR 64 RGBW",
                mode="Default",
                label="PAR 2",
                universe=2,
                start_address=401,
                position=Position3D(x=1, y=2, z=3),
            ),
        ],
    )

    patches = build_mvr_patches(rig, SAMPLE_FIXTURE_DIR)

    assert [(patch.name, patch.universe, patch.address) for patch in patches] == [
        ("PAR 1", 0, 37),
        ("PAR 2", 2, 401),
    ]
