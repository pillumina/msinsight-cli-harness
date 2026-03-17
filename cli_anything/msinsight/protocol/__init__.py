"""
Protocol layer for MindStudio Insight CLI.

This package provides WebSocket communication and protocol analysis
for interacting with the MindStudio Insight backend.
"""

from .websocket_client import (
    MindStudioWebSocketClient,
    Request,
    Response
)
from .protocol_analyzer import (
    ProtocolAnalyzer,
    MessageInterceptor,
    MessageLog
)

__all__ = [
    "MindStudioWebSocketClient",
    "Request",
    "Response",
    "ProtocolAnalyzer",
    "MessageInterceptor",
    "MessageLog"
]
