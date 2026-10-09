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
        content = WORKFLOW.read_text(encoding='utf-8')
        start = content.index('      - name: Report pre-existing project Skill candidates')
        end = content.index('      - name: Set up Python', start)
        part = content[start:end]
        start_py = part.index("          python - <<'PY'\n") + len("          python - <<'PY'\n")
        end_py = part.index('\n          PY', start_py)
        script = textwrap.dedent(part[start_py:end_py])
        compile(script, str(WORKFLOW), 'exec')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / '.claude' / 'skills' / 'yomiyasu' / 'SKILL.md'
            destination.parent.mkdir(parents=True)
            destination.write_bytes(b'project-customized yomiyasu\n')
            summary = root / 'summary.md'
            result = subprocess.run(
                [sys.executable, '-c', script],
                cwd=root, env={**os.environ, 'GITHUB_STEP_SUMMARY': str(summary)},
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('.claude/skills/yomiyasu/SKILL.md', summary.read_text(encoding='utf-8'))
            self.assertIn('presence only; active version not verified', summary.read_text(encoding='utf-8'))
            self.assertEqual(destination.read_bytes(), b'project-customized yomiyasu\n')

    def test_installation_guidance_prefers_reuse_and_disclaims_global_coverage(self):
        guide = (ROOT / 'docs' / 'japanese-prose-review.md').read_text(encoding='utf-8')
        self.assertLess(guide.index('## 既存のyomiyasuがある場合'), guide.index('npx skills add'))
        self.assertIn('新規インストールより再利用を優先', guide)
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
