"""Tests for the RayFlow progress tracker helper."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "progress_tracker.py"
SPEC = importlib.util.spec_from_file_location("progress_tracker", SCRIPT)
progress_tracker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(progress_tracker)


def _base_tracker() -> dict:
    return {
        "schema_version": 1,
        "updated_at": "2026-06-09",
        "canonical": True,
        "features": [
            {
                "id": "done-foundation",
                "title": "Done foundation",
                "category": "foundation",
                "status": "done",
                "priority": 10,
                "summary": "Already complete.",
                "acceptance": ["Works"],
                "verification": {"commands": ["uv run pytest"]},
                "source_refs": ["docs/implementation_schedule.md"],
                "updated_at": "2026-06-09",
            },
            {
                "id": "blocked-capture",
                "title": "Blocked Capture proof",
                "category": "capture",
                "status": "blocked",
                "priority": 1,
                "summary": "Waiting on fixture import proof.",
                "acceptance": ["Fixture imports"],
                "blockers": ["Capture imports zero fixtures"],
                "source_refs": [
                    "session_logs/06-06-2026/4 - Capture Library Mapping Proof.md"
                ],
                "updated_at": "2026-06-09",
            },
            {
                "id": "ready-work",
                "title": "Ready work",
                "category": "agent-harness",
                "status": "not_started",
                "priority": 2,
                "summary": "Ready to implement.",
                "acceptance": ["Feature works"],
                "dependencies": ["done-foundation"],
                "source_refs": [".agent/progress/feature_list.json"],
                "updated_at": "2026-06-09",
            },
            {
                "id": "waiting-work",
                "title": "Waiting work",
                "category": "capture",
                "status": "not_started",
                "priority": 1,
                "summary": "Dependency is not complete.",
                "acceptance": ["Can run later"],
                "dependencies": ["blocked-capture"],
                "source_refs": [".agent/progress/feature_list.json"],
                "updated_at": "2026-06-09",
            },
        ],
    }


def test_valid_tracker_passes_validation():
    assert progress_tracker.validate_tracker(_base_tracker()) == []


def test_done_without_verification_fails():
    tracker = _base_tracker()
    del tracker["features"][0]["verification"]

    errors = progress_tracker.validate_tracker(tracker)

    assert "done-foundation: done features require verification evidence" in errors


def test_invalid_dependency_fails():
    tracker = _base_tracker()
    tracker["features"][2]["dependencies"] = ["missing-feature"]

    errors = progress_tracker.validate_tracker(tracker)

    assert "ready-work: unknown dependency missing-feature" in errors


def test_next_skips_blocked_and_deferred_items():
    tracker = _base_tracker()
    tracker["features"].append(
        {
            "id": "deferred-work",
            "title": "Deferred work",
            "category": "agent-harness",
            "status": "deferred",
            "priority": 1,
            "summary": "Should not be selected.",
            "acceptance": ["No selection"],
            "source_refs": [".agent/progress/feature_list.json"],
            "updated_at": "2026-06-09",
        }
    )

    selected = progress_tracker.select_next_feature(tracker["features"])

    assert selected["id"] == "ready-work"


def test_next_priority_ordering_is_deterministic():
    tracker = _base_tracker()
    tracker["features"].append(
        {
            "id": "aaa-equal-priority",
            "title": "Equal priority but earlier id",
            "category": "agent-harness",
            "status": "not_started",
            "priority": 2,
            "summary": "Tie should sort by category then id.",
            "acceptance": ["Stable order"],
            "source_refs": [".agent/progress/feature_list.json"],
            "updated_at": "2026-06-09",
        }
    )

    selected = progress_tracker.select_next_feature(tracker["features"])

    assert selected["id"] == "aaa-equal-priority"


def test_markdown_summary_contains_active_and_blocked_work():
    summary = progress_tracker.format_markdown_summary(_base_tracker()["features"])

    assert "## Progress Tracker Summary" in summary
    assert "- Blocked: 1" in summary
    assert "`blocked-capture` [blocked, P1]" in summary
    assert "- Next: `ready-work` - Ready work" in summary


def test_cli_validate_seed_tracker(tmp_path: Path, capsys):
    tracker_path = tmp_path / "feature_list.json"
    tracker_path.write_text(json.dumps(_base_tracker()), encoding="utf-8")

    result = progress_tracker.main(["--file", str(tracker_path), "validate"])

    captured = capsys.readouterr()
    assert result == 0
    assert f"OK: {tracker_path}" in captured.out
