# MindStudio Insight CLI

Command-line interface for MindStudio Insight - Performance Analysis Tool for Ascend AI

## Overview

This CLI provides headless operation, batch processing, and AI agent integration for MindStudio Insight, enabling automated performance analysis of Ascend AI applications.

## Features

- **Interactive REPL**: Default interactive mode for exploratory analysis
- **Subcommand Mode**: One-shot operations for scripting and automation
- **JSON Output**: Machine-readable output for AI agents (`--json` flag)
- **Project Management**: Save and load analysis sessions
- **Data Import**: Load profiling data from directories
- **Analysis Commands**: Timeline, memory, operator, communication analysis
- **Export**: Generate reports in multiple formats

## Installation

### Prerequisites

1. **MindStudio Insight GUI Application** (Required)

   The CLI requires the MindStudio Insight backend server. **If you already have MindStudio Insight installed, you're all set!**

   **Download and install MindStudio Insight:**
   - **Windows**: Download the `.exe` installer from the [release page](https://gitcode.com/Ascend/msinsight/releases)
   - **macOS**: Download the `.dmg` file from the [release page](https://gitcode.com/Ascend/msinsight/releases)
   - **Linux**: Download the `.tar.gz` package from the [release page](https://gitcode.com/Ascend/msinsight/releases)

   The installer includes the backend server (`msinsight-server`).

   **No source code required!** ✅

2. **Python 3.10+**

### Install CLI

```bash
pip install cli-anything-msinsight
```

This installs the `cli-anything-msinsight` command to your PATH.

### Verify Installation

```bash
which cli-anything-msinsight
cli-anything-msinsight --version
cli-anything-msinsight --help
```

## Usage

### Interactive Mode (REPL)

```bash
$ cli-anything-msinsight
╔═══════════════════════════════════════════════════════════════╗
║                    MindStudio Insight CLI                      ║
║                   Performance Analysis Tool                    ║
╚═══════════════════════════════════════════════════════════════╝

Type 'help' for available commands, 'exit' to quit.

msinsight> project new -o analysis.json
✓ Created project: analysis.json

msinsight> import load-profiling /data/profiler_output
✓ Validated profiling data: /data/profiler_output
  - 4 JSON files
  - 2 DB files
  - 15 BIN files

msinsight> exit
Goodbye!
```

### Subcommand Mode

```bash
# Create project
cli-anything-msinsight project new -o analysis.json

# Load data
cli-anything-msinsight --project analysis.json import load-profiling /data/profiler_output

# Export report
cli-anything-msinsight --project analysis.json export report output.pdf --format pdf
```

### JSON Output (for AI Agents)

```bash
cli-anything-msinsight --json project new -o analysis.json
```

Output:
```json
{
  "status": "success",
  "project": {
    "name": "Untitled",
    "path": "analysis.json",
    "version": "1.0.0",
    "created_at": "2026-03-16T12:00:00Z"
  }
}
```

## Command Reference

### Project Management

```bash
cli-anything-msinsight project new --name "My Analysis" --output my_analysis.json
cli-anything-msinsight project open my_analysis.json
cli-anything-msinsight project info
cli-anything-msinsight project save
cli-anything-msinsight project close
```

### Data Import

```bash
# Load profiling directory
cli-anything-msinsight --project my_analysis.json import load-profiling /path/to/profiler_output

# Validate data files
cli-anything-msinsight import validate /path/to/profiler_output

# List detected files
cli-anything-msinsight import list-files /path/to/profiler_output
```

### Analysis (Requires Backend Integration)

```bash
# Timeline analysis
cli-anything-msinsight --project my_analysis.json timeline show --start 0 --end 1000

# Memory analysis
cli-anything-msinsight --project my_analysis.json memory summary

# Operator analysis
cli-anything-msinsight --project my_analysis.json operator list --sort duration

# Communication analysis
cli-anything-msinsight --project my_analysis.json communication matrix
```

### Export

```bash
# Generate report
cli-anything-msinsight --project my_analysis.json export report analysis.pdf --format pdf

# Export timeline data
cli-anything-msinsight --project my_analysis.json export timeline timeline.json

# Export all data
cli-anything-msinsight --project my_analysis.json export all ./exported_data/
```

### Session Management

```bash
# Show session status
cli-anything-msinsight session status
```

## Batch Processing

Example script for analyzing multiple profiling runs:

```bash
#!/bin/bash
# batch_analysis.sh

for dir in /data/profiler_*; do
    name=$(basename "$dir")
    cli-anything-msinsight project new -o "analysis_${name}.json"
    cli-anything-msinsight --project "analysis_${name}.json" import load-profiling "$dir"
    cli-anything-msinsight --project "analysis_${name}.json" export report "report_${name}.pdf"
done
```

## AI Agent Integration

The CLI is designed for AI agent use with `--json` output:

```python
import subprocess
import json

# Create project
result = subprocess.run([
    "cli-anything-msinsight", "--json",
    "project", "new", "-o", "analysis.json"
], capture_output=True, text=True)
project = json.loads(result.stdout)

# Load data
result = subprocess.run([
    "cli-anything-msinsight", "--json",
    "--project", "analysis.json",
    "import", "load-profiling", "/data/profiler_output"
], capture_output=True, text=True)
data_info = json.loads(result.stdout)

# Analyze operators
result = subprocess.run([
    "cli-anything-msinsight", "--json",
    "--project", "analysis.json",
    "operator", "top", "--count", "10", "--metric", "duration"
], capture_output=True, text=True)
top_operators = json.loads(result.stdout)

# Identify bottleneck
if top_operators["status"] == "success":
    bottleneck = top_operators["data"]["operators"][0]
    print(f"Performance bottleneck: {bottleneck['name']} ({bottleneck['duration_ms']}ms)")
```

## Architecture

```
cli-anything-msinsight/
├── core/
│   ├── project.py          # Project management
│   ├── import_data.py      # Data import
│   ├── timeline.py         # Timeline analysis
│   ├── memory.py           # Memory analysis
│   ├── operator.py         # Operator analysis
│   ├── communication.py    # Communication analysis
│   ├── summary.py          # Summary statistics
│   ├── export.py           # Export pipeline
│   └── session.py          # Session management
├── utils/
│   ├── msinsight_backend.py  # Backend server integration
│   └── repl_skin.py          # REPL interface
├── tests/
│   ├── TEST.md            # Test plan and results
│   ├── test_core.py       # Unit tests
│   └── test_full_e2e.py   # E2E tests
└── skills/
    └── SKILL.md           # AI agent skill definition
```

## Backend Server

The CLI automatically manages the MindStudio Insight backend server:

1. **Auto-start**: Starts server if not running
2. **Port discovery**: Finds available port in range 9000-9100
3. **Connection management**: Maintains WebSocket connection
4. **Graceful shutdown**: Closes server on exit

## Current Status

**Note**: This CLI is a functional skeleton that demonstrates the architecture. Full analysis capabilities require integration with the MindStudio Insight WebSocket backend.

### Implemented
- ✅ Project management (create, open, save, info)
- ✅ REPL interface
- ✅ JSON output mode
- ✅ Command structure and parsing
- ✅ Data validation
- ✅ Error handling

### Requires Backend Integration
- ⏳ Timeline analysis
- ⏳ Memory analysis
- ⏳ Operator analysis
- ⏳ Communication analysis
- ⏳ Report generation
- ⏳ WebSocket communication with backend

## Development

### Run Tests

```bash
cd agent-harness
pytest cli_anything/msinsight/tests/ -v
```

### Build Package

```bash
cd agent-harness
python setup.py sdist bdist_wheel
```

## Troubleshooting

### Backend Server Not Found

```
ERROR: MindStudio Insight backend server not found.

Please build the server from source:
  cd server
  python build/build.py build --release
```

**Solution**: Build the backend server from source as described in Prerequisites.

### No Available Port

```
ERROR: No available port found in range 9000-9100.
```

**Solution**: Close services using ports 9000-9100 or kill existing msinsight-server processes.

### WebSocket Connection Failed

```
ERROR: Failed to connect to server at ws://127.0.0.1:9000
```

**Solution**: Check that the backend server is running and logs show no errors.

## License

Mulan PSL v2 - See LICENSE file for details.

## Contributing

See CONTRIBUTING.md in the project root.

## Support

- **Issues**: https://gitcode.com/Ascend/msinsight/issues
- **Documentation**: https://msinsight.readthedocs.io/

## Authors

MindStudio Team at Huawei Technologies Co., Ltd.
