#!/usr/bin/env python3
"""
Debug script to test WebSocket communication with MindStudio Insight.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def debug_websocket():
    """Debug WebSocket communication."""
    print("\n" + "="*70)
    print("调试 MindStudio Insight WebSocket 通信")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    try:
        # Create WebSocket connection
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✓ 连接成功\n")

        # Try different command formats
        test_commands = [
            # Format 1: Our assumed format
            {
                "id": 1,
                "type": "request",
                "moduleName": "timeline",
                "command": "getSwimlaneList",
                "params": {}
            },
            # Format 2: Maybe module instead of moduleName
            {
                "id": 2,
                "type": "request",
                "module": "timeline",
                "command": "getSwimlaneList"
            },
            # Format 3: Maybe cmd instead of command
            {
                "id": 3,
                "type": "request",
                "moduleName": "timeline",
                "cmd": "getSwimlaneList"
            },
            # Format 4: Simple ping
            {
                "id": 4,
                "type": "ping"
            },
            # Format 5: Just module and command
            {
                "module": "timeline",
                "command": "getSwimlaneList"
            }
        ]

        for i, cmd in enumerate(test_commands, 1):
            print(f"{'='*70}")
            print(f"测试命令格式 {i}:")
            print(f"{'='*70}")
            print(f"发送: {json.dumps(cmd, indent=2)}\n")

            try:
                # Send command
                ws.send(json.dumps(cmd))

                # Try to receive response with short timeout
                ws.settimeout(3.0)
                try:
                    response = ws.recv()
                    print(f"✓ 收到响应:")
                    try:
                        response_data = json.loads(response)
                        print(json.dumps(response_data, indent=2, ensure_ascii=False))
                    except:
                        print(response)

                    print("\n✓ 这个格式正确！\n")
                    break

                except websocket.WebSocketTimeoutException:
                    print("✗ 超时，没有收到响应\n")

            except Exception as e:
                print(f"✗ 发送失败: {e}\n")

            time.sleep(0.5)

        # Close connection
        ws.close()
        print("\n✓ 已断开连接")

    except Exception as e:
        print(f"✗ 连接失败: {e}")

    print("\n" + "="*70)
    print("调试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    debug_websocket()
