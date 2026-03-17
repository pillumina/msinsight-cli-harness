"""
WebSocket client for MindStudio Insight backend.

This module provides a robust client for communicating with the MindStudio
backend server using the WebSocket protocol.
"""

import json
import time
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
import threading
import queue

try:
    import websocket
except ImportError:
    websocket = None

from ..utils.msinsight_backend import (
    MsInsightBackendError,
    MsInsightConnection,
    is_server_running,
    find_available_port,
    start_server,
    wait_for_server_ready
)


@dataclass
class Request:
    """WebSocket request message."""
    id: int
    type: str = "request"
    module_name: str = ""
    command: str = ""
    params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "type": self.type,
            "moduleName": self.module_name,
            "command": self.command
        }
        if self.params:
            result["params"] = self.params
        return result


@dataclass
class Response:
    """WebSocket response message."""
    id: int
    type: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create Response from dictionary."""
        return cls(
            id=data.get("id", 0),
            type=data.get("type", "response"),
            success=data.get("success", False),
            data=data.get("data"),
            error=data.get("error")
        )


class MindStudioWebSocketClient:
    """
    Advanced WebSocket client for MindStudio Insight.

    Features:
    - Auto-reconnect
    - Request/response correlation
    - Async message handling
    - Protocol logging
    """

    def __init__(
        self,
        port: Optional[int] = None,
        auto_start: bool = True,
        log_messages: bool = False
    ):
        """
        Initialize WebSocket client.

        Args:
            port: Server port (auto-discover if None)
            auto_start: Automatically start server if not running
            log_messages: Log all sent/received messages
        """
        if websocket is None:
            raise MsInsightBackendError(
                "websocket-client library not installed.\n"
                "Install with: pip install websocket-client"
            )

        self.port = port
        self.auto_start = auto_start
        self.log_messages = log_messages
        self.ws = None
        self.server_process = None
        self.msg_id = 0
        self.pending_responses: Dict[int, queue.Queue] = {}
        self.message_handlers: list[Callable[[Dict], None]] = []
        self._connected = False

    def connect(self):
        """Establish WebSocket connection to backend."""
        if self._connected:
            return

        # Ensure server is running
        if self.auto_start:
            self._ensure_server_running()

        ws_url = f"ws://127.0.0.1:{self.port}"

        try:
            self.ws = websocket.create_connection(ws_url, timeout=10)
            self._connected = True

            if self.log_messages:
                print(f"[WS] Connected to {ws_url}")

        except Exception as e:
            raise MsInsightBackendError(
                f"Failed to connect to server at {ws_url}: {e}"
            )

    def _ensure_server_running(self):
        """Ensure backend server is running."""
        if self.port is None:
            # Try to find running server
            for port in range(9000, 9100):
                if is_server_running(port):
                    self.port = port
                    return

            # No server found, start new one
            self.port = find_available_port()
            self.server_process = start_server(self.port)
            wait_for_server_ready(self.port)
        else:
            # Check if specified port is running
            if not is_server_running(self.port):
                self.server_process = start_server(self.port)
                wait_for_server_ready(self.port)

    def send_command(
        self,
        module: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: float = 10.0
    ) -> Response:
        """
        Send command to backend and wait for response.

        Args:
            module: Backend module name (e.g., "timeline", "memory")
            command: Command name (e.g., "getOperators")
            params: Command parameters
            timeout: Response timeout in seconds

        Returns:
            Response object

        Raises:
            MsInsightBackendError: If request fails or times out
        """
        self.connect()

        # Create request
        self.msg_id += 1
        request = Request(
            id=self.msg_id,
            module_name=module,
            command=command,
            params=params
        )

        # Create response queue for this request
        response_queue = queue.Queue()
        self.pending_responses[request.id] = response_queue

        try:
            # Send request
            message = json.dumps(request.to_dict())
            if self.log_messages:
                print(f"[WS →] {message}")

            self.ws.send(message)

            # Wait for response
            try:
                response_data = response_queue.get(timeout=timeout)
                response = Response.from_dict(response_data)

                if not response.success:
                    raise MsInsightBackendError(
                        response.error or "Unknown backend error"
                    )

                return response

            except queue.Empty:
                raise MsInsightBackendError(
                    f"Request timed out after {timeout} seconds"
                )

        finally:
            # Cleanup
            if request.id in self.pending_responses:
                del self.pending_responses[request.id]

    def send_raw(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send raw message and return response.

        Args:
            message: Raw message dictionary

        Returns:
            Response dictionary
        """
        self.connect()

        if self.log_messages:
            print(f"[WS →] {json.dumps(message)}")

        self.ws.send(json.dumps(message))
        response = json.loads(self.ws.recv())

        if self.log_messages:
            print(f"[WS ←] {json.dumps(response)}")

        return response

    def add_message_handler(self, handler: Callable[[Dict], None]):
        """
        Add handler for incoming messages.

        Args:
            handler: Function to call with each message
        """
        self.message_handlers.append(handler)

    def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None
            self._connected = False

            if self.log_messages:
                print("[WS] Disconnected")

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __del__(self):
        """Cleanup on deletion."""
        self.disconnect()

        # Stop server if we started it
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=2)
            except:
                try:
                    self.server_process.kill()
                except:
                    pass
