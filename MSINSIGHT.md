# MindStudio Insight CLI - Standard Operating Procedure

## Overview

This document defines the CLI architecture for MindStudio Insight (msinsight), a visual performance tuning tool for Ascend AI applications. The CLI enables headless operation, batch processing, and AI agent integration.

## Interaction Model

**Both REPL and Subcommand CLI** (recommended)

- **REPL Mode**: Default interactive mode for exploratory analysis
- **Subcommand Mode**: One-shot operations for scripting and automation
- **Unified Interface**: Same commands work in both modes

```bash
# REPL mode (default)
cli-anything-msinsight

# Subcommand mode
cli-anything-msinsight project new -o analysis.json
cli-anything-msinsight --project analysis.json import load-profiling /path/to/profiling
cli-anything-msinsight --project analysis.json export report output.pdf
```

## Command Groups

### 1. **Project Management** (`project`)
Manage analysis projects and sessions.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `new` | Create new analysis project | `-o, --output <path>` |
| `open` | Open existing project | `<path>` |
| `info` | Display project information | |
| `save` | Save current project state | `[-o, --output <path>]` |
| `close` | Close current project | |

**Example:**
```bash
cli-anything-msinsight project new -o my_analysis.json
cli-anything-msinsight project open my_analysis.json
cli-anything-msinsight project info
```

### 2. **Data Import** (`import`)
Load profiling data from various sources.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `load-profiling` | Load profiling directory | `<path> [--format auto\|db\|json\|bin]` |
| `load-db` | Load SQLite database | `<path>` |
| `validate` | Validate data files | `<path>` |
| `list-files` | List detected profiling files | `[--path <dir>]` |

**Example:**
```bash
cli-anything-msinsight import load-profiling /data/profiler_output
cli-anything-msinsight import load-db /data/profiler.db
cli-anything-msinsight import validate /data/profiler_output
```

### 3. **Timeline Analysis** (`timeline`)
Analyze execution timeline and events.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `show` | Display timeline data | `[--start <time>] [--end <time>] [--rank <id>]` |
| `filter` | Filter timeline events | `--type <event_type> [--duration-min <ms>]` |
| `export` | Export timeline data | `<output> [--format json\|csv]` |
| `zoom` | Zoom to time range | `--start <time> --end <time>` |
| `search` | Search events | `<pattern>` |

**Example:**
```bash
cli-anything-msinsight timeline show --start 0 --end 1000
cli-anything-msinsight timeline filter --type operator --duration-min 10
cli-anything-msinsight timeline export timeline.json --format json
```

### 4. **Memory Analysis** (`memory`)
Analyze memory allocation and usage.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `summary` | Memory usage summary | `[--rank <id>]` |
| `leaks` | Detect memory leaks | `[--threshold <bytes>]` |
| `lifecycle` | Memory block lifecycle | `[--block-id <id>]` |
| `trend` | Memory usage trend | `[--interval <ms>]` |
| `export` | Export memory data | `<output> [--format json\|csv]` |

**Example:**
```bash
cli-anything-msinsight memory summary
cli-anything-msinsight memory leaks --threshold 1024
cli-anything-msinsight memory lifecycle --block-id abc123
```

### 5. **Operator Analysis** (`operator`)
Analyze operator performance and kernels.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `list` | List all operators | `[--sort duration\|calls\|memory]` |
| `top` | Top N operators | `--count <n> --metric <metric>` |
| `details` | Operator details | `<operator_id>` |
| `filter` | Filter operators | `--type <type> [--duration-min <ms>]` |
| `source` | Show operator source code | `<operator_id>` |
| `export` | Export operator data | `<output> [--format json\|csv]` |

**Example:**
```bash
cli-anything-msinsight operator list --sort duration
cli-anything-msinsight operator top --count 10 --metric duration
cli-anything-msinsight operator details op_12345
```

### 6. **Communication Analysis** (`communication`)
Analyze cluster communication performance.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `matrix` | Communication matrix | `[--rank <id>]` |
| `overview` | Communication overview | |
| `bottleneck` | Identify bottlenecks | `[--threshold <ms>]` |
| `link` | Link performance | `--src <rank> --dst <rank>` |
| `export` | Export communication data | `<output> [--format json\|csv]` |

**Example:**
```bash
cli-anything-msinsight communication matrix
cli-anything-msinsight communication bottleneck --threshold 100
cli-anything-msinsight communication link --src 0 --dst 1
```

### 7. **Summary Statistics** (`summary`)
Performance summaries and overviews.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `overview` | Performance overview | |
| `compute` | Compute metrics summary | |
| `communication` | Communication summary | |
| `export` | Export summary | `<output> [--format json\|pdf]` |

**Example:**
```bash
cli-anything-msinsight summary overview
cli-anything-msinsight summary compute
cli-anything-msinsight summary export report.pdf --format pdf
```

### 8. **Export** (`export`)
Export reports and data in various formats.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `report` | Generate analysis report | `<output> [--format pdf\|html\|json]` |
| `timeline` | Export timeline data | `<output> [--format json\|csv]` |
| `operators` | Export operator data | `<output> [--format json\|csv]` |
| `memory` | Export memory data | `<output> [--format json\|csv]` |
| `all` | Export all data | `<output_dir>` |

**Example:**
```bash
cli-anything-msinsight export report analysis_report.pdf --format pdf
cli-anything-msinsight export timeline timeline_data.json
cli-anything-msinsight export all ./exported_data/
```

### 9. **Session Management** (`session`)
Manage analysis session state.

| Command | Description | Arguments |
|---------|-------------|-----------|
| `status` | Current session status | |
| `history` | Command history | `[--limit <n>]` |
| `clear` | Clear session cache | |
| `config` | Configure session | `<key> <value>` |

**Example:**
```bash
cli-anything-msinsight session status
cli-anything-msinsight session history --limit 20
cli-anything-msinsight session config log_level DEBUG
```

## State Model

### Persistent State (Project File)
```json
{
  "version": "1.0.0",
  "project_name": "My Analysis",
  "created_at": "2026-03-16T12:00:00Z",
  "data_sources": [
    {
      "type": "profiling",
      "path": "/data/profiler_output",
      "loaded_at": "2026-03-16T12:05:00Z"
    }
  ],
  "analysis_cache": {
    "timeline": {...},
    "memory": {...},
    "operators": {...}
  },
  "filters": {
    "time_range": {"start": 0, "end": 10000},
    "ranks": [0, 1, 2, 3]
  },
  "exports": [
    {"type": "report", "path": "./report.pdf", "exported_at": "..."}
  ]
}
```

### Session State (In-Memory)
- Current project reference
- Active filters and zoom ranges
- Command history
- WebSocket connection to backend server
- Cache of frequently accessed data

## Output Formats

### Human-Readable (Default)
- Tables with colors and formatting
- Progress bars for long operations
- Formatted summaries and statistics
- Tree structures for hierarchical data

### Machine-Readable (`--json` flag)
```bash
cli-anything-msinsight --json operator list
```

Output:
```json
{
  "status": "success",
  "data": {
    "operators": [
      {
        "id": "op_12345",
        "name": "MatMul",
        "type": "compute",
        "duration_ms": 15.3,
        "calls": 100,
        "memory_bytes": 1048576
      }
    ],
    "total_count": 1,
    "sort_by": "duration"
  }
}
```

## Backend Integration

### Server Management
The CLI manages the backend WebSocket server automatically:

1. **Auto-start**: Start server if not running
2. **Port discovery**: Find available port in range 9000-9100
3. **Connection management**: Maintain WebSocket connection
4. **Graceful shutdown**: Close server on exit

### Backend Communication
```python
# utils/msinsight_backend.py

def find_msinsight_server():
    """Find or start the msinsight backend server."""
    # Check if server is already running
    for port in range(9000, 9100):
        if is_server_running(port):
            return port

    # Start new server
    port = find_available_port(9000, 9100)
    start_server(port)
    wait_for_server_ready(port)
    return port

def send_request(port, module, command, params):
    """Send WebSocket request to backend."""
    # Connect to ws://localhost:{port}
    # Send JSON request
    # Receive JSON response
    # Return parsed data
```

## Error Handling

### Clear Error Messages
```bash
$ cli-anything-msinsight import load-profiling /invalid/path
ERROR: Profiling directory not found: /invalid/path

Suggestion: Verify the path contains profiling data files:
  - .db files (SQLite databases)
  - .json files (metadata)
  - .bin files (binary profiling data)

Run 'cli-anything-msinsight import validate <path>' to check data integrity.
```

### JSON Error Format
```json
{
  "status": "error",
  "error": {
    "code": "DATA_NOT_FOUND",
    "message": "Profiling directory not found: /invalid/path",
    "suggestion": "Verify the path contains valid profiling data files"
  }
}
```

## REPL Interface

### Startup Banner
```
╔═══════════════════════════════════════════════════════════════╗
║                    MindStudio Insight CLI                      ║
║                   Performance Analysis Tool                    ║
╚═══════════════════════════════════════════════════════════════╝

Version: 1.0.0
Backend: Connected to ws://localhost:9000
Project: my_analysis.json

◇ Skill: /path/to/cli_anything/msinsight/skills/SKILL.md

Type 'help' for available commands, 'exit' to quit.

msinsight> _
```

### Unified REPL Skin
Use `ReplSkin` from `utils/repl_skin.py`:
- `skin.print_banner()` - Branded startup
- `skin.get_input()` - Prompt with project status
- `skin.help()` - Formatted help
- `skin.success()`, `skin.error()`, `skin.warning()`, `skin.info()` - Messages
- `skin.table()` - Formatted tables
- `skin.print_goodbye()` - Exit message

## Directory Structure

```
msinsight/
└── agent-harness/
    ├── MSINSIGHT.md              # This file
    ├── MSINSIGHT_ANALYSIS.md     # Codebase analysis
    ├── setup.py                  # PyPI package
    └── cli_anything/             # Namespace package (NO __init__.py)
        └── msinsight/            # Sub-package (HAS __init__.py)
            ├── __init__.py
            ├── __main__.py
            ├── README.md
            ├── msinsight_cli.py  # Main CLI entry point
            ├── core/             # Core modules
            │   ├── __init__.py
            │   ├── project.py    # Project management
            │   ├── import_data.py # Data import
            │   ├── timeline.py   # Timeline analysis
            │   ├── memory.py     # Memory analysis
            │   ├── operator.py   # Operator analysis
            │   ├── communication.py # Communication analysis
            │   ├── summary.py    # Summary statistics
            │   ├── export.py     # Export pipeline
            │   └── session.py    # Session management
            ├── utils/
            │   ├── __init__.py
            │   ├── msinsight_backend.py # Backend integration
            │   └── repl_skin.py  # REPL interface
            ├── skills/
            │   └── SKILL.md      # AI agent skill definition
            └── tests/
                ├── TEST.md       # Test plan and results
                ├── test_core.py  # Unit tests
                └── test_full_e2e.py # E2E tests
```

## Implementation Priorities

### Phase 1: Core Functionality
1. Backend server integration (`utils/msinsight_backend.py`)
2. Project management (`core/project.py`)
3. Data import (`core/import_data.py`)
4. Basic analysis commands (timeline, memory, operator)

### Phase 2: Advanced Features
1. Export functionality
2. Communication analysis
3. Summary statistics
4. Session management

### Phase 3: Polish
1. REPL interface
2. JSON output mode
3. Error handling
4. Documentation

## Testing Strategy

### Unit Tests (`test_core.py`)
- Project creation/loading
- Data import validation
- Analysis algorithms (synthetic data)
- Export format generation

### E2E Tests (`test_full_e2e.py`)
- Load real profiling data
- Perform analysis
- Generate reports
- Verify output formats
- Subprocess tests with installed CLI

### Test Data
- Sample profiling directory with all file types
- Small SQLite database
- JSON metadata files
- Binary profiling data

## Dependencies

### Python Packages
```python
# setup.py
install_requires=[
    "click>=8.0.0",
    "prompt-toolkit>=3.0.0",
    "websocket-client>=1.0.0",
    "requests>=2.28.0",
]
```

### System Dependencies
- **MindStudio Insight Backend**: The C++ server binary
  - Build from source: `cd server && python build/build.py build --release`
  - Location: `server/output/<platform>/bin/msinsight-server` or similar
  - **Hard dependency**: CLI requires the backend server

## Success Criteria

The CLI succeeds when:
1. ✅ Can start backend server automatically
2. ✅ Load profiling data from directory
3. ✅ Perform all analysis types (timeline, memory, operator, communication)
4. ✅ Export reports in multiple formats
5. ✅ Work in both REPL and subcommand modes
6. ✅ Support `--json` output for all commands
7. ✅ All tests pass (unit + E2E + subprocess)
8. ✅ CLI available in PATH after `pip install`
9. ✅ AI agents can use CLI via skill file
10. ✅ Backend server is a hard dependency (not optional)

## Usage Examples

### Interactive Analysis
```bash
$ cli-anything-msinsight
msinsight> project new -o analysis.json
✓ Created project: analysis.json

msinsight> import load-profiling /data/profiler_output
✓ Loaded profiling data from /data/profiler_output
  - 4 JSON files
  - 2 DB files
  - 15 BIN files

msinsight> timeline show --start 0 --end 1000
Timeline: 0ms - 1000ms
┌──────────┬──────────┬────────────┐
│ Start    │ End      │ Event      │
├──────────┼──────────┼────────────┤
│ 0ms      │ 15ms     │ MatMul     │
│ 15ms     │ 32ms     │ AllReduce  │
│ ...      │ ...      │ ...        │
└──────────┴──────────┴────────────┘

msinsight> operator top --count 5 --metric duration
Top 5 Operators by Duration
┌──────┬──────────┬──────────┬───────┐
│ Rank │ Name     │ Duration │ Calls │
├──────┼──────────┼──────────┼───────┤
│ 1    │ MatMul   │ 15.3ms   │ 100   │
│ 2    │ Conv2D   │ 12.1ms   │ 50    │
│ 3    │ AllReduce│ 8.7ms    │ 20    │
│ 4    │ ReLU     │ 5.2ms    │ 150   │
│ 5    │ Softmax  │ 3.9ms    │ 30    │
└──────┴──────────┴──────────┴───────┘

msinsight> export report analysis_report.pdf --format pdf
✓ Exported report to: analysis_report.pdf (245 KB)

msinsight> exit
Goodbye!
```

### Batch Processing
```bash
#!/bin/bash
# batch_analysis.sh

for dir in /data/profiler_*; do
    name=$(basename "$dir")
    cli-anything-msinsight project new -o "analysis_${name}.json"
    cli-anything-msinsight --project "analysis_${name}.json" import load-profiling "$dir"
    cli-anything-msinsight --project "analysis_${name}.json" export report "report_${name}.pdf" --format pdf
done
```

### AI Agent Integration
```python
# AI agent using the CLI
import subprocess
import json

# Load profiling data
result = subprocess.run([
    "cli-anything-msinsight", "--json",
    "project", "new", "-o", "analysis.json"
], capture_output=True, text=True)
project = json.loads(result.stdout)

# Analyze operators
result = subprocess.run([
    "cli-anything-msinsight", "--json",
    "--project", "analysis.json",
    "operator", "top", "--count", "10", "--metric", "duration"
], capture_output=True, text=True)
top_operators = json.loads(result.stdout)

# Identify bottleneck
bottleneck = top_operators["data"]["operators"][0]
print(f"Performance bottleneck: {bottleneck['name']} ({bottleneck['duration_ms']}ms)")
```

## Next Steps

1. **Phase 3**: Implement core modules and CLI structure
2. **Phase 4**: Create comprehensive test plan
3. **Phase 5**: Write unit and E2E tests
4. **Phase 6**: Run tests and document results
5. **Phase 6.5**: Generate SKILL.md for AI discovery
6. **Phase 7**: Package and publish to PyPI
