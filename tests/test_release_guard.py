import tempfile
import unittest
from pathlib import Path

from scripts.release_guard import validate_release


def write_release_fixture(root: Path, version: str) -> None:
    (root / "scripts").mkdir(parents=True)
    (root / "docs" / "releases").mkdir(parents=True)
    (root / "VERSION").write_text(version + "\n", encoding="utf-8")
    (root / "scripts" / "pddr.py").write_text(
        f'KIT_VERSION = "{version}"\n',
        encoding="utf-8",
    )
    (root / "docs" / "releases" / f"v{version}.md").write_text(
        f"# PDDR Kit v{version}\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        f"# Changelog\n\n## [{version}] - 2026-09-23\n",
        encoding="utf-8",
    )


class ReleaseGuardTests(unittest.TestCase):
    def test_stable_release_metadata_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_release_fixture(root, "0.3.0")
            self.assertEqual(validate_release(root, "0.3.0", "stable"), [])

    def test_prerelease_metadata_passes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_release_fixture(root, "0.3.0-rc.1")
            self.assertEqual(
                validate_release(root, "0.3.0-rc.1", "prerelease"),
                [],
            )

    def test_version_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_release_fixture(root, "0.3.0")
            errors = validate_release(root, "0.3.1", "stable")
            self.assertTrue(any("VERSION mismatch" in error for error in errors))
            self.assertTrue(any("KIT_VERSION mismatch" in error for error in errors))

    def test_release_kind_must_match_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_release_fixture(root, "0.3.0-rc.1")
            errors = validate_release(root, "0.3.0-rc.1", "stable")
            self.assertIn(
                "stable release cannot use a prerelease version",
                errors,
            )

    def test_release_note_and_changelog_are_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_release_fixture(root, "0.3.0")
            (root / "docs" / "releases" / "v0.3.0.md").unlink()
            (root / "CHANGELOG.md").write_text("# Changelog\n", encoding="utf-8")
            errors = validate_release(root, "0.3.0", "stable")
            self.assertTrue(any("release note is missing" in error for error in errors))
            self.assertTrue(any("CHANGELOG.md has no release section" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
