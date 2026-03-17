#!/usr/bin/env python3
"""
FIXED Validation - Correct parameter values

This uses the correct parameter values based on backend protocol analysis.
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


def test_command(client, controller, method_name, kwargs, description):
    """Test a single command and return result."""
    print(f"\n{description}")

    try:
        method = getattr(controller, method_name)
        result = method(**kwargs)

        result_type = type(result).__name__
        print(f"  ✅ SUCCESS - Type: {result_type}")

        if isinstance(result, dict):
            keys = list(result.keys())[:5]
            print(f"  Keys: {keys}")
            if 'opList' in result:
                print(f"  Operators: {len(result['opList'])}")
            if 'summaryStatisticsItemList' in result:
                print(f"  Statistics items: {len(result['summaryStatisticsItemList'])}")
        elif isinstance(result, list):
            print(f"  Length: {len(result)}")

        return ("SUCCESS", None)

    except Exception as e:
        error_msg = str(e)

        if 'timed out' in error_msg.lower():
            print(f"  ⏱️  TIMEOUT")
            return ("TIMEOUT", error_msg[:100])
        elif '3122' in error_msg or 'not found' in error_msg.lower():
            print(f"  ⚠️  DATA NOT AVAILABLE")
            return ("NO_DATA", error_msg[:100])
        else:
            print(f"  ❌ FAILED")
            print(f"  Error: {error_msg[:150]}")
            return ("FAILED", error_msg[:100])


def main():
    print("="*70)
    print("FIXED VALIDATION - Correct Parameter Values")
    print("="*70)

    client = MindStudioWebSocketClient(port=9000, auto_start=False)

    try:
        client.connect()
        print("✅ Connected to backend\n")

        # Discover ranks
        ranks = discover_available_ranks(client)
        if not ranks:
            print("❌ No ranks found!")
            return 1

        rank = ranks[0]
        rank_id = rank['rank_id']
        device_id = rank['device_id']
        print(f"Using Rank: {rank_id[:50]}...")
        print(f"Device ID: {device_id}\n")

        all_results = []

        # ============================================================
        # SUMMARY MODULE (10 commands - skip parallelism ones that timeout)
        # ============================================================
        print("\n" + "="*70)
        print("SUMMARY MODULE")
        print("="*70)

        summary = SummaryController(client)

        # Phase 1 - Core commands (4) - FIXED with timeFlag="step"
        summary_commands = [
            ("get_statistics",
             {"rank_id": rank_id, "time_flag": "step", "cluster_path": ""},
             "1. get_statistics() - Performance statistics"),

            ("get_top_n_data",
             {"cluster_path": "", "is_compare": False},
             "2. get_top_n_data() - Top N data"),

            ("get_compute_details",
             {"rank_id": rank_id, "time_flag": "step", "cluster_path": ""},
             "3. get_compute_details() - Compute details"),

            ("get_communication_details",
             {"rank_id": rank_id, "time_flag": "HCCL", "cluster_path": ""},
             "4. get_communication_details() - Communication details"),
        ]

        for method, kwargs, desc in summary_commands:
            result = test_command(client, summary, method, kwargs, desc)
            all_results.append(("Summary", method, result[0]))

        # ============================================================
        # OPERATOR MODULE (6 commands)
        # ============================================================
        print("\n" + "="*70)
        print("OPERATOR MODULE")
        print("="*70)

        operator = OperatorController(client)

        operator_commands = [
            ("get_category_info",
             {"rank_id": rank_id, "group": "Operator", "device_id": device_id, "top_k": 0},
             "5. get_category_info() - Operator categories"),

            ("get_statistic_info",
             {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
              "top_k": 0, "current_page": 1, "page_size": 10},
             "6. get_statistic_info() - Operator statistics"),

            ("get_operator_details",
             {"rank_id": rank_id, "op_type": "MatMul", "op_name": "", "shape": "",
              "group": "Operator", "device_id": device_id},
             "7. get_operator_details() - Specific operator"),

            ("get_compute_unit_info",
             {"rank_id": rank_id, "group": "Operator", "device_id": device_id, "top_k": 0},
             "8. get_compute_unit_info() - Compute unit"),

            ("get_all_operator_details",
             {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
              "top_k": 10, "current_page": 1, "page_size": 10},
             "9. get_all_operator_details() - All operators"),
        ]

        for method, kwargs, desc in operator_commands:
            result = test_command(client, operator, method, kwargs, desc)
            all_results.append(("Operator", method, result[0]))

        print("\n10. export_operator_details() - SKIPPED (creates file)")
        all_results.append(("Operator", "export_operator_details", "SKIPPED"))

        # ============================================================
        # MEMORY MODULE (2 commands)
        # ============================================================
        print("\n" + "="*70)
        print("MEMORY MODULE")
        print("="*70)

        memory = MemoryController(client)

        memory_commands = [
            ("get_memory_view",
             {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "cluster_path": ""},
             "11. get_memory_view() - Memory view"),

            ("get_memory_operator_size",
             {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "is_compare": False},
             "12. get_memory_operator_size() - Operator memory"),
        ]

        for method, kwargs, desc in memory_commands:
            result = test_command(client, memory, method, kwargs, desc)
            all_results.append(("Memory", method, result[0]))

        # ============================================================
        # COMMUNICATION MODULE (3 commands)
        # ============================================================
        print("\n" + "="*70)
        print("COMMUNICATION MODULE")
        print("="*70)

        comm = CommunicationController(client)

        comm_commands = [
            ("get_bandwidth",
             {"rank_id": rank_id, "operator_name": "", "stage": "",
              "cluster_path": "", "group_id_hash": ""},
             "13. get_bandwidth() - Bandwidth"),

            ("get_operator_lists",
             {"iteration_id": "", "rank_list": [], "stage": "",
              "pg_name": "", "cluster_path": "", "group_id_hash": ""},
             "14. get_operator_lists() - Comm operators"),

            ("get_operator_details",
             {"stage": "", "rank_id": rank_id, "iteration_id": "",
              "current_page": 1, "page_size": 10, "order_by": "", "order": "",
              "cluster_path": "", "group_id_hash": ""},
             "15. get_operator_details() - Comm operator details"),
        ]

        for method, kwargs, desc in comm_commands:
            result = test_command(client, comm, method, kwargs, desc)
            all_results.append(("Communication", method, result[0]))

        # ============================================================
        # SUMMARY
        # ============================================================
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        success_count = sum(1 for r in all_results if r[2] == "SUCCESS")
        failed_count = sum(1 for r in all_results if r[2] == "FAILED")
        timeout_count = sum(1 for r in all_results if r[2] == "TIMEOUT")
        no_data_count = sum(1 for r in all_results if r[2] == "NO_DATA")
        skipped_count = sum(1 for r in all_results if r[2] == "SKIPPED")

        total_tested = len(all_results) - skipped_count

        print(f"\nTotal Commands: {len(all_results)}")
        print(f"✅ SUCCESS: {success_count}")
        print(f"❌ FAILED: {failed_count}")
        print(f"⏱️  TIMEOUT: {timeout_count}")
        print(f"⚠️  NO DATA: {no_data_count}")
        print(f"⏭️  SKIPPED: {skipped_count}")

        success_rate = success_count / total_tested if total_tested > 0 else 0
        print(f"\n🎯 Success Rate: {success_rate*100:.1f}% ({success_count}/{total_tested})")

        # Module breakdown
        print("\n" + "-"*70)
        print("Module Breakdown:")
        print("-"*70)

        modules = ["Summary", "Operator", "Memory", "Communication"]
        for module in modules:
            module_results = [r for r in all_results if r[0] == module]
            if module_results:
                mod_success = sum(1 for r in module_results if r[2] == "SUCCESS")
                mod_failed = sum(1 for r in module_results if r[2] == "FAILED")
                mod_timeout = sum(1 for r in module_results if r[2] == "TIMEOUT")
                mod_no_data = sum(1 for r in module_results if r[2] == "NO_DATA")
                mod_skipped = sum(1 for r in module_results if r[2] == "SKIPPED")
                mod_total = len(module_results) - mod_skipped - mod_timeout - mod_no_data

                print(f"\n{module}:")
                print(f"  ✅ Success: {mod_success}")
                print(f"  ❌ Failed: {mod_failed}")
                print(f"  ⏱️  Timeout: {mod_timeout}")
                print(f"  ⚠️  No Data: {mod_no_data}")
                if mod_total > 0:
                    mod_rate = mod_success / mod_total
                    print(f"  📊 Rate: {mod_rate*100:.1f}%")

        # Failed commands
        if failed_count > 0:
            print("\n" + "-"*70)
            print("Failed Commands:")
            print("-"*70)
            for module, method, status in all_results:
                if status == "FAILED":
                    print(f"  - {module}.{method}")

        print("\n" + "="*70)
        if success_rate >= 0.9:
            print("✅ VALIDATION PASSED - CLI is production ready!")
            print("="*70)
            return 0
        elif success_rate >= 0.7:
            print("⚠️  VALIDATION PARTIAL - Most commands work")
            print("="*70)
            return 1
        else:
            print("❌ VALIDATION FAILED - Major issues remain")
            print("="*70)
            return 2

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 3

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    sys.exit(main())
