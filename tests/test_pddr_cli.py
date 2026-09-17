import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("pddr_cli", ROOT / "scripts" / "pddr.py")
assert SPEC and SPEC.loader
pddr_cli = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = pddr_cli
SPEC.loader.exec_module(pddr_cli)


VALID_RECORD = """---
id: PDDR-0001
title: Test record
decision_date: 2026-09-17
recorded_date: 2026-09-17
decision_status: accepted
delivery_status: implemented
scope:
  - process
owners: []
evidence: []
related: []
supersedes: []
superseded_by: null
---

# PDDR-0001: Test record

## Summary
Test.

## Context and observations
Test.

## Options considered
Test.

## Decision
Test.

## Delivery and validation
Test.

## Consequences
Test.

## Revisit when
Test.

## Evidence
Test.

## Related records
None.
"""


class InitTests(unittest.TestCase):
    def test_init_creates_portable_files_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            args = type(
                "Args", (), {"target": str(target), "records_dir": "docs/records", "dry_run": False}
            )()
            self.assertEqual(pddr_cli.command_init(args), 0)
            self.assertTrue((target / ".pddr" / "config.json").is_file())
            self.assertTrue((target / ".pddr" / "pddr.py").is_file())
            self.assertTrue((target / ".pddr" / "template.md").is_file())
            self.assertTrue((target / "docs" / "records" / "README.md").is_file())
            self.assertEqual(pddr_cli.command_init(args), 0)
            installed = subprocess.run(
                [sys.executable, str(target / ".pddr" / "pddr.py"), "init", "--target", str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)

    def test_init_stops_before_writing_if_any_file_conflicts(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            conflict = target / ".pddr" / "config.json"
            conflict.parent.mkdir()
            conflict.write_text("different\n", encoding="utf-8")
            args = type(
                "Args", (), {"target": str(target), "records_dir": "docs/records", "dry_run": False}
            )()
            self.assertEqual(pddr_cli.command_init(args), 1)
            self.assertFalse((target / ".pddr" / "template.md").exists())


class ValidationTests(unittest.TestCase):
    def test_valid_record_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "PDDR-0001-test-record.md"
            path.write_text(VALID_RECORD, encoding="utf-8")
            metadata, diagnostics = pddr_cli.validate_record(path)
            self.assertEqual(metadata["id"], "PDDR-0001")
            self.assertEqual(diagnostics, [])

    def test_mismatched_filename_and_invalid_status_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "PDDR-0002-test-record.md"
            path.write_text(
                VALID_RECORD.replace("decision_status: accepted", "decision_status: maybe"),
                encoding="utf-8",
            )
            _, diagnostics = pddr_cli.validate_record(path)
            messages = {diagnostic.message for diagnostic in diagnostics}
            self.assertIn("front matter id does not match filename id", messages)
            self.assertIn("decision_status is not an allowed value", messages)

    def test_validated_record_requires_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "PDDR-0001-test-record.md"
            path.write_text(
                VALID_RECORD.replace("delivery_status: implemented", "delivery_status: validated"),
                encoding="utf-8",
            )
            _, diagnostics = pddr_cli.validate_record(path)
            self.assertIn(
                "validated records need metadata evidence",
                {diagnostic.message for diagnostic in diagnostics},
            )


if __name__ == "__main__":
    unittest.main()
