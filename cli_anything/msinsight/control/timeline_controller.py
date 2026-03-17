"""
Timeline controller for MindStudio Insight.

This module provides high-level operations for controlling the timeline
visualization in MindStudio Insight, such as zoom, pan, pin, and compare.
"""

from typing import Optional, List, Dict, Any
from ..protocol.websocket_client import MindStudioWebSocketClient


class TimelineController:
    """
    Controller for timeline operations.

    Provides methods to control the timeline visualization through
    the WebSocket backend.
    """

    def __init__(self, client: MindStudioWebSocketClient):
        """
        Initialize timeline controller.

        Args:
            client: WebSocket client for backend communication
        """
        self.client = client

    def zoom_to_time(
        self,
        start_time: float,
        end_time: float,
        unit: str = "ms"
    ) -> Dict[str, Any]:
        """
        Zoom to a specific time range on the timeline.

        Args:
            start_time: Start time
            end_time: End time
            unit: Time unit ("ms", "us", "ns")

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="zoomToRange",
            params={
                "startTime": start_time,
                "endTime": end_time,
                "unit": unit
            }
        )
        return response.data

    def pan_left(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Pan timeline left.

        Args:
            amount: Pan amount (default: 50% of current viewport)

        Returns:
            Response data
        """
        params = {}
        if amount is not None:
            params["amount"] = amount

        response = self.client.send_command(
            module="timeline",
            command="panLeft",
            params=params if params else None
        )
        return response.data

    def pan_right(self, amount: Optional[float] = None) -> Dict[str, Any]:
        """
        Pan timeline right.

        Args:
            amount: Pan amount (default: 50% of current viewport)

        Returns:
            Response data
        """
        params = {}
        if amount is not None:
            params["amount"] = amount

        response = self.client.send_command(
            module="timeline",
            command="panRight",
            params=params if params else None
        )
        return response.data

    def reset_zoom(self) -> Dict[str, Any]:
        """
        Reset timeline to show full range.

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="resetZoom"
        )
        return response.data

    def pin_swimlanes(
        self,
        lane_ids: List[str],
        unpin_others: bool = True
    ) -> Dict[str, Any]:
        """
        Pin specific swimlanes to top of timeline.

        Args:
            lane_ids: List of swimlane IDs to pin
            unpin_others: Unpin other lanes

        Returns:
            Response data
        """
        # Build lane order configuration
        lanes = []
        for lid in lane_ids:
            lanes.append({
                "id": lid,
                "pinned": True
            })

        params = {
            "lanes": lanes,
            "unpinOthers": unpin_others
        }

        response = self.client.send_command(
            module="timeline",
            command="setSwimlaneOrder",
            params=params
        )
        return response.data

    def unpin_all_swimlanes(self) -> Dict[str, Any]:
        """
        Unpin all swimlanes.

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="unpinAllSwimlanes"
        )
        return response.data

    def highlight_swimlane(
        self,
        lane_id: str,
        highlight: bool = True
    ) -> Dict[str, Any]:
        """
        Highlight or unhighlight a swimlane.

        Args:
            lane_id: Swimlane ID
            highlight: True to highlight, False to remove highlight

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="highlightSwimlane",
            params={
                "laneId": lane_id,
                "highlight": highlight
            }
        )
        return response.data

    def select_time_range(
        self,
        start_time: float,
        end_time: float,
        unit: str = "ms"
    ) -> Dict[str, Any]:
        """
        Select a time range on the timeline.

        Args:
            start_time: Start time
            end_time: End time
            unit: Time unit

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="selectRange",
            params={
                "startTime": start_time,
                "endTime": end_time,
                "unit": unit
            }
        )
        return response.data

    def clear_selection(self) -> Dict[str, Any]:
        """
        Clear time range selection.

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="clearSelection"
        )
        return response.data

    def go_to_operator(
        self,
        operator_id: str,
        zoom_to_fit: bool = True
    ) -> Dict[str, Any]:
        """
        Navigate to a specific operator on the timeline.

        Args:
            operator_id: Operator ID
            zoom_to_fit: Auto-zoom to show operator context

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="goToOperator",
            params={
                "operatorId": operator_id,
                "zoomToFit": zoom_to_fit
            }
        )
        return response.data

    def filter_swimlanes(
        self,
        filter_type: str,
        pattern: Optional[str] = None,
        show_only: bool = True
    ) -> Dict[str, Any]:
        """
        Filter swimlanes by type or pattern.

        Args:
            filter_type: Filter type ("type", "name", "rank")
            pattern: Filter pattern (regex for names, exact for type/rank)
            show_only: True to show only matching, False to hide matching

        Returns:
            Response data
        """
        params = {
            "filterType": filter_type,
            "showOnly": show_only
        }
        if pattern:
            params["pattern"] = pattern

        response = self.client.send_command(
            module="timeline",
            command="filterSwimlanes",
            params=params
        )
        return response.data

    def clear_filters(self) -> Dict[str, Any]:
        """
        Clear all swimlane filters.

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="clearFilters"
        )
        return response.data

    def set_view_mode(self, mode: str) -> Dict[str, Any]:
        """
        Set timeline view mode.

        Args:
            mode: View mode ("overview", "detail", "compare")

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="setViewMode",
            params={
                "mode": mode
            }
        )
        return response.data

    def compare_ranks(
        self,
        rank_ids: List[str],
        align_mode: str = "time"
    ) -> Dict[str, Any]:
        """
        Compare multiple ranks side-by-side.

        Args:
            rank_ids: List of rank IDs to compare
            align_mode: Alignment mode ("time", "operator")

        Returns:
            Response data
        """
        response = self.client.send_command(
            module="timeline",
            command="compareRanks",
            params={
                "rankIds": rank_ids,
                "alignMode": align_mode
            }
        )
        return response.data

    def get_visible_range(self) -> Dict[str, Any]:
        """
        Get currently visible time range.

        Returns:
            Dictionary with "startTime" and "endTime"
        """
        response = self.client.send_command(
            module="timeline",
            command="getVisibleRange"
        )
        return response.data

    def get_swimlane_list(self) -> Dict[str, Any]:
        """
        Get list of all swimlanes.

        Returns:
            Dictionary with swimlane information
        """
        response = self.client.send_command(
            module="timeline",
            command="getSwimlaneList"
        )
        return response.data

    def export_timeline_image(
        self,
        output_path: str,
        format: str = "png",
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Export timeline as image.

        Args:
            output_path: Output file path
            format: Image format ("png", "svg")
            width: Image width in pixels
            height: Image height in pixels

        Returns:
            Response data
        """
        params = {
            "outputPath": output_path,
            "format": format
        }
        if width:
            params["width"] = width
        if height:
            params["height"] = height

        response = self.client.send_command(
            module="timeline",
            command="exportImage",
            params=params
        )
        return response.data
