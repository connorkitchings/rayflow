"""Tests for MA3 safe probe helpers."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from rayflow.cli import app
from rayflow.console.probe import (
    ExpectedExport,
    ProbePlan,
    changed_show_files,
    check_expected_exports,
    run_probe_plan,
    show_isolation_passed,
    snapshot_show_mtimes,
)

runner = CliRunner()


def test_snapshot_show_mtimes(tmp_path: Path) -> None:
    show = tmp_path / "rayflow_control_probe.show"
    show.write_text("binary-ish")
    ignored = tmp_path / "notes.txt"
    ignored.write_text("ignore")

    snapshot = snapshot_show_mtimes(tmp_path)

    assert list(snapshot) == ["rayflow_control_probe.show"]
    assert snapshot["rayflow_control_probe.show"] == show.stat().st_mtime


def test_show_isolation_passes_only_for_target_change() -> None:
    before = {"rayflow_control_probe.show": 1.0, "other.show": 2.0}
    after = {"rayflow_control_probe.show": 3.0, "other.show": 2.0}

    assert show_isolation_passed(
        target_show="rayflow_control_probe", before=before, after=after
    )


def test_show_isolation_rejects_wrong_show_change() -> None:
    before = {"rayflow_control_probe.show": 1.0, "other.show": 2.0}
    after = {"rayflow_control_probe.show": 1.0, "other.show": 3.0}

    assert not show_isolation_passed(
        target_show="rayflow_control_probe", before=before, after=after
    )
    assert changed_show_files(before, after) == {"other.show": (2.0, 3.0)}


def test_expected_export_validation(tmp_path: Path) -> None:
    export = tmp_path / "sequence.xml"
    export.write_text('<Sequence><Cue Name="Dimmer Proof"/></Sequence>')
    expected = [
        ExpectedExport(
            label="sequence",
            path=export,
            required_substrings=["Sequence", "Dimmer Proof", "Missing"],
        ),
        ExpectedExport(label="missing", path=tmp_path / "missing.xml"),
    ]

    checks = check_expected_exports(expected)

    assert checks[0].exists
    assert checks[0].missing_substrings == ["Missing"]
    assert not checks[0].passed
    assert not checks[1].exists


def test_run_probe_plan_dry_run_does_not_send(tmp_path: Path) -> None:
    plan = ProbePlan(
        name="demo",
        target_show="not_required_for_dry_run",
        commands=["About", "List Sequence"],
    )
    client = MagicMock()

    result = run_probe_plan(
        plan,
        execute=False,
        shows_dir=tmp_path,
        client=client,
    )

    assert result.status == "dry-run"
    assert [entry.command for entry in result.commands] == ["About", "List Sequence"]
    assert all(not entry.sent for entry in result.commands)
    client.send.assert_not_called()


def test_run_probe_plan_execute_sends_in_order(tmp_path: Path) -> None:
    plan = ProbePlan(
        name="demo",
        target_show="rayflow_control_probe",
        commands=["About", "List Sequence"],
    )
    client = MagicMock()

    result = run_probe_plan(
        plan,
        execute=True,
        delay=0,
        shows_dir=tmp_path,
        client=client,
    )

    assert [call.args[0] for call in client.send.call_args_list] == [
        "About",
        "List Sequence",
    ]
    assert all(entry.sent for entry in result.commands)


def test_run_probe_plan_execute_rejects_bad_target(tmp_path: Path) -> None:
    plan = ProbePlan(name="demo", target_show="real_show", commands=["ClearAll"])

    try:
        run_probe_plan(
            plan,
            execute=True,
            delay=0,
            shows_dir=tmp_path,
            client=MagicMock(),
        )
    except ValueError as exc:
        assert "target_show must be" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_probe_run_cli_dry_run(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "name": "demo",
                "target_show": "rayflow_control_probe",
                "commands": ["About"],
                "expected_exports": [],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "console",
            "probe",
            "run",
            "--plan",
            str(plan_path),
            "--target-show",
            "rayflow_control_probe",
            "--shows-dir",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0
    assert "dry-run" in result.output
    assert "About" in result.output


@patch("rayflow.console.osc.Ma3OscClient")
def test_probe_run_cli_execute_sends(mock_client_cls, tmp_path: Path) -> None:
    mock_client = MagicMock()
    mock_client_cls.return_value = mock_client
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "name": "demo",
                "target_show": "rayflow_control_probe",
                "commands": ["About", "List Sequence"],
                "expected_exports": [],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "console",
            "probe",
            "run",
            "--plan",
            str(plan_path),
            "--target-show",
            "rayflow_control_probe",
            "--shows-dir",
            str(tmp_path),
            "--delay",
            "0",
            "--execute",
        ],
    )

    assert result.exit_code == 0
    assert [call.args[0] for call in mock_client.send.call_args_list] == [
        "About",
        "List Sequence",
    ]


def test_probe_run_cli_blocks_bad_target(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "name": "demo",
                "target_show": "real_show",
                "commands": ["ClearAll"],
            }
        )
    )

    result = runner.invoke(
        app,
        [
            "console",
            "probe",
            "run",
            "--plan",
            str(plan_path),
            "--target-show",
            "real_show",
            "--execute",
        ],
    )

    assert result.exit_code == 1
    assert "target_show must be" in result.output


def test_fixture_import_cli_dry_run() -> None:
    result = runner.invoke(app, ["console", "probe", "fixture-import"])

    assert result.exit_code == 0
    assert "Dry run" in result.output
    assert "rayflow_control_probe.mvr" in result.output


def test_fixture_import_cli_execute_writes_mvr(tmp_path: Path) -> None:
    output = tmp_path / "probe.mvr"

    result = runner.invoke(
        app,
        [
            "console",
            "probe",
            "fixture-import",
            "--mvr",
            str(output),
            "--target-show",
            "rayflow_control_probe",
            "--execute",
        ],
    )

    assert result.exit_code == 0
    assert output.exists()
    assert "Probe MVR exported" in result.output
