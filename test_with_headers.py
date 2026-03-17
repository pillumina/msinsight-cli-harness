#!/usr/bin/env python3
"""
Test with browser-like headers.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def test_with_headers():
    """Test connection with browser-like headers."""
    print("\n" + "="*70)
    print("测试带浏览器 Header 的连接")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    # Try different header combinations
    header_sets = [
        # Set 1: Origin header
        {
            "Origin": f"http://127.0.0.1:{port}",
        },
        # Set 2: More browser-like headers
        {
            "Origin": f"http://127.0.0.1:{port}",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
        # Set 3: With host
        {
            "Origin": f"http://127.0.0.1:{port}",
            "Host": f"127.0.0.1:{port}",
        },
    ]

    for i, headers in enumerate(header_sets, 1):
        print(f"{'='*70}")
        print(f"测试 Header 组合 {i}")
        print(f"{'='*70}")
        print(f"Headers: {json.dumps(headers, indent=2)}\n")

        try:
            ws = websocket.create_connection(
                ws_url,
                timeout=10,
                header=headers
            )
            print("✓ 连接成功")

            # Send heartbeat
            heartbeat = {
                "id": 1,
                "type": "request",
                "moduleName": "global",
                "command": "heartCheck",
                "params": {}
            }

            print(f"发送心跳: {json.dumps(heartbeat)}")
            ws.send(json.dumps(heartbeat))

            # Wait for response
            ws.settimeout(3.0)
            try:
                response = ws.recv()
                print(f"✓ 收到响应:")
                data = json.loads(response)
                print(json.dumps(data, indent=2, ensure_ascii=False))

                print(f"\n✓✓✓ 成功！这组 Header 可用！\n")

                # Try a real command
                command = {
                    "id": 2,
                    "type": "request",
                    "moduleName": "timeline",
                    "command": "getSwimlaneList",
                    "params": {}
                }

                print(f"发送测试命令...")
                ws.send(json.dumps(command))
                response = ws.recv()
                data = json.loads(response)
                print(f"✓ 命令响应:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])

                ws.close()
                return True

            except websocket.WebSocketTimeoutException:
                print("✗ 超时")

        except Exception as e:
            print(f"✗ 失败: {e}")

        print()

        if 'ws' in locals():
            try:
                ws.close()
            except:
                pass

    print("\n" + "="*70)
    print("所有 Header 组合都失败了")
    print("="*70 + "\n")

    return False


if __name__ == "__main__":
    success = test_with_headers()
    sys.exit(0 if success else 1)
