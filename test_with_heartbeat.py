#!/usr/bin/env python3
"""
Test with heartbeat initialization.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def test_with_heartbeat():
    """Test connection with heartbeat initialization."""
    print("\n" + "="*70)
    print("测试带心跳初始化的连接")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    try:
        ws = websocket.create_connection(ws_url, timeout=10)
        print("✓ 连接成功\n")

        # Step 1: Send heartbeat first (like frontend does)
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

        print(f"发送: {json.dumps(heartbeat, indent=2)}\n")
        ws.send(json.dumps(heartbeat))

        # Wait for heartbeat response
        ws.settimeout(5.0)
        try:
            response = ws.recv()
            print(f"✓ 收到心跳响应:")
            try:
                data = json.loads(response)
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(response[:500])

            print("\n✓ 心跳成功！连接已建立！\n")

        except websocket.WebSocketTimeoutException:
            print("✗ 心跳超时\n")
            return False

        time.sleep(0.5)

        # Step 2: Now try actual command
        print(f"{'='*70}")
        print("步骤 2: 发送实际命令")
        print(f"{'='*70}")

        command = {
            "id": 2,
            "type": "request",
            "moduleName": "timeline",
            "command": "getSwimlaneList",
            "params": {}
        }

        print(f"发送: {json.dumps(command, indent=2)}\n")
        ws.send(json.dumps(command))

        # Wait for response
        try:
            response = ws.recv()
            print(f"✓ 收到命令响应:")

            try:
                data = json.loads(response)
                print(json.dumps(data, indent=2, ensure_ascii=False))

                # Check response format
                print(f"\n响应分析:")
                print(f"  - type: {data.get('type')}")
                print(f"  - requestId: {data.get('requestId')}")
                print(f"  - result: {data.get('result')}")

                if 'body' in data:
                    body = data['body']
                    print(f"  - body 类型: {type(body)}")
                    if isinstance(body, dict):
                        print(f"  - body 键: {list(body.keys())[:10]}")
                    elif isinstance(body, list):
                        print(f"  - body 长度: {len(body)}")

                if 'error' in data:
                    print(f"  - error: {data['error']}")

                print(f"\n✓✓✓ 成功！CLI 可以连接和操作 MindStudio Insight！\n")

            except Exception as e:
                print(f"解析响应失败: {e}")
                print(f"原始响应: {response[:500]}")

        except websocket.WebSocketTimeoutException:
            print("✗ 命令超时\n")

        ws.close()
        print("✓ 已断开连接")

    except Exception as e:
        print(f"✗ 连接失败: {e}")

    print("\n" + "="*70)
    print("测试完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_with_heartbeat()
