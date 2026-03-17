---
name: cli-anything-msinsight
description: CLI tool for analyzing MindStudio Insight performance data. Supports performance statistics, operator analysis, memory analysis, and communication analysis through WebSocket connection to MindStudio Insight backend.
---

# MindStudio Insight CLI

CLI tool for analyzing MindStudio Insight profiling data through command-line interface.

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
 MindStudio Insight Backend (port 9000)
```

## Installation

```bash
# Clone and install
git clone git@github.com:pillumina/msinsight-cli-harness.git
cd msinsight-cli-harness
pip install -e .
```

**Prerequisites**:
- Python 3.10+
- MindStudio Insight running (backend on port 9000)
- Profiling data imported

## Usage for AI Agents

### Quick Start

```bash
# 1. Start backend (MindStudio Insight must be running on port 9000)
# Close GUI first - only ONE WebSocket connection allowed

# 2. Run CLI
cli-anything-msinsight

# 3. Connect to backend
msinsight> connect --port 9000

# 4. Use commands
msinsight> summary statistics
msinsight> operator categories
msinsight> memory view
```

### Core Commands

#### Connection Management

```bash
# Connect to backend
cli-anything-msinsight connect --port 9000

# Disconnect
cli-anything-msinsight disconnect

# Or in REPL mode:
msinsight> connect
msinsight> disconnect
```

#### Summary Analysis

```bash
# Get performance statistics (most commonly used)
cli-anything-msinsight --json summary statistics

# Get top N performance data
cli-anything-msinsight --json summary top-n

# With options
cli-anything-msinsight summary statistics --time-flag step --cluster-path /
```

#### Operator Analysis

```bash
# Get operator categories
cli-anything-msinsight --json operator categories

# Get operator statistics (paginated)
cli-anything-msinsight --json operator statistics --page 1 --page-size 10

# Get operator details
cli-anything-msinsight --json operator details --op-type MatMul
```

#### Memory Analysis

```bash
# Get memory view by type
cli-anything-msinsight --json memory view --view-type type

# Get operator memory size
cli-anything-msinsight --json memory operator-size --view-type Overall
```

#### Communication Analysis

```bash
# Get communication iterations
cli-anything-msinsight --json communication iterations

# Get bandwidth for specific operator
cli-anything-msinsight --json communication bandwidth --operator-name "hccl_broadcast"
```

### CLI Options

- `--json` - Output in JSON format (recommended for AI agents)
- `--port` - Backend port (default: 9000)
- `--help` - Show command help

### Available Commands

#### Connection
- `connect` - Connect to backend
- `disconnect` - Disconnect from backend

#### Summary
- `summary statistics` - Performance statistics
- `summary top-n` - Top N performance data

#### Operator
- `operator categories` - Operator categories
- `operator statistics` - Operator statistics
- `operator details` - Operator details

#### Memory
- `memory view` - Memory view
- `memory operator-size` - Operator memory size

#### Communication
- `communication iterations` - Communication iterations
- `communication bandwidth` - Bandwidth information

### AI Agent Workflow Example

```
User: "帮我分析性能瓶颈" (Help me analyze performance bottlenecks)

AI Agent:
1. Check if backend is running
   $ lsof -i :9000

2. Connect and get statistics
   $ cli-anything-msinsight --json summary statistics

3. Parse JSON and identify bottlenecks
   {
     "compute_time": 1234.5,
     "communication_time": 567.8,
     "total_time": 1802.3
   }

4. Get operator breakdown
   $ cli-anything-msinsight --json operator statistics --page 1 --page-size 5

5. Report findings
   "分析结果：
   - 计算时间占比: 68.5%
   - 通信时间占比: 31.5%
   - Top 3 慢算子:
     1. MatMul: 450.2 ms
     2. Conv2D: 320.8 ms
     3. LayerNorm: 180.5 ms
   建议: 优化 MatMul 和 Conv2D 算子"
```

## Important Notes

### Single Connection Limit
⚠️ **Backend only allows ONE WebSocket connection**
- Close MindStudio Insight GUI before using CLI
- Cannot use CLI and GUI simultaneously

### Data Dependency
⚠️ **Most commands require profiling data to be imported first**
- Import data using MindStudio Insight GUI
- Or use backend import API (advanced)

### Backend State
⚠️ **Backend must be running on port 9000**
- Start MindStudio Insight to launch backend
- Close GUI but keep backend process running

## When to Use This Skill

Use this skill when users want to:
- Analyze MindStudio Insight profiling data programmatically
- Get performance statistics and bottlenecks
- Query operator/memory/communication metrics
- Automate performance analysis
- Compare performance across runs

## Best Practices for AI Agents

1. **Always use --json flag** for structured output
2. **Check connection first** with `connect` command
3. **Handle errors gracefully** - backend may not have all data types
4. **Use pagination** for large datasets (--page, --page-size)
5. **Cache connection** - don't reconnect for every command

## Common Issues

### "Not connected to backend"
**Solution**: Run `connect` command first

### "No rank ID available"
**Solution**: Ensure profiling data is imported in backend

### "Request parameter exception"
**Solution**: Check required parameters (use --help)

### "No data available"
**Solution**: Some commands require specific data types (HCCL, static memory, etc.)

## Implementation Status

### ✅ Implemented & Working
- **Summary Module**: statistics, top-n data
- **Operator Module**: categories, statistics, details
- **Memory Module (dynamic)**: view, operator-size
- **Connection**: connect, disconnect

### ⚠️ Requires Specific Data
- **Memory (static)**: Requires static memory profiling data
- **Communication**: Requires HCCL communication operations

## Technical Details

### Backend Protocol
- WebSocket on port 9000
- JSON message format
- Automatic rank discovery

### Command Structure
```
cli-anything-msinsight [OPTIONS] COMMAND [ARGS]...

Commands:
  connect         Connect to backend
  disconnect      Disconnect
  summary         Summary analysis
  operator        Operator analysis
  memory          Memory analysis
  communication   Communication analysis
```

### Output Formats
- **JSON** (`--json` flag): Structured data for AI agents
- **Table** (default): Human-readable format

## Repository

https://github.com/pillumina/msinsight-cli-harness

## Version

2.0.0 - With real backend integration via api_v2.py

## License

Mulan PSL v2
