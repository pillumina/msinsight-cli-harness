#!/usr/bin/env python3
"""
Quick check of backend state and available data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient


def main():
    """Check backend state."""
    client = MindStudioWebSocketClient(port=9000)

    try:
        client.connect()
        print("✅ Connected to backend\n")

        # Try getProjectExplorer
        print("="*60)
        print("1. Checking available projects")
        print("="*60)

        response = client.send_command(
            module="global",
            command="files/getProjectExplorer",
            params={},
            timeout=10.0
        )

        if response.result:
            import json
            print("✅ getProjectExplorer succeeded!")
            print(json.dumps(response.body, indent=2)[:1000])

            # Check if we have projects
            if response.body and isinstance(response.body, list):
                print(f"\nFound {len(response.body)} project(s)")

                if len(response.body) > 0:
                    first_project = response.body[0]
                    print(f"\nFirst project info:")
                    print(f"  Name: {first_project.get('projectName', 'N/A')}")
                    print(f"  Path: {first_project.get('path', 'N/A')}")

        else:
            print(f"❌ getProjectExplorer failed: {response.error}")

        # Try heartCheck
        print("\n" + "="*60)
        print("2. Heartbeat check")
        print("="*60)

        response = client.send_command(
            module="global",
            command="global/heartCheck",
            params={},
            timeout=5.0
        )

        print(f"Heartbeat: {'✅ OK' if response.result else '❌ Failed'}")

        # Try moduleConfig/get
        print("\n" + "="*60)
        print("3. Module configuration")
        print("="*60)

        response = client.send_command(
            module="global",
            command="global/moduleConfig/get",
            params={},
            timeout=10.0
        )

        if response.result:
            import json
            print("✅ moduleConfig/get succeeded!")
            config = response.body
            if isinstance(config, dict):
                print(f"Config keys: {list(config.keys())[:10]}")
        else:
            print(f"❌ moduleConfig/get failed: {response.error}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        client.disconnect()
        print("\n✅ Disconnected")


if __name__ == "__main__":
    main()
