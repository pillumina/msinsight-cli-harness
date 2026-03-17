#!/usr/bin/env python3
"""
Standalone backend starter and data importer.
"""

import sys
import time
import subprocess
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import DataImportController


def start_backend():
    """Start backend manually using subprocess."""
    print("="*60)
    print("Step 1: Starting Backend Server")
    print("="*60)

    server_binary = "/Applications/MindStudioInsight.app/Contents/MacOS/resources/profiler/server/profiler_server"

    if not Path(server_binary).exists():
        print(f"❌ Server binary not found: {server_binary}")
        return None

    log_dir = Path("/tmp/msinsight_cli_backend")
    log_dir.mkdir(exist_ok=True)

    print(f"Server binary: {server_binary}")
    print(f"Log directory: {log_dir}")

    # Set library path
    env = os.environ.copy()
    lib_path = "/Applications/MindStudioInsight.app/Contents/MacOS/resources/profiler/server"
    env["DYLD_LIBRARY_PATH"] = f"{lib_path}:{env.get('DYLD_LIBRARY_PATH', '')}"

    cmd = [server_binary, f"--logPath={log_dir}", "--wsPort=9000"]

    print(f"\nStarting: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL
    )

    print(f"Backend PID: {process.pid}")
    print("\nWaiting for backend to start", end="", flush=True)

    # Wait for backend to be ready
    for i in range(20):
        time.sleep(0.5)
        print(".", end="", flush=True)

        # Check if process died
        if process.poll() is not None:
            print(" ❌")
            print(f"❌ Backend process died with code {process.returncode}")
            return None

        # Try to connect
        try:
            client = MindStudioWebSocketClient(port=9000, auto_start=False)
            client.connect()

            # Try heartbeat
            response = client.send_command(
                module="global",
                command="heartCheck",
                params={},
                timeout=2.0
            )

            if response.result:
                print(" ✅")
                print("✅ Backend started successfully!")
                client.disconnect()
                return process

        except Exception:
            pass
        finally:
            try:
                client.disconnect()
            except:
                pass

    print(" ❌")
    print("❌ Backend failed to start within 10 seconds")
    process.kill()
    return None


def import_data(client, project_name, data_path):
    """Import profiling data."""
    print("\n" + "="*60)
    print("Step 2: Importing Profiling Data")
    print("="*60)

    controller = DataImportController(client)

    print(f"Project Name: {project_name}")
    print(f"Data Path: {data_path}")
    print("\nImporting (this may take 1-2 minutes)...", end="", flush=True)

    try:
        result = controller.import_profiling_data(
            project_name=project_name,
            data_path=data_path,
            is_new_project=True,
            timeout=120.0
        )

        print(" ✅")
        print("✅ Import succeeded!")
        return result

    except Exception as e:
        print(" ❌")
        print(f"❌ Import failed: {e}")
        return None


def verify_data(client):
    """Verify imported data."""
    print("\n" + "="*60)
    print("Step 3: Verifying Imported Data")
    print("="*60)

    response = client.send_command(
        module="global",
        command="files/getProjectExplorer",
        params={},
        timeout=10.0
    )

    if response.result and response.body:
        projects = response.body
        print(f"✅ Found {len(projects)} project(s)")

        for i, project in enumerate(projects[:2]):
            print(f"\nProject {i+1}:")
            print(f"  Name: {project.get('projectName', 'N/A')}")

            # Check for rank data
            if 'children' in project and len(project['children']) > 0:
                child = project['children'][0]
                if 'children' in child and len(child['children']) > 0:
                    rank = child['children'][0]
                    rank_id = rank.get('rankId', 'N/A')
                    print(f"  Rank ID: {rank_id}")
                    return rank_id

    print("⚠️  No projects found")
    return None


def main():
    """Main workflow."""
    print("="*60)
    print("Standalone Backend + Data Import")
    print("="*60 + "\n")

    backend_process = None
    client = None

    try:
        # Step 1: Start backend
        backend_process = start_backend()
        if not backend_process:
            return 1

        # Step 2: Connect to backend
        print("\nConnecting to backend...")
        client = MindStudioWebSocketClient(port=9000, auto_start=False)
        client.connect()
        print("✅ Connected\n")

        # Step 3: Import data
        test_data = "/Users/huangyuxiao/projects/mvp/msinsight/test/st/level2/rank_0_ascend_pt"

        result = import_data(
            client=client,
            project_name="CLI_Import_Test",
            data_path=test_data
        )

        if not result:
            return 1

        # Step 4: Verify data
        rank_id = verify_data(client)

        if rank_id:
            print("\n" + "="*60)
            print("✅ Setup Complete!")
            print("="*60)
            print(f"\nBackend running on port 9000 (PID: {backend_process.pid})")
            print(f"Test data imported: CLI_Import_Test")
            print(f"Available rank_id: {rank_id}")
            print("\nYou can now run:")
            print("  python3 test_api_v2_live.py")
            print("\nTo stop backend:")
            print(f"  kill {backend_process.pid}")

            return 0
        else:
            print("\n⚠️  Import succeeded but no rank data found")
            return 1

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        if client:
            try:
                client.disconnect()
            except:
                pass


if __name__ == "__main__":
    sys.exit(main())
