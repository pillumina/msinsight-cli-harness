#!/usr/bin/env python3
"""
Start standalone backend and import test data.
"""

import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import DataImportController


def start_backend():
    """Start standalone backend on port 9000."""
    print("="*60)
    print("Step 1: Starting Standalone Backend")
    print("="*60)

    # Find msinsight binary
    possible_paths = [
        "/Applications/MindStudioInsight.app/Contents/MacOS/resources/profiler/server/profiler_server",
        "/usr/local/bin/profiler_server",
        "/usr/bin/profiler_server",
    ]

    server_binary = None
    for path in possible_paths:
        if Path(path).exists():
            server_binary = path
            break

    if not server_binary:
        print("❌ profiler_server binary not found")
        print("Please install MindStudio Insight first")
        return None

    print(f"✅ Found server at: {server_binary}")

    # Start server
    cmd = [server_binary, "--wsPort=9000", "--logPath=/tmp/msinsight_agent_test"]
    print(f"\nStarting: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL
    )

    # Wait for server to start
    print("Waiting for server to start", end="", flush=True)
    for i in range(10):
        time.sleep(1)
        print(".", end="", flush=True)

        # Try to connect
        try:
            client = MindStudioWebSocketClient(port=9000, auto_start=False)
            client.connect()
            print(" ✅")
            print(f"✅ Backend started (PID: {process.pid})")
            client.disconnect()
            return process
        except:
            continue

    print(" ❌")
    print("❌ Backend failed to start")
    process.kill()
    return None


def import_test_data(port=9000):
    """Import test profiling data."""
    print("\n" + "="*60)
    print("Step 2: Importing Test Data")
    print("="*60)

    client = MindStudioWebSocketClient(port=port, auto_start=False)

    try:
        client.connect()
        print("✅ Connected to backend\n")

        controller = DataImportController(client)

        test_data_path = "/Users/huangyuxiao/projects/mvp/msinsight/test/st/level2/rank_0_ascend_pt"

        print(f"Importing: {test_data_path}")
        print("This may take 1-2 minutes...\n")

        result = controller.import_profiling_data(
            project_name="TestProject_CLI",
            data_path=test_data_path,
            is_new_project=True,
            timeout=120.0
        )

        print("✅ Import succeeded!")
        print(f"Result keys: {list(result.keys())[:5]}")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        client.disconnect()


def main():
    """Main workflow."""
    print("="*60)
    print("Standalone Backend + Data Import")
    print("="*60 + "\n")

    # Step 1: Start backend
    backend_process = start_backend()
    if not backend_process:
        return 1

    # Step 2: Import data
    if not import_test_data():
        print("\n❌ Import failed, killing backend")
        backend_process.kill()
        return 1

    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    print(f"\nBackend running on port 9000 (PID: {backend_process.pid})")
    print("Test data imported")
    print("\nYou can now run:")
    print("  python3 test_api_v2_final.py")
    print("\nTo stop backend:")
    print(f"  kill {backend_process.pid}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
