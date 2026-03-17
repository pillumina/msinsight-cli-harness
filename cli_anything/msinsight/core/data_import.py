"""
Data import functionality for MindStudio Insight.

This module provides functions to import profiling data into MindStudio Insight.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from ..protocol.websocket_client import MindStudioWebSocketClient
from ..utils.msinsight_backend import MsInsightBackendError


class DataImporter:
    """
    Handles data import operations for MindStudio Insight.
    """

    def __init__(self, client: MindStudioWebSocketClient):
        """
        Initialize data importer.

        Args:
            client: WebSocket client for backend communication
        """
        self.client = client

    def import_profiling_data(
        self,
        project_name: str,
        data_path: str,
        rank_id: Optional[str] = None,
        is_new_project: bool = True,
        timeout: float = 60.0
    ) -> Dict[str, Any]:
        """
        Import profiling data into MindStudio Insight.

        Args:
            project_name: Name for the project
            data_path: Path to profiling data file or directory
            rank_id: Optional rank ID for multi-rank data
            is_new_project: True for new project, False to open existing
            timeout: Import timeout in seconds (default 60s)

        Returns:
            Import result dictionary with:
            - success: bool
            - cards: List of card information
            - isSimulation: bool
            - isCluster: bool
            - isIpynb: bool

        Raises:
            MsInsightBackendError: If import fails
            FileNotFoundError: If data_path doesn't exist
        """
        # Validate path
        path = Path(data_path)
        if not path.exists():
            raise FileNotFoundError(f"Data path not found: {data_path}")

        # Prepare import parameters
        params = {
            "projectName": project_name,
            "path": [str(path.absolute())],
            "projectAction": "NEW" if is_new_project else "OPEN",
            "isConflict": False
        }

        # Add rank ID if specified
        if rank_id:
            params["selectedRankId"] = rank_id
            params["selectedFilePath"] = str(path.absolute())

        # Send import command
        response = self.client.send_command(
            module="timeline",
            command="import/action",
            params=params,
            timeout=timeout
        )

        # Parse result
        if not response.result:
            error_msg = "Unknown import error"
            if response.error:
                error_msg = response.error.get("message", str(response.error))
            raise MsInsightBackendError(f"Import failed: {error_msg}")

        return response.body or {}

    def import_multi_rank_data(
        self,
        project_name: str,
        data_paths: List[str],
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Import multi-rank profiling data.

        Args:
            project_name: Name for the project
            data_paths: List of paths to profiling data (one per rank)
            timeout: Import timeout in seconds (default 120s for larger data)

        Returns:
            Import result dictionary

        Raises:
            MsInsightBackendError: If import fails
        """
        # Validate all paths
        for path_str in data_paths:
            path = Path(path_str)
            if not path.exists():
                raise FileNotFoundError(f"Data path not found: {path_str}")

        # Prepare import parameters
        params = {
            "projectName": project_name,
            "path": [str(Path(p).absolute()) for p in data_paths],
            "projectAction": "NEW",
            "isConflict": False
        }

        # Send import command
        response = self.client.send_command(
            module="timeline",
            command="import/action",
            params=params,
            timeout=timeout
        )

        if not response.result:
            error_msg = "Unknown import error"
            if response.error:
                error_msg = response.error.get("message", str(response.error))
            raise MsInsightBackendError(f"Import failed: {error_msg}")

        return response.body or {}

    def get_import_history(self) -> List[Dict[str, Any]]:
        """
        Get list of previously imported projects.

        Returns:
            List of project directories
        """
        response = self.client.send_command(
            module="global",
            command="files/getProjectExplorer",
            params={}
        )

        if not response.result:
            return []

        body = response.body or {}
        return body.get("projectDirectoryList", [])

    def check_project_valid(
        self,
        project_name: str,
        data_path: str
    ) -> Dict[str, Any]:
        """
        Check if a project is valid before importing.

        Args:
            project_name: Project name to check
            data_path: Data path to check

        Returns:
            Validation result
        """
        response = self.client.send_command(
            module="global",
            command="files/checkProjectValid",
            params={
                "projectName": project_name,
                "dataPath": [data_path]
            }
        )

        return response.body or {}


# Convenience functions

def import_data(
    client: MindStudioWebSocketClient,
    project_name: str,
    data_path: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Convenience function to import data.

    Args:
        client: WebSocket client
        project_name: Project name
        data_path: Data path
        **kwargs: Additional arguments for import_profiling_data

    Returns:
        Import result
    """
    importer = DataImporter(client)
    return importer.import_profiling_data(project_name, data_path, **kwargs)
