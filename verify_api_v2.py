#!/usr/bin/env python3
"""
Quick verification script to test updated Control Layer API v2.

This script verifies that the updated parameter structures work correctly
with the MindStudio Insight backend.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import (
    DataImportController,
    SummaryController,
    OperatorController,
    MemoryController,
    CommunicationController
)


def test_basic_connection():
    """Test basic WebSocket connection."""
    print("Testing basic connection...")

    client = MindStudioWebSocketClient(port=9000)

    try:
        client.connect()
        print("✅ Connected to backend on port 9000")

        # Test heartbeat
        response = client.send_command(
            module="global",
            command="heartCheck",
            params={},
            timeout=5.0
        )
        print(f"✅ Heartbeat successful: {response.result}")

        return client
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None


def test_summary_controller(client):
    """Test Summary controller with updated parameters."""
    print("\nTesting SummaryController...")

    controller = SummaryController(client)

    # Test get_top_n_data (requires cluster_path)
    try:
        top_data = controller.get_top_n_data(cluster_path="")
        print(f"✅ get_top_n_data() succeeded: returned {len(top_data) if isinstance(top_data, list) else 'data'}")
    except Exception as e:
        print(f"❌ get_top_n_data() failed: {e}")

    # Test get_statistics (requires rank_id, time_flag, cluster_path)
    try:
        stats = controller.get_statistics(
            rank_id="0",
            time_flag="",
            cluster_path=""
        )
        print(f"✅ get_statistics() succeeded: returned {type(stats).__name__}")
    except Exception as e:
        print(f"❌ get_statistics() failed: {e}")


def test_operator_controller(client):
    """Test Operator controller with updated parameters."""
    print("\nTesting OperatorController...")

    controller = OperatorController(client)

    # Test get_category_info (requires rank_id)
    try:
        categories = controller.get_category_info(
            rank_id="0",
            group="Operator"
        )
        print(f"✅ get_category_info() succeeded: returned {len(categories) if isinstance(categories, list) else 'data'}")
    except Exception as e:
        print(f"❌ get_category_info() failed: {e}")


def test_memory_controller(client):
    """Test Memory controller with updated parameters."""
    print("\nTesting MemoryController...")

    controller = MemoryController(client)

    # Test get_memory_view (requires rank_id)
    try:
        view = controller.get_memory_view(
            rank_id="0",
            view_type="type",
            device_id="",
            cluster_path=""
        )
        print(f"✅ get_memory_view() succeeded: returned {type(view).__name__}")
    except Exception as e:
        print(f"❌ get_memory_view() failed: {e}")


def test_communication_controller(client):
    """Test Communication controller with updated parameters."""
    print("\nTesting CommunicationController...")

    controller = CommunicationController(client)

    # Test get_operator_lists (requires stage, cluster_path, group_id_hash)
    try:
        op_list = controller.get_operator_lists(
            stage="",
            cluster_path="",
            group_id_hash=""
        )
        print(f"✅ get_operator_lists() succeeded: returned {len(op_list) if isinstance(op_list, list) else 'data'}")
    except Exception as e:
        print(f"❌ get_operator_lists() failed: {e}")


def main():
    """Run verification tests."""
    print("=" * 60)
    print("Control Layer API v2 - Verification Test")
    print("=" * 60)

    # Test connection
    client = test_basic_connection()
    if not client:
        print("\n❌ Cannot proceed without connection. Is backend running on port 9000?")
        return 1

    try:
        # Test each controller
        test_summary_controller(client)
        test_operator_controller(client)
        test_memory_controller(client)
        test_communication_controller(client)

        print("\n" + "=" * 60)
        print("✅ Verification complete!")
        print("=" * 60)
        return 0

    finally:
        client.disconnect()
        print("\nDisconnected from backend")


if __name__ == "__main__":
    sys.exit(main())
