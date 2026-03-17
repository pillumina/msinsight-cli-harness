"""
Protocol analyzer for MindStudio Insight.

This module captures and analyzes WebSocket messages between the GUI and backend,
enabling reverse engineering of the protocol for CLI implementation.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
import threading


@dataclass
class MessageLog:
    """Logged WebSocket message."""
    timestamp: str
    direction: str  # "send" or "receive"
    message: Dict[str, Any]
    module: Optional[str] = None
    command: Optional[str] = None
    success: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ProtocolAnalyzer:
    """
    Analyzes WebSocket protocol messages.

    Features:
    - Message logging
    - Command pattern extraction
    - Protocol documentation generation
    """

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize analyzer.

        Args:
            log_file: Path to log file for message storage
        """
        self.log_file = Path(log_file) if log_file else None
        self.messages: List[MessageLog] = []
        self.command_patterns: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def log_message(
        self,
        direction: str,
        message: Dict[str, Any],
        auto_analyze: bool = True
    ):
        """
        Log a WebSocket message.

        Args:
            direction: "send" or "receive"
            message: Message dictionary
            auto_analyze: Automatically analyze command patterns
        """
        with self._lock:
            # Extract metadata
            module = message.get("moduleName")
            command = message.get("command")
            success = message.get("success")

            # Create log entry
            log_entry = MessageLog(
                timestamp=datetime.now().isoformat(),
                direction=direction,
                message=message,
                module=module,
                command=command,
                success=success
            )

            self.messages.append(log_entry)

            # Analyze patterns
            if auto_analyze and direction == "send":
                self._analyze_command(module, command, message.get("params"))

            # Write to file
            if self.log_file:
                self._write_log(log_entry)

    def _analyze_command(
        self,
        module: Optional[str],
        command: Optional[str],
        params: Optional[Dict[str, Any]]
    ):
        """Analyze command pattern."""
        if not module or not command:
            return

        key = f"{module}.{command}"

        if key not in self.command_patterns:
            self.command_patterns[key] = {
                "module": module,
                "command": command,
                "param_examples": [],
                "call_count": 0,
                "first_seen": datetime.now().isoformat()
            }

        pattern = self.command_patterns[key]
        pattern["call_count"] += 1
        pattern["last_seen"] = datetime.now().isoformat()

        # Store unique param examples (max 5)
        if params and len(pattern["param_examples"]) < 5:
            if params not in pattern["param_examples"]:
                pattern["param_examples"].append(params)

    def _write_log(self, log_entry: MessageLog):
        """Write log entry to file."""
        if not self.log_file:
            return

        # Create directory if needed
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Append to file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry.to_dict()) + "\n")

    def get_command_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovered commands.

        Returns:
            Dictionary with command patterns and statistics
        """
        with self._lock:
            return {
                "total_messages": len(self.messages),
                "unique_commands": len(self.command_patterns),
                "commands": self.command_patterns,
                "modules": self._get_module_summary()
            }

    def _get_module_summary(self) -> Dict[str, List[str]]:
        """Get commands grouped by module."""
        modules = {}
        for key, pattern in self.command_patterns.items():
            module = pattern["module"]
            command = pattern["command"]
            if module not in modules:
                modules[module] = []
            if command not in modules[module]:
                modules[module].append(command)
        return modules

    def export_protocol_doc(self, output_path: str):
        """
        Export protocol documentation in markdown format.

        Args:
            output_path: Path to output markdown file
        """
        summary = self.get_command_summary()

        doc = [
            "# MindStudio Insight Protocol Documentation",
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "## Overview",
            "",
            f"- **Total Messages Captured**: {summary['total_messages']}",
            f"- **Unique Commands**: {summary['unique_commands']}",
            f"- **Modules**: {len(summary['modules'])}",
            "",
            "## Commands by Module",
            ""
        ]

        for module, commands in sorted(summary["modules"].items()):
            doc.append(f"### {module}")
            doc.append("")
            doc.append("| Command | Call Count | Parameters |")
            doc.append("|---------|------------|------------|")

            for command in sorted(commands):
                key = f"{module}.{command}"
                pattern = summary["commands"][key]
                param_count = len(pattern["param_examples"])
                doc.append(
                    f"| {command} | {pattern['call_count']} | {param_count} examples |"
                )

            doc.append("")

        # Add detailed parameter examples
        doc.append("## Parameter Examples")
        doc.append("")

        for key, pattern in sorted(summary["commands"].items()):
            if pattern["param_examples"]:
                doc.append(f"### {key}")
                doc.append("")
                for i, params in enumerate(pattern["param_examples"], 1):
                    doc.append(f"**Example {i}:**")
                    doc.append("```json")
                    doc.append(json.dumps(params, indent=2))
                    doc.append("```")
                    doc.append("")

        # Write to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(doc))

    def load_logs(self, log_file: str):
        """
        Load messages from log file.

        Args:
            log_file: Path to log file
        """
        with open(log_file, "r") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    log_entry = MessageLog(**data)
                    self.messages.append(log_entry)

                    # Re-analyze
                    if log_entry.direction == "send":
                        self._analyze_command(
                            log_entry.module,
                            log_entry.command,
                            log_entry.message.get("params")
                        )
                except Exception as e:
                    print(f"Failed to load log entry: {e}")

    def clear(self):
        """Clear all logged messages and patterns."""
        with self._lock:
            self.messages.clear()
            self.command_patterns.clear()


class MessageInterceptor:
    """
    Intercepts WebSocket messages for analysis.

    This class wraps a WebSocket client and logs all messages
    passing through it.
    """

    def __init__(
        self,
        client,  # MindStudioWebSocketClient
        analyzer: Optional[ProtocolAnalyzer] = None
    ):
        """
        Initialize interceptor.

        Args:
            client: WebSocket client to wrap
            analyzer: Protocol analyzer for logging
        """
        self.client = client
        self.analyzer = analyzer or ProtocolAnalyzer()

    def send_command(
        self,
        module: str,
        command: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Any:
        """
        Send command and log both request and response.

        Args:
            module: Module name
            command: Command name
            params: Command parameters
            **kwargs: Additional arguments for client

        Returns:
            Response from client
        """
        # Log request
        request = {
            "moduleName": module,
            "command": command,
            "params": params
        }
        self.analyzer.log_message("send", request)

        # Send command
        response = self.client.send_command(module, command, params, **kwargs)

        # Log response
        self.analyzer.log_message(
            "receive",
            {
                "success": response.success,
                "data": response.data,
                "error": response.error
            }
        )

        return response

    def get_analyzer(self) -> ProtocolAnalyzer:
        """Get the protocol analyzer."""
        return self.analyzer
