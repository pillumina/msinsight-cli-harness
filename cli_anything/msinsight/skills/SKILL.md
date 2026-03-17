---
name: cli-anything-msinsight
description: ⚠️ WORK IN PROGRESS - WebSocket protocol works, but Control Layer API needs complete redesign to match backend actual commands (115+ handlers). Currently supports basic commands only (heartbeat, config, project list). Full timeline/operator/memory analysis capabilities not yet implemented.
---

# MindStudio Insight CLI Harness

CLI harness for controlling MindStudio Insight performance analysis tool through AI agents using command-line interface.

## Architecture

```
User Natural Language
        ↓
    AI Agent
        ↓
  Skill (this file)
        ↓
    CLI Commands
        ↓
 WebSocket Protocol
        ↓
 MindStudio Insight Backend
```

## Core Components

### 1. CLI Entry Point
Command-line interface with REPL mode:
- `cli-anything-msinsight` - Main CLI command
- Interactive REPL mode for multi-step operations
- JSON output support with `--json` flag

### 2. Command Groups
- **import**: Data import commands
- **timeline**: Timeline analysis and control
- **operator**: Operator analysis
- **memory**: Memory analysis
- **export**: Report generation
- **project**: Project management
- **session**: Session management

## Installation

```bash
# Clone repository
git clone git@github.com:pillumina/msinsight-cli-harness.git
cd msinsight-cli-harness

# Install
pip install -e .
```

**Prerequisites**:
- Python 3.10+
- MindStudio Insight installed (for backend server)
- websocket-client library

## Usage for AI Agents

### CLI Commands (Recommended)

**Important**: Always use CLI commands, not Python API.

#### 1. Start CLI and Import Data

```bash
# Start CLI (close MindStudio Insight GUI first - single connection limit)
cli-anything-msinsight

# Import profiling data
msinsight> import load-profiling /path/to/profiling/data --project-name MyProject

# Or import multi-rank data
msinsight> import load-profiling /path/to/rank0 --project-name MyProject
msinsight> import load-profiling /path/to/rank1 --project-name MyProject
```

#### 2. Query Data

```bash
# Get top N operators by duration
msinsight> operator list --sort duration

# Get memory summary
msinsight> memory summary

# Get project info
msinsight> project info

# Check session status
msinsight> session status
```

#### 3. Timeline Control

```bash
# Show timeline data
msinsight> timeline show --start 0 --end 1000

# Filter by rank
msinsight> timeline show --rank 0
```

#### 4. Export Reports

```bash
# Generate report
msinsight> export report /path/to/output.pdf --format pdf
```

#### 5. Non-Interactive Mode (Single Commands)

```bash
# Run single command without entering REPL
cli-anything-msinsight --json import load-profiling /path/to/data

# Get project info in JSON format
cli-anything-msinsight --json project info
```

### Key CLI Commands Reference

#### Import Commands
```bash
import load-profiling <PATH>        # Import profiling data
  --format <auto|db|json|bin>      # Data format (default: auto)
  --project-name <NAME>            # Project name
  --rank-id <ID>                   # Rank ID for multi-rank data

import validate <PATH>              # Validate data files
```

#### Project Commands
```bash
project new                         # Create new project
  --name <NAME>                    # Project name
  --output <PATH>                  # Output file path

project open <PATH>                 # Open existing project
project info                        # Display project info
project save                        # Save current project
  --output <PATH>                  # Output file path
```

#### Analysis Commands
```bash
operator list                       # List all operators
  --sort <duration|calls|memory>   # Sort by metric

memory summary                      # Get memory usage summary
  --rank <ID>                      # Filter by rank

timeline show                       # Display timeline data
  --start <TIME>                   # Start time (ms)
  --end <TIME>                     # End time (ms)
  --rank <ID>                      # Filter by rank
```

#### Export Commands
```bash
export report <OUTPUT>              # Generate analysis report
  --format <pdf|html|json>         # Report format
```

#### Session Commands
```bash
session status                      # Show session status
```

## Important Notes

### Single Connection Limit
⚠️ **Backend only allows ONE WebSocket connection**
- Close MindStudio Insight GUI before using CLI
- Cannot use CLI and GUI simultaneously

### Data Dependency
⚠️ **Most commands require data to be imported first**
- Import data using `import load-profiling` command
- Then query and analysis operations will work

### Backend State
⚠️ **Backend must be running before using CLI**
- Start MindStudio Insight to launch backend
- Close GUI but keep backend running
- Or start backend standalone if supported

## For AI Agents

### When to Use This Skill
Use this skill when users want to:
- Analyze MindStudio Insight profiling data
- Control timeline visualization
- Query performance metrics
- Identify bottlenecks
- Compare ranks
- Get optimization suggestions

### Best Practices
1. **Use CLI commands**: Execute commands via Bash tool, not Python API
2. **Import data first**: Most commands need data to be imported
3. **Close GUI**: Single connection limit
4. **Use --json flag**: For structured output when needed
5. **Check session status**: Use `session status` to verify state

### Example Agent Workflow

```
User: "帮我分析最慢的算子"

AI Agent:
1. Check if backend is running
   lsof -i :9000

2. Start CLI and import data
   cli-anything-msinsight --json import load-profiling /path/to/data --project-name MyProject

3. Query top operators
   cli-anything-msinsight --json operator list --sort duration

4. Parse JSON response and return results to user
   "最慢的算子是：
    1. MatMul_123: 45.23 ms
    2. Conv2d_456: 32.10 ms
    ..."
```

### Example: Multi-step Analysis in REPL

```bash
# Start REPL
cli-anything-msinsight

# Create project
msinsight> project new --name "Performance Analysis"

# Import data
msinsight> import load-profiling /data/rank_0 --project-name "Performance Analysis"

# Check import
msinsight> session status

# Analyze
msinsight> operator list --sort duration
msinsight> memory summary

# Export report
msinsight> export report analysis_report.pdf --format pdf

# Exit
msinsight> exit
```

## Status

⚠️ **Work in Progress - Protocol Layer Complete, Control Layer Needs Reimplementation**

### ✅ Completed (Verified):
- **Protocol Layer**: WebSocket connection, message format, heartbeat
- **Basic Commands**: `heartCheck`, `moduleConfig/get`, `files/getProjectExplorer`
- **Connection Management**: Connect, disconnect, reconnect

### ⚠️ Known Issues:
- **Control Layer API Mismatch**: Designed commands do not match backend actual commands
  - My API: `getTopNOperators`, `getMemorySummary`, `zoomToRange`
  - Backend: `op/statistic/info`, `mem/scope/*`, `thread/traces`, etc.
- **Needs Complete Redesign**: Control Layer must be reimplemented based on actual backend commands
- **Backend has 115+ handlers**: Need to map each to CLI commands

### ⏳ Not Yet Implemented:
- Timeline manipulation (zoom, pan, filter)
- Data queries (operators, memory, communication)
- Analysis commands
- Export/report generation

**Overall Progress**: 40% - Protocol layer works, Control layer needs complete redesign

## Known Limitations

1. **Backend Required**: Commands need MindStudio Insight backend running
2. **Single Connection**: Only one client can connect at a time
3. **Data Import First**: Most commands require imported data
4. **Limited Backend Commands**: Some analysis commands may not be implemented in backend yet

## Testing Status

- ✅ CLI structure and commands
- ✅ WebSocket connection
- ✅ Heartbeat mechanism
- ⏳ Data import with real data
- ⏳ Query operations with real data
- ⏳ Timeline control with real data

## Repository

https://github.com/pillumina/msinsight-cli-harness

## Documentation

- `README.md` - Quick start guide
- `IMPLEMENTATION_ROADMAP.md` - Development roadmap
- `USER_INSTALLATION_GUIDE.md` - Installation guide
- `MSINSIGHT.md` - API documentation
- `examples/CONTROL_LAYER_GUIDE.md` - Usage examples

## Version

1.0.0

## License

Mulan PSL v2
