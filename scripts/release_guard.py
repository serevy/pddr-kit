#!/usr/bin/env python3
"""Validate repository metadata before publishing a PDDR Kit release."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
KIT_VERSION_RE = re.compile(r'^KIT_VERSION\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def validate_release(root: Path, expected_version: str, kind: str) -> list[str]:
    errors: list[str] = []

    if not SEMVER_RE.fullmatch(expected_version):
        errors.append(f"expected version is not supported SemVer: {expected_version}")

    is_prerelease = "-" in expected_version
    if kind == "stable" and is_prerelease:
        errors.append("stable release cannot use a prerelease version")
    if kind == "prerelease" and not is_prerelease:
        errors.append("prerelease kind requires a prerelease version")

    version_path = root / "VERSION"
    if not version_path.is_file():
        errors.append("VERSION file is missing")
    else:
        actual_version = version_path.read_text(encoding="utf-8").strip()
        if actual_version != expected_version:
            errors.append(
                f"VERSION mismatch: expected {expected_version}, found {actual_version}"
            )

    cli_path = root / "scripts" / "pddr.py"
    if not cli_path.is_file():
        errors.append("scripts/pddr.py is missing")
    else:
        match = KIT_VERSION_RE.search(cli_path.read_text(encoding="utf-8"))
        if not match:
            errors.append("KIT_VERSION was not found in scripts/pddr.py")
        elif match.group(1) != expected_version:
            errors.append(
                "KIT_VERSION mismatch: "
                f"expected {expected_version}, found {match.group(1)}"
            )

    release_note = root / "docs" / "releases" / f"v{expected_version}.md"
    if not release_note.is_file():
        errors.append(f"release note is missing: docs/releases/v{expected_version}.md")

    changelog_path = root / "CHANGELOG.md"
    if not changelog_path.is_file():
        errors.append("CHANGELOG.md is missing")
    else:
        changelog = changelog_path.read_text(encoding="utf-8")
        heading = re.compile(
            rf"^## \[{re.escape(expected_version)}\](?:\s+-\s+\d{{4}}-\d{{2}}-\d{{2}})?\s*$",
            re.MULTILINE,
        )
        if not heading.search(changelog):
            errors.append(
                f"CHANGELOG.md has no release section for {expected_version}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-version", required=True)
    parser.add_argument("--kind", choices=("stable", "prerelease"), required=True)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()

    errors = validate_release(args.root, args.expected_version, args.kind)
    if errors:
        for error in errors:
            print(f"release guard: {error}", file=sys.stderr)
        return 1

    print(
        f"release guard: {args.kind} v{args.expected_version} metadata is consistent"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
