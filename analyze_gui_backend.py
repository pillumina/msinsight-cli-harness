#!/usr/bin/env python3
"""
Analyze GUI backend to understand import process.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient


def main():
    print("="*60)
    print("Analyzing GUI Backend (Port 9001)")
    print("="*60)

    # Try to connect to GUI backend
    print("\n1. Connecting to GUI backend (port 9001)...")

    try:
        client = MindStudioWebSocketClient(port=9001, auto_start=False)
        client.connect()
        print("✅ Connected!\n")

        # Get project explorer
        print("2. Getting project explorer...")
        response = client.send_command(
            module="global",
            command="files/getProjectExplorer",
            params={},
            timeout=10.0
        )

        if response.result and response.body:
            projects = response.body
            print(f"✅ Found {len(projects)} project(s)\n")

            if len(projects) > 0:
                # Show first project structure
                project = projects[0]
                print(f"First Project Structure:")
                print(f"  projectName: {project.get('projectName', 'N/A')}")
                print(f"  path: {project.get('path', 'N/A')[:80]}")
                print(f"  children: {len(project.get('children', []))} items")

                if project.get('children'):
                    child = project['children'][0]
                    print(f"\n  First child:")
                    print(f"    fileDir: {child.get('fileDir', 'N/A')}")
                    print(f"    filePath: {child.get('filePath', 'N/A')[:80]}")

                    if child.get('children'):
                        rank = child['children'][0]
                        print(f"\n    First rank:")
                        print(f"      rankId: {rank.get('rankId', 'N/A')}")
                        print(f"      filePath: {rank.get('filePath', 'N/A')[:80]}")

                # Now try import on port 9000 with same structure
                print("\n" + "="*60)
                print("3. Trying Import on Port 9000")
                print("="*60)

                client2 = MindStudioWebSocketClient(port=9000, auto_start=False)
                client2.connect()
                print("✅ Connected to port 9000\n")

                # Try import with proper structure
                test_data = "/Users/huangyuxiao/projects/mvp/msinsight/test/st/level2/rank_0_ascend_pt"

                import_params = {
                    "projectName": "CLI_Import_Test",
                    "path": [test_data],
                    "projectAction": 0,  # TRANSFER_PROJECT
                    "isConflict": False
                }

                print(f"Import params:")
                print(json.dumps(import_params, indent=2))

                response = client2.send_command(
                    module="timeline",
                    command="import/action",
                    params=import_params,
                    timeout=120.0
                )

                if response.result:
                    print("\n✅ Import succeeded!")
                    print(f"Result: {json.dumps(response.body, indent=2)[:500]}")
                else:
                    error = response.error or {}
                    print(f"\n❌ Import failed: {error.get('message', str(error))}")
                    print(f"Error code: {error.get('code', 'N/A')}")

                client2.disconnect()

        client.disconnect()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

        print("\n⚠️  GUI backend (port 9001) is not running")
        print("Please open MindStudio Insight GUI first, then run this script again")


if __name__ == "__main__":
    main()
