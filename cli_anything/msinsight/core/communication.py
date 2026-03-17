"""Communication analysis for MindStudio Insight CLI."""

from typing import Dict, Any, Optional, List

def communication_matrix(project, connection, rank: Optional[int] = None) -> Dict[str, Any]:
    """Get communication matrix."""
    return {"message": "Communication analysis requires backend integration"}

def communication_overview(project, connection) -> Dict[str, Any]:
    """Get communication overview."""
    return {"message": "Communication overview requires backend integration"}

def identify_bottlenecks(project, connection, threshold: Optional[float] = None) -> List[Dict[str, Any]]:
    """Identify communication bottlenecks."""
    return []

def link_performance(project, connection, src_rank: int, dst_rank: int) -> Dict[str, Any]:
    """Get link performance between two ranks."""
    return {"src": src_rank, "dst": dst_rank,
            "message": "Link performance requires backend integration"}

def export_communication(project, connection, output_path: str, format: str = "json") -> str:
    """Export communication data."""
    return output_path
