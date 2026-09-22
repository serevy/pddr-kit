import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_eval_validator", ROOT / "scripts" / "validate_skill_evals.py"
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def load_suite():
    return json.loads(
        (ROOT / "evals" / "pddr-recorder" / "cases.json").read_text(encoding="utf-8")
    )


def load_consumption_suite():
    return json.loads(
        (ROOT / "evals" / "pddr-recorder" / "consumption-cases.json").read_text(
            encoding="utf-8"
        )
    )


def load_milestone_audit_suite():
    return json.loads(
        (ROOT / "evals" / "pddr-recorder" / "milestone-audit-cases.json").read_text(
            encoding="utf-8"
        )
    )


class SkillEvalValidationTests(unittest.TestCase):
    def test_repository_suite_is_valid(self):
        suite = load_suite()
        self.assertEqual(validator.validate_suite(suite), [])

    def test_consumption_suite_is_valid(self):
        suite = load_consumption_suite()
        self.assertEqual(validator.validate_suite(suite), [])

    def test_milestone_audit_suite_is_valid(self):
        suite = load_milestone_audit_suite()
        self.assertEqual(validator.validate_suite(suite), [])

    def test_duplicate_case_id_is_rejected(self):
        suite = load_suite()
        suite["cases"][1]["id"] = suite["cases"][0]["id"]
        errors = validator.validate_suite(suite)
        self.assertTrue(any("duplicated" in error for error in errors))

    def test_invalid_status_is_rejected(self):
        suite = load_suite()
        suite["cases"][2]["expected"]["decision_status"] = "approved"
        errors = validator.validate_suite(suite)
        self.assertTrue(any("decision_status is invalid" in error for error in errors))

    def test_no_record_action_cannot_assert_status(self):
        suite = copy.deepcopy(load_suite())
        suite["cases"][0]["expected"]["decision_status"] = "accepted"
        errors = validator.validate_suite(suite)
        self.assertTrue(any("statuses must be null" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
