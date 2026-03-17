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
    file_id: str = ""
    project_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "id": self.id,
            "type": self.type,
            "moduleName": self.module_name,
            "command": self.command,
            "fileId": self.file_id,
            "projectName": self.project_name,
        }
        if self.params is not None:
            result["params"] = self.params
        else:
            result["params"] = {}
        return result


@dataclass
class Response:
    """WebSocket response message."""
    type: str
    request_id: int  # Maps to requestId in JSON
    result: bool  # Not 'success'
    body: Optional[Any] = None  # Not 'data', can be dict, list, or primitive
    error: Optional[Dict[str, Any]] = None  # {code, message}
    command: Optional[str] = None
    module_name: Optional[str] = None

    @property
    def success(self) -> bool:
        """Alias for result for backward compatibility."""
        return self.result

    @property
    def data(self) -> Optional[Any]:
        """Alias for body for backward compatibility."""
        return self.body

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Response':
        """Create Response from dictionary."""
        return cls(
            type=data.get("type", "response"),
            request_id=data.get("requestId", data.get("id", 0)),  # Handle both formats
            result=data.get("result", False),
            body=data.get("body", data.get("data")),  # Handle both formats
            error=data.get("error"),
            command=data.get("command"),
            module_name=data.get("moduleName")
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

        try:
            # Send request as plain JSON (like GUI does)
            json_body = json.dumps(request.to_dict())
            if self.log_messages:
                print(f"[WS →] {json_body}")

            self.ws.send(json_body)

            # Wait for response
            response_text = self.ws.recv()

            # Parse LSP-style response (skip Content-Length header)
            if response_text.startswith("Content-Length:"):
                header_end = response_text.find("\r\n\r\n")
                if header_end != -1:
                    response_text = response_text[header_end + 4:]

            response_data = json.loads(response_text)
            if self.log_messages:
                print(f"[WS ←] {json.dumps(response_data)}")

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
