#!/usr/bin/env python3
"""Validate recorded Skill forward-test results and their adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "evals" / "pddr-recorder" / "results"
RESULT_FILES = (
    RESULTS_DIR / "2026-09-18-gpt-5.6-sol.json",
    RESULTS_DIR / "2026-09-18-gpt-5.6-luna.json",
)
ADJUDICATION_FILE = RESULTS_DIR / "2026-09-18-adjudication.json"
SNAPSHOT_DIR = ROOT / "evals" / "pddr-recorder" / "snapshots" / "2026-09-18"
SOURCE_FILES = {
    "skill_sha256": SNAPSHOT_DIR / "SKILL.md",
    "specification_sha256": SNAPSHOT_DIR / "specification.md",
    "template_sha256": SNAPSHOT_DIR / "template.md",
}
CONSUMPTION_RESULT_FILES = (
    RESULTS_DIR / "2026-09-18-consumption-gpt-5.6-sol.json",
    RESULTS_DIR / "2026-09-18-consumption-gpt-5.6-luna.json",
)
CONSUMPTION_ADJUDICATION_FILE = (
    RESULTS_DIR / "2026-09-18-consumption-adjudication.json"
)
CONSUMPTION_SNAPSHOT_DIR = (
    ROOT / "evals" / "pddr-recorder" / "snapshots" / "2026-09-18-consumption"
)
CONSUMPTION_SOURCE_FILES = {
    "skill_sha256": CONSUMPTION_SNAPSHOT_DIR / "SKILL.md",
    "specification_sha256": CONSUMPTION_SNAPSHOT_DIR / "specification.md",
    "template_sha256": CONSUMPTION_SNAPSHOT_DIR / "template.md",
}
RECORD_ACTIONS = {"none", "analyze-only", "create", "update", "create-successor"}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_results(
    suite: Any,
    result_documents: list[Any],
    adjudication: Any,
    source_files: dict[str, Path] = SOURCE_FILES,
) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    if not isinstance(suite, dict) or not isinstance(suite.get("cases"), list):
        return ["suite cases are missing"], {}
    expected_by_id = {case["id"]: case["expected"] for case in suite["cases"]}

    reviews: dict[tuple[str, str], Any] = {}
    if not isinstance(adjudication, dict) or adjudication.get("schema_version") != 1:
        errors.append("adjudication schema_version must be 1")
    for review in adjudication.get("reviews", []) if isinstance(adjudication, dict) else []:
        key = (review.get("model"), review.get("id"))
        if key in reviews:
            errors.append(f"duplicate adjudication review: {key}")
        reviews[key] = review

    computed: dict[str, dict[str, Any]] = {}
    for document in result_documents:
        if not isinstance(document, dict) or document.get("schema_version") != 1:
            errors.append("result schema_version must be 1")
            continue
        run = document.get("run", {})
        model = run.get("model")
        if not isinstance(model, str) or not model:
            errors.append("result model must be a non-empty string")
            continue
        for field, path in source_files.items():
            if run.get(field) != _sha256(path):
                errors.append(f"{model}: {field} does not match {path.relative_to(ROOT)}")

        results = document.get("results")
        if not isinstance(results, list):
            errors.append(f"{model}: results must be a list")
            continue
        by_id = {result.get("id"): result for result in results if isinstance(result, dict)}
        if set(by_id) != set(expected_by_id) or len(results) != len(expected_by_id):
            errors.append(f"{model}: result case IDs do not match the suite")
            continue

        failed_ids: list[str] = []
        for case_id, expected in expected_by_id.items():
            result = by_id[case_id]
            automatic_pass = True
            for field in ("should_invoke", "record_action"):
                if result.get(field) != expected[field]:
                    errors.append(
                        f"{model}/{case_id}: {field} is {result.get(field)!r}, "
                        f"expected {expected[field]!r}"
                    )
                    automatic_pass = False
            if result.get("record_action") not in RECORD_ACTIONS:
                errors.append(f"{model}/{case_id}: record_action is invalid")
                automatic_pass = False
            # Statuses are scored only when the case asserts a record state.
            for field in ("decision_status", "delivery_status"):
                if expected[field] is not None and result.get(field) != expected[field]:
                    errors.append(
                        f"{model}/{case_id}: {field} is {result.get(field)!r}, "
                        f"expected {expected[field]!r}"
                    )
                    automatic_pass = False
            if not isinstance(result.get("response"), str) or not result["response"].strip():
                errors.append(f"{model}/{case_id}: response must be non-empty")
                automatic_pass = False

            review = reviews.get((model, case_id))
            if not isinstance(review, dict):
                errors.append(f"{model}/{case_id}: adjudication review is missing")
                semantic_pass = False
            else:
                required_met = review.get("required_behaviors_met")
                forbidden_observed = review.get("forbidden_behaviors_observed")
                if not isinstance(required_met, bool) or not isinstance(
                    forbidden_observed, bool
                ):
                    errors.append(f"{model}/{case_id}: adjudication booleans are invalid")
                    semantic_pass = False
                else:
                    semantic_pass = required_met and not forbidden_observed
            if not (automatic_pass and semantic_pass):
                failed_ids.append(case_id)

        computed[model] = {
            "passed": len(expected_by_id) - len(failed_ids),
            "failed": len(failed_ids),
            "failed_case_ids": failed_ids,
        }

    declared = {
        summary.get("model"): {
            "passed": summary.get("passed"),
            "failed": summary.get("failed"),
            "failed_case_ids": summary.get("failed_case_ids"),
        }
        for summary in adjudication.get("summaries", [])
        if isinstance(summary, dict)
    }
    if declared != computed:
        errors.append("declared summaries do not match computed results")
    return errors, computed


def main() -> int:
    evaluations = (
        (
            "recording",
            ROOT / "evals" / "pddr-recorder" / "cases.json",
            RESULT_FILES,
            ADJUDICATION_FILE,
            SOURCE_FILES,
        ),
        (
            "consumption",
            ROOT / "evals" / "pddr-recorder" / "consumption-cases.json",
            CONSUMPTION_RESULT_FILES,
            CONSUMPTION_ADJUDICATION_FILE,
            CONSUMPTION_SOURCE_FILES,
        ),
    )
    all_errors: list[str] = []
    summaries_by_evaluation: list[tuple[str, int, dict[str, dict[str, Any]]]] = []
    try:
        for name, suite_path, result_paths, adjudication_path, source_files in evaluations:
            suite = _read_json(suite_path)
            results = [_read_json(path) for path in result_paths]
            adjudication = _read_json(adjudication_path)
            errors, summaries = validate_results(
                suite, results, adjudication, source_files
            )
            all_errors.extend(f"{name}: {error}" for error in errors)
            summaries_by_evaluation.append((name, len(suite["cases"]), summaries))
    except (OSError, UnicodeError, json.JSONDecodeError, KeyError) as exc:
        print(f"error: cannot read evaluation evidence: {exc}", file=sys.stderr)
        return 2

    for error in all_errors:
        print(error, file=sys.stderr)
    if all_errors:
        print(f"FAILED: {len(all_errors)} result issue(s)", file=sys.stderr)
        return 1
    for name, case_count, summaries in summaries_by_evaluation:
        for model, summary in summaries.items():
            print(
                f"{name}/{model}: {summary['passed']}/{case_count} passed; "
                f"failed={summary['failed_case_ids']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
