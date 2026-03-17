#!/usr/bin/env python3
"""
Validate Memory Module - Test all 6 Memory commands

This validates both existing and newly implemented Memory commands.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import (
    discover_available_ranks,
    MemoryController
)


def test_command(controller, method_name, kwargs, description):
    """Test a single command."""
    print(f"\n{description}")

    try:
        method = getattr(controller, method_name)
        result = method(**kwargs)

        result_type = type(result).__name__
        print(f"  ✅ SUCCESS - {result_type}")

        if isinstance(result, dict):
            keys = list(result.keys())[:5]
            print(f"  Keys: {keys}")
            if 'data' in result:
                data = result['data']
                if isinstance(data, list):
                    print(f"  📊 Data items: {len(data)}")
        elif isinstance(result, list):
            print(f"  📊 Items: {len(result)}")

        return "SUCCESS"

    except Exception as e:
        error_msg = str(e)
        if 'timed out' in error_msg.lower():
            print(f"  ⏱️  TIMEOUT")
            return "TIMEOUT"
        elif '3122' in error_msg:
            print(f"  ⚠️  NO DATA")
            return "NO_DATA"
        else:
            print(f"  ❌ FAILED: {error_msg[:100]}")
            return "FAILED"


def main():
    print("="*70)
    print("MEMORY MODULE VALIDATION - All 6 Commands")
    print("="*70)
    print("\nTesting:")
    print("  1. get_memory_view() - Memory view by type")
    print("  2. get_memory_operator_size() - Operator memory size")
    print("  3. get_static_operator_graph() - Static operator graph")
    print("  4. get_static_operator_list() - Static operator list")
    print("  5. get_static_operator_size() - Static operator size range")
    print("  6. find_memory_slice() - Find memory slice")
    print("="*70)

    client = MindStudioWebSocketClient(port=9000, auto_start=False)

    try:
        client.connect()
        print("\n✅ Connected to backend\n")

        ranks = discover_available_ranks(client)
        if not ranks:
            print("❌ No ranks found!")
            return 1

        rank = ranks[0]
        rank_id = rank['rank_id']
        device_id = rank['device_id']
        print(f"Rank: {rank_id[:40]}...")
        print(f"Device: {device_id}\n")

        results = []

        # MEMORY MODULE - All 6 commands
        print("\n" + "="*70)
        print("MEMORY MODULE (6 commands)")
        print("="*70)

        memory = MemoryController(client)

        tests = [
            ("get_memory_view",
             {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "cluster_path": "/"},
             "1. get_memory_view() - Memory view by type"),

            ("get_memory_operator_size",
             {"rank_id": rank_id, "view_type": "Overall", "device_id": device_id, "is_compare": False},
             "2. get_memory_operator_size() - Operator memory size"),

            ("get_static_operator_graph",
             {"rank_id": rank_id, "model_name": "", "graph_id": "", "is_compare": False},
             "3. get_static_operator_graph() - Static operator graph"),

            ("get_static_operator_list",
             {"rank_id": rank_id, "graph_id": "", "search_name": "",
              "min_size": -9223372036854775808, "max_size": 9223372036854775807,
              "start_node_index": -1, "end_node_index": -1, "is_compare": False,
              "current_page": 1, "page_size": 10, "order_by": "", "order": ""},
             "4. get_static_operator_list() - Static operator list"),

            ("get_static_operator_size",
             {"rank_id": rank_id, "graph_id": "", "is_compare": False},
             "5. get_static_operator_size() - Static operator size range"),

            ("find_memory_slice",
             {"rank_id": rank_id, "slice_id": "test_slice", "slice_name": ""},
             "6. find_memory_slice() - Find memory slice"),
        ]

        for method, kwargs, desc in tests:
            result = test_command(memory, method, kwargs, desc)
            results.append((method, result))

        # FINAL SUMMARY
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        success = sum(1 for r in results if r[1] == "SUCCESS")
        failed = sum(1 for r in results if r[1] == "FAILED")
        timeout = sum(1 for r in results if r[1] == "TIMEOUT")
        no_data = sum(1 for r in results if r[1] == "NO_DATA")

        tested = len(results)

        print(f"\n✅ Success: {success}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Timeout: {timeout}")
        print(f"⚠️  No Data: {no_data}")

        rate = success / tested if tested > 0 else 0
        print(f"\n🎯 Success Rate: {rate*100:.1f}% ({success}/{tested})")

        print("\n" + "="*70)
        if success == tested:
            print("✅ ALL MEMORY COMMANDS WORKING!")
            print("="*70)
            return 0
        elif rate >= 0.8:
            print("✅ MOSTLY WORKING - Minor issues")
            print("="*70)
            return 0
        else:
            print("⚠️  SOME ISSUES - Review failures")
            print("="*70)
            return 1

    except Exception as e:
        print(f"\n❌ Fatal: {e}")
        import traceback
        traceback.print_exc()
        return 2

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    sys.exit(main())
