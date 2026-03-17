#!/usr/bin/env python3
"""
Diagnose Phase 1B commands - test parameter structures
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient


def test_command(client, module, command, params, description):
    """Test a single command."""
    print(f"\n{description}")
    print(f"  Module: {module}")
    print(f"  Command: {command}")
    print(f"  Params: {json.dumps(params)[:100]}")

    try:
        response = client.send_command(
            module=module,
            command=command,
            params=params,
            timeout=10.0
        )

        if response.result:
            result_type = type(response.body).__name__
            print(f"  ✅ SUCCESS - {result_type}")
            if isinstance(response.body, dict):
                keys = list(response.body.keys())[:5]
                print(f"  Keys: {keys}")
            elif isinstance(response.body, list):
                print(f"  Length: {len(response.body)}")
            return True
        else:
            error = response.error or {}
            print(f"  ❌ FAILED - {error}")
            return False

    except Exception as e:
        print(f"  ❌ EXCEPTION - {e}")
        return False


def main():
    print("="*60)
    print("Phase 1B Command Diagnostics")
    print("="*60)

    client = MindStudioWebSocketClient(port=9000, auto_start=False)

    try:
        client.connect()
        print("✅ Connected\n")

        tests = [
            # Test 1: summary/queryModelInfo
            ("summary", "summary/queryModelInfo", {"clusterPath": ""}, "1. summary/queryModelInfo"),

            # Test 2: summary/queryExpertHotspot
            ("summary", "summary/queryExpertHotspot", {
                "modelStage": "train",
                "version": "1.0",
                "layerNum": 4,
                "expertNum": 8,
                "denseLayerList": [],
                "clusterPath": ""
            }, "2. summary/queryExpertHotspot"),

            # Test 3: summary/importExpertData
            # ("summary", "summary/importExpertData", {
            #     "filePath": "/tmp/test.json",
            #     "version": "1.0",
            #     "clusterPath": ""
            # }, "3. summary/importExpertData"),

            # Test 4: summary/query/parallelStrategy
            ("summary", "summary/query/parallelStrategy", {"clusterPath": ""}, "4. summary/query/parallelStrategy"),

            # Test 5: parallelism/pipeline/fwdBwdTimeline
            ("summary", "parallelism/pipeline/fwdBwdTimeline", {
                "stageId": "0",
                "clusterPath": "",
                "stepId": ""
            }, "5. parallelism/pipeline/fwdBwdTimeline"),

            # Test 6: parallelism/arrangement/all
            ("summary", "parallelism/arrangement/all", {
                "config": {
                    "algorithm": "MegatronLM-TP-CP-EP-DP-PP",
                    "ppSize": 1,
                    "tpSize": 1,
                    "dpSize": 1,
                    "cpSize": 1,
                    "epSize": 1,
                    "moeTpSize": 1
                },
                "dimension": "ep-dp-pp",
                "clusterPath": ""
            }, "6. parallelism/arrangement/all"),

            # Test 7: parallelism/performance/data
            ("summary", "parallelism/performance/data", {
                "config": {
                    "algorithm": "MegatronLM-TP-CP-EP-DP-PP",
                    "ppSize": 1,
                    "tpSize": 1,
                    "dpSize": 1,
                    "cpSize": 1,
                    "epSize": 1,
                    "moeTpSize": 1
                },
                "dimension": "ep-dp-pp",
                "clusterPath": "",
                "orderBy": "",
                "step": "",
                "isCompare": False,
                "baselineStep": "",
                "indexList": []
            }, "7. parallelism/performance/data"),
        ]

        results = []
        for module, command, params, desc in tests:
            success = test_command(client, module, command, params, desc)
            results.append((command, success))

        # Summary
        print("\n" + "="*60)
        print("Summary")
        print("="*60)

        success_count = sum(1 for _, success in results if success)
        failed_count = sum(1 for _, success in results if not success)

        print(f"\n✅ Success: {success_count}/{len(results)}")
        print(f"❌ Failed: {failed_count}/{len(results)}")

        if failed_count > 0:
            print("\nFailed commands:")
            for command, success in results:
                if not success:
                    print(f"  - {command}")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    main()
