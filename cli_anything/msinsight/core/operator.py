"""Operator analysis for MindStudio Insight CLI."""

from typing import Dict, Any, List, Optional

def list_operators(project, connection, sort_by: str = "duration") -> List[Dict[str, Any]]:
    """List all operators."""
    return []

def top_operators(project, connection, count: int, metric: str = "duration") -> List[Dict[str, Any]]:
    """Get top N operators."""
    return []

def operator_details(project, connection, operator_id: str) -> Dict[str, Any]:
    """Get operator details."""
    return {"id": operator_id, "message": "Operator details require backend integration"}

def filter_operators(project, connection, op_type: Optional[str] = None,
                    duration_min: Optional[float] = None) -> List[Dict[str, Any]]:
    """Filter operators."""
    return []

def operator_source(project, connection, operator_id: str) -> str:
    """Show operator source code."""
    return f"Source code for {operator_id} requires backend integration"

def export_operators(project, connection, output_path: str, format: str = "json") -> str:
    """Export operator data."""
    return output_path
