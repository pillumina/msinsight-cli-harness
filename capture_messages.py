#!/usr/bin/env python3
"""
Capture all WebSocket messages including special formats.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import websocket


def capture_all_messages():
    """Capture all messages from backend."""
    print("\n" + "="*70)
    print("捕获所有 WebSocket 消息")
    print("="*70 + "\n")

    port = 9000
    ws_url = f"ws://127.0.0.1:{port}"

    print(f"连接到: {ws_url}\n")

    all_messages = []

    def on_message(ws, message):
        """Handle incoming message."""
        all_messages.append(message)
        print(f"\n收到消息 #{len(all_messages)}:")
        print(f"长度: {len(message)} 字节")
        print(f"前 100 字符: {message[:100]}")

        if message.startswith('Content-Length'):
            print("  → Content-Length 消息")
        else:
            try:
                data = json.loads(message)
                print("  → JSON 消息:")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
            except:
                print(f"  → 纯文本消息: {message[:200]}")

    def on_error(ws, error):
        print(f"\n✗ 错误: {error}")

    def on_close(ws, close_status_code, close_msg):
        print(f"\n连接关闭:")
        print(f"  状态码: {close_status_code}")
        print(f"  消息: {close_msg}")

    def on_open(ws):
        print("✓ 连接已建立\n")
        print("发送测试命令...")

        # Send a command
        cmd = {
            "id": 1,
            "type": "request",
            "moduleName": "timeline",
            "command": "getSwimlaneList",
            "params": {}
        }

        print(f"发送: {json.dumps(cmd, indent=2)}\n")
        ws.send(json.dumps(cmd))

        # Wait a bit for responses
        import time
        time.sleep(3)

        print(f"\n总共收到 {len(all_messages)} 条消息")
        ws.close()

    # Create WebSocket connection with callbacks
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )

    # Run
    ws.run_forever()

    print("\n" + "="*70)
    print("捕获完成")
    print("="*70 + "\n")


if __name__ == "__main__":
    capture_all_messages()
