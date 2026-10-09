"""Protect the opt-in, read-only Japanese prose review boundary."""

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
