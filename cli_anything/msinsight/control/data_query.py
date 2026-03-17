"""
Data query module for MindStudio Insight.

This module provides high-level data query operations for retrieving
analysis data from the backend.
"""

from typing import Optional, List, Dict, Any
from ..protocol.websocket_client import MindStudioWebSocketClient


class DataQuery:
    """
    High-level data query operations.

    Provides methods to query operators, memory, communication, and
    other analysis data from the backend.
    """

    def __init__(self, client: MindStudioWebSocketClient):
        """
        Initialize data query.

        Args:
            client: WebSocket client for backend communication
        """
        self.client = client

    # Operator queries

    def get_operators(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "duration",
        sort_order: str = "desc",
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get operators with optional filtering and sorting.

        Args:
            filters: Filter criteria (e.g., {"type": "MatMul", "duration_min": 1000})
            sort_by: Sort field ("duration", "start_time", "name")
            sort_order: Sort order ("asc", "desc")
            limit: Maximum number of results

        Returns:
            Dictionary with operator list
        """
        params = {
            "sortBy": sort_by,
            "sortOrder": sort_order
        }
        if filters:
            params["filters"] = filters
        if limit:
            params["limit"] = limit

        response = self.client.send_command(
            module="operator",
            command="getOperators",
            params=params
        )
        return response.data

    def get_top_n_operators(
        self,
        n: int = 10,
        metric: str = "duration"
    ) -> Dict[str, Any]:
        """
        Get top N operators by specified metric.

        Args:
            n: Number of operators to return
            metric: Metric to sort by ("duration", "memory", "calls")

        Returns:
            Dictionary with top operators
        """
        response = self.client.send_command(
            module="operator",
            command="getTopN",
            params={
                "n": n,
                "metric": metric
            }
        )
        return response.data

    def get_operator_by_id(self, operator_id: str) -> Dict[str, Any]:
        """
        Get operator details by ID.

        Args:
            operator_id: Operator ID

        Returns:
            Dictionary with operator details
        """
        response = self.client.send_command(
            module="operator",
            command="getOperatorById",
            params={
                "operatorId": operator_id
            }
        )
        return response.data

    def get_operator_statistics(self) -> Dict[str, Any]:
        """
        Get overall operator statistics.

        Returns:
            Dictionary with statistics
        """
        response = self.client.send_command(
            module="operator",
            command="getStatistics"
        )
        return response.data

    # Memory queries

    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get memory usage summary.

        Returns:
            Dictionary with memory statistics
        """
        response = self.client.send_command(
            module="memory",
            command="getSummary"
        )
        return response.data

    def get_memory_timeline(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Get memory usage over time.

        Args:
            start_time: Start time filter
            end_time: End time filter

        Returns:
            Dictionary with memory timeline data
        """
        params = {}
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time

        response = self.client.send_command(
            module="memory",
            command="getTimeline",
            params=params if params else None
        )
        return response.data

    def get_memory_blocks(
        self,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get memory blocks with optional filtering.

        Args:
            filters: Filter criteria

        Returns:
            Dictionary with memory blocks
        """
        params = {}
        if filters:
            params["filters"] = filters

        response = self.client.send_command(
            module="memory",
            command="getBlocks",
            params=params if params else None
        )
        return response.data

    def get_memory_leaks(self) -> Dict[str, Any]:
        """
        Detect potential memory leaks.

        Returns:
            Dictionary with leak detection results
        """
        response = self.client.send_command(
            module="memory",
            command="detectLeaks"
        )
        return response.data

    # Communication queries

    def get_communication_matrix(
        self,
        rank_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get communication matrix between ranks.

        Args:
            rank_ids: List of rank IDs (all ranks if None)

        Returns:
            Dictionary with communication matrix
        """
        params = {}
        if rank_ids:
            params["rankIds"] = rank_ids

        response = self.client.send_command(
            module="communication",
            command="getMatrix",
            params=params if params else None
        )
        return response.data

    def get_communication_events(
        self,
        rank_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get communication events.

        Args:
            rank_id: Filter by rank ID
            event_type: Filter by event type ("send", "receive", "collective")

        Returns:
            Dictionary with communication events
        """
        params = {}
        if rank_id:
            params["rankId"] = rank_id
        if event_type:
            params["eventType"] = event_type

        response = self.client.send_command(
            module="communication",
            command="getEvents",
            params=params if params else None
        )
        return response.data

    def get_communication_hotspots(self, n: int = 10) -> Dict[str, Any]:
        """
        Get communication hotspots.

        Args:
            n: Number of hotspots to return

        Returns:
            Dictionary with hotspots
        """
        response = self.client.send_command(
            module="communication",
            command="getHotspots",
            params={
                "n": n
            }
        )
        return response.data

    # Summary queries

    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get overall performance summary.

        Returns:
            Dictionary with performance summary
        """
        response = self.client.send_command(
            module="summary",
            command="getPerformanceSummary"
        )
        return response.data

    def get_bottleneck_analysis(self) -> Dict[str, Any]:
        """
        Get bottleneck analysis.

        Returns:
            Dictionary with bottleneck information
        """
        response = self.client.send_command(
            module="summary",
            command="getBottleneckAnalysis"
        )
        return response.data

    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """
        Get optimization suggestions.

        Returns:
            Dictionary with suggestions
        """
        response = self.client.send_command(
            module="advisor",
            command="getSuggestions"
        )
        return response.data

    # Source code queries

    def get_source_location(
        self,
        operator_id: str
    ) -> Dict[str, Any]:
        """
        Get source code location for an operator.

        Args:
            operator_id: Operator ID

        Returns:
            Dictionary with source location (file, line, function)
        """
        response = self.client.send_command(
            module="source",
            command="getSourceLocation",
            params={
                "operatorId": operator_id
            }
        )
        return response.data

    def get_call_stack(
        self,
        operator_id: str
    ) -> Dict[str, Any]:
        """
        Get call stack for an operator.

        Args:
            operator_id: Operator ID

        Returns:
            Dictionary with call stack
        """
        response = self.client.send_command(
            module="source",
            command="getCallStack",
            params={
                "operatorId": operator_id
            }
        )
        return response.data

    # Generic query

    def query(
        self,
        module: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generic query method.

        Args:
            module: Module name
            command: Command name
            params: Command parameters

        Returns:
            Response data
        """
        response = self.client.send_command(module, command, params)
        return response.data
