"""
Natural language intent recognition for MindStudio Insight.

This module provides intent recognition capabilities for converting
natural language commands into structured intents.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class IntentType(Enum):
    """Types of recognized intents."""
    # Navigation intents
    ZOOM_TO_TIME = "zoom_to_time"
    GO_TO_OPERATOR = "go_to_operator"
    PIN_SWIMLANES = "pin_swimlanes"
    COMPARE_RANKS = "compare_ranks"
    FILTER_SWIMLANES = "filter_swimlanes"

    # Query intents
    GET_TOP_OPERATORS = "get_top_operators"
    GET_OPERATOR_INFO = "get_operator_info"
    GET_MEMORY_SUMMARY = "get_memory_summary"
    GET_COMMUNICATION_MATRIX = "get_communication_matrix"

    # Analysis intents
    FIND_BOTTLENECK = "find_bottleneck"
    FIND_MEMORY_LEAKS = "find_memory_leaks"
    COMPARE_PERFORMANCE = "compare_performance"

    # Export intents
    EXPORT_TIMELINE = "export_timeline"
    EXPORT_REPORT = "export_report"


@dataclass
class Intent:
    """Recognized intent with parameters."""
    type: IntentType
    params: Dict[str, Any]
    confidence: float
    original_text: str


class IntentRecognizer:
    """
    Recognizes intents from natural language commands.

    Uses pattern matching to identify user intents and extract parameters.
    """

    def __init__(self):
        """Initialize intent recognizer with pattern rules."""
        self.patterns = self._build_patterns()

    def _build_patterns(self) -> List[Dict[str, Any]]:
        """Build pattern matching rules."""
        return [
            # Zoom patterns
            {
                "pattern": r"定位到.*(\d+(?:\.\d+)?)\s*(ms|us|ns).*到.*(\d+(?:\.\d+)?)\s*(ms|us|ns)",
                "intent_type": IntentType.ZOOM_TO_TIME,
                "extractor": self._extract_time_range
            },
            {
                "pattern": r"zoom.*(\d+(?:\.\d+)?)\s*(ms|us|ns).*(\d+(?:\.\d+)?)\s*(ms|us|ns)",
                "intent_type": IntentType.ZOOM_TO_TIME,
                "extractor": self._extract_time_range
            },
            {
                "pattern": r"跳转到.*(\d+(?:\.\d+)?)\s*(ms|us|ns)",
                "intent_type": IntentType.ZOOM_TO_TIME,
                "extractor": self._extract_single_time
            },

            # Operator navigation
            {
                "pattern": r"定位到.*算子[：:]\s*(.+)",
                "intent_type": IntentType.GO_TO_OPERATOR,
                "extractor": self._extract_operator_name
            },
            {
                "pattern": r"go to operator[：:]\s*(.+)",
                "intent_type": IntentType.GO_TO_OPERATOR,
                "extractor": self._extract_operator_name
            },
            {
                "pattern": r"找到.*算子\s+(.+)",
                "intent_type": IntentType.GO_TO_OPERATOR,
                "extractor": self._extract_operator_name
            },

            # Pin swimlanes
            {
                "pattern": r"置顶.*泳道[：:]\s*(.+)",
                "intent_type": IntentType.PIN_SWIMLANES,
                "extractor": self._extract_swimlane_list
            },
            {
                "pattern": r"pin.*(?:lanes?|swimlanes?)[：:]\s*(.+)",
                "intent_type": IntentType.PIN_SWIMLANES,
                "extractor": self._extract_swimlane_list
            },
            {
                "pattern": r"对比\s+(.+)",
                "intent_type": IntentType.COMPARE_RANKS,
                "extractor": self._extract_compare_targets
            },

            # Filter swimlanes
            {
                "pattern": r"只显示.*(?:类型|type)[：:]\s*(.+)",
                "intent_type": IntentType.FILTER_SWIMLANES,
                "extractor": lambda m: {"filter_type": "type", "pattern": m.group(1).strip()}
            },
            {
                "pattern": r"过滤.*(?:类型|type)[：:]\s*(.+)",
                "intent_type": IntentType.FILTER_SWIMLANES,
                "extractor": lambda m: {"filter_type": "type", "pattern": m.group(1).strip()}
            },

            # Top operators
            {
                "pattern": r"(?:最慢|耗时最长|top)\s*(\d+)?\s*个?算子",
                "intent_type": IntentType.GET_TOP_OPERATORS,
                "extractor": self._extract_top_n
            },
            {
                "pattern": r"top\s*(\d+)?\s*operators?",
                "intent_type": IntentType.GET_TOP_OPERATORS,
                "extractor": self._extract_top_n
            },
            {
                "pattern": r"慢算子",
                "intent_type": IntentType.GET_TOP_OPERATORS,
                "extractor": lambda m: {"n": 10, "metric": "duration"}
            },

            # Operator info
            {
                "pattern": r"算子\s+(.+?)\s*(?:的)?详情",
                "intent_type": IntentType.GET_OPERATOR_INFO,
                "extractor": lambda m: {"operator_name": m.group(1).strip()}
            },

            # Memory analysis
            {
                "pattern": r"内存(?:使用)?(?:情况|摘要|summary)",
                "intent_type": IntentType.GET_MEMORY_SUMMARY,
                "extractor": lambda m: {}
            },
            {
                "pattern": r"内存泄漏",
                "intent_type": IntentType.FIND_MEMORY_LEAKS,
                "extractor": lambda m: {}
            },

            # Communication
            {
                "pattern": r"通信(?:矩阵|情况)",
                "intent_type": IntentType.GET_COMMUNICATION_MATRIX,
                "extractor": lambda m: {}
            },

            # Bottleneck
            {
                "pattern": r"性能瓶颈",
                "intent_type": IntentType.FIND_BOTTLENECK,
                "extractor": lambda m: {}
            },
            {
                "pattern": r"bottleneck",
                "intent_type": IntentType.FIND_BOTTLENECK,
                "extractor": lambda m: {}
            },

            # Export
            {
                "pattern": r"导出.*timeline.*(?:到|to)?\s*(.+)",
                "intent_type": IntentType.EXPORT_TIMELINE,
                "extractor": lambda m: {"output_path": m.group(1).strip()}
            },
            {
                "pattern": r"export.*timeline\s+(.+)",
                "intent_type": IntentType.EXPORT_TIMELINE,
                "extractor": lambda m: {"output_path": m.group(1).strip()}
            }
        ]

    def recognize(self, text: str) -> Optional[Intent]:
        """
        Recognize intent from natural language text.

        Args:
            text: Natural language command

        Returns:
            Recognized intent or None
        """
        text_lower = text.lower().strip()

        # Try each pattern
        for rule in self.patterns:
            match = re.search(rule["pattern"], text_lower, re.IGNORECASE)
            if match:
                # Extract parameters
                params = rule["extractor"](match)

                # Calculate confidence based on pattern complexity
                confidence = min(1.0, len(rule["pattern"]) / 50.0 + 0.5)

                return Intent(
                    type=rule["intent_type"],
                    params=params,
                    confidence=confidence,
                    original_text=text
                )

        return None

    # Parameter extractors

    def _extract_time_range(self, match) -> Dict[str, Any]:
        """Extract time range from match."""
        start_time = float(match.group(1))
        start_unit = match.group(2)
        end_time = float(match.group(3))
        end_unit = match.group(4)

        return {
            "start_time": start_time,
            "start_unit": start_unit,
            "end_time": end_time,
            "end_unit": end_unit
        }

    def _extract_single_time(self, match) -> Dict[str, Any]:
        """Extract single time point from match."""
        time_val = float(match.group(1))
        unit = match.group(2)

        # Create a small range around the time
        return {
            "start_time": time_val,
            "end_time": time_val + 100,  # Add 100 units
            "start_unit": unit,
            "end_unit": unit
        }

    def _extract_operator_name(self, match) -> Dict[str, Any]:
        """Extract operator name from match."""
        return {
            "operator_name": match.group(1).strip()
        }

    def _extract_swimlane_list(self, match) -> Dict[str, Any]:
        """Extract swimlane list from match."""
        lane_str = match.group(1).strip()
        # Split by comma, Chinese comma, or "and"
        lanes = re.split(r'[,，]|and', lane_str)
        lanes = [l.strip() for l in lanes if l.strip()]
        return {
            "lane_ids": lanes
        }

    def _extract_compare_targets(self, match) -> Dict[str, Any]:
        """Extract comparison targets from match."""
        target_str = match.group(1).strip()
        # Split by "和", "与", comma, or "and"
        targets = re.split(r'[和与,，]|and', target_str)
        targets = [t.strip() for t in targets if t.strip()]
        return {
            "rank_ids": targets
        }

    def _extract_top_n(self, match) -> Dict[str, Any]:
        """Extract top N from match."""
        n_str = match.group(1)
        n = int(n_str) if n_str else 10
        return {
            "n": n,
            "metric": "duration"
        }

    def get_supported_intents(self) -> List[str]:
        """
        Get list of supported intent types.

        Returns:
            List of intent type names
        """
        return [intent_type.value for intent_type in IntentType]
