"""
Session management for MindStudio Insight CLI.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

from cli_anything.msinsight.core.project import Project


class Session:
    """Manages the current CLI session."""

    def __init__(self):
        """Initialize session."""
        self.project: Optional[Project] = None
        self.command_history: List[str] = []
        self.config: Dict[str, Any] = {
            "log_level": "INFO",
            "output_format": "table",
            "auto_save": False,
        }

    def set_project(self, project: Optional[Project]) -> None:
        """Set current project."""
        self.project = project

    def get_project(self) -> Optional[Project]:
        """Get current project."""
        return self.project

    def require_project(self) -> Project:
        """Get current project or raise error."""
        if self.project is None:
            raise RuntimeError("No project is currently open. Use 'project new' or 'project open' first.")
        return self.project

    def add_to_history(self, command: str) -> None:
        """Add command to history."""
        self.command_history.append(command)
        # Keep only last 1000 commands
        if len(self.command_history) > 1000:
            self.command_history = self.command_history[-1000:]

    def get_history(self, limit: Optional[int] = None) -> List[str]:
        """Get command history."""
        if limit:
            return self.command_history[-limit:]
        return self.command_history.copy()

    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def clear_cache(self) -> None:
        """Clear session cache."""
        if self.project:
            self.project.analysis_cache.clear()

    def get_status(self) -> Dict[str, Any]:
        """Get session status."""
        return {
            "project": self.project.name if self.project else None,
            "project_path": self.project.path if self.project else None,
            "modified": self.project.modified if self.project else False,
            "history_count": len(self.command_history),
            "config": self.config,
        }
