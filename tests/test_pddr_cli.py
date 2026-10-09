import importlib.util
import json
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


class VersionTests(unittest.TestCase):
    def test_cli_version_matches_version_file(self):
        self.assertEqual(
            pddr_cli.KIT_VERSION,
            (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        )


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
            self.assertTrue((target / ".pddr" / "manifest.json").is_file())
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


class UpgradeTests(unittest.TestCase):
    @staticmethod
    def args(target, *, dry_run=False, bootstrap_manifest=False, include_skill=False, skill_path=None):
        return type(
            "Args",
            (),
            {
                "target": str(target),
                "dry_run": dry_run,
                "bootstrap_manifest": bootstrap_manifest,
                "include_skill": include_skill,
                "skill_path": skill_path,
            },
        )()

    @staticmethod
    def init(target):
        args = type(
            "Args", (), {"target": str(target), "records_dir": "docs/records", "dry_run": False}
        )()
        return pddr_cli.command_init(args)

    def test_upgrade_updates_only_clean_managed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.init(target), 0)
            installed = target / ".pddr" / "template.md"
            installed.write_bytes(b"old template\n")
            manifest_path = target / ".pddr" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["kit_version"] = "legacy-test"
            manifest["managed_files"][".pddr/template.md"] = pddr_cli._sha256(
                installed.read_bytes()
            )
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            config_before = (target / ".pddr" / "config.json").read_bytes()

            self.assertEqual(pddr_cli.command_upgrade(self.args(target)), 0)
            self.assertEqual(
                installed.read_bytes(), (ROOT / "templates" / "pddr.md").read_bytes()
            )
            self.assertEqual((target / ".pddr" / "config.json").read_bytes(), config_before)
            updated = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["kit_version"], pddr_cli.KIT_VERSION)

    def test_upgrade_dry_run_does_not_change_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.init(target), 0)
            installed = target / ".pddr" / "template.md"
            installed.write_bytes(b"old template\n")
            manifest_path = target / ".pddr" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["managed_files"][".pddr/template.md"] = pddr_cli._sha256(
                installed.read_bytes()
            )
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            before = installed.read_bytes()

            self.assertEqual(
                pddr_cli.command_upgrade(self.args(target, dry_run=True)), 0
            )
            self.assertEqual(installed.read_bytes(), before)

    def test_upgrade_stops_before_writing_on_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.init(target), 0)
            customized = target / ".pddr" / "template.md"
            customized.write_text("project customization\n", encoding="utf-8")
            installed_cli = target / ".pddr" / "pddr.py"
            before = installed_cli.read_bytes()

            self.assertEqual(pddr_cli.command_upgrade(self.args(target)), 1)
            self.assertEqual(installed_cli.read_bytes(), before)
            self.assertEqual(customized.read_text(encoding="utf-8"), "project customization\n")

    def test_installed_copy_cannot_upgrade_itself(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.init(target), 0)
            installed = subprocess.run(
                [
                    sys.executable,
                    str(target / ".pddr" / "pddr.py"),
                    "upgrade",
                    "--target",
                    str(target),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(installed.returncode, 2)
            self.assertIn("run upgrade from a newer PDDR Kit checkout", installed.stderr)

    def test_legacy_bootstrap_only_creates_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.init(target), 0)
            manifest_path = target / ".pddr" / "manifest.json"
            manifest_path.unlink()
            managed_before = {
                path: (target / path).read_bytes() for path in pddr_cli.MANAGED_PATHS
            }

            self.assertEqual(
                pddr_cli.command_upgrade(self.args(target, bootstrap_manifest=True)), 0
            )
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["kit_version"], "legacy")
            self.assertEqual(
                {path: (target / path).read_bytes() for path in pddr_cli.MANAGED_PATHS},
                managed_before,
            )




class SkillUpgradeTests(unittest.TestCase):
    SKILL_PATH = ".claude/skills/pddr-recorder/SKILL.md"

    @staticmethod
    def initialize(target):
        args = type("Args", (), {
            "target": str(target), "records_dir": "docs/records", "dry_run": False
        })()
        return pddr_cli.command_init(args)

    @staticmethod
    def upgrade(target, *, include_skill=True, skill_path=None, dry_run=False):
        args = type("Args", (), {
            "target": str(target), "dry_run": dry_run, "bootstrap_manifest": False,
            "include_skill": include_skill, "skill_path": skill_path,
        })()
        return pddr_cli.command_upgrade(args)

    @staticmethod
    def manifest(target):
        return json.loads(
            (target / ".pddr" / "skill-manifest.json").read_text(encoding="utf-8")
        )

    def test_first_opt_in_and_noop_with_saved_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            installed = target / self.SKILL_PATH
            expected = (ROOT / "skills" / "pddr-recorder" / "SKILL.md").read_bytes()
            self.assertEqual(installed.read_bytes(), expected)
            manifest = self.manifest(target)
            self.assertEqual(manifest["skill_path"], self.SKILL_PATH)
            self.assertEqual(manifest["source_kit_version"], pddr_cli.KIT_VERSION)
            self.assertEqual(manifest["sha256"], pddr_cli._sha256(expected))
            before = (target / ".pddr" / "skill-manifest.json").read_bytes()

            self.assertEqual(self.upgrade(target), 0)
            self.assertEqual((target / ".pddr" / "skill-manifest.json").read_bytes(), before)
            self.assertEqual(self.upgrade(target, include_skill=False), 0)
            self.assertEqual((target / ".pddr" / "skill-manifest.json").read_bytes(), before)

    def test_opt_in_dry_run_does_not_install_or_track_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            core_before = (target / ".pddr" / "manifest.json").read_bytes()
            self.assertEqual(
                self.upgrade(target, skill_path=self.SKILL_PATH, dry_run=True), 0
            )
            self.assertFalse((target / self.SKILL_PATH).exists())
            self.assertFalse((target / ".pddr" / "skill-manifest.json").exists())
            self.assertEqual((target / ".pddr" / "manifest.json").read_bytes(), core_before)

    def test_modified_skill_conflict_stops_core_upgrade_too(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            skill = target / self.SKILL_PATH
            skill.write_text("locally modified\n", encoding="utf-8")
            template = target / ".pddr" / "template.md"
            template.write_bytes(b"previous tracked template\n")
            core_manifest = target / ".pddr" / "manifest.json"
            state = json.loads(core_manifest.read_text(encoding="utf-8"))
            state["managed_files"][".pddr/template.md"] = pddr_cli._sha256(
                template.read_bytes()
            )
            core_manifest.write_text(json.dumps(state) + "\n", encoding="utf-8")
            before = core_manifest.read_bytes()
            skill_manifest_before = (target / ".pddr" / "skill-manifest.json").read_bytes()
            self.assertEqual(self.upgrade(target), 1)
            self.assertEqual(template.read_bytes(), b"previous tracked template\n")
            self.assertEqual(core_manifest.read_bytes(), before)
            self.assertEqual(skill.read_text(encoding="utf-8"), "locally modified\n")
            self.assertEqual((target / ".pddr" / "skill-manifest.json").read_bytes(),
                             skill_manifest_before)

    def test_missing_or_untracked_different_skill_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            skill = target / self.SKILL_PATH
            skill.parent.mkdir(parents=True)
            skill.write_text("consumer customization\n", encoding="utf-8")
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 1)
            self.assertEqual(skill.read_text(encoding="utf-8"), "consumer customization\n")
            self.assertFalse((target / ".pddr" / "skill-manifest.json").exists())
            skill.unlink()
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            skill.unlink()
            self.assertEqual(self.upgrade(target), 1)
            self.assertFalse(skill.exists())

    def test_same_source_preinstalled_file_can_be_enrolled(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            skill = target / self.SKILL_PATH
            skill.parent.mkdir(parents=True)
            source = (ROOT / "skills" / "pddr-recorder" / "SKILL.md").read_bytes()
            skill.write_bytes(source)
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            self.assertEqual(skill.read_bytes(), source)
            self.assertEqual(self.manifest(target)["sha256"], pddr_cli._sha256(source))

    def test_path_override_mismatch_requires_explicit_reenrollment(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            other = ".agents/skills/pddr-recorder/SKILL.md"
            self.assertEqual(self.upgrade(target, skill_path=other), 1)
            self.assertFalse((target / other).exists())
            self.assertEqual(self.manifest(target)["skill_path"], self.SKILL_PATH)

    def test_unsafe_paths_and_symlink_parents_fail_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "project"
            outside = Path(directory) / "outside"
            outside.mkdir()
            target.mkdir()
            self.assertEqual(self.initialize(target), 0)
            for unsafe in (
                "../outside/SKILL.md", "/tmp/outside/SKILL.md",
                ".git/hooks/SKILL.md", ".pddr/SKILL.md",
                "C:\\outside\\SKILL.md", "nested//SKILL.md",
            ):
                with self.subTest(path=unsafe):
                    self.assertNotEqual(self.upgrade(target, skill_path=unsafe), 0)
                    self.assertFalse((target / ".pddr" / "skill-manifest.json").exists())
            link = target / "external"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("symlinks are unavailable on this filesystem")
            self.assertEqual(self.upgrade(target, skill_path="external/SKILL.md"), 1)
            self.assertFalse((outside / "SKILL.md").exists())
            self.assertFalse((target / ".pddr" / "skill-manifest.json").exists())

    def test_corrupted_skill_manifest_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            self.assertEqual(self.upgrade(target, skill_path=self.SKILL_PATH), 0)
            manifest_path = target / ".pddr" / "skill-manifest.json"
            manifest_path.write_text('{"schema_version": 1, "skill_path": "../oops", "sha256": "invalid"}\n')
            before = manifest_path.read_bytes()
            self.assertEqual(self.upgrade(target), 1)
            self.assertEqual(manifest_path.read_bytes(), before)

    def test_skill_path_requires_explicit_include_and_cannot_bootstrap_together(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(self.initialize(target), 0)
            self.assertEqual(
                self.upgrade(target, include_skill=False, skill_path=self.SKILL_PATH), 2
            )
            args = type("Args", (), {
                "target": str(target), "bootstrap_manifest": True, "dry_run": False,
                "include_skill": True, "skill_path": self.SKILL_PATH,
            })()
            self.assertEqual(pddr_cli.command_upgrade(args), 2)
            self.assertFalse((target / ".pddr" / "skill-manifest.json").exists())




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

    def test_unknown_delivery_status_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "PDDR-0001-test-record.md"
            path.write_text(
                VALID_RECORD.replace("delivery_status: implemented", "delivery_status: unknown"),
                encoding="utf-8",
            )
            _, diagnostics = pddr_cli.validate_record(path)
            self.assertEqual(diagnostics, [])


if __name__ == "__main__":
    unittest.main()
