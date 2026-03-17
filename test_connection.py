#!/usr/bin/env python3
"""
Quick test to connect to MindStudio Insight backend.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.msinsight.protocol import MindStudioWebSocketClient

def test_connection():
    """Test connection to MindStudio Insight backend."""
    print("\n" + "="*70)
    print("测试连接到 MindStudio Insight")
    print("="*70 + "\n")

    # Try common ports
    ports_to_try = [9000, 9001, 9002, 9003, 9004, 9005]

    for port in ports_to_try:
        print(f"尝试连接端口 {port}...", end=" ")

        try:
            client = MindStudioWebSocketClient(port=port, auto_start=False)
            client.connect()

            print("✓ 连接成功！")

            # Try a simple command
            print(f"\n发送测试命令: getSwimlaneList")
            response = client.send_command("timeline", "getSwimlaneList", timeout=5.0)

            print(f"✓ 命令执行成功！")
            print(f"\n响应:")
            print(f"  - ID: {response.id}")
            print(f"  - Success: {response.success}")

            if response.data:
                lanes = response.data.get("lanes", [])
                print(f"  - 泳道数量: {len(lanes)}")

                if lanes:
                    print(f"\n  前 3 个泳道:")
                    for i, lane in enumerate(lanes[:3], 1):
                        print(f"    {i}. {lane.get('name', 'Unknown')}")

            client.disconnect()

            print(f"\n{'='*70}")
            print(f"✓ 成功连接到 MindStudio Insight (端口 {port})")
            print(f"{'='*70}\n")

            return True

        except Exception as e:
            print(f"✗ 失败: {e}")

    print(f"\n{'='*70}")
    print("✗ 无法连接到 MindStudio Insight")
    print("请确保 MindStudio Insight 正在运行，并且后端服务器已启动")
    print(f"{'='*70}\n")

    return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
