#!/usr/bin/env python3
"""test_qa_enum_lint.py — Unit tests for validate_qa_request_enums.py
Asserts stdout content; exit code is always 0 (advisory script).
"""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SCRIPT = REPO_ROOT / "lean-kit/modules/validation-quality/scripts/validate_qa_request_enums.py"
FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "qa_request"

COMPLETE_CONTENT = (FIXTURE_DIR / "sample_complete.md").read_text(encoding="utf-8")
ERRORS_CONTENT = (FIXTURE_DIR / "sample_errors.md").read_text(encoding="utf-8")


def run_script(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(root)],
        capture_output=True,
        text=True,
    )


class TestQaEnumLint(unittest.TestCase):

    def test_valid_artifacts_no_warn(self):
        """Two valid QA_REQUEST.md files → no WARN: lines."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_a").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_b").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_a" / "QA_REQUEST.md").write_text(COMPLETE_CONTENT)
            (root / "_COMMUNICATION" / "team_b" / "QA_REQUEST.md").write_text(COMPLETE_CONTENT)
            result = run_script(root)
        self.assertNotIn("WARN:", result.stdout, msg=f"Unexpected WARN in stdout:\n{result.stdout}")

    def test_bad_verdict_emits_warn(self):
        """Artifact with invalid verdict → WARN: line mentioning 'verdict'."""
        bad_content = COMPLETE_CONTENT.replace("verdict: PASS", "verdict: APPROVED")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_qa").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_qa" / "QA_REQUEST.md").write_text(bad_content)
            result = run_script(root)
        self.assertIn("WARN:", result.stdout, msg="Expected WARN: line in stdout")
        self.assertIn("verdict", result.stdout, msg="Expected 'verdict' in WARN output")

    def test_bad_blocked_reason_emits_warn(self):
        """Artifact with invalid blocked_reason_code → WARN: line mentioning field."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_qa").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_qa" / "QA_REQUEST.md").write_text(ERRORS_CONTENT)
            result = run_script(root)
        self.assertIn("WARN:", result.stdout, msg="Expected WARN: line in stdout")
        self.assertIn("blocked_reason_code", result.stdout,
                      msg="Expected 'blocked_reason_code' in WARN output")

    def test_exit_code_always_zero(self):
        """Script exits 0 even when violations are found (advisory mode)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_qa").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_qa" / "QA_REQUEST.md").write_text(ERRORS_CONTENT)
            result = run_script(root)
        self.assertEqual(result.returncode, 0,
                         msg=f"Expected exit 0; got {result.returncode}\nstdout: {result.stdout}")

    def test_no_communication_dir_exits_zero(self):
        """Missing _COMMUNICATION/ → exit 0, no crash."""
        with tempfile.TemporaryDirectory() as tmp:
            result = run_script(Path(tmp))
        self.assertEqual(result.returncode, 0)

    def test_warn_format_includes_path_and_expected(self):
        """WARN line includes artifact path, field, got value, and expected values."""
        bad_content = COMPLETE_CONTENT.replace("verdict: PASS", "verdict: APPROVED")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_qa").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_qa" / "QA_REQUEST.md").write_text(bad_content)
            result = run_script(root)
        warn_lines = [l for l in result.stdout.splitlines() if l.startswith("WARN:")]
        self.assertTrue(warn_lines, "No WARN: lines found")
        line = warn_lines[0]
        self.assertIn("APPROVED", line, msg="got-value missing from WARN line")
        self.assertIn("PASS", line, msg="expected values missing from WARN line")

    def test_gate_field_not_flagged(self):
        """gate field is out of scope — must never produce a WARN:."""
        bad_gate = COMPLETE_CONTENT + "\n"
        # Replace gate value with something non-standard
        bad_gate = bad_gate.replace("gate: L-GATE_BUILD", "gate: INVALID_GATE_VALUE")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "_COMMUNICATION" / "team_qa").mkdir(parents=True)
            (root / "_COMMUNICATION" / "team_qa" / "QA_REQUEST.md").write_text(bad_gate)
            result = run_script(root)
        self.assertNotIn("WARN:", result.stdout,
                         msg="gate field must not be validated (out of scope)")


if __name__ == "__main__":
    unittest.main(verbosity=2)
