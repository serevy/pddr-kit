import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "pddr_checkpoint", ROOT / "scripts" / "pddr_checkpoint.py"
)
assert SPEC and SPEC.loader
checkpoint = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = checkpoint
SPEC.loader.exec_module(checkpoint)


class CheckpointSignalTests(unittest.TestCase):
    def test_agents_change_recommends_review(self):
        reasons = checkpoint.detect_reasons(["AGENTS.md"])
        self.assertTrue(reasons)
        self.assertIn("agent guidance changed", reasons[0])

    def test_nested_roadmap_change_recommends_review(self):
        reasons = checkpoint.detect_reasons(["docs/roadmap/phase-2.md"])
        self.assertTrue(any("roadmap surface changed" in reason for reason in reasons))

    def test_architecture_change_recommends_review(self):
        reasons = checkpoint.detect_reasons(["docs/architecture.md"])
        self.assertTrue(any("architecture surface changed" in reason for reason in reasons))

    def test_routine_source_change_does_not_recommend_review(self):
        self.assertEqual(checkpoint.detect_reasons(["src/widget.py", "README.md"]), [])

    def test_explicit_label_recommends_review(self):
        reasons = checkpoint.detect_reasons([], labels=["pddr-checkpoint"])
        self.assertIn("explicit label: `pddr-checkpoint`", reasons)

    def test_explicit_body_marker_recommends_review(self):
        reasons = checkpoint.detect_reasons(
            [], pr_body="Please review this phase boundary. [pddr-checkpoint]"
        )
        self.assertIn("explicit PR marker: `[pddr-checkpoint]`", reasons)

    def test_existing_checkpoint_heading_counts_as_review_surface(self):
        self.assertTrue(
            checkpoint.has_checkpoint_review(
                "## PDDR checkpoint\n\n- Review: completed\n"
            )
        )

    def test_pending_marker_is_advisory(self):
        marker = checkpoint.marker_markdown(["roadmap surface changed: `docs/roadmap.md`"])
        self.assertIn("- Review: pending", marker)
        self.assertIn("Checkpoint Signal ≠ PDDR required.", marker)
        self.assertIn(checkpoint.HIDDEN_MARKER, marker)


class CheckpointWorkflowSecurityTests(unittest.TestCase):
    def test_signal_workflow_is_read_only(self):
        workflow = (
            ROOT / "templates" / "checkpoint-ci" / "pddr-checkpoint.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("pull-requests: read", workflow)
        self.assertNotIn("pull-requests: write", workflow)
        self.assertNotIn("issues: write", workflow)

    def test_marker_writer_runs_from_trusted_default_branch(self):
        workflow = (
            ROOT / "templates" / "checkpoint-ci" / "pddr-checkpoint-marker.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("workflow_run:", workflow)
        self.assertIn('workflows: ["PDDR checkpoint"]', workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("issues: write", workflow)
        self.assertIn("github.event.repository.default_branch", workflow)
        self.assertNotIn("github.event.pull_request.head.sha", workflow)
        self.assertNotIn("allow-unsafe-pr-checkout", workflow)
        self.assertIn("Recompute checkpoint signal from trusted code", workflow)


if __name__ == "__main__":
    unittest.main()
