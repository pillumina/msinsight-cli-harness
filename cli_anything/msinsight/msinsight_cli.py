#!/usr/bin/env python3
"""
MindStudio Insight CLI - Main Entry Point

Command-line interface for MindStudio Insight performance analysis tool.
"""

import sys
import os
import json
import click
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli_anything.msinsight.core.project import (
    create_project,
    open_project,
    save_project,
    get_project_info,
    close_project,
    Project,
)
from cli_anything.msinsight.core.session import Session
from cli_anything.msinsight.core import (
    import_data,
    timeline,
    memory,
    operator,
    communication,
    summary,
    export,
)
from cli_anything.msinsight.utils.msinsight_backend import (
    MsInsightConnection,
    MsInsightBackendError,
)

# Try to import ReplSkin, provide fallback if not available
try:
    from cli_anything.msinsight.utils.repl_skin import ReplSkin
    HAS_REPL_SKIN = True
except ImportError:
    HAS_REPL_SKIN = False
    print("Warning: ReplSkin not available, using basic REPL interface")


# Global session
session = Session()


def get_version():
    """Get CLI version."""
    try:
        from cli_anything.msinsight import __version__
        return __version__
    except:
        return "1.0.0"


def print_json(data: dict):
    """Print JSON output."""
    print(json.dumps(data, indent=2))


def print_error(message: str):
    """Print error message."""
    click.echo(click.style(f"ERROR: {message}", fg="red", bold=True), err=True)


def print_success(message: str):
    """Print success message."""
    click.echo(click.style(f"✓ {message}", fg="green"))


def print_warning(message: str):
    """Print warning message."""
    click.echo(click.style(f"⚠ {message}", fg="yellow"))


def print_info(message: str):
    """Print info message."""
    click.echo(click.style(f"● {message}", fg="blue"))


# Main CLI group
@click.group(invoke_without_command=True)
@click.option("--project", "-p", type=click.Path(exists=True), help="Project file to open")
@click.option("--json", "output_json", is_flag=True, help="Output in JSON format")
@click.option("--version", "-v", is_flag=True, help="Show version")
@click.pass_context
def cli(ctx, project, output_json, version):
    """
    MindStudio Insight CLI - Performance Analysis Tool for Ascend AI

    Analyze profiling data, identify bottlenecks, and generate reports.
    """
    if version:
        click.echo(f"cli-anything-msinsight version {get_version()}")
        return

    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["json"] = output_json

    # Load project if specified
    if project:
        try:
            proj = open_project(project)
            session.set_project(proj)
            if not output_json:
                print_success(f"Opened project: {project}")
        except Exception as e:
            print_error(str(e))
            sys.exit(1)

    # If no subcommand, enter REPL mode
    if ctx.invoked_subcommand is None:
        ctx.invoke(repl, project_path=project)


# Project commands
@cli.group()
@click.pass_context
def project(ctx):
    """Project management commands."""
    pass


@project.command("new")
@click.option("--name", "-n", default="Untitled", help="Project name")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def project_new(ctx, name, output):
    """Create a new analysis project."""
    try:
        proj = create_project(name=name, output_path=output)
        session.set_project(proj)

        if ctx.obj["json"]:
            print_json({
                "status": "success",
                "project": {
                    "name": proj.name,
                    "path": proj.path,
                    "created_at": proj.created_at
                }
            })
        else:
            print_success(f"Created project: {name}")
            if output:
                print_info(f"Saved to: {output}")
    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            print_error(str(e))
        sys.exit(1)


@project.command("open")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def project_open(ctx, path):
    """Open an existing project."""
    try:
        proj = open_project(path)
        session.set_project(proj)

        if ctx.obj["json"]:
            print_json({
                "status": "success",
                "project": get_project_info(proj)
            })
        else:
            print_success(f"Opened project: {proj.name}")
    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            print_error(str(e))
        sys.exit(1)


@project.command("info")
@click.pass_context
def project_info(ctx):
    """Display project information."""
    if not session.project:
        print_error("No project open")
        sys.exit(1)

    info = get_project_info(session.project)

    if ctx.obj["json"]:
        print_json({"status": "success", "project": info})
    else:
        click.echo(f"Project: {info['name']}")
        click.echo(f"Path: {info['path']}")
        click.echo(f"Version: {info['version']}")
        click.echo(f"Created: {info['created_at']}")
        click.echo(f"Data Sources: {info['data_sources_count']}")


@project.command("save")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.pass_context
def project_save(ctx, output):
    """Save current project."""
    if not session.project:
        print_error("No project open")
        sys.exit(1)

    try:
        path = save_project(session.project, output)

        if ctx.obj["json"]:
            print_json({"status": "success", "path": path})
        else:
            print_success(f"Saved project to: {path}")
    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            print_error(str(e))
        sys.exit(1)


# Import commands
@cli.group()
@click.pass_context
def import_cmd(ctx):
    """Data import commands."""
    pass


@import_cmd.command("load-profiling")
@click.argument("path", type=click.Path(exists=True))
@click.option("--format", type=click.Choice(["auto", "db", "json", "bin"]), default="auto", help="Data format")
@click.option("--project-name", "-n", help="Project name (default: auto-detect)")
@click.option("--rank-id", help="Rank ID for multi-rank data")
@click.pass_context
def import_load_profiling(ctx, path, format, project_name, rank_id):
    """Load and import profiling data into MindStudio Insight."""
    try:
        # First validate the data
        result = import_data.validate_data(path)

        if not result["valid"]:
            raise Exception(result.get("error", "Validation failed"))

        # Auto-generate project name if not provided
        if not project_name:
            from pathlib import Path
            project_name = Path(path).stem

        # Import data to backend if connected
        if session.connection and session.connection.is_connected():
            from cli_anything.msinsight.core.data_import import DataImporter

            print_info(f"Importing data to backend: {path}")
            importer = DataImporter(session.connection)

            import_result = importer.import_profiling_data(
                project_name=project_name,
                data_path=path,
                rank_id=rank_id,
                is_new_project=True,
                timeout=120.0
            )

            # Create or update project
            if not session.project:
                from cli_anything.msinsight.core.project import create_project
                session.project = create_project(name=project_name)

            # Add to project data sources
            session.project.data_sources.append({
                "type": "profiling",
                "path": path,
                "format": format,
                "files": result["files"],
                "import_result": import_result
            })
            session.project.modified = True

            if ctx.obj["json"]:
                print_json({
                    "status": "success",
                    "validation": result,
                    "import": import_result
                })
            else:
                print_success(f"Imported profiling data: {path}")
                print_info(f"Project: {project_name}")
                click.echo(f"Total files: {result['total_files']}")
                for ftype, count in result["files"].items():
                    if count > 0:
                        click.echo(f"  - {ftype}: {count} files")

                # Show import result
                if import_result.get("cards"):
                    click.echo(f"\nImported cards: {len(import_result['cards'])}")
                    for card in import_result["cards"][:3]:  # Show first 3
                        click.echo(f"  - {card.get('cardName', 'Unknown')}")

        else:
            # No backend connection, just validate
            if ctx.obj["json"]:
                print_json({"status": "validated", "result": result})
            else:
                print_warning("No backend connection. Data validated but not imported.")
                print_info(f"Valid profiling data: {path}")
                click.echo(f"Total files: {result['total_files']}")
                for ftype, count in result["files"].items():
                    if count > 0:
                        click.echo(f"  - {ftype}: {count} files")

    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            print_error(str(e))
        sys.exit(1)


@import_cmd.command("validate")
@click.argument("path", type=click.Path(exists=True))
@click.pass_context
def import_validate(ctx, path):
    """Validate profiling data files."""
    try:
        result = import_data.validate_data(path)

        if ctx.obj["json"]:
            print_json({"status": "success", "result": result})
        else:
            if result["valid"]:
                print_success(f"Valid profiling data: {path}")
                click.echo(f"Total files: {result['total_files']}")
                for ftype, count in result["files"].items():
                    click.echo(f"  {ftype}: {count}")
            else:
                print_error(result.get("error", "Validation failed"))
    except Exception as e:
        if ctx.obj["json"]:
            print_json({"status": "error", "error": str(e)})
        else:
            print_error(str(e))
        sys.exit(1)


# Analysis commands (simplified - would need backend integration)
@cli.group()
@click.pass_context
def timeline_cmd(ctx):
    """Timeline analysis commands."""
    pass


@timeline_cmd.command("show")
@click.option("--start", type=float, help="Start time (ms)")
@click.option("--end", type=float, help="End time (ms)")
@click.option("--rank", type=int, help="Rank ID")
@click.pass_context
def timeline_show(ctx, start, end, rank):
    """Display timeline data."""
    print_warning("Timeline analysis requires backend integration")
    if ctx.obj["json"]:
        print_json({"status": "error", "error": "Backend integration required"})


@cli.group()
@click.pass_context
def operator_cmd(ctx):
    """Operator analysis commands."""
    pass


@operator_cmd.command("list")
@click.option("--sort", type=click.Choice(["duration", "calls", "memory"]), default="duration", help="Sort by")
@click.pass_context
def operator_list(ctx, sort):
    """List all operators."""
    print_warning("Operator analysis requires backend integration")
    if ctx.obj["json"]:
        print_json({"status": "error", "error": "Backend integration required"})


@cli.group()
@click.pass_context
def memory_cmd(ctx):
    """Memory analysis commands."""
    pass


@memory_cmd.command("summary")
@click.option("--rank", type=int, help="Rank ID")
@click.pass_context
def memory_summary(ctx, rank):
    """Get memory usage summary."""
    print_warning("Memory analysis requires backend integration")
    if ctx.obj["json"]:
        print_json({"status": "error", "error": "Backend integration required"})


# Export commands
@cli.group()
@click.pass_context
def export_cmd(ctx):
    """Export commands."""
    pass


@export_cmd.command("report")
@click.argument("output", type=click.Path())
@click.option("--format", type=click.Choice(["pdf", "html", "json"]), default="pdf", help="Report format")
@click.pass_context
def export_report(ctx, output, format):
    """Generate analysis report."""
    if not session.project:
        print_error("No project open")
        sys.exit(1)

    print_warning(f"Report generation requires backend integration")
    print_info(f"Would export to: {output} (format: {format})")

    if ctx.obj["json"]:
        print_json({
            "status": "success",
            "output": output,
            "format": format,
            "message": "Report generation requires backend integration"
        })


# Session commands
@cli.group()
@click.pass_context
def session_cmd(ctx):
    """Session management commands."""
    pass


@session_cmd.command("status")
@click.pass_context
def session_status(ctx):
    """Show session status."""
    status = session.get_status()

    if ctx.obj["json"]:
        print_json({"status": "success", "session": status})
    else:
        click.echo("Session Status:")
        click.echo(f"  Project: {status['project'] or 'None'}")
        click.echo(f"  Modified: {status['modified']}")
        click.echo(f"  History: {status['history_count']} commands")


# REPL command
@cli.command()
@click.option("--project-path", type=click.Path(exists=True), help="Project to open")
@click.pass_context
def repl(ctx, project_path):
    """Start interactive REPL mode."""
    if HAS_REPL_SKIN:
        skin = ReplSkin("msinsight", version=get_version())
        skin.print_banner()

        if session.project:
            skin.info(f"Project: {session.project.name}")
    else:
        click.echo("=" * 60)
        click.echo("MindStudio Insight CLI - Interactive Mode")
        click.echo("=" * 60)
        click.echo(f"Version: {get_version()}")
        if session.project:
            click.echo(f"Project: {session.project.name}")
        click.echo()

    click.echo("Type 'help' for available commands, 'exit' to quit.\n")

    # Simple REPL loop
    while True:
        try:
            prompt = "msinsight> "
            if session.project:
                modified = "*" if session.project.modified else ""
                prompt = f"msinsight({session.project.name}{modified})> "

            line = input(prompt).strip()

            if not line:
                continue

            if line.lower() in ["exit", "quit", "q"]:
                if session.project and session.project.modified:
                    click.echo("Warning: Project has unsaved changes.")
                    response = input("Save before exiting? (y/n): ").strip().lower()
                    if response == "y":
                        if session.project.path:
                            save_project(session.project)
                            print_success("Project saved")
                        else:
                            click.echo("No save path specified. Use 'project save -o <path>' to save.")

                if HAS_REPL_SKIN:
                    skin.print_goodbye()
                else:
                    click.echo("\nGoodbye!")
                break

            elif line.lower() == "help":
                click.echo("\nAvailable commands:")
                click.echo("  project new/open/info/save  - Project management")
                click.echo("  import load-profiling       - Load profiling data")
                click.echo("  timeline/memory/operator    - Analysis (requires backend)")
                click.echo("  export report               - Export reports")
                click.echo("  session status              - Show session status")
                click.echo("  help                        - Show this help")
                click.echo("  exit                        - Exit REPL\n")

            elif line.lower() == "status":
                ctx.invoke(session_status)

            else:
                # Try to execute as CLI command
                try:
                    args = line.split()
                    cli.main(args=args, standalone_mode=False, obj=ctx.obj)
                except SystemExit:
                    pass
                except Exception as e:
                    print_error(f"Command failed: {e}")

        except KeyboardInterrupt:
            click.echo("\nUse 'exit' to quit.")
        except EOFError:
            click.echo("\nGoodbye!")
            break


# Register command groups
cli.add_command(import_cmd, name="import")
cli.add_command(timeline_cmd, name="timeline")
cli.add_command(operator_cmd, name="operator")
cli.add_command(memory_cmd, name="memory")
cli.add_command(export_cmd, name="export")
cli.add_command(session_cmd, name="session")


def main():
    """Main entry point."""
    try:
        cli(obj={})
    except MsInsightBackendError as e:
        print_error(str(e))
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
