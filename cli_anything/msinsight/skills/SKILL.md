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

# Get operator statistics (IMPORTANT: group must be specific values!)
cli-anything-msinsight --json operator statistics --group "Operator Type" --top-k -1

# Get operator details (IMPORTANT: need op_type OR op_name!)
cli-anything-msinsight --json operator details --group "Operator Type" --op-type MatMul
```

**⚠️ IMPORTANT: Operator Parameter Constraints**

1. **`group` parameter** - Must be one of these EXACT values:
   - `"Operator Type"` (recommended for statistics)
   - `"Input Shape"`
   - `"Communication Operator Type"`
   - ❌ NOT `"Operator"` (will cause parameter error)

2. **`top_k` parameter** - Must be **non-zero**:
   - Use `-1` to get all results (recommended)
   - Use `10`, `20`, etc. to limit results
   - ❌ NOT `0` (will cause parameter error)

3. **`op_type` or `op_name`** - Required for operator details:
   - Must provide at least one
   - Example: `--op-type MatMul` or `--op-name "Conv2d"`

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

## Parameter Requirements & Limitations

### Critical Parameter Constraints

#### Operator Module

**`operator statistics` and `operator details`**:
- `--group` must be one of:
  - `"Operator Type"` (default, recommended)
  - `"Input Shape"`
  - `"Communication Operator Type"`
  - ❌ NOT accepted: `"Operator"`, `"Communication Operator"`

- `--top-k` must be **non-zero** (use `-1` for all results)
  - ✅ Correct: `--top-k -1` (get all)
  - ✅ Correct: `--top-k 10` (top 10)
  - ❌ Wrong: `--top-k 0` (will fail with 1101 error)

**Example**:
```bash
# ✅ Correct usage
cli-anything-msinsight operator statistics --group "Operator Type" --top-k -1

# ❌ Wrong - will fail
cli-anything-msinsight operator statistics --group "Operator" --top-k 0
```

#### Summary Module

**`summary compute-details` and `summary communication-details`**:
- `--current-page` must be **> 0** (default: 1)
- `--page-size` must be **> 0** (default: 10)
- Requires profiling data with detailed breakdown (not available in all datasets)

**Example**:
```bash
# ✅ Correct usage
cli-anything-msinsight summary compute-details --current-page 1 --page-size 10

# ❌ Wrong - will fail
cli-anything-msinsight summary compute-details --current-page 0 --page-size 0
```

### Data Requirements

Some commands require specific profiling data types:

| Command Type | Required Data | Status Without Data |
|--------------|---------------|---------------------|
| **Communication** commands | HCCL communication ops | Timeout (needs cluster profiling) |
| **Memory static** commands | Static memory analysis | No data (needs static profiling) |
| **Summary compute-details** | Detailed compute breakdown | Query failed (needs detailed profiling) |
| **Summary comm-details** | Communication breakdown | Query failed (needs HCCL data) |

### Working Commands (9/17 = 53%)

**Fully Working** (no special data needed):
1. ✅ `summary statistics` - Overall performance
2. ✅ `summary top-n` - Top operators
3. ✅ `operator categories` - Operator breakdown
4. ✅ `operator statistics` - Detailed stats (with correct params)
5. ✅ `operator details` - Operator info (with correct params)
6. ✅ `operator compute-units` - Compute unit breakdown
7. ✅ `operator all-details` - All operators
8. ✅ `memory view` - Memory overview
9. ✅ `memory operator-size` - Memory size info

**Need Special Data**:
- Communication commands (4) - Need HCCL profiling
- Memory static commands (2) - Need static memory profiling
- Summary detail commands (2) - Need detailed breakdown data

## Troubleshooting

### Error Code 1101 (Parameter Error)

**Cause**: Invalid parameter value

**Common fixes**:
- Operator commands: Use `--group "Operator Type"` (not `"Operator"`)
- Operator commands: Use `--top-k -1` (not `0`)
- Summary commands: Use `--current-page 1 --page-size 10` (not 0)

### Error Code 3105/3106 (Query Failed)

**Cause**: Profiling data doesn't contain required information

**Solution**: Use more comprehensive profiling data with:
- HCCL communication operations (for communication analysis)
- Detailed compute breakdown (for summary details)
- Static memory analysis (for memory static commands)

### Timeout Errors

**Cause**: Command taking too long (>10s)

**Common causes**:
- No HCCL data available (communication commands)
- Large dataset without pagination

**Solution**: Ensure profiling data includes required information

## AI Agent Workflow

### Recommended Analysis Flow

```bash
# 1. Connect and check data
cli-anything-msinsight connect
cli-anything-msinsight --json summary statistics

# 2. Identify bottlenecks
cli-anything-msinsight --json operator categories --group "Operator Type"
cli-anything-msinsight --json summary top-n

# 3. Deep dive into operators
cli-anything-msinsight --json operator statistics --group "Operator Type" --top-k -1
cli-anything-msinsight --json operator details --op-type MatMul

# 4. Check memory usage
cli-anything-msinsight --json memory view
cli-anything-msinsight --json memory operator-size

# 5. Communication analysis (if cluster data available)
cli-anything-msinsight --json comm iterations
cli-anything-msinsight --json comm bandwidth
```

### JSON Output for AI Parsing

Always use `--json` flag for AI agent consumption:

```bash
cli-anything-msinsight --json summary statistics
cli-anything-msinsight --json operator categories --group "Operator Type"
```

This ensures structured output that's easy to parse programmatically.

## Version

**Current Version**: 2.0.0
**Status**: Production Ready for Core Features
**Success Rate**: 53% (9/17 commands) - Limited by test data availability
**Zero Parameter Errors**: All parameter issues resolved

