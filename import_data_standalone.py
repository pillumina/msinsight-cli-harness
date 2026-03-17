#!/usr/bin/env python3
"""
Standalone backend starter and data importer.
Uses the same approach as GUI.
"""

import sys
import time
import subprocess
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import DataImportController


def start_backend_manual():
    """Start backend manually using subprocess."""
    print("="*60)
    print("Starting Backend Server")
    print("="*60)

    # Use the profiler_server from MindStudio Insight
    server_binary = "/Applications/MindStudioInsight.app/Contents/MacOS/resources/profiler/server/profiler_server"

    if not Path(server_binary).exists():
        print(f"❌ Server binary not found: {server_binary}")
        return None

    # Create log directory
    log_dir = Path("/tmp/msinsight_cli_backend")
    log_dir.mkdir(exist_ok=True)

    print(f"Server binary: {server_binary}")
    print(f"Log directory: {log_dir}")

    # Start server - use same approach as GUI
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = f"/Applications/MindStudioInsight.app/Contents/MacOS/resources/profiler/server:{env.get('DYLD_LIBRARY_PATH', '')}"

    cmd = [
        server_binary,
        f"--logPath={log_dir}",
        "--wsPort=9000"
    ]

    print(f"\nStarting: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL
    )

    print(f"Backend PID: {process.pid}")
    print("Waiting for backend to start", end="", flush=True)

    # Wait for backend to be ready
    for i in range(15):
        time.sleep(1)
        print(".", end="", flush=True)

        try:
            client = MindStudioWebSocketClient(port=9000, auto_start=False)
            client.connect()

            # Try heartbeat
            response = client.send_command(
                module="global",
                command="heartCheck",
                params={},
                timeout=5.0
            )

            if response.result:
                print(" ✅")
                print("✅ Backend started successfully!")
                client.disconnect()
                return process

        except Exception as e:
            # Check if process is still alive
            if process.poll() is not None:
                print(f"\n❌ Backend process died: {e}")
                stdout, stderr = process.communicate()
                if stdout:
                    print(f"stdout: {stdout.decode()[:500]}")
                if stderr:
                    print(f"stderr: {stderr.decode()[:500]}")
                return None

    print(" ❌")
    print("❌ Backend failed to start within 15 seconds")

    # Check logs
    log_files = list(log_dir.glob("*.log"))
    if log_files:
        print(f"\nLog files: {log_files}")
        for log_file in log_files[:2]:
            print(f"\n{log_file.name}:")
            with open(log_file, 'r') as f:
                print(f.read()[:500])

    process.kill()
    return None


def import_data_with_progress(client, project_name, data_path):
    """Import data with progress updates."""
    import json

    controller = DataImportController(client)

    print(f"Project Name: {project_name}")
    print(f"Data Path: {data_path}")

    # Send import command
    params = {
        "projectName": project_name,
        "path": [data_path],
        "projectAction": 0,  # 0 = TRANSFER_PROJECT (new project)
        "isConflict": False
    }

    print("\nSending import command...")
    print(f"Parameters: {json.dumps(params, indent=2)}")

    try:
        response = client.send_command(
            module="timeline",
            command="import/action",
            params=params,
            timeout=120.0  # 2 minutes timeout
        )

        if response.result:
            print("\n✅ Import command succeeded!")
            print(f"Result: {json.dumps(response.body, indent=2)[:500]}")
            return response.body
        else:
            print(f"\n❌ Import command failed: {response.error}")
            return None

    except Exception as e:
        print(f"\n❌ Import failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main workflow."""
    print("="*60)
    print("CLI Data Import - Standalone Backend")
    print("="*60 + "\n")

    # Step 1: Start backend
    backend_process = start_backend_manual()

    if not backend_process:
        print("\n❌ Failed to start backend")
        return 1

    try:
        # Step 2: Connect to backend
        print("\n" + "="*60)
        print("Step 2: Connecting to Backend")
        print("="*60)

        client = MindStudioWebSocketClient(port=9000, auto_start=False)
        client.connect()
        print("✅ Connected to backend\n")

        # Step 3: Import data
        print("="*60)
        print("Step 3: Importing Profiling Data")
        print("="*60 + "\n")

        test_data = "/Users/huangyuxiao/projects/mvp/msinsight/test/st/level2/rank_0_ascend_pt"

        result = import_data_with_progress(
            client=client,
            project_name="CLI_Test_Project",
            data_path=test_data
        )

        if result:
            print("\n" + "="*60)
            print("✅ Data Import Complete!")
            print("="*60)

            # Step 4: Verify data
            print("\nVerifying imported data...")

            response = client.send_command(
                module="global",
                command="files/getProjectExplorer",
                params={},
                timeout=10.0
            )

            if response.result and response.body:
                projects = response.body
                print(f"✅ Found {len(projects)} project(s)")

                for project in projects:
                    print(f"\n  Project: {project.get('projectName', 'N/A')}")

            print("\n" + "="*60)
            print("Backend is ready for testing!")
            print("="*60)
            print(f"Backend PID: {backend_process.pid}")
            print(f"Port: 9000")
            print("\nYou can now run tests:")
            print("  python3 test_api_v2_final.py")
            print("\nTo stop backend:")
            print(f"  kill {backend_process.pid}")

            return 0
        else:
            print("\n❌ Data import failed")
            return 1

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        client.disconnect()
        print("\n✅ Disconnected from backend")


if __name__ == "__main__":
    sys.exit(main())
