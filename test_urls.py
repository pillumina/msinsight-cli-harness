#!/usr/bin/env python3
"""
Try different connection methods and parameters.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def test_different_connections():
    """Test different connection methods."""
    print("\n" + "="*70)
    print("测试不同的连接方式")
    print("="*70 + "\n")

    port = 9000

    # Different URL patterns to try
    test_urls = [
        f"ws://127.0.0.1:{port}",
        f"ws://127.0.0.1:{port}/",
        f"ws://127.0.0.1:{port}/resources/profiler/frontend",
        f"ws://localhost:{port}",
        f"ws://127.0.0.1:{port}?port={port}",
    ]

    for ws_url in test_urls:
        print(f"{'='*70}")
        print(f"测试 URL: {ws_url}")
        print(f"{'='*70}")

        try:
            ws = websocket.create_connection(ws_url, timeout=5)
            print("✓ 连接成功")

            # Try a simple command
            cmd = {
                "id": 1,
                "type": "request",
                "moduleName": "timeline",
                "command": "getSwimlaneList",
                "params": {}
            }

            ws.send(json.dumps(cmd))
            print("✓ 命令已发送")

            # Wait for response
            ws.settimeout(3.0)
            try:
                response = ws.recv()
                print(f"✓ 收到响应:")
                print(response[:500])

                # Parse and display
                try:
                    data = json.loads(response)
                    print("\n解析后的响应:")
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                except:
                    pass

                print(f"\n✓✓✓ 成功！这个 URL 可用！\n")
                ws.close()
                return True

            except websocket.WebSocketTimeoutException:
                print("✗ 超时")

        except Exception as e:
            print(f"✗ 失败: {e}")

        print()
        ws.close() if 'ws' in locals() else None

    print("\n" + "="*70)
    print("所有连接方式都失败了")
    print("="*70 + "\n")

    return False


if __name__ == "__main__":
    success = test_different_connections()
    sys.exit(0 if success else 1)
