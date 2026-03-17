#!/usr/bin/env python3
"""
Protocol capture tool for MindStudio Insight.

This script helps capture WebSocket messages between the GUI and backend,
enabling protocol analysis and documentation.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli_anything.msinsight.protocol import (
    MindStudioWebSocketClient,
    ProtocolAnalyzer,
    MessageInterceptor
)


def main():
    """Capture protocol messages."""
    print("\n" + "="*70)
    print("MindStudio Insight 协议捕获工具")
    print("="*70 + "\n")

    print("用途:")
    print("  1. 捕获 GUI 和后端之间的 WebSocket 消息")
    print("  2. 分析命令模式和参数")
    print("  3. 生成协议文档")
    print()

    # 设置日志文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"protocol_capture_{timestamp}.log"
    doc_file = f"protocol_doc_{timestamp}.md"

    print(f"日志文件: {log_file}")
    print(f"文档文件: {doc_file}")
    print()

    # 创建客户端和分析器
    print("初始化...")
    try:
        client = MindStudioWebSocketClient(port=9000, auto_start=False)
        analyzer = ProtocolAnalyzer(log_file=log_file)
        interceptor = MessageInterceptor(client, analyzer)

        print("✓ 初始化成功")
        print()

    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return

    print("="*70)
    print("捕获模式")
    print("="*70)
    print()
    print("现在可以:")
    print("  1. 手动操作 MindStudio Insight GUI")
    print("  2. 所有 WebSocket 消息会被自动记录")
    print("  3. 按 Ctrl+C 停止捕获并生成报告")
    print()

    try:
        # 连接到后端
        print("连接到后端...")
        client.connect()
        print("✓ 连接成功")
        print()

        # 测试几个命令
        print("发送测试命令...")
        print("-" * 70)

        # 测试 1: 获取泳道列表
        print("  1. getSwimlaneList")
        try:
            response = interceptor.send_command("timeline", "getSwimlaneList")
            print(f"     ✓ 成功 (泳道数: {len(response.data.get('lanes', []))})")
        except Exception as e:
            print(f"     ✗ 失败: {e}")

        time.sleep(0.5)

        # 测试 2: 获取可见范围
        print("  2. getVisibleRange")
        try:
            response = interceptor.send_command("timeline", "getVisibleRange")
            print(f"     ✓ 成功")
        except Exception as e:
            print(f"     ✗ 失败: {e}")

        time.sleep(0.5)

        # 测试 3: 获取算子列表
        print("  3. getOperators (limit=5)")
        try:
            response = interceptor.send_command(
                "operator",
                "getOperators",
                {"limit": 5, "sortBy": "duration"}
            )
            ops = response.data.get("operators", [])
            print(f"     ✓ 成功 (算子数: {len(ops)})")
        except Exception as e:
            print(f"     ✗ 失败: {e}")

        print()

        # 等待用户操作 GUI
        print("-" * 70)
        print("等待 GUI 操作...")
        print("(现在可以手动操作 MindStudio Insight GUI)")
        print("-" * 70)
        print()

        # 保持运行，等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n捕获中断")

    except Exception as e:
        print(f"\n✗ 错误: {e}")

    finally:
        # 生成报告
        print("\n" + "="*70)
        print("生成报告")
        print("="*70 + "\n")

        try:
            # 获取统计
            summary = analyzer.get_command_summary()

            print(f"捕获统计:")
            print(f"  - 总消息数: {summary['total_messages']}")
            print(f"  - 唯一命令数: {summary['unique_commands']}")
            print(f"  - 模块数: {len(summary['modules'])}")
            print()

            # 按模块显示命令
            print("发现的命令:")
            print("-" * 70)
            for module, commands in sorted(summary["modules"].items()):
                print(f"\n[{module}]")
                for cmd in sorted(commands):
                    key = f"{module}.{cmd}"
                    pattern = summary["commands"][key]
                    print(f"  • {cmd:30s} (调用 {pattern['call_count']} 次)")

            print()

            # 生成文档
            print(f"生成协议文档: {doc_file}")
            analyzer.export_protocol_doc(doc_file)
            print("✓ 文档生成成功")

            print()
            print(f"协议日志已保存到: {log_file}")

        except Exception as e:
            print(f"✗ 生成报告失败: {e}")

        finally:
            # 断开连接
            client.disconnect()
            print("\n✓ 已断开连接")

    print("\n" + "="*70)
    print("捕获完成！")
    print("="*70)
    print()
    print("下一步:")
    print(f"  1. 查看协议文档: cat {doc_file}")
    print(f"  2. 查看原始日志: cat {log_file}")
    print(f"  3. 根据发现的命令修正 API 实现")
    print()


if __name__ == "__main__":
    main()
