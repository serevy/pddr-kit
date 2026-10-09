"""Protect the opt-in, read-only Japanese prose review boundary."""

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / '.github' / 'workflows' / 'yomiyasu-review.yml'
PINNED_UPSTREAM = 'c2ffae670994fec96daef92e0bc219f5c1923113'


class YomiyasuReviewTests(unittest.TestCase):
    def test_manual_only_and_read_only(self):
        content = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('on:\n  workflow_dispatch:', content)
        triggers = content.split('\npermissions:', 1)[0]
        for forbidden_event in ('pull_request:', 'pull_request_target:', 'push:', 'workflow_run:', 'schedule:'):
            with self.subTest(event=forbidden_event):
                self.assertNotIn(forbidden_event, triggers)
        self.assertIn('permissions:\n  contents: read', content)
        self.assertNotIn('contents: write', content)
        self.assertNotIn('pull-requests: write', content)
        self.assertNotIn('issues: write', content)
        self.assertNotIn('--strict', content)
        self.assertNotIn('gh pr', content)
        self.assertNotIn('git push', content)

    def test_immutable_upstream_and_allowlisted_documents(self):
        content = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('repository: nanaism/yomiyasu', content)
        self.assertIn('ref: ' + PINNED_UPSTREAM, content)
        self.assertIn('persist-credentials: false', content)
        self.assertIn('python scripts/report_japanese_skill_candidates.py', content)
        self.assertNotIn('python scripts/report_japanese_skill_candidates.py --include-user', content)
        for expected in (
            "'readme': 'README.md'",
            "'adoption': 'docs/adoption.md'",
            "'skill-evaluation': 'docs/skill-evaluation.md'",
        ):
            self.assertIn(expected, content)
        self.assertNotIn('docs/records/', content)
        self.assertIn("raise SystemExit('Unsupported review target')", content)

    def test_guard_refuses_to_replace_existing_checkout(self):
        if shutil.which('bash') is None:
            self.skipTest('bash not installed')
        content = WORKFLOW.read_text(encoding='utf-8')
        guard = content.index('      - name: Protect an existing local review-tool directory')
        upstream = content.index('      - name: Check out pinned yomiyasu v1.1.0')
        self.assertLess(guard, upstream)
        segment = content[guard:upstream]
        self.assertIn('-L .external', segment)
        self.assertIn('-e .external/yomiyasu', segment)
        marker = '        run: |\n'
        self.assertIn(marker, segment)
        shell_script = textwrap.dedent(segment.split(marker, 1)[1])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checkout = root / '.external' / 'yomiyasu'
            checkout.mkdir(parents=True)
            sentinel = checkout / 'SKILL.md'
            sentinel.write_text('existing review tool\n', encoding='utf-8')
            result = subprocess.run(
                ['bash', '-e', '-c', shell_script], cwd=root,
                text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(sentinel.read_text(encoding='utf-8'), 'existing review tool\n')

    def test_existing_local_skill_is_reported_without_modification(self):
        detector = ROOT / 'scripts' / 'report_japanese_skill_candidates.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def skill(relative, value):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value, encoding='utf-8')
                return path

            existing = skill('.claude/skills/yomiyasu/SKILL.md', 'custom yomiyasu\n')
            alternative = skill(
                '.agents/skills/natural-japanese/SKILL.md',
                '---\nname: natural-japanese\ndescription: 日本語文章を校正する\n---\n',
            )
            nonoverlap = skill(
                '.agents/skills/japanese-translator/SKILL.md',
                '---\nname: japanese-translator\ndescription: Japanese translation\n---\n',
            )
            local_custom = skill(
                '.codex/skills/custom-review/SKILL.md',
                '---\nname: custom-review\ndescription: 日本語の文章を推敲する\n---\n',
            )
            result = subprocess.run(
                [sys.executable, str(detector), '--target', str(root)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            for path in (
                '.claude/skills/yomiyasu/SKILL.md',
                '.agents/skills/natural-japanese/SKILL.md',
                '.codex/skills/custom-review/SKILL.md',
            ):
                self.assertIn(path, result.stdout)
            self.assertNotIn('japanese-translator/SKILL.md', result.stdout)
            self.assertEqual(existing.read_bytes(), b'custom yomiyasu\n')
            self.assertIn('natural-japanese', alternative.read_text(encoding='utf-8'))
            self.assertIn('Japanese translation', nonoverlap.read_text(encoding='utf-8'))
            self.assertIn('日本語の文章を推敲する', local_custom.read_text(encoding='utf-8'))

    def test_user_scoped_skills_are_opt_in(self):
        detector = ROOT / 'scripts' / 'report_japanese_skill_candidates.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'project'
            home = root / 'home'
            project.mkdir()
            skill = home / '.agents/skills/natural-japanese/SKILL.md'
            skill.parent.mkdir(parents=True)
            skill.write_text('---\nname: natural-japanese\n---\n', encoding='utf-8')
            env = {**os.environ, 'HOME': str(home)}
            args = [sys.executable, str(detector), '--target', str(project)]
            basic = subprocess.run(args, env=env, text=True, capture_output=True, check=False)
            extended = subprocess.run(
                [*args, '--include-user'], env=env,
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(basic.returncode, 0, basic.stderr)
            self.assertEqual(extended.returncode, 0, extended.stderr)
            self.assertNotIn('natural-japanese/SKILL.md', basic.stdout)
            self.assertIn('user: .agents/skills/natural-japanese/SKILL.md', extended.stdout)

    def test_linked_parent_not_traversed(self):
        detector = ROOT / 'scripts' / 'report_japanese_skill_candidates.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / 'project'
            outside = root / 'outside'
            project.mkdir()
            target = outside / 'skills' / 'natural-japanese' / 'SKILL.md'
            target.parent.mkdir(parents=True)
            target.write_text('---\nname: natural-japanese\n---\n', encoding='utf-8')
            try:
                (project / '.claude').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('symlinks not supported')
            result = subprocess.run(
                [sys.executable, str(detector), '--target', str(project)],
                text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn('natural-japanese/SKILL.md', result.stdout)
            self.assertIn('linked parent directory not inspected', result.stdout)
            self.assertEqual(target.read_text(encoding='utf-8'), '---\nname: natural-japanese\n---\n')

    def test_installation_guidance_prefers_reuse_and_disclaims_global_coverage(self):
        guide = (ROOT / 'docs' / 'japanese-prose-review.md').read_text(encoding='utf-8')
        self.assertLess(guide.index('## 既存の日本語Skillがある場合'), guide.index('npx skills add'))
        self.assertIn('新規インストールより既存の運用を優先', guide)
        self.assertIn('別名の日本語推敲Skill', guide)
        self.assertIn('report_japanese_skill_candidates.py', guide)
        self.assertIn('プラグイン', guide)
        self.assertIn('導入先へインストールせず', guide)
        self.assertIn('`pddr-recorder`のみ', guide)

    def test_advisory_script_is_valid_python(self):
        content = WORKFLOW.read_text(encoding='utf-8')
        start = content.index("          python - <<'PY'\n") + len("          python - <<'PY'\n")
        end = content.index('\n          PY', start)
        code = textwrap.dedent(content[start:end])
        compile(code, str(WORKFLOW), 'exec')

    def test_trial_documentation_preserves_approval_and_evaluation_limits(self):
        readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        adoption = (ROOT / 'docs' / 'adoption.md').read_text(encoding='utf-8')
        eval_doc = (ROOT / 'docs' / 'skill-evaluation.md').read_text(encoding='utf-8')
        guide = (ROOT / 'docs' / 'japanese-prose-review.md').read_text(encoding='utf-8')
        self.assertIn('必要に応じて見直される', readme)
        self.assertIn('なぜ現在の形になったか', readme)
        self.assertIn('checkpointを設けることを推奨します', adoption)
        self.assertIn('revision-cases.json', eval_doc)
        self.assertIn('forward-testは未実施', eval_doc)
        self.assertIn(PINNED_UPSTREAM, guide)
        self.assertIn('PRの自動マージ', guide)


if __name__ == '__main__':
    unittest.main()
