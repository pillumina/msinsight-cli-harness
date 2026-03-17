"""
Project management for MindStudio Insight CLI.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List


class Project:
    """Represents a MindStudio Insight analysis project."""

    def __init__(self, name: str = "Untitled", path: Optional[str] = None):
        """
        Initialize project.

        Args:
            name: Project name
            path: Project file path
        """
        self.name = name
        self.path = path
        self.version = "1.0.0"
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.modified = False

        # Project data
        self.data_sources: List[Dict[str, Any]] = []
        self.analysis_cache: Dict[str, Any] = {}
        self.filters: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert project to dictionary."""
        return {
            "version": self.version,
            "project_name": self.name,
            "created_at": self.created_at,
            "data_sources": self.data_sources,
            "analysis_cache": self.analysis_cache,
            "filters": self.filters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], path: str) -> "Project":
        """Create project from dictionary."""
        project = cls(name=data.get("project_name", "Untitled"), path=path)
        project.version = data.get("version", "1.0.0")
        project.created_at = data.get("created_at", project.created_at)
        project.data_sources = data.get("data_sources", [])
        project.analysis_cache = data.get("analysis_cache", {})
        project.filters = data.get("filters", {})
        return project


def create_project(name: str = "Untitled", output_path: Optional[str] = None) -> Project:
    """
    Create a new analysis project.

    Args:
        name: Project name
        output_path: Optional path to save project

    Returns:
        New Project instance
    """
    project = Project(name=name, path=output_path)

    if output_path:
        save_project(project, output_path)

    return project


def open_project(path: str) -> Project:
    """
    Open an existing project.

    Args:
        path: Path to project file

    Returns:
        Project instance

    Raises:
        FileNotFoundError: If project file doesn't exist
        ValueError: If project file is invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Project file not found: {path}")

    with open(path, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid project file: {e}")

    return Project.from_dict(data, path)


def save_project(project: Project, path: Optional[str] = None) -> str:
    """
    Save project to file.

    Args:
        project: Project to save
        path: Path to save to (uses project.path if None)

    Returns:
        Path where project was saved

    Raises:
        ValueError: If no path specified
    """
    save_path = path or project.path

    if not save_path:
        raise ValueError("No save path specified")

    # Ensure directory exists
    os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

    with open(save_path, "w") as f:
        json.dump(project.to_dict(), f, indent=2)

    project.path = save_path
    project.modified = False

    return save_path


def get_project_info(project: Project) -> Dict[str, Any]:
    """
    Get project information.

    Args:
        project: Project instance

    Returns:
        Dictionary with project information
    """
    return {
        "name": project.name,
        "path": project.path,
        "version": project.version,
        "created_at": project.created_at,
        "modified": project.modified,
        "data_sources_count": len(project.data_sources),
        "has_cache": bool(project.analysis_cache),
    }


def close_project(project: Project) -> None:
    """
    Close project (cleanup).

    Args:
        project: Project to close
    """
    # Clear caches
    project.analysis_cache.clear()
    project.data_sources.clear()
    project.filters.clear()
