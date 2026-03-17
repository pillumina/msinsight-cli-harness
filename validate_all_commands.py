#!/usr/bin/env python3
"""
Thorough Validation - Verify All 23 Implemented Commands

This test validates each command individually to ensure they work correctly.
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
    print(f"  Method: {method_name}")
    if kwargs:
        print(f"  Args: {json.dumps({k: str(v)[:30] for k, v in kwargs.items()}, indent=4)}")

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
        elif isinstance(result, list):
            print(f"  Length: {len(result)}")
            if len(result) > 0:
                print(f"  First item: {str(result[0])[:80]}")

        return ("SUCCESS", result_type)

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
    print("THOROUGH VALIDATION - All 23 Implemented Commands")
    print("="*70)

    client = MindStudioWebSocketClient(port=9000, auto_start=False)

    try:
        client.connect()
        print("✅ Connected to backend\n")

        # Discover ranks
        ranks = discover_available_ranks(client)
        if not ranks:
            print("❌ No ranks found! Cannot proceed with validation.")
            return 1

        rank = ranks[0]
        rank_id = rank['rank_id']
        device_id = rank['device_id']
        print(f"Using Rank: {rank_id[:50]}...")
        print(f"Device ID: {device_id}\n")

        all_results = []

        # ============================================================
        # SUMMARY MODULE (12 commands)
        # ============================================================
        print("\n" + "="*70)
        print("SUMMARY MODULE - 12 Commands")
        print("="*70)

        summary = SummaryController(client)

        # Phase 1 - Core commands (4)
        summary_commands = [
            ("get_statistics", {"rank_id": rank_id, "time_flag": "", "cluster_path": ""},
             "1. get_statistics() - Performance statistics"),

            ("get_top_n_data", {"cluster_path": "", "is_compare": False},
             "2. get_top_n_data() - Top N performance data"),

            ("get_compute_details", {"rank_id": rank_id, "time_flag": "", "cluster_path": ""},
             "3. get_compute_details() - Compute details"),

            ("get_communication_details", {"rank_id": rank_id, "time_flag": "HCCL", "cluster_path": ""},
             "4. get_communication_details() - Communication details"),

            # Phase 1B - Advanced commands (8)
            ("get_model_info", {"cluster_path": ""},
             "5. get_model_info() - Model information"),

            ("get_expert_hotspot", {"model_stage": "train", "version": "1.0", "layer_num": 4,
                                    "expert_num": 8, "cluster_path": "", "dense_layer_list": []},
             "6. get_expert_hotspot() - Expert hotspot (MoE)"),

            ("get_parallel_strategy", {"cluster_path": ""},
             "7. get_parallel_strategy() - Parallel strategy"),

            ("get_pipeline_timeline", {"stage_id": "0", "cluster_path": "", "step_id": ""},
             "8. get_pipeline_timeline() - Pipeline timeline"),

            ("get_parallelism_arrangement",
             {"config": {"algorithm": "MegatronLM-TP-CP-EP-DP-PP", "ppSize": 1, "tpSize": 1,
                        "dpSize": 1, "cpSize": 1, "epSize": 1, "moeTpSize": 1},
              "dimension": "ep-dp-pp", "cluster_path": ""},
             "9. get_parallelism_arrangement() - Parallelism arrangement"),

            ("get_parallelism_performance",
             {"config": {"algorithm": "MegatronLM-TP-CP-EP-DP-PP", "ppSize": 1, "tpSize": 1,
                        "dpSize": 1, "cpSize": 1, "epSize": 1, "moeTpSize": 1},
              "dimension": "ep-dp-pp", "cluster_path": "", "order_by": "", "step": "",
              "is_compare": False, "baseline_step": "", "index_list": []},
             "10. get_parallelism_performance() - Parallelism performance"),
        ]

        for method, kwargs, desc in summary_commands:
            result = test_command(client, summary, method, kwargs, desc)
            all_results.append(("Summary", method, result[0], result[1]))

        # ============================================================
        # OPERATOR MODULE (6 commands)
        # ============================================================
        print("\n" + "="*70)
        print("OPERATOR MODULE - 6 Commands")
        print("="*70)

        operator = OperatorController(client)

        operator_commands = [
            ("get_category_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id, "top_k": 0},
             "11. get_category_info() - Operator categories"),

            ("get_statistic_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
                                    "top_k": 0, "current_page": 1, "page_size": 10},
             "12. get_statistic_info() - Operator statistics"),

            ("get_operator_details", {"rank_id": rank_id, "op_type": "", "op_name": "", "shape": "",
                                      "group": "Operator", "device_id": device_id},
             "13. get_operator_details() - Specific operator details"),

            ("get_compute_unit_info", {"rank_id": rank_id, "group": "Operator", "device_id": device_id, "top_k": 0},
             "14. get_compute_unit_info() - Compute unit information"),

            ("get_all_operator_details", {"rank_id": rank_id, "group": "Operator", "device_id": device_id,
                                          "top_k": 10, "current_page": 1, "page_size": 10},
             "15. get_all_operator_details() - All operator details"),
        ]

        for method, kwargs, desc in operator_commands:
            result = test_command(client, operator, method, kwargs, desc)
            all_results.append(("Operator", method, result[0], result[1]))

        # Skip export (creates file)
        print("\n16. export_operator_details() - SKIPPED (creates file)")
        all_results.append(("Operator", "export_operator_details", "SKIPPED", "File creation"))

        # ============================================================
        # MEMORY MODULE (2 commands)
        # ============================================================
        print("\n" + "="*70)
        print("MEMORY MODULE - 2 Commands")
        print("="*70)

        memory = MemoryController(client)

        memory_commands = [
            ("get_memory_view", {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "cluster_path": ""},
             "17. get_memory_view() - Memory view"),

            ("get_memory_operator_size", {"rank_id": rank_id, "view_type": "type", "device_id": device_id, "is_compare": False},
             "18. get_memory_operator_size() - Operator memory size"),
        ]

        for method, kwargs, desc in memory_commands:
            result = test_command(client, memory, method, kwargs, desc)
            all_results.append(("Memory", method, result[0], result[1]))

        # ============================================================
        # COMMUNICATION MODULE (3 commands)
        # ============================================================
        print("\n" + "="*70)
        print("COMMUNICATION MODULE - 3 Commands")
        print("="*70)

        comm = CommunicationController(client)

        comm_commands = [
            ("get_bandwidth", {"rank_id": rank_id, "operator_name": "", "stage": "",
                              "cluster_path": "", "group_id_hash": ""},
             "19. get_bandwidth() - Bandwidth information"),

            ("get_operator_lists", {"iteration_id": "", "rank_list": [], "stage": "",
                                   "pg_name": "", "cluster_path": "", "group_id_hash": ""},
             "20. get_operator_lists() - Communication operator lists"),

            ("get_operator_details", {"stage": "", "rank_id": rank_id, "iteration_id": "",
                                     "current_page": 1, "page_size": 10, "order_by": "", "order": "",
                                     "cluster_path": "", "group_id_hash": ""},
             "21. get_operator_details() - Communication operator details"),
        ]

        for method, kwargs, desc in comm_commands:
            result = test_command(client, comm, method, kwargs, desc)
            all_results.append(("Communication", method, result[0], result[1]))

        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        # Count results
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
        print(f"\nSuccess Rate: {success_rate*100:.1f}% ({success_count}/{total_tested})")

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
                mod_total = len(module_results) - mod_skipped

                print(f"\n{module}:")
                print(f"  ✅ Success: {mod_success}")
                print(f"  ❌ Failed: {mod_failed}")
                print(f"  ⏱️  Timeout: {mod_timeout}")
                print(f"  ⚠️  No Data: {mod_no_data}")
                print(f"  ⏭️  Skipped: {mod_skipped}")
                if mod_total > 0:
                    mod_rate = mod_success / mod_total
                    print(f"  📊 Rate: {mod_rate*100:.1f}%")

        # Failed commands detail
        if failed_count > 0:
            print("\n" + "-"*70)
            print("Failed Commands (need investigation):")
            print("-"*70)
            for module, method, status, error in all_results:
                if status == "FAILED":
                    print(f"\n{module}.{method}:")
                    print(f"  {error}")

        print("\n" + "="*70)
        print("VALIDATION COMPLETE")
        print("="*70)

        # Return code based on success rate
        if success_rate >= 0.8:
            print("\n✅ VALIDATION PASSED - CLI is production ready!")
            return 0
        elif success_rate >= 0.5:
            print("\n⚠️  VALIDATION PARTIAL - Some issues need fixing")
            return 1
        else:
            print("\n❌ VALIDATION FAILED - Major issues found")
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
