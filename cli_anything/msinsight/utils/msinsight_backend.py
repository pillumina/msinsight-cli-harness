"""
Backend integration for MindStudio Insight server.

This module handles finding, starting, and communicating with the
MindStudio Insight WebSocket backend server.
"""

import os
import sys
import time
import socket
import subprocess
import shutil
import json
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import websocket
except ImportError:
    websocket = None


class MsInsightBackendError(Exception):
    """Exception raised for backend errors."""
    pass


def find_msinsight_binary() -> str:
    """
    Find the msinsight-server binary.

    Search order:
    1. System PATH
    2. Installed MindStudio Insight GUI application
    3. Source code build directory

    Returns:
        Path to the server binary

    Raises:
        MsInsightBackendError: If binary not found
    """
    search_paths = []

    # 1. Check PATH first (highest priority)
    path_binary = shutil.which("msinsight-server")
    if path_binary:
        return path_binary

    # 2. Check installed MindStudio Insight GUI application
    if sys.platform == "win32":
        # Windows: Check Program Files
        search_paths.extend([
            Path("C:/Program Files/MindStudio Insight/bin/msinsight-server.exe"),
            Path("C:/Program Files (x86)/MindStudio Insight/bin/msinsight-server.exe"),
            Path(os.path.expandvars(r"%LOCALAPPDATA%/MindStudio Insight/bin/msinsight-server.exe")),
        ])
    elif sys.platform == "darwin":
        # macOS: Check Applications
        search_paths.extend([
            Path("/Applications/MindStudio Insight.app/Contents/MacOS/msinsight-server"),
            Path("/Applications/MindStudio Insight.app/Contents/Resources/bin/msinsight-server"),
            Path(os.path.expanduser("~/Applications/MindStudio Insight.app/Contents/MacOS/msinsight-server")),
        ])
    else:  # Linux
        import platform
        arch = platform.machine()
        # Linux: Check common installation directories
        search_paths.extend([
            Path("/opt/mindstudio-insight/bin/msinsight-server"),
            Path("/usr/local/bin/msinsight-server"),
            Path("/usr/bin/msinsight-server"),
            Path(f"/opt/mindstudio-insight-{arch}/bin/msinsight-server"),
        ])

    # 3. Check source code build directory (for development)
    msinsight_root = Path(__file__).parent.parent.parent.parent.parent
    server_root = msinsight_root / "server"

    if sys.platform == "win32":
        search_paths.extend([
            server_root / "output" / "win_mingw64" / "bin" / "msinsight-server.exe",
            server_root / "output" / "build" / "server" / "msinsight-server.exe",
        ])
    elif sys.platform == "darwin":
        search_paths.extend([
            server_root / "output" / "darwin" / "bin" / "msinsight-server",
            server_root / "output" / "build" / "server" / "msinsight-server",
        ])
    else:  # Linux
        import platform
        arch = platform.machine()
        search_paths.extend([
            server_root / "output" / f"linux-{arch}" / "bin" / "msinsight-server",
            server_root / "output" / "build" / "server" / "msinsight-server",
        ])

    # Check all search paths
    for path in search_paths:
        if path.exists():
            return str(path)

    # Provide helpful error message
    install_instructions = """
MindStudio Insight backend server not found.

Please ensure MindStudio Insight is installed:

  Windows: Download and run the installer from the release page
  macOS:   Download and install the .dmg file
  Linux:   Download and extract the .tar.gz package

Alternatively, if you have source code access:
  cd server
  python build/build.py build --release

The backend server is a hard dependency - the CLI cannot work without it.
"""

    raise MsInsightBackendError(install_instructions)


def find_available_port(start: int = 9000, end: int = 9100) -> int:
    """
    Find an available port in the given range.

    Args:
        start: Start of port range
        end: End of port range

    Returns:
        Available port number

    Raises:
        MsInsightBackendError: If no port available
    """
    for port in range(start, end):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            sock.connect(("127.0.0.1", port))
            sock.close()
            # Port is in use, check if it's our server
            continue
        except (socket.timeout, ConnectionRefusedError):
            sock.close()
            return port

    raise MsInsightBackendError(
        f"No available port found in range {start}-{end}.\n"
        "Close some services and try again."
    )


def is_server_running(port: int, timeout: float = 2.0) -> bool:
    """
    Check if a server is running on the given port.

    Args:
        port: Port to check
        timeout: Connection timeout

    Returns:
        True if server is running
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect(("127.0.0.1", port))
        sock.close()
        return True
    except (socket.timeout, ConnectionRefusedError):
        sock.close()
        return False


def start_server(port: int, log_path: Optional[str] = None) -> subprocess.Popen:
    """
    Start the MindStudio Insight backend server.

    Args:
        port: Port to listen on
        log_path: Optional log file path

    Returns:
        Subprocess handle

    Raises:
        MsInsightBackendError: If server fails to start
    """
    binary = find_msinsight_binary()

    cmd = [binary, f"--wsPort={port}", "--wsHost=127.0.0.1"]

    if log_path:
        cmd.append(f"--logPath={log_path}")

    try:
        # Start server in background
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        return process
    except Exception as e:
        raise MsInsightBackendError(f"Failed to start server: {e}")


def wait_for_server_ready(port: int, timeout: float = 10.0) -> bool:
    """
    Wait for server to be ready.

    Args:
        port: Server port
        timeout: Maximum wait time in seconds

    Returns:
        True if server is ready

    Raises:
        MsInsightBackendError: If server doesn't become ready
    """
    start_time = time.time()

    while time.time() - start_time < timeout:
        if is_server_running(port):
            # Additional wait for server to fully initialize
            time.sleep(0.5)
            return True
        time.sleep(0.1)

    raise MsInsightBackendError(
        f"Server did not become ready within {timeout} seconds.\n"
        "Check server logs for errors."
    )


class MsInsightConnection:
    """
    Connection to MindStudio Insight backend server.

    Handles WebSocket communication with the backend.
    """

    def __init__(self, port: Optional[int] = None, auto_start: bool = True):
        """
        Initialize connection.

        Args:
            port: Server port (auto-discover if None)
            auto_start: Automatically start server if not running
        """
        if websocket is None:
            raise MsInsightBackendError(
                "websocket-client library not installed.\n"
                "Install with: pip install websocket-client"
            )

        self.port = port
        self.ws = None
        self.server_process = None

        if auto_start:
            self._ensure_server_running()

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

    def connect(self):
        """Establish WebSocket connection."""
        if self.ws is None:
            ws_url = f"ws://127.0.0.1:{self.port}"
            try:
                self.ws = websocket.create_connection(ws_url, timeout=10)
            except Exception as e:
                raise MsInsightBackendError(
                    f"Failed to connect to server at {ws_url}: {e}"
                )

    def disconnect(self):
        """Close WebSocket connection."""
        if self.ws:
            try:
                self.ws.close()
            except:
                pass
            self.ws = None

    def send_request(self, module: str, command: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send request to backend server.

        Args:
            module: Backend module name
            command: Command name
            params: Request parameters

        Returns:
            Response data

        Raises:
            MsInsightBackendError: If request fails
        """
        self.connect()

        request = {
            "module": module,
            "command": command,
            "params": params
        }

        try:
            # Send request
            self.ws.send(json.dumps(request))

            # Receive response
            response = self.ws.recv()
            data = json.loads(response)

            if data.get("status") == "error":
                raise MsInsightBackendError(
                    data.get("error", "Unknown error from backend")
                )

            return data

        except json.JSONDecodeError as e:
            raise MsInsightBackendError(f"Invalid JSON response: {e}")
        except Exception as e:
            raise MsInsightBackendError(f"Communication error: {e}")

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
