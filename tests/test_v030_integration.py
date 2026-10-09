"""Consumer-facing smoke tests for v0.3.0 optional Skill adoption."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "pddr.py"
SKILL_SOURCE = ROOT / "skills" / "pddr-recorder" / "SKILL.md"
SKILL_DESTINATION = ".claude/skills/pddr-recorder/SKILL.md"
README_PATHS = (
    "README.md",
    "README.en.md",
    "README.zh-CN.md",
    "README.ko.md",
    "README.fr.md",
)


def run_cli(*args):
    return subprocess.run(
        [sys.executable, str(CLI), *map(str, args)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class ConsumerUpgradeSmokeTests(unittest.TestCase):
    def test_init_opt_in_skill_dry_run_upgrade_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "consumer"
            target.mkdir()

            result = run_cli("init", "--target", target)
            self.assertEqual(result.returncode, 0, result.stderr)
            core_manifest_path = target / ".pddr" / "manifest.json"
            original_core_manifest = core_manifest_path.read_bytes()
            optional_manifest_path = target / ".pddr" / "skill-manifest.json"
            installed_skill_path = target / SKILL_DESTINATION
            self.assertFalse(installed_skill_path.exists())

            preview = run_cli(
                "upgrade", "--target", target, "--include-skill",
                "--skill-path", SKILL_DESTINATION, "--dry-run",
            )
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertIn("Would update: " + SKILL_DESTINATION, preview.stdout)
            self.assertFalse(installed_skill_path.exists())
            self.assertFalse(optional_manifest_path.exists())
            self.assertEqual(core_manifest_path.read_bytes(), original_core_manifest)

            installed = run_cli(
                "upgrade", "--target", target, "--include-skill",
                "--skill-path", SKILL_DESTINATION,
            )
            self.assertEqual(installed.returncode, 0, installed.stderr)
            source_bytes = SKILL_SOURCE.read_bytes()
            self.assertEqual(installed_skill_path.read_bytes(), source_bytes)
            installed_manifest = json.loads(optional_manifest_path.read_text(encoding="utf-8"))
            product_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
            self.assertEqual(installed_manifest["source_kit_version"], product_version)
            self.assertEqual(installed_manifest["skill_path"], SKILL_DESTINATION)
            self.assertEqual(
                installed_manifest["sha256"],
                "sha256:" + hashlib.sha256(source_bytes).hexdigest(),
            )
            core_manifest = json.loads(core_manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(core_manifest["kit_version"], product_version)
            self.assertNotIn(SKILL_DESTINATION, core_manifest["managed_files"])

            next_preview = run_cli("upgrade", "--target", target, "--include-skill", "--dry-run")
            self.assertEqual(next_preview.returncode, 0, next_preview.stderr)
            self.assertIn("Unchanged: " + SKILL_DESTINATION, next_preview.stdout)
            repeat = run_cli("upgrade", "--target", target, "--include-skill")
            self.assertEqual(repeat.returncode, 0, repeat.stderr)

            validation = run_cli(
                "validate", "--target", target, "--allow-empty",
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_readme_localizations_include_same_opt_in_command(self):
        command = (
            "python scripts/pddr.py upgrade --target /path/to/your-project "
            "--include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md"
        )
        for relative in README_PATHS:
            with self.subTest(readme=relative):
                content = (ROOT / relative).read_text(encoding="utf-8")
                self.assertIn(command + " --dry-run", content)
                self.assertIn(command + "\n", content)
                self.assertIn("docs/concurrent-record-ids.md", content)
                self.assertIn("CLAUDE.md", content)
                self.assertIn("AGENTS.md", content)


if __name__ == "__main__":
    unittest.main()
