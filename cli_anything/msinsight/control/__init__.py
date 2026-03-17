"""
Control layer for MindStudio Insight CLI.

This package provides high-level control operations for manipulating
the MindStudio Insight frontend through the WebSocket backend.
"""

from .timeline_controller import TimelineController
from .data_query import DataQuery

__all__ = [
    "TimelineController",
    "DataQuery"
]
