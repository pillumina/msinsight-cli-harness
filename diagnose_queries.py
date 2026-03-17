#!/usr/bin/env python3
"""
Diagnose API query issues after data import.
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient


def test_all_possible_queries(client):
    """Test various query commands to find what works."""
    print("="*60)
    print("Diagnosing Query Issues")
    print("="*60)

    tests = [
        # Global commands
        ("global", "heartCheck", {}),
        ("global", "moduleConfig/get", {}),

        # File/project commands
        ("global", "files/getProjectExplorer", {}),

        # Timeline commands
        ("timeline", "parse/cards", {}),

        # Summary commands with various params
        ("summary", "summary/queryTopData", {"clusterPath": ""}),
        ("summary", "summary/statistic", {"rankId": "0", "timeFlag": "", "clusterPath": ""}),

        # Operator commands
        ("operator", "operator/category", {"rankId": "0", "group": "Operator", "deviceId": ""}),
        ("operator", "operator/statistic", {"rankId": "0", "group": "Operator", "deviceId": ""}),

        # Memory commands
        ("memory", "Memory/view/type", {"rankId": "0", "deviceId": "", "clusterPath": ""}),

        # Communication commands
        ("communication", "communication/bandwidth", {
            "rankId": "0",
            "operatorName": "",
            "stage": "",
            "pgName": "",
            "clusterPath": "",
            "groupIdHash": ""
        }),
    ]

    results = []

    for module, command, params in tests:
        print(f"\n{module}/{command}")
        print(f"  Params: {json.dumps(params)[:80]}")

        try:
            response = client.send_command(
                module=module,
                command=command,
                params=params,
                timeout=10.0
            )

            if response.result:
                result_type = type(response.body).__name__
                if isinstance(response.body, dict):
                    keys = list(response.body.keys())[:5]
                    print(f"  ✅ SUCCESS - {result_type}, keys: {keys}")
                    results.append((module, command, "SUCCESS", result_type))
                elif isinstance(response.body, list):
                    print(f"  ✅ SUCCESS - {result_type}, length: {len(response.body)}")
                    results.append((module, command, "SUCCESS", f"list({len(response.body)})"))
                else:
                    print(f"  ✅ SUCCESS - {result_type}")
                    results.append((module, command, "SUCCESS", result_type))
            else:
                error = response.error or {}
                error_msg = error.get('message', 'Unknown error')
                error_code = error.get('code', 'N/A')
                print(f"  ❌ FAILED - Code {error_code}: {error_msg}")
                results.append((module, command, "FAILED", f"{error_code}:{error_msg[:30]}"))

        except Exception as e:
            print(f"  ❌ EXCEPTION - {type(e).__name__}: {str(e)[:50]}")
            results.append((module, command, "EXCEPTION", str(e)[:30]))

    return results


def test_unit_threads(client):
    """Try unit/threads to get rank information."""
    print("\n" + "="*60)
    print("Testing unit/threads for rank discovery")
    print("="*60)

    try:
        response = client.send_command(
            module="timeline",
            command="unit/threads",
            params={},
            timeout=30.0
        )

        if response.result:
            print("✅ unit/threads succeeded!")
            body = response.body

            if isinstance(body, dict) and 'unitList' in body:
                units = body['unitList']
                print(f"Found {len(units)} units")

                if len(units) > 0:
                    unit = units[0]
                    print(f"\nFirst unit:")
                    print(f"  rankId: {unit.get('rankId', 'N/A')}")
                    print(f"  deviceId: {unit.get('deviceId', 'N/A')}")
                    print(f"  host: {unit.get('host', 'N/A')}")

                    return unit.get('rankId', '0')
        else:
            error = response.error or {}
            print(f"❌ unit/threads failed: {error.get('message', 'Unknown')}")

    except Exception as e:
        print(f"❌ Exception: {e}")

    return None


def test_with_different_rank_ids(client):
    """Try different rank ID formats."""
    print("\n" + "="*60)
    print("Testing with different rank ID formats")
    print("="*60)

    rank_formats = [
        "0",
        "1",
        "localhost.localdomain2152938157304401006_0 0",
        "",
    ]

    for rank_id in rank_formats:
        print(f"\nTrying rankId='{rank_id}'")

        try:
            response = client.send_command(
                module="operator",
                command="operator/category",
                params={
                    "rankId": rank_id,
                    "group": "Operator",
                    "deviceId": ""
                },
                timeout=10.0
            )

            if response.result:
                print(f"  ✅ SUCCESS!")
                if isinstance(response.body, list):
                    print(f"  Found {len(response.body)} categories")
                return rank_id
            else:
                error = response.error or {}
                print(f"  ❌ Failed: {error.get('message', 'Unknown')}")

        except Exception as e:
            print(f"  ❌ Exception: {e}")

    return None


def main():
    print("="*60)
    print("API Query Diagnosis")
    print("="*60 + "\n")

    client = MindStudioWebSocketClient(port=9000, auto_start=False)

    try:
        client.connect()
        print("✅ Connected to backend on port 9000\n")

        # Test 1: Try all possible queries
        results = test_all_possible_queries(client)

        # Summary
        print("\n" + "="*60)
        print("Test Summary")
        print("="*60)

        success_count = sum(1 for r in results if r[2] == "SUCCESS")
        failed_count = sum(1 for r in results if r[2] == "FAILED")
        exception_count = sum(1 for r in results if r[2] == "EXCEPTION")

        print(f"\n✅ Success: {success_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"❌ Exceptions: {exception_count}")

        if success_count > 0:
            print("\nWorking commands:")
            for module, command, status, info in results:
                if status == "SUCCESS":
                    print(f"  - {module}/{command}: {info}")

        # Test 2: Try unit/threads
        rank_id = test_unit_threads(client)

        # Test 3: Try different rank formats
        if not rank_id:
            rank_id = test_with_different_rank_ids(client)

        print("\n" + "="*60)
        print("Diagnosis Complete")
        print("="*60)

        if rank_id:
            print(f"\n✅ Found working rank_id: {rank_id}")
        else:
            print("\n⚠️  Could not find working rank_id")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    main()
