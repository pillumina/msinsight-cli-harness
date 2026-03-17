#!/usr/bin/env python3
"""
Test connection with correct protocol format.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def test_correct_format():
    """Test with correct protocol format."""
    print("\n" + "="*70)
    print("使用正确格式测试 WebSocket 通信")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✓ 连接成功\n")

        # Test command with correct format
        test_commands = [
            # Command 1: Simple command without fileId/projectName
            {
                "id": 1,
                "type": "request",
                "moduleName": "timeline",
                "command": "getSwimlaneList",
                "params": {}
            },
            # Command 2: With fileId and projectName (if needed)
            {
                "id": 2,
                "type": "request",
                "moduleName": "operator",
                "command": "getStatistics",
                "fileId": "",
                "projectName": "",
                "params": {}
            },
        ]

        for i, cmd in enumerate(test_commands, 1):
            print(f"{'='*70}")
            print(f"测试命令 {i}: {cmd['moduleName']}.{cmd['command']}")
            print(f"{'='*70}")
            print(f"发送:\n{json.dumps(cmd, indent=2, ensure_ascii=False)}\n")

            try:
                ws.send(json.dumps(cmd))
                print("✓ 命令已发送")

                # Wait for response
                ws.settimeout(5.0)
                try:
                    response_str = ws.recv()
                    print(f"\n✓ 收到响应:")

                    response = json.loads(response_str)
                    print(json.dumps(response, indent=2, ensure_ascii=False))

                    # Check response format
                    print(f"\n响应分析:")
                    print(f"  - type: {response.get('type')}")
                    print(f"  - requestId: {response.get('requestId')}")
                    print(f"  - result: {response.get('result')}")

                    if 'body' in response:
                        print(f"  - body: {type(response['body'])}")

                    if 'error' in response:
                        print(f"  - error: {response['error']}")

                    print(f"\n✓ 命令执行成功！格式正确！\n")

                except websocket.WebSocketTimeoutException:
                    print("✗ 超时，没有收到响应\n")

            except Exception as e:
                print(f"✗ 发送/接收失败: {e}\n")

            time.sleep(1)

        # Close connection
        ws.close()
        print("\n✓ 已断开连接")

    except Exception as e:
        print(f"✗ 连接失败: {e}")

    print("\n" + "="*70)
    print("测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_correct_format()
