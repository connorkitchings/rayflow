"""Tests for deterministic rig building."""

from pathlib import Path

import pytest

from rayflow.design.rig_builder import plan_rig_build
from rayflow.design.serializers import load_rig, save_rig

SAMPLE_FIXTURE_DIR = Path("data/fixtures/samples")


def test_plan_rig_build_infers_small_medium_large() -> None:
    small = plan_rig_build(
        "Small",
        "small warm club wash",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )
    medium = plan_rig_build(
        "Medium",
        "medium theater with beams",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )
    large = plan_rig_build(
        "Large",
        "large outdoor festival psychedelic beam rig",
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert small.scale == "small"
    assert small.rig.venue.dimensions == (10.0, 6.0, 4.0)
    assert small.fixture_counts["wash"] == 4
    assert medium.scale == "medium"
    assert medium.fixture_counts["beam"] >= 2
    assert large.scale == "large"
    assert large.fixture_counts["pixel"] >= 2


def test_plan_rig_build_overrides_take_precedence() -> None:
    plan = plan_rig_build(
        "Override Rig",
        "small club",
        overrides={
            "scale": "large",
            "dimensions": [30, 20, 10],
            "venue_name": "Override Venue",
            "fixture_counts": {"wash": 2, "pixel": 1, "beam": 0},
        },
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert plan.scale == "large"
    assert plan.rig.venue.name == "Override Venue"
    assert plan.rig.venue.dimensions == (30.0, 20.0, 10.0)
    assert plan.fixture_counts == {"wash": 2, "pixel": 1, "beam": 0}
    assert len(plan.rig.fixtures) == 3


def test_plan_rig_build_warns_for_invalid_fixture_override() -> None:
    plan = plan_rig_build(
        "Bad Fixture Rig",
        "small club",
        overrides={"fixtures": {"wash": {"fixture": "Missing Fixture"}}},
        fixture_dir=SAMPLE_FIXTURE_DIR,
    )

    assert any("not found" in warning for warning in plan.warnings)
    assert plan.as_dict()["readiness"]["status"] == "warnings"


def test_plan_rig_build_rejects_invalid_overrides() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        plan_rig_build(
            "Bad",
            "small",
            overrides={"dimensions": [1, 2]},
            fixture_dir=SAMPLE_FIXTURE_DIR,
        )


def test_rig_build_apply_result_is_loadable(tmp_path: Path) -> None:
    plan = plan_rig_build(
        "Applied Rig",
        "medium theater beam rig",
        fixture_dir=SAMPLE_FIXTURE_DIR,
        apply=True,
    )
    path = save_rig(plan.rig, tmp_path / "Applied Rig.yaml")
    loaded = load_rig(path)

    labels = [slot.label for slot in loaded.fixtures]
    addresses = [slot.start_address for slot in loaded.fixtures]
    assert loaded.name == "Applied Rig"
    assert len(labels) == len(set(labels))
    assert addresses == sorted(addresses)
    assert all(
        slot.channels == str(index + 1) for index, slot in enumerate(loaded.fixtures)
    )
