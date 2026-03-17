"""
Command executor for MindStudio Insight.

This module executes recognized intents by calling the appropriate
backend operations.
"""

from typing import Dict, Any, Optional
from .intent_recognizer import Intent, IntentType
from .timeline_controller import TimelineController
from .data_query import DataQuery
from ..protocol.websocket_client import MindStudioWebSocketClient


class CommandExecutor:
    """
    Executes recognized intents.

    Maps intents to concrete backend operations.
    """

    def __init__(self, client: MindStudioWebSocketClient):
        """
        Initialize command executor.

        Args:
            client: WebSocket client for backend communication
        """
        self.client = client
        self.timeline = TimelineController(client)
        self.query = DataQuery(client)

    def execute(self, intent: Intent) -> Dict[str, Any]:
        """
        Execute a recognized intent.

        Args:
            intent: Recognized intent

        Returns:
            Execution result

        Raises:
            ValueError: If intent type is not supported
        """
        executor_map = {
            IntentType.ZOOM_TO_TIME: self._execute_zoom_to_time,
            IntentType.GO_TO_OPERATOR: self._execute_go_to_operator,
            IntentType.PIN_SWIMLANES: self._execute_pin_swimlanes,
            IntentType.COMPARE_RANKS: self._execute_compare_ranks,
            IntentType.FILTER_SWIMLANES: self._execute_filter_swimlanes,
            IntentType.GET_TOP_OPERATORS: self._execute_get_top_operators,
            IntentType.GET_OPERATOR_INFO: self._execute_get_operator_info,
            IntentType.GET_MEMORY_SUMMARY: self._execute_get_memory_summary,
            IntentType.GET_COMMUNICATION_MATRIX: self._execute_get_communication_matrix,
            IntentType.FIND_BOTTLENECK: self._execute_find_bottleneck,
            IntentType.FIND_MEMORY_LEAKS: self._execute_find_memory_leaks,
            IntentType.EXPORT_TIMELINE: self._execute_export_timeline,
        }

        executor = executor_map.get(intent.type)
        if not executor:
            raise ValueError(f"Unsupported intent type: {intent.type}")

        return executor(intent.params)

    # Navigation executors

    def _execute_zoom_to_time(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute zoom to time range."""
        return self.timeline.zoom_to_time(
            start_time=params["start_time"],
            end_time=params["end_time"],
            unit=params.get("start_unit", "ms")
        )

    def _execute_go_to_operator(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute go to operator."""
        operator_name = params["operator_name"]

        # First, search for operator by name
        operators = self.query.get_operators(
            filters={"name": operator_name},
            limit=1
        )

        if not operators.get("operators"):
            return {
                "success": False,
                "error": f"Operator not found: {operator_name}"
            }

        operator_id = operators["operators"][0]["id"]

        # Navigate to operator
        return self.timeline.go_to_operator(
            operator_id=operator_id,
            zoom_to_fit=True
        )

    def _execute_pin_swimlanes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pin swimlanes."""
        return self.timeline.pin_swimlanes(
            lane_ids=params["lane_ids"],
            unpin_others=True
        )

    def _execute_compare_ranks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute compare ranks."""
        return self.timeline.compare_ranks(
            rank_ids=params["rank_ids"],
            align_mode="time"
        )

    def _execute_filter_swimlanes(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filter swimlanes."""
        return self.timeline.filter_swimlanes(
            filter_type=params["filter_type"],
            pattern=params.get("pattern"),
            show_only=True
        )

    # Query executors

    def _execute_get_top_operators(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get top operators."""
        result = self.query.get_top_n_operators(
            n=params.get("n", 10),
            metric=params.get("metric", "duration")
        )

        # Format for readability
        operators = result.get("operators", [])
        formatted = []
        for i, op in enumerate(operators, 1):
            formatted.append({
                "rank": i,
                "name": op.get("name"),
                "duration_ms": op.get("duration") / 1000,  # Convert to ms
                "type": op.get("type"),
                "calls": op.get("calls", 1)
            })

        return {
            "success": True,
            "count": len(formatted),
            "operators": formatted
        }

    def _execute_get_operator_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get operator info."""
        operator_name = params["operator_name"]

        # Search for operator
        operators = self.query.get_operators(
            filters={"name": operator_name},
            limit=1
        )

        if not operators.get("operators"):
            return {
                "success": False,
                "error": f"Operator not found: {operator_name}"
            }

        operator = operators["operators"][0]

        # Get additional details
        operator_id = operator["id"]
        details = self.query.get_operator_by_id(operator_id)

        return {
            "success": True,
            "operator": details
        }

    def _execute_get_memory_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get memory summary."""
        return self.query.get_memory_summary()

    def _execute_get_communication_matrix(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute get communication matrix."""
        return self.query.get_communication_matrix()

    # Analysis executors

    def _execute_find_bottleneck(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find bottleneck."""
        # Get bottleneck analysis
        analysis = self.query.get_bottleneck_analysis()

        # Also get top slow operators
        top_operators = self.query.get_top_n_operators(n=5, metric="duration")

        return {
            "success": True,
            "bottleneck_analysis": analysis,
            "top_slow_operators": top_operators.get("operators", [])
        }

    def _execute_find_memory_leaks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find memory leaks."""
        return self.query.get_memory_leaks()

    # Export executors

    def _execute_export_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute export timeline."""
        return self.timeline.export_timeline_image(
            output_path=params["output_path"],
            format="png"
        )
