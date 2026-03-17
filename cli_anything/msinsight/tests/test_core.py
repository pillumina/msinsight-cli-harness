"""
Unit tests for MindStudio Insight CLI core modules.

Tests all core functionality with synthetic data and no external dependencies.
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from cli_anything.msinsight.core import (
    project,
    session,
    import_data,
)
from cli_anything.msinsight.utils import msinsight_backend


# ============================================================================
# Project Management Tests
# ============================================================================

class TestProject:
    """Tests for project management module."""

    def test_create_project_default(self):
        """Create project with default parameters."""
        proj = project.create_project()

        assert proj is not None
        assert proj.name == "Untitled"
        assert proj.version == "1.0.0"
        assert proj.path is None
        assert proj.data_sources == []
        assert proj.analysis_cache == {}
        assert proj.filters == {}

    def test_create_project_with_name(self):
        """Create project with custom name."""
        proj = project.create_project(name="My Analysis")

        assert proj.name == "My Analysis"
        assert proj.created_at is not None

    def test_create_project_save_to_file(self, tmp_path):
        """Create and save project to file."""
        output_file = tmp_path / "test_project.json"

        proj = project.create_project(name="Test Project", output_path=str(output_file))

        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        assert data["project_name"] == "Test Project"
        assert proj.path == str(output_file)

    def test_open_project_valid_file(self, tmp_path):
        """Open existing valid project file."""
        # Create a project file
        proj_file = tmp_path / "test.json"
        proj_data = {
            "version": "1.0.0",
            "project_name": "Test",
            "created_at": "2026-03-16T12:00:00Z",
            "data_sources": [],
            "analysis_cache": {},
            "filters": {}
        }
        with open(proj_file, "w") as f:
            json.dump(proj_data, f)

        # Open it
        proj = project.open_project(str(proj_file))

        assert proj.name == "Test"
        assert proj.version == "1.0.0"
        assert proj.path == str(proj_file)

    def test_open_project_file_not_found(self):
        """Error when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            project.open_project("/nonexistent/path/project.json")

    def test_open_project_invalid_json(self, tmp_path):
        """Error when JSON is malformed."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json {{{")

        with pytest.raises(ValueError, match="Invalid project file"):
            project.open_project(str(bad_file))

    def test_save_project(self, tmp_path):
        """Save project modifications."""
        proj_file = tmp_path / "save_test.json"

        # Create and save project
        proj = project.create_project(name="Save Test", output_path=str(proj_file))

        # Modify and save again
        proj.data_sources.append({"type": "profiling", "path": "/data/test"})
        proj.modified = True
        project.save_project(proj)

        # Verify persistence
        with open(proj_file) as f:
            data = json.load(f)
        assert len(data["data_sources"]) == 1
        assert data["data_sources"][0]["type"] == "profiling"

    def test_get_project_info(self, tmp_path):
        """Get project information."""
        proj_file = tmp_path / "info_test.json"
        proj = project.create_project(name="Info Test", output_path=str(proj_file))

        info = project.get_project_info(proj)

        assert info["name"] == "Info Test"
        assert info["path"] == str(proj_file)
        assert info["version"] == "1.0.0"
        assert info["data_sources_count"] == 0


# ============================================================================
# Data Import Tests
# ============================================================================

class TestImportData:
    """Tests for data import module."""

    def test_validate_data_valid_directory(self, tmp_path):
        """Validate directory with all file types."""
        # Create test files
        (tmp_path / "data.json").write_text('{}')
        (tmp_path / "profiler.db").write_bytes(b"SQLite format 3\x00" + b"\x00" * 100)
        (tmp_path / "info.bin").write_bytes(b"\x00" * 50)
        (tmp_path / "details.csv").write_text("a,b\n1,2\n")

        result = import_data.validate_data(str(tmp_path))

        assert result["valid"] is True
        assert result["path"] == str(tmp_path)
        assert result["files"]["json"] == 1
        assert result["files"]["db"] == 1
        assert result["files"]["bin"] == 1
        assert result["files"]["csv"] == 1
        assert result["total_files"] == 4

    def test_validate_data_invalid_path(self):
        """Error when path doesn't exist."""
        result = import_data.validate_data("/nonexistent/path")

        assert result["valid"] is False
        assert "not found" in result["error"]

    def test_validate_data_empty_directory(self, tmp_path):
        """Validate empty directory."""
        result = import_data.validate_data(str(tmp_path))

        assert result["valid"] is True
        assert result["total_files"] == 0

    def test_list_profiling_files_json(self, tmp_path):
        """List JSON files."""
        (tmp_path / "file1.json").write_text('{}')
        (tmp_path / "file2.json").write_text('{}')

        files = import_data.list_profiling_files(str(tmp_path))

        json_files = [f for f in files if f["type"] == "json"]
        assert len(json_files) == 2

    def test_list_profiling_files_mixed(self, tmp_path):
        """List mixed file types."""
        (tmp_path / "data.json").write_text('{}')
        (tmp_path / "profiler.db").write_bytes(b"\x00" * 10)
        (tmp_path / "info.bin").write_bytes(b"\x00" * 10)
        (tmp_path / "readme.txt").write_text("readme")

        files = import_data.list_profiling_files(str(tmp_path))

        # Should find json, db, bin, csv (not .txt)
        assert len(files) == 4
        types = {f["type"] for f in files}
        assert "json" in types
        assert "db" in types
        assert "bin" in types
        assert "csv" in types

    def test_list_profiling_files_empty(self, tmp_path):
        """List files in empty directory."""
        files = import_data.list_profiling_files(str(tmp_path))
        assert files == []


# ============================================================================
# Session Management Tests
# ============================================================================

class TestSession:
    """Tests for session management module."""

    def test_session_init(self):
        """Initialize empty session."""
        sess = session.Session()

        assert sess.project is None
        assert sess.command_history == []
        assert sess.config == {}

    def test_session_set_project(self):
        """Set project in session."""
        sess = session.Session()
        proj = project.create_project(name="Test")

        sess.set_project(proj)

        assert sess.project == proj

    def test_session_status(self):
        """Get session status."""
        sess = session.Session()
        proj = project.create_project(name="Status Test")
        sess.set_project(proj)

        status = sess.get_status()

        assert status["project"] == "Status Test"
        assert status["modified"] is False
        assert status["history_count"] == 0

    def test_session_history(self):
        """Command history tracking."""
        sess = session.Session()

        sess.add_to_history("project new")
        sess.add_to_history("import load-profiling /data")

        assert len(sess.command_history) == 2
        history = sess.get_history()
        assert history[0] == "project new"
        assert history[1] == "import load-profiling /data"

    def test_session_config(self):
        """Set and get configuration."""
        sess = session.Session()

        sess.set_config("log_level", "DEBUG")
        sess.set_config("output_format", "json")

        assert sess.get_config("log_level") == "DEBUG"
        assert sess.get_config("output_format") == "json"
        assert sess.get_config("nonexistent", "default") == "default"

    def test_session_clear_cache(self):
        """Clear session cache."""
        sess = session.Session()
        proj = project.create_project()
        proj.analysis_cache["test"] = "data"
        sess.set_project(proj)

        sess.clear_cache()

        assert len(sess.project.analysis_cache) == 0


# ============================================================================
# Backend Integration Tests
# ============================================================================

class TestBackend:
    """Tests for backend integration."""

    def test_find_available_port(self, tmp_path):
        """Find available port in range."""
        # Should find an available port
        port = msinsight_backend.find_available_port(9500, 9510)
        assert 9500 <= port < 9510

    def test_find_available_port_all_used(self, monkeypatch):
        """Error when all ports used."""
        def mock_is_running(port):
            return True

        monkeypatch.setattr(msinsight_backend, "is_server_running", mock_is_running)

        with pytest.raises(msinsight_backend.MsInsightBackendError, match="No available port"):
            msinsight_backend.find_available_port(9000, 9010)

    def test_is_server_running_false(self):
        """Check non-running server."""
        # Port 9999 is unlikely to be used
        result = msinsight_backend.is_server_running(9999, timeout=0.1)

        assert result is False

    def test_backend_error_message(self):
        """Error message formatting."""
        error = msinsight_backend.MsInsightBackendError("Test error")

        assert "Test error" in str(error)

    def test_backend_binary_not_found(self, monkeypatch):
        """Error when binary missing."""
        def mock_which(cmd):
            return None

        monkeypatch.setattr(msinsight_backend.shutil, "which", mock_which)

        with pytest.raises(msinsight_backend.MsInsightBackendError, match="not found"):
            msinsight_backend.find_msinsight_binary()


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple modules."""

    def test_full_project_workflow(self, tmp_path):
        """Complete project workflow: create, save, open, modify."""
        proj_file = tmp_path / "workflow.json"

        # Create
        proj = project.create_project(name="Workflow Test", output_path=str(proj_file))
        assert proj_file.exists()

        # Close and reopen
        project.close_project(proj)
        proj = project.open_project(str(proj_file))
        assert proj.name == "Workflow Test"

        # Modify
        proj.data_sources.append({"type": "profiling", "path": "/data/test"})
        proj.modified = True

        # Save
        project.save_project(proj)

        # Verify persistence
        proj2 = project.open_project(str(proj_file))
        assert len(proj2.data_sources) == 1
        assert proj2.data_sources[0]["type"] == "profiling"

    def test_session_with_project(self, tmp_path):
        """Session with project management."""
        sess = session.Session()
        proj_file = tmp_path / "session_test.json"

        # Create project via session
        proj = project.create_project(name="Session Project", output_path=str(proj_file))
        sess.set_project(proj)

        # Add commands to history
        sess.add_to_history("import load-profiling /data")
        sess.add_to_history("timeline show")

        # Get status
        status = sess.get_status()
        assert status["project"] == "Session Project"
        assert status["history_count"] == 2

        # Save and verify
        project.save_project(proj)
        assert proj_file.exists()


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
