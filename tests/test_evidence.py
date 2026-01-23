# ABOUTME: Tests for the evidence export module
# ABOUTME: Verifies evidence package generation and verification

import json
import os
import tempfile
import unittest
import zipfile
from unittest.mock import MagicMock, patch

from src.evidence import (
    create_evidence_package,
    verify_evidence_package,
    generate_manifest,
)


class TestEvidenceModule(unittest.TestCase):
    """Test cases for evidence module functions."""

    def test_generate_manifest(self):
        """Test evidence package manifest generation."""
        evidence_data = {
            "falco_alerts": [{"rule": "Test Alert"}],
            "argocd_history": [{"revision": "abc123"}],
            "kyverno_reports": [{"policy": "test-policy"}],
            "git_history": [{"hash": "abc123"}],
        }

        manifest = generate_manifest(evidence_data)

        self.assertIn("generated_at", manifest)
        self.assertIn("evidence_files", manifest)
        self.assertIn("counts", manifest)
        self.assertEqual(manifest["counts"]["falco_alerts"], 1)
        self.assertEqual(manifest["counts"]["argocd_history"], 1)

    def test_create_evidence_package(self):
        """Test creating evidence ZIP package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            evidence_data = {
                "falco_alerts": [{"rule": "Test Alert", "priority": "WARNING"}],
                "argocd_history": [{"revision": "abc123"}],
                "kyverno_reports": [{"policy": "test-policy"}],
                "git_history": [{"hash": "abc123", "message": "Test commit"}],
            }

            output_path = os.path.join(tmpdir, "evidence.zip")
            create_evidence_package(evidence_data, output_path)

            self.assertTrue(os.path.exists(output_path))

            with zipfile.ZipFile(output_path, "r") as zf:
                names = zf.namelist()
                self.assertIn("manifest.json", names)
                self.assertIn("falco/alerts.json", names)
                self.assertIn("argocd/sync-history.json", names)
                self.assertIn("kyverno/policy-reports.json", names)
                self.assertIn("git/commit-history.json", names)
                self.assertIn("README.md", names)

    def test_verify_evidence_package_valid(self):
        """Test verifying a valid evidence package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid package
            evidence_data = {
                "falco_alerts": [],
                "argocd_history": [],
                "kyverno_reports": [],
                "git_history": [],
            }
            output_path = os.path.join(tmpdir, "evidence.zip")
            create_evidence_package(evidence_data, output_path)

            result = verify_evidence_package(output_path)

            self.assertTrue(result["valid"])
            self.assertEqual(result["integrity"], "verified")

    def test_verify_evidence_package_missing_files(self):
        """Test verifying package with missing required files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create an incomplete package
            output_path = os.path.join(tmpdir, "bad-evidence.zip")
            with zipfile.ZipFile(output_path, "w") as zf:
                zf.writestr("manifest.json", "{}")

            result = verify_evidence_package(output_path)

            self.assertFalse(result["valid"])
            self.assertIn("missing_files", result)

    def test_verify_evidence_package_not_found(self):
        """Test verifying non-existent package."""
        result = verify_evidence_package("/nonexistent/path.zip")

        self.assertFalse(result["valid"])
        self.assertIn("error", result)

    @patch("subprocess.run")
    def test_collect_git_history(self, mock_run):
        """Test collecting git commit history."""
        from src.evidence import collect_git_history

        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc123|John Doe|john@example.com|2026-01-15T10:00:00|Initial commit\ndef456|Jane Doe|jane@example.com|2026-01-14T10:00:00|Add feature",
        )

        history = collect_git_history(days=30)

        self.assertIsInstance(history, list)
        mock_run.assert_called_once()


class TestEvidenceIntegration(unittest.TestCase):
    """Integration tests for evidence collection workflow."""

    def test_full_evidence_workflow(self):
        """Test complete evidence collection and packaging workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "full-evidence.zip")

            # Create evidence data directly (no mocking needed)
            evidence_data = {
                "falco_alerts": [{"rule": "Test", "time": "2026-01-15T10:00:00Z"}],
                "argocd_history": [{"revision": "abc123"}],
                "kyverno_reports": [{"policy": "require-labels"}],
                "git_history": [{"hash": "def456", "message": "Commit"}],
            }

            # Create package
            create_evidence_package(evidence_data, output_path)

            # Verify package
            result = verify_evidence_package(output_path)

            self.assertTrue(result["valid"])
            self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
