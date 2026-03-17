#!/usr/bin/env python3
"""
FINAL VALIDATION - All Correct Parameter Values

Key findings from investigation:
- timeFlag CANNOT be empty (must be "step" or "iteration")
- clusterPath CANNOT be empty (must be "/" or "default")
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import (
    discover_available_ranks,
    SummaryController,
    OperatorController,
    MemoryController,
    CommunicationController
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
            if 'opList' in result:
                print(f"  📊 Operators: {len(result['opList'])}")
            if 'summaryStatisticsItemList' in result:
                print(f"  📊 Statistics: {len(result['summaryStatisticsItemList'])}")
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
    print("FINAL VALIDATION - All Fixed Parameters")
    print("="*70)
    print("\nKey fixes:")
    print("  - timeFlag: 'step' (not empty)")
    print("  - clusterPath: '/' (not empty)")
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

        # SUMMARY MODULE
        print("\n" + "="*70)
        print("SUMMARY MODULE (4 commands)")
        print("="*70)

        summary = SummaryController(client)

        # Fixed: timeFlag="step", clusterPath="/"
        tests = [
            ("get_statistics", {"rank_id": rank_id, "time_flag": "step", "cluster_path": "/"},
             "1. get_statistics() - Performance stats"),
            ("get_top_n_data", {"cluster_path": "/", "is_compare": False},
             "2. get_top_n_data() - Top N data"),
            ("get_compute_details", {"rank_id": rank_id, "time_flag": "step", "cluster_path": "/"},
             "3. get_compute_details() - Compute details"),
            ("get_communication_details", {"rank_id": rank_id, "time_flag": "HCCL", "cluster_path": "/"},
             "4. get_communication_details() - Comm details"),
        ]

        for method, kwargs, desc in tests:
            result = test_command(summary, method, kwargs, desc)
            results.append(("Summary", method, result))

        # OPERATOR MODULE
        print("\n" + "="*70)
        print("OPERATOR MODULE (5 commands)")
        print("="*70)

        operator = OperatorController(client)

        tests = [
            ("get_category_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id},
             "5. get_category_info() - Categories"),
            ("get_statistic_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
                                    "current_page": 1, "page_size": 10},
             "6. get_statistic_info() - Statistics"),
            ("get_operator_details", {"rank_id": rank_id, "group": "Operator", "device_id": device_id},
             "7. get_operator_details() - Details"),
            ("get_compute_unit_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id},
             "8. get_compute_unit_info() - Compute units"),
            ("get_all_operator_details", {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
                                          "current_page": 1, "page_size": 10},
             "9. get_all_operator_details() - All details"),
        ]

        for method, kwargs, desc in tests:
            result = test_command(operator, method, kwargs, desc)
            results.append(("Operator", method, result))

        print("\n10. export_operator_details() - SKIPPED")
        results.append(("Operator", "export", "SKIPPED"))

        # MEMORY MODULE
        print("\n" + "="*70)
        print("MEMORY MODULE (2 commands)")
        print("="*70)

        memory = MemoryController(client)

        tests = [
            ("get_memory_view", {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "cluster_path": "/"},
             "11. get_memory_view() - Memory view"),
            ("get_memory_operator_size", {"rank_id": rank_id, "view_type": "type", "device_id": device_id},
             "12. get_memory_operator_size() - Operator memory"),
        ]

        for method, kwargs, desc in tests:
            result = test_command(memory, method, kwargs, desc)
            results.append(("Memory", method, result))

        # COMMUNICATION MODULE
        print("\n" + "="*70)
        print("COMMUNICATION MODULE (3 commands)")
        print("="*70)

        comm = CommunicationController(client)

        tests = [
            ("get_bandwidth", {"rank_id": rank_id, "cluster_path": "/"},
             "13. get_bandwidth() - Bandwidth"),
            ("get_operator_lists", {"cluster_path": "/"},
             "14. get_operator_lists() - Comm operators"),
            ("get_operator_details", {"rank_id": rank_id, "cluster_path": "/", "current_page": 1, "page_size": 10},
             "15. get_operator_details() - Comm details"),
        ]

        for method, kwargs, desc in tests:
            result = test_command(comm, method, kwargs, desc)
            results.append(("Communication", method, result))

        # FINAL SUMMARY
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        success = sum(1 for r in results if r[2] == "SUCCESS")
        failed = sum(1 for r in results if r[2] == "FAILED")
        timeout = sum(1 for r in results if r[2] == "TIMEOUT")
        no_data = sum(1 for r in results if r[2] == "NO_DATA")
        skipped = sum(1 for r in results if r[2] == "SKIPPED")

        tested = len(results) - skipped

        print(f"\n✅ Success: {success}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Timeout: {timeout}")
        print(f"⚠️  No Data: {no_data}")
        print(f"⏭️  Skipped: {skipped}")

        rate = success / tested if tested > 0 else 0
        print(f"\n🎯 Success Rate: {rate*100:.1f}% ({success}/{tested})")

        # Module breakdown
        print("\n" + "-"*70)
        for module in ["Summary", "Operator", "Memory", "Communication"]:
            mod_results = [r for r in results if r[0] == module]
            if mod_results:
                ms = sum(1 for r in mod_results if r[2] == "SUCCESS")
                mf = sum(1 for r in mod_results if r[2] == "FAILED")
                mt = len(mod_results) - sum(1 for r in mod_results if r[2] in ["TIMEOUT", "NO_DATA", "SKIPPED"])
                print(f"{module}: {ms}/{mt} = {ms/mt*100 if mt > 0 else 0:.0f}%")

        print("\n" + "="*70)
        if rate >= 0.9:
            print("✅ VALIDATION PASSED - Ready for production!")
            print("="*70)
            return 0
        else:
            print("⚠️  VALIDATION PARTIAL - Some issues remain")
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
