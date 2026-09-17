import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_eval_result_validator", ROOT / "scripts" / "validate_skill_eval_results.py"
)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


def load_inputs():
    suite = json.loads(
        (ROOT / "evals" / "pddr-recorder" / "cases.json").read_text(encoding="utf-8")
    )
    results = [json.loads(path.read_text(encoding="utf-8")) for path in validator.RESULT_FILES]
    adjudication = json.loads(validator.ADJUDICATION_FILE.read_text(encoding="utf-8"))
    return suite, results, adjudication


class SkillEvalResultValidationTests(unittest.TestCase):
    def test_repository_results_are_consistent(self):
        errors, summaries = validator.validate_results(*load_inputs())
        self.assertEqual(errors, [])
        self.assertEqual(summaries["gpt-5.6-sol"]["passed"], 11)
        self.assertEqual(summaries["gpt-5.6-luna"]["passed"], 10)

    def test_wrong_action_is_rejected(self):
        suite, results, adjudication = load_inputs()
        results = copy.deepcopy(results)
        results[0]["results"][0]["record_action"] = "create"
        errors, _ = validator.validate_results(suite, results, adjudication)
        self.assertTrue(any("record_action" in error for error in errors))

    def test_missing_review_is_rejected(self):
        suite, results, adjudication = load_inputs()
        adjudication = copy.deepcopy(adjudication)
        adjudication["reviews"].pop()
        errors, _ = validator.validate_results(suite, results, adjudication)
        self.assertTrue(any("review is missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
