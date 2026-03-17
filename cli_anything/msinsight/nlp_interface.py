"""
Natural language interface for MindStudio Insight.

This module provides a high-level interface for controlling MindStudio Insight
through natural language commands.
"""

from typing import Dict, Any, Optional
from ..protocol.websocket_client import MindStudioWebSocketClient
from ..nlp.intent_recognizer import IntentRecognizer, Intent
from ..nlp.command_executor import CommandExecutor


class NaturalLanguageInterface:
    """
    Natural language interface for MindStudio Insight.

    This is the main entry point for natural language control of the
    MindStudio Insight frontend.
    """

    def __init__(
        self,
        client: Optional[MindStudioWebSocketClient] = None,
        auto_start: bool = True
    ):
        """
        Initialize natural language interface.

        Args:
            client: WebSocket client (created automatically if None)
            auto_start: Auto-start backend server
        """
        self.client = client or MindStudioWebSocketClient(auto_start=auto_start)
        self.recognizer = IntentRecognizer()
        self.executor = CommandExecutor(self.client)

    def process(self, text: str) -> Dict[str, Any]:
        """
        Process natural language command.

        Args:
            text: Natural language command

        Returns:
            Dictionary with:
            - success: bool
            - intent: recognized intent (if any)
            - result: execution result (if successful)
            - error: error message (if failed)
        """
        # Recognize intent
        intent = self.recognizer.recognize(text)

        if not intent:
            return {
                "success": False,
                "error": "无法识别命令意图",
                "supported_commands": self.get_supported_commands()
            }

        # Execute intent
        try:
            result = self.executor.execute(intent)

            return {
                "success": True,
                "intent": {
                    "type": intent.type.value,
                    "params": intent.params,
                    "confidence": intent.confidence
                },
                "result": result
            }

        except Exception as e:
            return {
                "success": False,
                "intent": {
                    "type": intent.type.value,
                    "params": intent.params
                },
                "error": str(e)
            }

    def get_supported_commands(self) -> list[Dict[str, str]]:
        """
        Get list of supported natural language commands.

        Returns:
            List of command examples
        """
        return [
            {
                "command": "定位到 100ms 到 200ms",
                "description": "Zoom to time range"
            },
            {
                "command": "定位到算子：MatMul_123",
                "description": "Navigate to operator"
            },
            {
                "command": "置顶泳道：rank 0, rank 1",
                "description": "Pin swimlanes"
            },
            {
                "command": "对比 rank 0 和 rank 1",
                "description": "Compare ranks"
            },
            {
                "command": "最慢的10个算子",
                "description": "Get top 10 slow operators"
            },
            {
                "command": "慢算子",
                "description": "Get top slow operators"
            },
            {
                "command": "内存使用情况",
                "description": "Get memory summary"
            },
            {
                "command": "通信矩阵",
                "description": "Get communication matrix"
            },
            {
                "command": "性能瓶颈",
                "description": "Find performance bottleneck"
            },
            {
                "command": "内存泄漏",
                "description": "Detect memory leaks"
            },
            {
                "command": "导出timeline到 timeline.png",
                "description": "Export timeline image"
            }
        ]

    def interactive(self):
        """
        Start interactive natural language session.

        This provides a REPL for natural language commands.
        """
        print("\n" + "="*70)
        print("MindStudio Insight - 自然语言控制界面")
        print("="*70)
        print("\n输入 'help' 查看支持的命令，输入 'quit' 退出\n")

        while True:
            try:
                # Read command
                text = input("msinsight> ").strip()

                if not text:
                    continue

                # Handle meta commands
                if text.lower() in ["quit", "exit", "q"]:
                    print("再见！")
                    break

                if text.lower() in ["help", "?"]:
                    self._print_help()
                    continue

                # Process command
                result = self.process(text)

                # Display result
                if result["success"]:
                    print("✓ 执行成功")
                    self._display_result(result["result"])
                else:
                    print(f"✗ 执行失败: {result['error']}")

                    if "supported_commands" in result:
                        print("\n支持的命令:")
                        self._print_commands(result["supported_commands"])

                print()

            except KeyboardInterrupt:
                print("\n\n再见！")
                break
            except Exception as e:
                print(f"✗ 错误: {e}\n")

    def _print_help(self):
        """Print help information."""
        print("\n" + "="*70)
        print("支持的命令示例")
        print("="*70 + "\n")

        commands = self.get_supported_commands()
        self._print_commands(commands)

        print("\n输入 'quit' 退出交互模式")

    def _print_commands(self, commands: list[Dict[str, str]]):
        """Print list of commands."""
        for cmd in commands:
            print(f"  • {cmd['command']}")
            print(f"    {cmd['description']}\n")

    def _display_result(self, result: Any, indent: int = 0):
        """Display execution result in readable format."""
        prefix = "  " * indent

        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, (dict, list)):
                    print(f"{prefix}{key}:")
                    self._display_result(value, indent + 1)
                else:
                    print(f"{prefix}{key}: {value}")

        elif isinstance(result, list):
            for i, item in enumerate(result, 1):
                print(f"{prefix}{i}.")
                self._display_result(item, indent + 1)

        else:
            print(f"{prefix}{result}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.client.disconnect()
