"""Validate and summarize RayFlow's agent progress tracker."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_TRACKER = Path(".agent/progress/feature_list.json")
STATUSES = {"not_started", "in_progress", "blocked", "done", "deferred"}
REQUIRED_ROOT_KEYS = {"schema_version", "updated_at", "canonical", "features"}
REQUIRED_FEATURE_KEYS = {
    "id",
    "title",
    "category",
    "status",
    "priority",
    "summary",
    "acceptance",
    "source_refs",
    "updated_at",
}
VERIFICATION_KEYS = ("commands", "artifacts", "session_logs", "notes")
READY_STATUSES = {"not_started", "in_progress"}


class ProgressTrackerError(ValueError):
    """Raised when the progress tracker is invalid."""


def load_tracker(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        tracker = json.load(file)
    if not isinstance(tracker, dict):
        raise ProgressTrackerError("tracker root must be a JSON object")
    return tracker


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(_nonempty_string(item) for item in value)


def _verification_has_evidence(feature: dict[str, Any]) -> bool:
    verification = feature.get("verification")
    if not isinstance(verification, dict):
        return False
    return any(
        _nonempty_string_list(verification.get(key, [])) for key in VERIFICATION_KEYS
    )


def validate_tracker(tracker: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing_root = REQUIRED_ROOT_KEYS - set(tracker)
    if missing_root:
        errors.append(f"root missing required keys: {', '.join(sorted(missing_root))}")

    if tracker.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if tracker.get("canonical") is not True:
        errors.append("canonical must be true")

    features = tracker.get("features")
    if not isinstance(features, list) or not features:
        errors.append("features must be a non-empty list")
        return errors

    ids: set[str] = set()
    for index, feature in enumerate(features):
        label = (
            feature.get("id", f"index {index}")
            if isinstance(feature, dict)
            else f"index {index}"
        )
        if not isinstance(feature, dict):
            errors.append(f"{label}: feature must be an object")
            continue

        missing = REQUIRED_FEATURE_KEYS - set(feature)
        if missing:
            missing_keys = ", ".join(sorted(missing))
            errors.append(f"{label}: missing required keys: {missing_keys}")

        feature_id = feature.get("id")
        if not _nonempty_string(feature_id):
            errors.append(f"{label}: id must be a non-empty string")
        elif feature_id in ids:
            errors.append(f"{label}: duplicate feature id")
        else:
            ids.add(feature_id)

        status = feature.get("status")
        if status not in STATUSES:
            status_values = ", ".join(sorted(STATUSES))
            errors.append(f"{label}: status must be one of {status_values}")

        priority = feature.get("priority")
        if not isinstance(priority, int) or priority < 1:
            errors.append(f"{label}: priority must be a positive integer")

        for key in ("title", "category", "summary", "updated_at"):
            if key in feature and not _nonempty_string(feature[key]):
                errors.append(f"{label}: {key} must be a non-empty string")

        for key in ("acceptance", "source_refs"):
            if key in feature and not _nonempty_string_list(feature[key]):
                errors.append(f"{label}: {key} must be a non-empty string list")

        for key in ("dependencies", "blockers", "notes"):
            if key in feature and not isinstance(feature[key], list):
                errors.append(f"{label}: {key} must be a list when provided")

        verification = feature.get("verification")
        if verification is not None:
            if not isinstance(verification, dict):
                errors.append(f"{label}: verification must be an object when provided")
            else:
                unknown = set(verification) - set(VERIFICATION_KEYS)
                if unknown:
                    unknown_keys = ", ".join(sorted(unknown))
                    errors.append(
                        f"{label}: verification has unknown keys: {unknown_keys}"
                    )
                for key, value in verification.items():
                    if key in VERIFICATION_KEYS and not _nonempty_string_list(value):
                        errors.append(
                            f"{label}: verification.{key} must be a non-empty "
                            "string list"
                        )

        if status == "done" and not _verification_has_evidence(feature):
            errors.append(f"{label}: done features require verification evidence")
        if status == "blocked" and not _nonempty_string_list(
            feature.get("blockers", [])
        ):
            errors.append(f"{label}: blocked features require blockers")

    for feature in features:
        if not isinstance(feature, dict):
            continue
        label = feature.get("id", "<unknown>")
        for dependency in feature.get("dependencies", []):
            if dependency not in ids:
                errors.append(f"{label}: unknown dependency {dependency}")
        parent_id = feature.get("parent_id")
        if parent_id and parent_id not in ids:
            errors.append(f"{label}: unknown parent_id {parent_id}")

    return errors


def summarize_counts(features: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    return {
        "status": Counter(feature["status"] for feature in features),
        "category": Counter(feature["category"] for feature in features),
        "priority": Counter(str(feature["priority"]) for feature in features),
    }


def select_next_feature(features: list[dict[str, Any]]) -> dict[str, Any] | None:
    by_id = {feature["id"]: feature for feature in features}

    def dependencies_done(feature: dict[str, Any]) -> bool:
        return all(
            by_id[dependency]["status"] == "done"
            for dependency in feature.get("dependencies", [])
        )

    candidates = [
        feature
        for feature in features
        if feature["status"] in READY_STATUSES and dependencies_done(feature)
    ]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda item: (item["priority"], item["category"], item["id"]),
    )[0]


def format_status(features: list[dict[str, Any]]) -> str:
    counts = summarize_counts(features)
    lines = [f"Total features: {len(features)}", ""]
    for label in ("status", "category", "priority"):
        lines.append(f"{label.title()}:")
        for key, count in sorted(counts[label].items()):
            lines.append(f"  {key}: {count}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_markdown_summary(features: list[dict[str, Any]]) -> str:
    counts = summarize_counts(features)
    next_feature = select_next_feature(features)
    active = [
        feature
        for feature in sorted(features, key=lambda item: (item["priority"], item["id"]))
        if feature["status"] in {"in_progress", "blocked"}
    ]

    lines = [
        "## Progress Tracker Summary",
        "",
        f"- Total: {len(features)}",
        f"- Done: {counts['status'].get('done', 0)}",
        f"- In progress: {counts['status'].get('in_progress', 0)}",
        f"- Blocked: {counts['status'].get('blocked', 0)}",
        f"- Deferred: {counts['status'].get('deferred', 0)}",
    ]
    if next_feature:
        lines.append(f"- Next: `{next_feature['id']}` - {next_feature['title']}")
    else:
        lines.append("- Next: no unblocked ready feature")

    if active:
        lines.extend(["", "### Active Work"])
        for feature in active:
            lines.append(
                f"- `{feature['id']}` [{feature['status']}, P{feature['priority']}]: "
                f"{feature['summary']}"
            )

    return "\n".join(lines)


def _validated_features(path: Path) -> list[dict[str, Any]]:
    tracker = load_tracker(path)
    errors = validate_tracker(tracker)
    if errors:
        raise ProgressTrackerError("\n".join(errors))
    return tracker["features"]


def command_validate(args: argparse.Namespace) -> int:
    tracker = load_tracker(args.file)
    errors = validate_tracker(tracker)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"OK: {args.file}")
    return 0


def command_status(args: argparse.Namespace) -> int:
    features = _validated_features(args.file)
    print(format_status(features))
    return 0


def command_next(args: argparse.Namespace) -> int:
    features = _validated_features(args.file)
    feature = select_next_feature(features)
    if feature is None:
        print("No unblocked ready feature.")
        return 0
    if args.json:
        print(json.dumps(feature, indent=2, sort_keys=True))
    else:
        print(f"{feature['id']}: {feature['title']}")
        print(f"Status: {feature['status']}")
        print(f"Priority: {feature['priority']}")
        print(f"Summary: {feature['summary']}")
    return 0


def command_summary(args: argparse.Namespace) -> int:
    features = _validated_features(args.file)
    if args.markdown:
        print(format_markdown_summary(features))
    else:
        print(format_status(features))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--file",
        type=Path,
        default=DEFAULT_TRACKER,
        help=f"Progress tracker JSON path. Default: {DEFAULT_TRACKER}",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate tracker structure")
    validate.set_defaults(func=command_validate)

    status = subparsers.add_parser("status", help="Print progress counts")
    status.set_defaults(func=command_status)

    next_parser = subparsers.add_parser("next", help="Print next unblocked feature")
    next_parser.add_argument(
        "--json", action="store_true", help="Emit full feature JSON"
    )
    next_parser.set_defaults(func=command_next)

    summary = subparsers.add_parser("summary", help="Print a progress summary")
    summary.add_argument(
        "--markdown", action="store_true", help="Emit Markdown summary"
    )
    summary.set_defaults(func=command_summary)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ProgressTrackerError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
