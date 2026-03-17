#!/usr/bin/env python3
"""
Discover available metadata (ranks, time flags, etc.) from backend.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient


def main():
    """Discover available metadata."""
    client = MindStudioWebSocketClient(port=9000)

    try:
        client.connect()
        print("✅ Connected to backend\n")

        # Test 1: Get unit/threads
        print("="*60)
        print("1. Get unit/threads (rank information)")
        print("="*60)

        response = client.send_command(
            module="timeline",
            command="unit/threads",
            params={},
            timeout=30.0
        )

        if response.result:
            print("✅ unit/threads succeeded!")
            print(json.dumps(response.body, indent=2)[:1500])

            # Extract rank info
            if response.body and isinstance(response.body, dict):
                if "unitList" in response.body:
                    units = response.body["unitList"]
                    print(f"\n✅ Found {len(units)} units")

                    if len(units) > 0:
                        first_unit = units[0]
                        print(f"\nFirst unit info:")
                        print(f"  rank_id: {first_unit.get('rankId', 'N/A')}")
                        print(f"  device_id: {first_unit.get('deviceId', 'N/A')}")

        else:
            print(f"❌ unit/threads failed: {response.error}")

        # Test 2: Try summary/statistic with discovered rank
        print("\n" + "="*60)
        print("2. Try summary/statistic with discovered data")
        print("="*60)

        if response.result and response.body and "unitList" in response.body:
            units = response.body["unitList"]
            if len(units) > 0:
                rank_id = units[0].get("rankId", "")
                print(f"\nUsing rank_id: {rank_id}")

                # Try with different time_flag values
                time_flags = ["", "0", "HCCL", "COMPUTE"]

                for time_flag in time_flags:
                    print(f"\nTrying time_flag='{time_flag}'...")

                    stat_response = client.send_command(
                        module="summary",
                        command="summary/statistic",
                        params={
                            "rankId": rank_id,
                            "timeFlag": time_flag,
                            "clusterPath": ""
                        },
                        timeout=10.0
                    )

                    if stat_response.result:
                        print(f"   ✅ Success with time_flag='{time_flag}'!")
                        print(f"   Result keys: {list(stat_response.body.keys())[:5]}")
                        break
                    else:
                        print(f"   ❌ Failed: {stat_response.error.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    main()
