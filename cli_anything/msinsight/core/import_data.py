"""Data import functionality for MindStudio Insight CLI."""

from pathlib import Path
from typing import Dict, Any, List, Optional

def load_profiling_data(path: str, project, connection, format: str = "auto") -> Dict[str, Any]:
    """Load profiling data from directory."""
    # TODO: Implement WebSocket communication with backend
    # This is a placeholder that would send requests to the backend
    return {
        "status": "success",
        "files_loaded": 0,
        "data_types": [],
        "message": "Data loading not yet implemented - requires backend integration"
    }

def validate_data(path: str) -> Dict[str, Any]:
    """Validate profiling data files."""
    p = Path(path)
    if not p.exists():
        return {"valid": False, "error": f"Path not found: {path}"}

    files = {
        "json": list(p.glob("*.json")),
        "db": list(p.glob("*.db")),
        "bin": list(p.glob("*.bin")),
        "csv": list(p.glob("*.csv")),
    }

    return {
        "valid": True,
        "path": path,
        "files": {k: len(v) for k, v in files.items()},
        "total_files": sum(len(v) for v in files.values())
    }

def list_profiling_files(path: str) -> List[Dict[str, Any]]:
    """List profiling files in directory."""
    p = Path(path)
    if not p.exists():
        return []

    files = []
    for ext in ["*.json", "*.db", "*.bin", "*.csv"]:
        for f in p.glob(ext):
            files.append({
                "path": str(f),
                "name": f.name,
                "type": f.suffix[1:],
                "size": f.stat().st_size
            })
    return files
