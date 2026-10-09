#!/usr/bin/env python3
"""Advisory inventory of conventional Japanese prose Agent Skill locations.

No skill is executed, imported, installed, removed, or modified. File name and
front matter heuristics identify candidates only; they cannot prove activation,
conflicts, correctness, or absence of plugins and custom rules.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SKILL_DIRS = (
    ".agents/skills",
    ".claude/skills",
    ".codex/skills",
    ".cursor/skills",
    "skills",
)
JAPANESE_HINT = re.compile(r"日本語|和文|japanese|nihongo|(?:^|[-_])jp(?:$|[-_])", re.I)
PROSE_HINT = re.compile(
    r"推敲|校正|文章|文体|執筆|読みやす|書き直|ライティング|"
    r"writing|proofread|copyedit|rewrite|prose|natural|slop|style",
    re.I,
)
FRONT_FIELD = re.compile(r"^(?:name|description)\s*:\s*(.*)$", re.I | re.M)
MAX_SKILLS_PER_ROOT = 128
MAX_HEADER_BYTES = 4096


def _skill_header(path: Path) -> str:
    """Read a bounded YAML header as text only; never execute Skill content."""
    if path.is_symlink() or not path.is_file():
        return ""
    try:
        with path.open("rb") as stream:
            content = stream.read(MAX_HEADER_BYTES).decode("utf-8", errors="replace")
    except OSError:
        return ""
    if not content.startswith("---\n"):
        return ""
    ending = content.find("\n---", 4)
    return content[4:ending] if ending >= 0 else content[4:]


def find_candidates(root: Path) -> tuple[list[str], list[str]]:
    """Inspect only immediate Skill children under conventional directories."""
    detected: list[str] = []
    caveats: list[str] = []
    for prefix in SKILL_DIRS:
        parent = root
        linked_ancestor = False
        for component in Path(prefix).parts:
            parent = parent / component
            if parent.is_symlink():
                linked_ancestor = True
                caveats.append(f"{prefix}: linked parent directory not inspected")
                break
        # Do not follow linked folders that could point outside the requested root.
        if linked_ancestor or not parent.is_dir():
            continue
        try:
            children = sorted(parent.iterdir(), key=lambda p: p.name)
        except OSError:
            caveats.append(f"{prefix}: cannot inspect directory")
            continue
        if len(children) > MAX_SKILLS_PER_ROOT:
            caveats.append(f"{prefix}: candidate count exceeds {MAX_SKILLS_PER_ROOT}; inspect manually")
        for child in children[:MAX_SKILLS_PER_ROOT]:
            if child.is_symlink() or not child.is_dir():
                continue
            skill_file = child / "SKILL.md"
            if skill_file.is_symlink():
                caveats.append(f"{prefix}/{child.name}: linked Skill not inspected")
                continue
            header = _skill_header(skill_file)
            metadata = " ".join(FRONT_FIELD.findall(header))
            searchable = f"{child.name} {metadata}"
            # Candidate for human inspection, not proof of an overlapping role.
            if child.name.casefold() == "yomiyasu" or (
                JAPANESE_HINT.search(searchable) and PROSE_HINT.search(searchable)
            ):
                detected.append(f"{prefix}/{child.name}/SKILL.md")
    return detected, caveats


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target", type=Path, default=Path("."),
        help="project root to inspect; only conventional Skill directories are scanned",
    )
    parser.add_argument(
        "--include-user", action="store_true",
        help="also inspect conventional Skill directories in the current user's home",
    )
    args = parser.parse_args()
    if not args.target.is_dir():
        parser.error("--target must be an existing directory")
    targets = [("project", args.target)]
    if args.include_user:
        targets.append(("user", Path.home()))

    print("Advisory: possible Japanese prose Skill overlap (presence is not activation).")
    print("No Skill files will be changed. Check plugins and custom agent rules manually.")
    found_any = False
    for scope, root in targets:
        found, caveats = find_candidates(root)
        for path in found:
            found_any = True
            print(f"{scope}: {path} (review its role before installing another)")
        for note in caveats:
            print(f"{scope}: not inspected: {note}")
    if not found_any:
        print("No candidates found in scanned conventional paths; absence is NOT verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
