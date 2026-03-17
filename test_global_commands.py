#!/usr/bin/env python3
"""
Test global commands that don't require a project.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def test_global_commands():
    """Test global commands without project."""
    print("\n" + "="*70)
    print("测试全局命令（不需要项目）")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✓ 连接成功\n")

        # Step 1: Heartbeat
        print(f"{'='*70}")
        print("步骤 1: 发送心跳检查")
        print(f"{'='*70}")

        heartbeat = {
            "id": 1,
            "type": "request",
            "moduleName": "global",
            "command": "heartCheck",
            "params": {}
        }

        ws.send(json.dumps(heartbeat))
        response = ws.recv()
        data = json.loads(response)
        print(f"✓ 心跳成功: result={data.get('result')}\n")

        time.sleep(0.3)

        # Step 2: Try various global commands
        test_commands = [
            {
                "name": "获取服务器状态",
                "command": {
                    "id": 2,
                    "type": "request",
                    "moduleName": "global",
                    "command": "getServerStatus",
                    "params": {}
                }
            },
            {
                "name": "获取项目列表",
                "command": {
                    "id": 3,
                    "type": "request",
                    "moduleName": "project",
                    "command": "getProjectList",
                    "params": {}
                }
            },
            {
                "name": "获取支持的分析类型",
                "command": {
                    "id": 4,
                    "type": "request",
                    "moduleName": "global",
                    "command": "getSupportedAnalysisTypes",
                    "params": {}
                }
            },
            {
                "name": "获取版本信息",
                "command": {
                    "id": 5,
                    "type": "request",
                    "moduleName": "global",
                    "command": "getVersion",
                    "params": {}
                }
            }
        ]

        for i, test_cmd in enumerate(test_commands, 1):
            print(f"{'='*70}")
            print(f"步骤 {i+1}: {test_cmd['name']}")
            print(f"{'='*70}")
            print(f"发送: {json.dumps(test_cmd['command'], indent=2, ensure_ascii=False)}")

            try:
                ws.send(json.dumps(test_cmd['command']))
                ws.settimeout(3.0)

                response = ws.recv()
                data = json.loads(response)

                print(f"\n✓ 收到响应:")
                print(f"  - type: {data.get('type')}")
                print(f"  - requestId: {data.get('requestId')}")
                print(f"  - result: {data.get('result')}")

                if data.get('body'):
                    body = data['body']
                    if isinstance(body, dict):
                        print(f"  - body keys: {list(body.keys())[:10]}")
                        # Show some content
                        for key in list(body.keys())[:3]:
                            value = body[key]
                            if isinstance(value, (str, int, float, bool)):
                                print(f"    • {key}: {value}")
                            elif isinstance(value, list):
                                print(f"    • {key}: [{len(value)} items]")
                            elif isinstance(value, dict):
                                print(f"    • {key}: {{{len(value)} keys}}")
                    elif isinstance(body, list):
                        print(f"  - body: [{len(body)} items]")
                        if body:
                            print(f"    第一个元素: {str(body[0])[:100]}")
                    else:
                        print(f"  - body: {str(body)[:200]}")

                if data.get('error'):
                    print(f"  - error: {data['error']}")

                print()

            except websocket.WebSocketTimeoutException:
                print(f"✗ 超时\n")
            except Exception as e:
                print(f"✗ 错误: {e}\n")

            time.sleep(0.3)

        # Close connection
        ws.close()
        print("✓ 已断开连接")

    except Exception as e:
        print(f"✗ 连接失败: {e}")

    print("\n" + "="*70)
    print("测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_global_commands()
