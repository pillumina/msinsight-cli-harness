#!/usr/bin/env python3
"""
MindStudio Insight CLI v2 - With Real Backend Integration

This version actually calls the implemented api_v2.py methods.
"""

import sys
import json
import click
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli_anything.msinsight.protocol.websocket_client import MindStudioWebSocketClient
from cli_anything.msinsight.control.api_v2 import (
    discover_available_ranks,
    SummaryController,
    OperatorController,
    MemoryController,
    CommunicationController,
)


class Session:
    """Enhanced session with connection management."""

    def __init__(self):
        self.connection: Optional[MindStudioWebSocketClient] = None
        self.project_name: Optional[str] = None
        self.rank_id: Optional[str] = None
        self.device_id: Optional[str] = None

    def connect(self, port: int = 9000) -> bool:
        """Connect to backend."""
        if self.connection and self.connection.is_connected():
            return True

        try:
            self.connection = MindStudioWebSocketClient(port=port, auto_start=False)
            self.connection.connect()

            # Discover ranks
            ranks = discover_available_ranks(self.connection)
            if ranks:
                self.rank_id = ranks[0]['rank_id']
                self.device_id = ranks[0]['device_id']

            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from backend."""
        if self.connection:
            self.connection.disconnect()
            self.connection = None

    def ensure_connected(self):
        """Ensure backend is connected."""
        if not self.connection or not self.connection.is_connected():
            raise click.ClickException("Not connected to backend. Use 'connect' command first.")


# Global session
session = Session()


def print_json(data):
    """Print JSON output."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_table(data, headers=None):
    """Print table output."""
    if isinstance(data, dict):
        # Print key-value pairs
        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0:
                print(f"\n{key}:")
                for item in value[:10]:  # Show first 10
                    print(f"  - {item}")
            elif isinstance(value, dict):
                print(f"{key}: {json.dumps(value, ensure_ascii=False)}")
            else:
                print(f"{key}: {value}")
    elif isinstance(data, list):
        for item in data[:20]:  # Show first 20
            print(f"  - {item}")


# CLI Main
@click.group(invoke_without_command=True)
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--port", default=9000, help="Backend port (default: 9000)")
@click.pass_context
def cli(ctx, output_json, port):
    """MindStudio Insight CLI - Performance Analysis Tool"""
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json
    ctx.obj["port"] = port

    if ctx.invoked_subcommand is None:
        # Enter REPL mode
        print("MindStudio Insight CLI v2")
        print("Type 'help' for commands, 'exit' to quit.\n")
        repl_loop(ctx)


# Connection commands
@cli.command()
@click.option("--port", default=9000, help="Backend port")
@click.pass_context
def connect(ctx, port):
    """Connect to MindStudio Insight backend."""
    try:
        if session.connect(port):
            if ctx.obj["json"]:
                print_json({
                    "status": "connected",
                    "port": port,
                    "rank_id": session.rank_id,
                    "device_id": session.device_id
                })
            else:
                print(f"✓ Connected to backend (port {port})")
                if session.rank_id:
                    print(f"  Rank: {session.rank_id[:40]}...")
                    print(f"  Device: {session.device_id}")
        else:
            raise click.ClickException("Failed to connect")
    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@cli.command()
@click.pass_context
def disconnect(ctx):
    """Disconnect from backend."""
    session.disconnect()
    if ctx.obj["json"]:
        print_json({"status": "disconnected"})
    else:
        print("✓ Disconnected")


# Summary commands
@cli.group()
@click.pass_context
def summary(ctx):
    """Summary analysis commands."""
    pass


@summary.command("statistics")
@click.option("--rank-id", help="Rank ID (default: auto-detect)")
@click.option("--time-flag", default="step", help="Time flag (step/iteration)")
@click.option("--cluster-path", default="/", help="Cluster path")
@click.pass_context
def summary_statistics(ctx, rank_id, time_flag, cluster_path):
    """Get performance statistics."""
    session.ensure_connected()

    try:
        ctrl = SummaryController(session.connection)
        rid = rank_id or session.rank_id

        if not rid:
            raise click.ClickException("No rank ID available")

        result = ctrl.get_statistics(
            rank_id=rid,
            time_flag=time_flag,
            cluster_path=cluster_path
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@summary.command("top-n")
@click.option("--cluster-path", default="/", help="Cluster path")
@click.option("--compare", is_flag=True, help="Comparison mode")
@click.pass_context
def summary_top_n(ctx, cluster_path, compare):
    """Get top N performance data."""
    session.ensure_connected()

    try:
        ctrl = SummaryController(session.connection)
        result = ctrl.get_top_n_data(
            cluster_path=cluster_path,
            is_compare=compare
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


# Operator commands
@cli.group()
@click.pass_context
def operator(ctx):
    """Operator analysis commands."""
    pass


@operator.command("categories")
@click.option("--rank-id", help="Rank ID")
@click.option("--device-id", help="Device ID")
@click.option("--group", default="Operator", help="Group type")
@click.pass_context
def operator_categories(ctx, rank_id, device_id, group):
    """Get operator categories."""
    session.ensure_connected()

    try:
        ctrl = OperatorController(session.connection)
        rid = rank_id or session.rank_id
        did = device_id or session.device_id

        result = ctrl.get_category_info(
            rank_id=rid,
            group=group,
            device_id=did
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@operator.command("statistics")
@click.option("--rank-id", help="Rank ID")
@click.option("--device-id", help="Device ID")
@click.option("--group", default="Operator", help="Group type")
@click.option("--page", default=1, help="Page number")
@click.option("--page-size", default=10, help="Page size")
@click.pass_context
def operator_statistics(ctx, rank_id, device_id, group, page, page_size):
    """Get operator statistics."""
    session.ensure_connected()

    try:
        ctrl = OperatorController(session.connection)
        rid = rank_id or session.rank_id
        did = device_id or session.device_id

        result = ctrl.get_statistic_info(
            rank_id=rid,
            group=group,
            device_id=did,
            current_page=page,
            page_size=page_size
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@operator.command("details")
@click.option("--rank-id", help="Rank ID")
@click.option("--device-id", help="Device ID")
@click.option("--op-type", default="", help="Operator type filter")
@click.option("--group", default="Operator", help="Group type")
@click.pass_context
def operator_details(ctx, rank_id, device_id, op_type, group):
    """Get operator details."""
    session.ensure_connected()

    try:
        ctrl = OperatorController(session.connection)
        rid = rank_id or session.rank_id
        did = device_id or session.device_id

        result = ctrl.get_operator_details(
            rank_id=rid,
            group=group,
            device_id=did,
            op_type=op_type
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


# Memory commands
@cli.group()
@click.pass_context
def memory(ctx):
    """Memory analysis commands."""
    pass


@memory.command("view")
@click.option("--rank-id", help="Rank ID")
@click.option("--device-id", help="Device ID")
@click.option("--view-type", default="type", help="View type (type/resourceType/operator/component)")
@click.option("--cluster-path", default="/", help="Cluster path")
@click.pass_context
def memory_view(ctx, rank_id, device_id, view_type, cluster_path):
    """Get memory view."""
    session.ensure_connected()

    try:
        ctrl = MemoryController(session.connection)
        rid = rank_id or session.rank_id
        did = device_id or session.device_id

        result = ctrl.get_memory_view(
            rank_id=rid,
            view_type=view_type,
            device_id=did,
            cluster_path=cluster_path
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@memory.command("operator-size")
@click.option("--rank-id", help="Rank ID")
@click.option("--device-id", help="Device ID")
@click.option("--view-type", default="Overall", help="View type (Overall/Stream)")
@click.pass_context
def memory_operator_size(ctx, rank_id, device_id, view_type):
    """Get operator memory size."""
    session.ensure_connected()

    try:
        ctrl = MemoryController(session.connection)
        rid = rank_id or session.rank_id
        did = device_id or session.device_id

        result = ctrl.get_memory_operator_size(
            rank_id=rid,
            view_type=view_type,
            device_id=did
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


# Communication commands
@cli.group()
@click.pass_context
def communication(ctx):
    """Communication analysis commands."""
    pass


@communication.command("bandwidth")
@click.option("--rank-id", help="Rank ID")
@click.option("--operator-name", required=True, help="Operator name")
@click.option("--stage", default="", help="Stage")
@click.pass_context
def comm_bandwidth(ctx, rank_id, operator_name, stage):
    """Get communication bandwidth."""
    session.ensure_connected()

    try:
        ctrl = CommunicationController(session.connection)
        rid = rank_id or session.rank_id

        result = ctrl.get_bandwidth(
            rank_id=rid,
            operator_name=operator_name,
            stage=stage
        )

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


@communication.command("iterations")
@click.option("--cluster-path", default="/", help="Cluster path")
@click.pass_context
def comm_iterations(ctx, cluster_path):
    """Get communication iterations."""
    session.ensure_connected()

    try:
        ctrl = CommunicationController(session.connection)
        result = ctrl.get_iterations(cluster_path=cluster_path)

        if ctx.obj["json"]:
            print_json(result)
        else:
            print_table(result)

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            raise click.ClickException(str(e))


# REPL loop
def repl_loop(ctx):
    """Interactive REPL loop."""
    while True:
        try:
            prompt = "msinsight> "
            line = input(prompt).strip()

            if not line:
                continue

            if line.lower() in ["exit", "quit", "q"]:
                session.disconnect()
                print("Goodbye!")
                break

            elif line.lower() == "help":
                print("\nAvailable commands:")
                print("  connect                     - Connect to backend")
                print("  disconnect                  - Disconnect from backend")
                print("  summary statistics          - Get performance statistics")
                print("  summary top-n               - Get top N data")
                print("  operator categories         - Get operator categories")
                print("  operator statistics         - Get operator statistics")
                print("  operator details            - Get operator details")
                print("  memory view                 - Get memory view")
                print("  memory operator-size        - Get operator memory size")
                print("  communication bandwidth     - Get bandwidth info")
                print("  communication iterations    - Get communication iterations")
                print("  help                        - Show this help")
                print("  exit                        - Exit REPL\n")

            else:
                # Execute command
                try:
                    args = line.split()
                    cli.main(args=args, standalone_mode=False, obj=ctx.obj)
                except SystemExit:
                    pass
                except Exception as e:
                    print(f"Error: {e}")

        except KeyboardInterrupt:
            print("\nUse 'exit' to quit.")
        except EOFError:
            session.disconnect()
            print("\nGoodbye!")
            break


def main():
    """Main entry point."""
    try:
        cli(obj={})
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
