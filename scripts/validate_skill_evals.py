#!/usr/bin/env python3
"""Validate the portable schema and internal consistency of Skill eval cases."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DECISION_STATUSES = {
    "proposed",
    "accepted",
    "rejected",
    "superseded",
    "needs-confirmation",
}
DELIVERY_STATUSES = {
    "not-started",
    "in-progress",
    "implemented",
    "validated",
    "not-applicable",
}
RECORD_ACTIONS = {
    "none",
    "analyze-only",
    "create",
    "update",
    "create-successor",
}
ACTIONS_WITH_STATUSES = {"create", "update", "create-successor"}
EXPECTED_FIELDS = {
    "should_invoke",
    "record_action",
    "decision_status",
    "delivery_status",
    "required_behaviors",
    "forbidden_behaviors",
}


def _nonempty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def validate_suite(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["suite must be a JSON object"]
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("skill") != "pddr-recorder":
        errors.append("skill must be pddr-recorder")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append("cases must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, case in enumerate(cases):
        prefix = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{prefix} must be an object")
            continue

        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{prefix}.id must be a non-empty string")
        elif case_id in seen_ids:
            errors.append(f"{prefix}.id is duplicated: {case_id}")
        else:
            seen_ids.add(case_id)

        if not isinstance(case.get("prompt"), str) or not case["prompt"].strip():
            errors.append(f"{prefix}.prompt must be a non-empty string")
        artifacts = case.get("artifacts")
        if not isinstance(artifacts, list) or not all(
            isinstance(item, str) and item.strip() for item in artifacts
        ):
            errors.append(f"{prefix}.artifacts must be a list of non-empty strings")

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{prefix}.expected must be an object")
            continue
        missing = sorted(EXPECTED_FIELDS - expected.keys())
        if missing:
            errors.append(f"{prefix}.expected is missing: {', '.join(missing)}")

        if not isinstance(expected.get("should_invoke"), bool):
            errors.append(f"{prefix}.expected.should_invoke must be boolean")
        action = expected.get("record_action")
        if action not in RECORD_ACTIONS:
            errors.append(f"{prefix}.expected.record_action is invalid")

        decision_status = expected.get("decision_status")
        delivery_status = expected.get("delivery_status")
        if action in ACTIONS_WITH_STATUSES:
            if decision_status not in DECISION_STATUSES:
                errors.append(f"{prefix}.expected.decision_status is invalid")
            if delivery_status not in DELIVERY_STATUSES:
                errors.append(f"{prefix}.expected.delivery_status is invalid")
        elif decision_status is not None or delivery_status is not None:
            errors.append(
                f"{prefix}.expected statuses must be null when no record state is asserted"
            )

        for field in ("required_behaviors", "forbidden_behaviors"):
            if not _nonempty_string_list(expected.get(field)):
                errors.append(f"{prefix}.expected.{field} must be a non-empty string list")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default="evals/pddr-recorder/cases.json",
        help="path to the eval suite JSON",
    )
    args = parser.parse_args()
    path = Path(args.path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {path}: {exc}", file=sys.stderr)
        return 2

    errors = validate_suite(data)
    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        print(f"FAILED: {len(errors)} eval suite issue(s)", file=sys.stderr)
        return 1
    print(f"OK: {len(data['cases'])} pddr-recorder eval case(s) validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
