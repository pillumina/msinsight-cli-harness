"""Summary statistics for MindStudio Insight CLI."""

from typing import Dict, Any

def performance_overview(project, connection) -> Dict[str, Any]:
    """Get performance overview."""
    return {"message": "Performance overview requires backend integration"}

def compute_summary(project, connection) -> Dict[str, Any]:
    """Get compute metrics summary."""
    return {"message": "Compute summary requires backend integration"}

def communication_summary(project, connection) -> Dict[str, Any]:
    """Get communication summary."""
    return {"message": "Communication summary requires backend integration"}

def export_summary(project, connection, output_path: str, format: str = "json") -> str:
    """Export summary."""
    return output_path
