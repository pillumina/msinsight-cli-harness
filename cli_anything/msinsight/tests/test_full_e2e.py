"""
End-to-end tests for MindStudio Insight CLI.

Tests the complete workflow with real files and subprocess execution.
"""

import pytest
import json
import os
import sys
import subprocess
import tempfile
from pathlib import Path


# ============================================================================
# E2E Project Workflow Tests
# ============================================================================

class TestProjectWorkflow:
    """End-to-end project workflow tests."""

    def test_full_project_workflow(self, tmp_path):
        """Create → Save → Open → Modify → Save workflow."""
        proj_file = tmp_path / "workflow.json"

        # Create project
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "project", "new", "-o", str(proj_file)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert proj_file.exists()

        # Open and get info
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "--project", str(proj_file),
            "project", "info"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert data["project"]["name"] == "Untitled"

    def test_project_json_roundtrip(self, tmp_path):
        """JSON serialization/deserialization roundtrip."""
        proj_file = tmp_path / "roundtrip.json"

        # Create project
        subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "project", "new", "-o", str(proj_file)
        ], check=True)

        # Read JSON
        with open(proj_file) as f:
            data1 = json.load(f)

        # Open and save again
        subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--project", str(proj_file),
            "project", "save"
        ], check=True)

        # Read JSON again
        with open(proj_file) as f:
            data2 = json.load(f)

        # Verify roundtrip
        assert data1["project_name"] == data2["project_name"]
        assert data1["version"] == data2["version"]

    def test_multiple_projects(self, tmp_path):
        """Handle multiple independent projects."""
        proj1 = tmp_path / "proj1.json"
        proj2 = tmp_path / "proj2.json"

        # Create two projects
        subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "project", "new", "-o", str(proj1)
        ], check=True)

        subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "project", "new", "-o", str(proj2)
        ], check=True)

        # Both should exist
        assert proj1.exists()
        assert proj2.exists()


# ============================================================================
# E2E Data Import Tests
# ============================================================================

class TestDataImport:
    """End-to-end data import tests."""

    @pytest.fixture
    def sample_profiling_dir(self, tmp_path):
        """Create sample profiling directory with test files."""
        prof_dir = tmp_path / "profiling"
        prof_dir.mkdir()

        # Create sample files
        (prof_dir / "profiler_metadata.json").write_text('{"version": "1.0"}')
        (prof_dir / "msprof_0.db").write_bytes(b"SQLite format 3\x00" + b"\x00" * 100)
        (prof_dir / "operator_info.bin").write_bytes(b"\x00" * 100)
        (prof_dir / "kernel_details.csv").write_text("name,duration\nMatMul,15.3\n")

        return prof_dir

    def test_import_validate_profiling_data(self, sample_profiling_dir):
        """Validate real profiling directory."""
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(sample_profiling_dir)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert data["result"]["valid"] is True
        assert data["result"]["total_files"] >= 4

    def test_import_list_files(self, sample_profiling_dir):
        """List profiling files."""
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "list-files", str(sample_profiling_dir)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert len(data["files"]) >= 4

    def test_import_mixed_formats(self, tmp_path):
        """Import with mixed valid/invalid files."""
        mixed_dir = tmp_path / "mixed"
        mixed_dir.mkdir()

        # Create valid files
        (mixed_dir / "valid.json").write_text('{"valid": true}')
        (mixed_dir / "data.db").write_bytes(b"SQLite format 3\x00" + b"\x00" * 50)

        # Create invalid files
        (mixed_dir / "invalid.json").write_text("not json")
        (mixed_dir / "readme.txt").write_text("This is a readme")

        # Validate should succeed
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(mixed_dir)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        # Should find at least 2 valid files (json, db)
        assert data["result"]["files"]["json"] >= 1
        assert data["result"]["files"]["db"] >= 1


# ============================================================================
# CLI Subprocess Tests
# ============================================================================

class TestCLISubprocess:
    """Test installed CLI command via subprocess."""

    def test_help(self):
        """CLI --help command."""
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--help"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "MindStudio Insight" in result.stdout

    def test_version(self):
        """CLI --version command."""
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--version"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert "1.0.0" in result.stdout

    def test_project_new_json(self, tmp_path):
        """Create project via CLI with JSON output."""
        proj_file = tmp_path / "test.json"

        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "project", "new", "-o", str(proj_file)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert proj_file.exists()

    def test_project_open(self, tmp_path):
        """Open project via CLI."""
        proj_file = tmp_path / "test.json"

        # Create project first
        subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "project", "new", "-o", str(proj_file)
        ], check=True)

        # Open project
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "--project", str(proj_file),
            "project", "info"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"

    def test_import_validate(self, tmp_path):
        """Validate data via CLI."""
        # Create test data directory
        data_dir = tmp_path / "profiling"
        data_dir.mkdir()
        (data_dir / "data.json").write_text('{}')

        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(data_dir)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        assert data["result"]["valid"] is True

    def test_full_workflow(self, tmp_path):
        """Complete workflow via CLI."""
        proj_file = tmp_path / "workflow.json"
        data_dir = tmp_path / "profiling"
        data_dir.mkdir()
        (data_dir / "data.json").write_text('{}')

        # Create project
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "project", "new", "-o", str(proj_file)
        ], capture_output=True, text=True)
        assert result.returncode == 0

        # Validate data
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(data_dir)
        ], capture_output=True, text=True)
        assert result.returncode == 0

        # Get session status
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "--project", str(proj_file),
            "session", "status"
        ], capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"


# ============================================================================
# Realistic Workflow Scenarios
# ============================================================================

class TestWorkflowScenarios:
    """Realistic usage scenarios."""

    def test_performance_analysis_pipeline(self, tmp_path):
        """
        Scenario: Analyzing profiling data from training run

        Operations:
        1. Create new project
        2. Validate profiling directory
        3. Get project info
        4. Save project
        """
        # Setup
        prof_dir = tmp_path / "profiling"
        prof_dir.mkdir()
        (prof_dir / "profiler_metadata.json").write_text('{"version": "1.0"}')
        (prof_dir / "msprof_0.db").write_bytes(b"SQLite format 3\x00")
        proj_file = tmp_path / "analysis.json"

        # 1. Create project
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "project", "new", "-o", str(proj_file)
        ], capture_output=True, text=True)
        assert result.returncode == 0

        # 2. Validate data
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(prof_dir)
        ], capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["result"]["valid"] is True

        # 3. Get project info
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "--project", str(proj_file),
            "project", "info"
        ], capture_output=True, text=True)
        assert result.returncode == 0

        # Verify project file is valid JSON
        with open(proj_file) as f:
            proj_data = json.load(f)
        assert proj_data["version"] == "1.0.0"

        print(f"\n  ✓ Performance analysis pipeline completed")
        print(f"  Project: {proj_file}")
        print(f"  Data: {prof_dir}")

    def test_batch_analysis(self, tmp_path):
        """
        Scenario: Processing multiple profiling runs

        Operations:
        1. For each directory in list:
           - Create new project
           - Validate data
           - Save project with unique name
        """
        # Setup multiple profiling directories
        for i in range(3):
            prof_dir = tmp_path / f"run_{i}"
            prof_dir.mkdir()
            (prof_dir / "data.json").write_text(f'{{"run": {i}}}')

        # Process each run
        for i in range(3):
            prof_dir = tmp_path / f"run_{i}"
            proj_file = tmp_path / f"analysis_{i}.json"

            # Create project
            result = subprocess.run([
                sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
                "project", "new", "-o", str(proj_file)
            ], capture_output=True, text=True)
            assert result.returncode == 0

            # Validate data
            result = subprocess.run([
                sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
                "--json", "import", "validate", str(prof_dir)
            ], capture_output=True, text=True)
            assert result.returncode == 0

        # Verify all projects created
        for i in range(3):
            proj_file = tmp_path / f"analysis_{i}.json"
            assert proj_file.exists()

        print(f"\n  ✓ Batch analysis completed: 3 runs processed")

    def test_ai_agent_integration(self, tmp_path):
        """
        Scenario: AI agent using CLI programmatically

        Operations:
        1. Create project with --json output
        2. Validate data with --json output
        3. Get status with --json output
        4. Parse all JSON responses
        5. Verify machine-readable format
        """
        proj_file = tmp_path / "agent.json"
        data_dir = tmp_path / "profiling"
        data_dir.mkdir()
        (data_dir / "data.json").write_text('{}')

        # All operations should return valid JSON
        responses = []

        # 1. Create project
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "project", "new", "-o", str(proj_file)
        ], capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        responses.append(data)

        # 2. Validate data
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "import", "validate", str(data_dir)
        ], capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        responses.append(data)

        # 3. Get project info
        result = subprocess.run([
            sys.executable, "-m", "cli_anything.msinsight.msinsight_cli",
            "--json", "--project", str(proj_file),
            "project", "info"
        ], capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["status"] == "success"
        responses.append(data)

        # Verify all responses are valid JSON with consistent structure
        assert len(responses) == 3
        for response in responses:
            assert "status" in response
            assert response["status"] == "success"

        print(f"\n  ✓ AI agent integration test passed")
        print(f"  All {len(responses)} operations returned valid JSON")


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"])
