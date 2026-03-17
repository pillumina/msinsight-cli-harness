#!/usr/bin/env python3
"""
Demo script for MindStudio Insight natural language control.

This script demonstrates how to use the natural language interface
to control MindStudio Insight.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.msinsight.nlp_interface import NaturalLanguageInterface


def demo_basic_commands():
    """Demonstrate basic natural language commands."""
    print("\n" + "="*70)
    print("Demo: MindStudio Insight 自然语言控制")
    print("="*70 + "\n")

    with NaturalLanguageInterface() as nlp:

        # Example 1: Get top slow operators
        print("示例 1: 查找最慢的算子")
        print("命令: '最慢的5个算子'")
        print("-" * 70)

        result = nlp.process("最慢的5个算子")

        if result["success"]:
            print("✓ 执行成功")
            print(f"识别意图: {result['intent']['type']}")
            print(f"置信度: {result['intent']['confidence']:.2f}")
            print("\n结果:")
            for i, op in enumerate(result["result"]["operators"], 1):
                print(f"  {i}. {op['name']}: {op['duration_ms']:.2f} ms")
        else:
            print(f"✗ 执行失败: {result['error']}")

        print("\n" + "="*70 + "\n")

        # Example 2: Zoom to time range
        print("示例 2: 定位到时间范围")
        print("命令: '定位到 100ms 到 200ms'")
        print("-" * 70)

        result = nlp.process("定位到 100ms 到 200ms")

        if result["success"]:
            print("✓ 执行成功")
            print(f"识别意图: {result['intent']['type']}")
            print(f"参数: {result['intent']['params']}")
        else:
            print(f"✗ 执行失败: {result['error']}")

        print("\n" + "="*70 + "\n")

        # Example 3: Compare ranks
        print("示例 3: 对比不同 rank")
        print("命令: '对比 rank 0 和 rank 1'")
        print("-" * 70)

        result = nlp.process("对比 rank 0 和 rank 1")

        if result["success"]:
            print("✓ 执行成功")
            print(f"识别意图: {result['intent']['type']}")
            print(f"对比对象: {result['intent']['params']['rank_ids']}")
        else:
            print(f"✗ 执行失败: {result['error']}")

        print("\n" + "="*70 + "\n")

        # Example 4: Get memory summary
        print("示例 4: 查看内存使用情况")
        print("命令: '内存使用情况'")
        print("-" * 70)

        result = nlp.process("内存使用情况")

        if result["success"]:
            print("✓ 执行成功")
            print(f"识别意图: {result['intent']['type']}")
            print("\n内存统计:")
            # Display memory summary if available
            if "result" in result and result["result"]:
                nlp._display_result(result["result"])
        else:
            print(f"✗ 执行失败: {result['error']}")

        print("\n" + "="*70 + "\n")

        # Example 5: Pin swimlanes
        print("示例 5: 置顶泳道")
        print("命令: '置顶泳道：rank 0, rank 1'")
        print("-" * 70)

        result = nlp.process("置顶泳道：rank 0, rank 1")

        if result["success"]:
            print("✓ 执行成功")
            print(f"识别意图: {result['intent']['type']}")
            print(f"置顶泳道: {result['intent']['params']['lane_ids']}")
        else:
            print(f"✗ 执行失败: {result['error']}")

        print("\n" + "="*70 + "\n")


def demo_interactive():
    """Demonstrate interactive natural language session."""
    print("\n" + "="*70)
    print("Demo: 交互式自然语言控制")
    print("="*70 + "\n")

    nlp = NaturalLanguageInterface()

    print("进入交互模式...")
    print("支持的命令:")
    for cmd in nlp.get_supported_commands()[:5]:  # Show first 5
        print(f"  • {cmd['command']}")

    print("\n输入 'help' 查看所有命令，输入 'quit' 退出\n")

    # Start interactive session
    nlp.interactive()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="MindStudio Insight Natural Language Demo"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start interactive session"
    )

    args = parser.parse_args()

    if args.interactive:
        demo_interactive()
    else:
        demo_basic_commands()


if __name__ == "__main__":
    main()
