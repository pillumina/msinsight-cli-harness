"""
MindStudio Insight Control Layer - Redesigned for Real Backend Commands

This module provides high-level APIs that map to actual backend WebSocket commands.
Based on ProtocolDefs.h - 127 real commands.
"""

from typing import Optional, Dict, Any, List
from ..protocol.websocket_client import MindStudioWebSocketClient
from ..utils.msinsight_backend import MsInsightBackendError


def discover_available_ranks(client: MindStudioWebSocketClient) -> List[Dict[str, str]]:
    """
    Discover available ranks from imported profiling data.

    This extracts rank information from files/getProjectExplorer response.

    Args:
        client: WebSocket client

    Returns:
        List of rank info dicts with keys:
        - rank_id: Full rank ID string
        - rank_index: Rank index (0, 1, 2, ...)
        - device_id: Device ID
        - host: Host name
    """
    response = client.send_command(
        module="global",
        command="files/getProjectExplorer",
        params={},
        timeout=10.0
    )

    if not response.result or not response.body:
        return []

    result = response.body
    ranks = []

    # Navigate the project structure to find ranks
    if isinstance(result, dict) and 'projectDirectoryList' in result:
        projects = result['projectDirectoryList']

        for project in projects:
            if 'children' not in project:
                continue

            # Navigate: project -> rank_group -> rank
            for rank_group in project.get('children', []):
                for rank in rank_group.get('children', []):
                    rank_id = rank.get('rankId', '')
                    if rank_id:
                        # Parse rank info
                        # Format: "hostname123456789_0 0"
                        # Extract rank_index and device_id
                        parts = rank_id.split()
                        rank_index = parts[0].split('_')[-1] if len(parts) > 0 else '0'
                        device_id = parts[1] if len(parts) > 1 else '0'

                        ranks.append({
                            'rank_id': rank_id,
                            'rank_index': rank_index,
                            'device_id': device_id,
                            'host': rank.get('host', ''),
                            'file_path': rank.get('filePath', '')
                        })

    return ranks


class DataImportController:
    """Controller for data import operations."""

    def __init__(self, client: MindStudioWebSocketClient):
        self.client = client

    def import_profiling_data(
        self,
        project_name: str,
        data_path: str,
        is_new_project: bool = True,
        import_type: str = "file",
        timeout: float = 120.0
    ) -> Dict[str, Any]:
        """
        Import profiling data into MindStudio Insight.

        Backend command: import/action
        Module: timeline

        Args:
            project_name: Project name
            data_path: Path to profiling data (file or directory)
            is_new_project: True to create new project, False to add to existing
            import_type: Import type - "file" for new import, "drag" for drag-drop
            timeout: Import timeout

        Returns:
            Import result with cards and analysis info
        """
        params = {
            "projectName": project_name,
            "path": [data_path],
            "projectAction": 1,  # ADD_FILE - always use this for import
            "isConflict": False,
            "importType": import_type
        }

        response = self.client.send_command(
            module="timeline",
            command="import/action",
            params=params,
            timeout=timeout
        )

        return response.body or {}

    def get_import_cards(self) -> List[Dict[str, Any]]:
        """
        Get parsed analysis cards after import.

        Backend command: parse/cards
        Module: timeline

        Returns:
            List of analysis cards (operator, memory, communication, etc.)
        """
        response = self.client.send_command(
            module="timeline",
            command="parse/cards",
            params={},
            timeout=10.0
        )

        return response.body if response.body else []


class SummaryController:
    """Controller for performance summary and statistics."""

    def __init__(self, client: MindStudioWebSocketClient):
        self.client = client

    def get_statistics(
        self,
        rank_id: str,
        time_flag: str,
        cluster_path: str = "",
        step_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance statistics.

        Backend command: summary/statistic
        Module: summary

        Args:
            rank_id: Rank ID (required)
            time_flag: Time flag (required)
            cluster_path: Cluster path (required, can be empty string)
            step_id: Optional step ID

        Returns:
            Statistics data including operator counts, duration, etc.
        """
        params = {
            "rankId": rank_id,
            "timeFlag": time_flag,
            "clusterPath": cluster_path
        }
        if step_id is not None:
            params["stepId"] = step_id

        response = self.client.send_command(
            module="summary",
            command="summary/statistic",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_top_n_data(
        self,
        cluster_path: str = "",
        is_compare: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get top N performance data.

        Backend command: summary/queryTopData
        Module: summary

        Args:
            cluster_path: Cluster path (required, can be empty string)
            is_compare: Whether in comparison mode

        Returns:
            List of top N operators/tasks
        """
        params = {
            "clusterPath": cluster_path,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="summary",
            command="summary/queryTopData",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_compute_details(
        self,
        rank_id: str,
        time_flag: str,
        cluster_path: str = "",
        current_page: int = 0,
        page_size: int = 0,
        order_by: str = "",
        order: str = "",
        db_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get compute performance details.

        Backend command: summary/queryComputeDetail
        Module: summary

        Args:
            rank_id: Rank ID (required)
            time_flag: Time flag (required)
            cluster_path: Cluster path (required, can be empty)
            current_page: Current page number (default: 0)
            page_size: Page size (default: 0, meaning all data)
            order_by: Field to order by
            order: Sort order (asc/desc)
            db_path: Optional database path

        Returns:
            Compute details including operator breakdown
        """
        params = {
            "rankId": rank_id,
            "timeFlag": time_flag,
            "clusterPath": cluster_path,
            "currentPage": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order
        }
        if db_path:
            params["dbPath"] = db_path

        response = self.client.send_command(
            module="summary",
            command="summary/queryComputeDetail",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_communication_details(
        self,
        rank_id: str,
        time_flag: str = "HCCL",
        cluster_path: str = "",
        current_page: int = 0,
        page_size: int = 0,
        order_by: str = "",
        order: str = ""
    ) -> Dict[str, Any]:
        """
        Get communication performance details.

        Backend command: summary/queryCommunicationDetail
        Module: summary

        Args:
            rank_id: Rank ID (required)
            time_flag: Time flag (required, default: "HCCL")
            cluster_path: Cluster path (required, can be empty)
            current_page: Current page number (default: 0)
            page_size: Page size (default: 0, meaning all data)
            order_by: Field to order by
            order: Sort order (asc/desc)

        Returns:
            Communication details including bandwidth, matrix
        """
        params = {
            "rankId": rank_id,
            "timeFlag": time_flag,
            "clusterPath": cluster_path,
            "currentPage": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order
        }

        response = self.client.send_command(
            module="summary",
            command="summary/queryCommunicationDetail",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_model_info(
        self,
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Get model information.

        Backend command: summary/queryModelInfo
        Module: summary

        Args:
            cluster_path: Cluster path (required, can be empty string)

        Returns:
            Model information including architecture, parameters, etc.
        """
        params = {
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/queryModelInfo",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_expert_hotspot(
        self,
        model_stage: str,
        version: str,
        layer_num: int,
        expert_num: int,
        cluster_path: str = "",
        dense_layer_list: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Get expert hotspot analysis for MoE models.

        Backend command: summary/queryExpertHotspot
        Module: summary

        Args:
            model_stage: Model stage (required)
            version: Version string (required)
            layer_num: Number of layers (must be > 0)
            expert_num: Number of experts (must be > 0)
            cluster_path: Cluster path (required, can be empty)
            dense_layer_list: List of dense layer indices (default: empty)

        Returns:
            Expert hotspot analysis data
        """
        if dense_layer_list is None:
            dense_layer_list = []

        params = {
            "modelStage": model_stage,
            "version": version,
            "layerNum": layer_num,
            "expertNum": expert_num,
            "denseLayerList": dense_layer_list,
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/queryExpertHotspot",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def import_expert_data(
        self,
        file_path: str,
        version: str,
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Import expert data for MoE analysis.

        Backend command: summary/importExpertData
        Module: summary

        Args:
            file_path: Path to expert data file (required)
            version: Version string (required)
            cluster_path: Cluster path (required, can be empty)

        Returns:
            Import result
        """
        params = {
            "filePath": file_path,
            "version": version,
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/importExpertData",
            params=params,
            timeout=30.0
        )

        return response.body or {}

    def get_parallel_strategy(
        self,
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Query parallel strategy configuration.

        Backend command: summary/query/parallelStrategy
        Module: summary

        Args:
            cluster_path: Cluster path (required, can be empty string)

        Returns:
            Parallel strategy configuration including PP, TP, DP, CP, EP sizes
        """
        params = {
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/query/parallelStrategy",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def set_parallel_strategy(
        self,
        config: Dict[str, Any],
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Set parallel strategy configuration.

        Backend command: summary/set/parallelStrategy
        Module: summary

        Args:
            config: Parallel strategy config dict with keys:
                - algorithm: Strategy algorithm (e.g., "MegatronLM-TP-CP-EP-DP-PP")
                - ppSize: Pipeline parallel size
                - tpSize: Tensor parallel size
                - dpSize: Data parallel size
                - cpSize: Context parallel size (default: 1)
                - epSize: Expert parallel size (default: 1)
                - moeTpSize: MoE tensor parallel size (default: 1)
            cluster_path: Cluster path (required, can be empty string)

        Returns:
            Set result
        """
        params = {
            "config": config,
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/set/parallelStrategy",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_pipeline_timeline(
        self,
        stage_id: str,
        cluster_path: str = "",
        step_id: str = ""
    ) -> Dict[str, Any]:
        """
        Get pipeline forward-backward timeline.

        Backend command: parallelism/pipeline/fwdBwdTimeline
        Module: summary

        Args:
            stage_id: Stage ID (required)
            cluster_path: Cluster path (required, can be empty)
            step_id: Step ID (optional, can be empty)

        Returns:
            Pipeline timeline data showing forward and backward stages
        """
        params = {
            "stageId": stage_id,
            "clusterPath": cluster_path,
            "stepId": step_id
        }

        response = self.client.send_command(
            module="summary",
            command="parallelism/pipeline/fwdBwdTimeline",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_parallelism_arrangement(
        self,
        config: Dict[str, Any],
        dimension: str,
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Get parallelism arrangement information.

        Backend command: parallelism/arrangement/all
        Module: summary

        Args:
            config: Parallel strategy config dict
            dimension: Dimension string, must be one of:
                - "ep-dp-pp"
                - "ep-dp-pp-cp"
                - "ep-dp-pp-cp-tp"
            cluster_path: Cluster path (required, can be empty string)

        Returns:
            Parallelism arrangement data
        """
        params = {
            "config": config,
            "dimension": dimension,
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="parallelism/arrangement/all",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_parallelism_performance(
        self,
        config: Dict[str, Any],
        dimension: str,
        cluster_path: str = "",
        order_by: str = "",
        step: str = "",
        is_compare: bool = False,
        baseline_step: str = "",
        index_list: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Get parallelism performance data.

        Backend command: parallelism/performance/data
        Module: summary

        Args:
            config: Parallel strategy config dict
            dimension: Dimension string (see get_parallelism_arrangement)
            cluster_path: Cluster path (required, can be empty)
            order_by: Field to order by (optional)
            step: Step ID (optional)
            is_compare: Whether in comparison mode
            baseline_step: Baseline step for comparison (optional)
            index_list: List of indices to query (optional)

        Returns:
            Parallelism performance data
        """
        if index_list is None:
            index_list = []

        params = {
            "config": config,
            "dimension": dimension,
            "clusterPath": cluster_path,
            "orderBy": order_by,
            "step": step,
            "isCompare": is_compare,
            "baselineStep": baseline_step,
            "indexList": index_list
        }

        response = self.client.send_command(
            module="summary",
            command="parallelism/performance/data",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_slow_rank_advisor(
        self,
        cluster_path: str = "/"
    ) -> Dict[str, Any]:
        """
        Get slow rank advisor recommendations.

        Backend command: summary/slowRank/advisor
        Module: summary

        Args:
            cluster_path: Cluster path (required, use "/" as default)

        Returns:
            Slow rank advisor data including:
            - topNElements: List of top N advice info
            - matchSuccess: Whether matching succeeded
            - hasSlowRank: Whether slow rank issue exists
        """
        params = {
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="summary",
            command="summary/slowRank/advisor",
            params=params,
            timeout=10.0
        )

        return response.body or {}


class OperatorController:
    """Controller for operator analysis."""

    def __init__(self, client: MindStudioWebSocketClient):
        self.client = client

    def get_category_info(
        self,
        rank_id: str,
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get operator category information.

        Backend command: operator/category
        Module: operator

        Args:
            rank_id: Rank ID (required)
            group: Group type (Operator, Operator Type, Input Shape)
            device_id: Device ID (optional)
            top_k: Top K results (default: 0, meaning all)

        Returns:
            List of operator categories with duration info
        """
        params = {
            "rankId": rank_id,
            "group": group,
            "deviceId": device_id,
            "topK": top_k
        }

        response = self.client.send_command(
            module="operator",
            command="operator/category",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_statistic_info(
        self,
        rank_id: str,
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0,
        current_page: int = 1,
        page_size: int = 0,
        order_by: str = "",
        order: str = "",
        is_compare: bool = False,
        filters: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Get operator statistics.

        Backend command: operator/statistic
        Module: operator

        Args:
            rank_id: Rank ID (required)
            group: Group type (Operator, Operator Type, Input Shape)
            device_id: Device ID (optional)
            top_k: Top K results (default: 0)
            current_page: Current page (default: 1)
            page_size: Page size (default: 0, meaning all)
            order_by: Field to order by
            order: Sort order (asc/desc)
            is_compare: Comparison mode flag
            filters: List of filter dictionaries

        Returns:
            Operator statistics including counts, durations
        """
        params = {
            "rankId": rank_id,
            "group": group,
            "deviceId": device_id,
            "topK": top_k,
            "current": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order,
            "isCompare": is_compare
        }
        if filters:
            params["filters"] = filters

        response = self.client.send_command(
            module="operator",
            command="operator/statistic",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_operator_details(
        self,
        rank_id: str,
        op_type: str = "",
        op_name: str = "",
        shape: str = "",
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0,
        current_page: int = 1,
        page_size: int = 0,
        order_by: str = "",
        order: str = ""
    ) -> Dict[str, Any]:
        """
        Get detailed information for specific operator(s).

        Backend command: operator/more_info
        Module: operator

        Args:
            rank_id: Rank ID (required)
            op_type: Operator type (optional)
            op_name: Operator name (optional)
            shape: Input shape (optional)
            group: Group type (Operator, Operator Type, Input Shape)
            device_id: Device ID (optional)
            top_k: Top K results
            current_page: Current page
            page_size: Page size
            order_by: Field to order by
            order: Sort order

        Returns:
            Detailed operator information
        """
        params = {
            "rankId": rank_id,
            "opType": op_type,
            "opName": op_name,
            "shape": shape,
            "group": group,
            "deviceId": device_id,
            "topK": top_k,
            "current": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order
        }

        response = self.client.send_command(
            module="operator",
            command="operator/more_info",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_compute_unit_info(
        self,
        rank_id: str,
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get operator compute unit information.

        Backend command: operator/compute_unit
        Module: operator

        Args:
            rank_id: Rank ID (required)
            group: Group type (Operator, Operator Type, Input Shape)
            device_id: Device ID (optional)
            top_k: Top K results (default: 0, meaning all)

        Returns:
            List of compute unit information with duration breakdown
        """
        params = {
            "rankId": rank_id,
            "group": group,
            "deviceId": device_id,
            "topK": top_k
        }

        response = self.client.send_command(
            module="operator",
            command="operator/compute_unit",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_all_operator_details(
        self,
        rank_id: str,
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0,
        current_page: int = 1,
        page_size: int = 0,
        order_by: str = "",
        order: str = "",
        is_compare: bool = False,
        filters: Optional[List[Dict[str, str]]] = None,
        range_filters: Optional[List[Dict[str, List[str]]]] = None
    ) -> Dict[str, Any]:
        """
        Get all operator details (full dataset).

        Backend command: operator/details
        Module: operator

        Args:
            rank_id: Rank ID (required)
            group: Group type (Operator, Operator Type, Input Shape)
            device_id: Device ID (optional)
            top_k: Top K results (default: 0)
            current_page: Current page (default: 1)
            page_size: Page size (default: 0, meaning all)
            order_by: Field to order by
            order: Sort order (asc/desc)
            is_compare: Comparison mode flag
            filters: List of filter dictionaries with 'column' and 'value'
            range_filters: List of range filter dictionaries with 'column' and 'values'

        Returns:
            Full operator details dataset
        """
        params = {
            "rankId": rank_id,
            "group": group,
            "deviceId": device_id,
            "topK": top_k,
            "current": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order,
            "isCompare": is_compare
        }
        if filters:
            params["filters"] = filters
        if range_filters:
            params["rangeFilters"] = range_filters

        response = self.client.send_command(
            module="operator",
            command="operator/details",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def export_operator_details(
        self,
        rank_id: str,
        group: str = "Operator",
        device_id: str = "",
        top_k: int = 0,
        is_compare: bool = False
    ) -> Dict[str, Any]:
        """
        Export all operator details to file.

        Backend command: operator/exportDetails
        Module: operator

        Args:
            rank_id: Rank ID (required)
            group: Group type (Operator, Operator Type, Input Shape, Operator Name, Communication Name)
            device_id: Device ID (optional)
            top_k: Top K results (default: 0)
            is_compare: Comparison mode flag

        Returns:
            Export result with file path or download info
        """
        params = {
            "rankId": rank_id,
            "group": group,
            "deviceId": device_id,
            "topK": top_k,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="operator",
            command="operator/exportDetails",
            params=params,
            timeout=30.0  # Longer timeout for export
        )

        return response.body or {}


class MemoryController:
    """Controller for memory analysis."""

    def __init__(self, client: MindStudioWebSocketClient):
        self.client = client

    def get_memory_view(
        self,
        rank_id: str,
        view_type: str = "type",
        device_id: str = "",
        cluster_path: str = ""
    ) -> Dict[str, Any]:
        """
        Get memory view data.

        Backend command: Memory/view/{type|resourceType|operator|component}
        Module: memory

        Args:
            rank_id: Rank ID (required)
            view_type: Type of view (type, resourceType, operator, component)
            device_id: Device ID (optional)
            cluster_path: Cluster path (required, can be empty)

        Returns:
            Memory view data
        """
        params = {
            "rankId": rank_id,
            "deviceId": device_id,
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="memory",
            command=f"Memory/view/{view_type}",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_memory_operator_size(
        self,
        rank_id: str,
        view_type: str = "Overall",
        device_id: str = "",
        is_compare: bool = False
    ) -> Dict[str, Any]:
        """
        Get memory size for operator.

        Backend command: Memory/view/operatorSize
        Module: memory

        Args:
            rank_id: Rank ID (required)
            view_type: View type (Overall or Stream)
            device_id: Device ID (optional)
            is_compare: Comparison mode flag

        Returns:
            Memory size information for the operator
        """
        params = {
            "rankId": rank_id,
            "type": view_type,
            "deviceId": device_id,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="memory",
            command="Memory/view/operatorSize",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_static_operator_graph(
        self,
        rank_id: str,
        model_name: str = "",
        graph_id: str = "",
        is_compare: bool = False
    ) -> Dict[str, Any]:
        """
        Get static operator memory graph.

        Backend command: Memory/view/staticOpMemoryGraph
        Module: memory

        Args:
            rank_id: Rank ID (required)
            model_name: Model name (optional)
            graph_id: Graph ID (optional)
            is_compare: Comparison mode flag

        Returns:
            Static operator memory graph data
        """
        params = {
            "rankId": rank_id,
            "modelName": model_name,
            "graphId": graph_id,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="memory",
            command="Memory/view/staticOpMemoryGraph",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_static_operator_list(
        self,
        rank_id: str,
        graph_id: str = "",
        search_name: str = "",
        min_size: int = -9223372036854775808,  # std::numeric_limits<int64_t>::min()
        max_size: int = 9223372036854775807,   # std::numeric_limits<int64_t>::max()
        start_node_index: int = -1,
        end_node_index: int = -1,
        is_compare: bool = False,
        current_page: int = 1,
        page_size: int = 10,
        order_by: str = "",
        order: str = ""
    ) -> Dict[str, Any]:
        """
        Get static operator memory list.

        Backend command: Memory/view/staticOpMemoryList
        Module: memory

        Args:
            rank_id: Rank ID (required)
            graph_id: Graph ID (optional)
            search_name: Search name filter (optional)
            min_size: Minimum size filter (default: int64 min)
            max_size: Maximum size filter (default: int64 max)
            start_node_index: Start node index (default: -1, meaning all)
            end_node_index: End node index (default: -1, meaning all)
            is_compare: Comparison mode flag
            current_page: Current page number (default: 1)
            page_size: Page size (default: 10)
            order_by: Field to order by (e.g., "opName")
            order: Sort order (e.g., "descend", "ascend")

        Returns:
            Static operator memory list with pagination
        """
        params = {
            "rankId": rank_id,
            "graphId": graph_id,
            "searchName": search_name,
            "minSize": min_size,
            "maxSize": max_size,
            "startNodeIndex": start_node_index,
            "endNodeIndex": end_node_index,
            "isCompare": is_compare,
            "currentPage": current_page,
            "pageSize": page_size,
            "orderBy": order_by,
            "order": order
        }

        response = self.client.send_command(
            module="memory",
            command="Memory/view/staticOpMemoryList",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_static_operator_size(
        self,
        rank_id: str,
        graph_id: str = "",
        is_compare: bool = False
    ) -> Dict[str, Any]:
        """
        Get static operator memory size range.

        Backend command: Memory/view/staticOpMemorySize
        Module: memory

        Args:
            rank_id: Rank ID (required)
            graph_id: Graph ID (optional)
            is_compare: Comparison mode flag

        Returns:
            Min and max memory size for static operators
        """
        params = {
            "rankId": rank_id,
            "graphId": graph_id,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="memory",
            command="Memory/view/staticOpMemorySize",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def find_memory_slice(
        self,
        rank_id: str,
        slice_id: str,
        slice_name: str = ""
    ) -> Dict[str, Any]:
        """
        Find memory slice by ID or name.

        Backend command: Memory/find/slice
        Module: memory

        Args:
            rank_id: Rank ID (required)
            slice_id: Slice ID (required)
            slice_name: Slice name (optional)

        Returns:
            Memory slice information
        """
        params = {
            "rankId": rank_id,
            "id": slice_id,
            "name": slice_name
        }

        response = self.client.send_command(
            module="memory",
            command="Memory/find/slice",
            params=params,
            timeout=10.0
        )

        return response.body or {}


class CommunicationController:
    """Controller for communication analysis."""

    def __init__(self, client: MindStudioWebSocketClient):
        self.client = client

    def get_bandwidth(
        self,
        rank_id: str,
        operator_name: str,
        stage: str = "",
        iteration_id: str = "",
        pg_name: str = "",
        cluster_path: str = "",
        group_id_hash: str = ""
    ) -> Dict[str, Any]:
        """
        Get communication bandwidth information.

        Backend command: communication/bandwidth
        Module: communication

        Args:
            rank_id: Rank ID (required)
            operator_name: Operator name (required)
            stage: Stage (required, can be empty)
            iteration_id: Iteration ID (optional)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required, can be empty)
            group_id_hash: Group ID hash (required)

        Returns:
            Bandwidth data including transfer rates
        """
        params = {
            "rankId": rank_id,
            "operatorName": operator_name,
            "stage": stage,
            "iterationId": iteration_id,
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/bandwidth",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_operator_lists(
        self,
        iteration_id: str = "",
        rank_list: Optional[List[str]] = None,
        stage: str = "",
        pg_name: str = "",
        cluster_path: str = "",
        group_id_hash: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get communication operator lists.

        Backend command: communication/operatorNames
        Module: communication

        Args:
            iteration_id: Iteration ID (optional)
            rank_list: List of rank IDs (optional)
            stage: Stage (required, can be empty)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required)
            group_id_hash: Group ID hash (required)

        Returns:
            List of communication operators
        """
        params = {
            "iterationId": iteration_id,
            "rankList": rank_list or [],
            "stage": stage,
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/operatorNames",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_operator_details(
        self,
        stage: str,
        rank_id: str = "",
        iteration_id: str = "",
        order_by: str = "",
        order: str = "",
        query_type: str = "Comparison",
        pg_name: str = "",
        cluster_path: str = "",
        group_id_hash: str = "",
        current_page: int = 0,
        page_size: int = 0
    ) -> Dict[str, Any]:
        """
        Get communication details for operators.

        Backend command: communication/operatorDetails
        Module: communication

        Args:
            stage: Stage (required)
            rank_id: Rank ID (optional)
            iteration_id: Iteration ID (optional)
            order_by: Field to order by
            order: Sort order (asc/desc)
            query_type: Query type (default: Comparison)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required)
            group_id_hash: Group ID hash (required)
            current_page: Current page number
            page_size: Page size

        Returns:
            Communication details for the operator
        """
        params = {
            "stage": stage,
            "rankId": rank_id,
            "iterationId": iteration_id,
            "orderBy": order_by,
            "order": order,
            "queryType": query_type,
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash,
            "currentPage": current_page,
            "pageSize": page_size
        }

        response = self.client.send_command(
            module="communication",
            command="communication/operatorDetails",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_distribution_data(
        self,
        rank_id: str,
        operator_name: str,
        transport_type: str,
        stage: str = "",
        iteration_id: str = "",
        pg_name: str = "",
        cluster_path: str = "/",
        group_id_hash: str = ""
    ) -> Dict[str, Any]:
        """
        Get communication distribution data.

        Backend command: communication/distribution
        Module: communication

        Args:
            rank_id: Rank ID (required)
            operator_name: Operator name (required)
            transport_type: Transport type (required)
            stage: Stage (required, can be empty)
            iteration_id: Iteration ID (optional)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required)
            group_id_hash: Group ID hash (required)

        Returns:
            Distribution data for the communication operator
        """
        params = {
            "rankId": rank_id,
            "operatorName": operator_name,
            "transportType": transport_type,
            "stage": stage,
            "iterationId": iteration_id,
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/distribution",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_iterations(
        self,
        cluster_path: str = "/",
        is_compare: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get communication iterations.

        Backend command: communication/iterations
        Module: communication

        Args:
            cluster_path: Cluster path (required)
            is_compare: Comparison mode flag

        Returns:
            List of communication iterations
        """
        params = {
            "clusterPath": cluster_path,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="communication",
            command="communication/iterations",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_matrix_sort_operator_names(
        self,
        stage: str = "",
        iteration_id: str = "",
        rank_list: Optional[List[str]] = None,
        pg_name: str = "",
        cluster_path: str = "/",
        group_id_hash: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get matrix sorted operator names.

        Backend command: communication/matrixSortOpNames
        Module: communication

        Args:
            stage: Stage (required, can be empty)
            iteration_id: Iteration ID (optional)
            rank_list: List of rank IDs (optional)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required)
            group_id_hash: Group ID hash (required)

        Returns:
            Sorted list of communication operator names
        """
        params = {
            "stage": stage,
            "iterationId": iteration_id,
            "rankList": rank_list or [],
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/matrixSortOpNames",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_duration_list(
        self,
        operator_name: str,
        stage: str = "",
        iteration_id: str = "",
        rank_list: Optional[List[str]] = None,
        target_operator_name: str = "",
        is_compare: bool = False,
        baseline_iteration_id: str = "",
        pg_name: str = "",
        cluster_path: str = "/",
        group_id_hash: str = "",
        baseline_group_id_hash: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Get communication duration list.

        Backend command: communication/list
        Module: communication

        Args:
            operator_name: Operator name (required)
            stage: Stage (required, can be empty)
            iteration_id: Iteration ID (optional)
            rank_list: List of rank IDs (optional)
            target_operator_name: Target operator name (optional)
            is_compare: Comparison mode flag
            baseline_iteration_id: Baseline iteration ID for comparison (optional)
            pg_name: Process group name (optional)
            cluster_path: Cluster path (required)
            group_id_hash: Group ID hash (required)
            baseline_group_id_hash: Baseline group ID hash (optional)

        Returns:
            List of communication duration data
        """
        params = {
            "operatorName": operator_name,
            "stage": stage,
            "iterationId": iteration_id,
            "rankList": rank_list or [],
            "targetOperatorName": target_operator_name,
            "isCompare": is_compare,
            "baselineIterationId": baseline_iteration_id,
            "pgName": pg_name,
            "clusterPath": cluster_path,
            "groupIdHash": group_id_hash,
            "baselineGroupIdHash": baseline_group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/list",
            params=params,
            timeout=10.0
        )

        return response.body if response.body else []

    def get_matrix_group(
        self,
        cluster_path: str = "/",
        iteration_id: str = "",
        baseline_iteration_id: str = "",
        is_compare: bool = False
    ) -> Dict[str, Any]:
        """
        Get communication matrix group.

        Backend command: communication/matrixGroup
        Module: communication

        Args:
            cluster_path: Cluster path (required)
            iteration_id: Iteration ID (optional)
            baseline_iteration_id: Baseline iteration ID for comparison (optional)
            is_compare: Comparison mode flag

        Returns:
            Communication matrix group data
        """
        params = {
            "clusterPath": cluster_path,
            "iterationId": iteration_id,
            "baselineIterationId": baseline_iteration_id,
            "isCompare": is_compare
        }

        response = self.client.send_command(
            module="communication",
            command="communication/matrixGroup",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_matrix_bandwidth(
        self,
        operator_name: str,
        stage: str = "",
        iteration_id: str = "",
        pg_name: str = "",
        group_id_hash: str = "",
        is_compare: bool = False,
        baseline_iteration_id: str = "",
        cluster_path: str = "/",
        baseline_group_id_hash: str = ""
    ) -> Dict[str, Any]:
        """
        Get communication matrix bandwidth.

        Backend command: communication/matrixBandwidth
        Module: communication

        Args:
            operator_name: Operator name (required)
            stage: Stage (required, can be empty)
            iteration_id: Iteration ID (optional)
            pg_name: Process group name (optional)
            group_id_hash: Group ID hash (required)
            is_compare: Comparison mode flag
            baseline_iteration_id: Baseline iteration ID for comparison (optional)
            cluster_path: Cluster path (required)
            baseline_group_id_hash: Baseline group ID hash (optional)

        Returns:
            Communication matrix bandwidth data
        """
        params = {
            "operatorName": operator_name,
            "stage": stage,
            "iterationId": iteration_id,
            "pgName": pg_name,
            "groupIdHash": group_id_hash,
            "isCompare": is_compare,
            "baselineIterationId": baseline_iteration_id,
            "clusterPath": cluster_path,
            "baselineGroupIdHash": baseline_group_id_hash
        }

        response = self.client.send_command(
            module="communication",
            command="communication/matrixBandwidth",
            params=params,
            timeout=10.0
        )

        return response.body or {}

    def get_communication_advisor(
        self,
        cluster_path: str = "/"
    ) -> Dict[str, Any]:
        """
        Get communication advisor recommendations.

        Backend command: communication/communicationAdvisor
        Module: communication

        Args:
            cluster_path: Cluster path (required)

        Returns:
            Communication advisor data including optimization recommendations
        """
        params = {
            "clusterPath": cluster_path
        }

        response = self.client.send_command(
            module="communication",
            command="communication/communicationAdvisor",
            params=params,
            timeout=10.0
        )

        return response.body or {}


# Convenience functions for common use cases

def analyze_performance(
    client: MindStudioWebSocketClient,
    rank_id: str,
    time_flag: str,
    cluster_path: str = ""
) -> Dict[str, Any]:
    """
    Perform comprehensive performance analysis.

    Args:
        client: WebSocket client
        rank_id: Rank ID (required)
        time_flag: Time flag (required)
        cluster_path: Cluster path (can be empty)

    Returns:
        Combined analysis including statistics, top operators, compute/communication details
    """
    summary = SummaryController(client)

    result = {
        "statistics": summary.get_statistics(
            rank_id=rank_id,
            time_flag=time_flag,
            cluster_path=cluster_path
        ),
        "top_operators": summary.get_top_n_data(cluster_path=cluster_path),
        "compute": summary.get_compute_details(
            rank_id=rank_id,
            time_flag=time_flag,
            cluster_path=cluster_path
        ),
        "communication": summary.get_communication_details(
            rank_id=rank_id,
            time_flag=time_flag,
            cluster_path=cluster_path
        )
    }

    return result


def get_operator_breakdown(
    client: MindStudioWebSocketClient,
    rank_id: str,
    group: str = "Operator"
) -> Dict[str, Any]:
    """
    Get operator breakdown analysis.

    Args:
        client: WebSocket client
        rank_id: Rank ID (required)
        group: Group type (Operator, Operator Type, Input Shape)

    Returns:
        Operator categories and statistics
    """
    operator_ctrl = OperatorController(client)

    result = {
        "categories": operator_ctrl.get_category_info(rank_id=rank_id, group=group),
        "statistics": operator_ctrl.get_statistic_info(rank_id=rank_id, group=group),
    }

    return result
