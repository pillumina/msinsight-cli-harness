#!/usr/bin/env python3
"""
Basic usage example for MindStudio Insight control layer.

This script demonstrates how to use the control layer API to control
MindStudio Insight programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli_anything.msinsight.protocol import MindStudioWebSocketClient
from cli_anything.msinsight.control import TimelineController, DataQuery


def main():
    """Demonstrate basic usage of control layer."""
    print("\n" + "="*70)
    print("MindStudio Insight 控制层使用示例")
    print("="*70 + "\n")

    # 1. 连接到后端
    print("1. 连接到 MindStudio Insight 后端...")
    print("-" * 70)

    try:
        client = MindStudioWebSocketClient(port=9000, auto_start=False)
        client.connect()
        print("✓ 连接成功")
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        print("\n请确保 MindStudio Insight 后端正在运行:")
        print("  msinsight-server --wsPort=9000")
        return

    # 创建控制器
    timeline = TimelineController(client)
    query = DataQuery(client)

    print()

    # 2. 查询最慢的算子
    print("2. 查询最慢的 10 个算子...")
    print("-" * 70)

    try:
        top_ops = query.get_top_n_operators(n=10, metric="duration")

        if top_ops.get("operators"):
            print("✓ 查询成功\n")
            for i, op in enumerate(top_ops["operators"], 1):
                print(f"{i:2d}. {op['name']:30s} {op['duration_ms']:8.2f} ms")
        else:
            print("✗ 未找到算子数据")

    except Exception as e:
        print(f"✗ 查询失败: {e}")

    print()

    # 3. 查询内存使用情况
    print("3. 查询内存使用情况...")
    print("-" * 70)

    try:
        memory = query.get_memory_summary()

        print("✓ 查询成功\n")
        print(f"  峰值内存: {memory.get('peak_memory_mb', 0):.2f} MB")
        print(f"  当前内存: {memory.get('current_memory_mb', 0):.2f} MB")
        print(f"  内存泄漏: {memory.get('leak_count', 0)}")

    except Exception as e:
        print(f"✗ 查询失败: {e}")

    print()

    # 4. Timeline 控制
    print("4. Timeline 控制示例...")
    print("-" * 70)

    try:
        # 缩放到时间范围
        print("  a) 缩放到 0-1000ms...")
        timeline.zoom_to_time(0, 1000, unit="ms")
        print("  ✓ 缩放成功")

        # 获取可见范围
        print("  b) 获取当前可见范围...")
        visible_range = timeline.get_visible_range()
        print(f"  ✓ 可见范围: {visible_range.get('startTime', 0)} - {visible_range.get('endTime', 0)} ms")

        # 获取泳道列表
        print("  c) 获取泳道列表...")
        swimlanes = timeline.get_swimlane_list()
        lane_count = len(swimlanes.get("lanes", []))
        print(f"  ✓ 泳道数量: {lane_count}")

    except Exception as e:
        print(f"  ✗ 操作失败: {e}")

    print()

    # 5. 通信分析
    print("5. 通信分析...")
    print("-" * 70)

    try:
        comm_matrix = query.get_communication_matrix()

        print("✓ 查询成功\n")
        ranks = comm_matrix.get("ranks", [])
        print(f"  Rank 数量: {len(ranks)}")
        print(f"  总通信量: {comm_matrix.get('total_traffic_mb', 0):.2f} MB")

    except Exception as e:
        print(f"✗ 查询失败: {e}")

    print()

    # 6. 性能瓶颈分析
    print("6. 性能瓶颈分析...")
    print("-" * 70)

    try:
        bottleneck = query.get_bottleneck_analysis()

        print("✓ 分析成功\n")
        print(f"  主要瓶颈: {bottleneck.get('type', 'Unknown')}")
        print(f"  影响程度: {bottleneck.get('severity', 'N/A')}")
        print(f"  建议: {bottleneck.get('recommendation', 'N/A')}")

    except Exception as e:
        print(f"✗ 分析失败: {e}")

    print()

    # 清理
    print("7. 断开连接...")
    print("-" * 70)
    client.disconnect()
    print("✓ 已断开连接")

    print("\n" + "="*70)
    print("示例完成！")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
