---
name: cli-anything-msinsight
description: Python API and CLI harness for controlling MindStudio Insight through AI agents - enables natural language control of performance analysis, timeline manipulation, and data queries
---

# MindStudio Insight CLI Harness

Python API and CLI harness for controlling MindStudio Insight performance analysis tool through AI agents.

## Architecture

```
User Natural Language
        ↓
    AI Agent
        ↓
  Skill (this file)
        ↓
 Python API / CLI
        ↓
 WebSocket Protocol
        ↓
 MindStudio Insight Backend
```

## Core Components

### 1. Protocol Layer
WebSocket client for backend communication:
- Connect to MindStudio Insight backend (port 9000)
- Send commands and receive responses
- Protocol analyzer for debugging

### 2. Control Layer
High-level control APIs:
- **TimelineController**: Timeline manipulation (zoom, pan, pin swimlanes, compare ranks)
- **DataQuery**: Data queries (operators, memory, communication, bottleneck analysis)

### 3. Data Import
Import profiling data:
- Single-rank and multi-rank data import
- Project management

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

### Python API (Recommended)

```python
from cli_anything.msinsight.protocol import MindStudioWebSocketClient
from cli_anything.msinsight.control import TimelineController, DataQuery
from cli_anything.msinsight.core.data_import import DataImporter

# 1. Connect to backend (close GUI first - single connection limit)
client = MindStudioWebSocketClient(port=9000)
client.connect()

# 2. Import data
importer = DataImporter(client)
importer.import_profiling_data(
    project_name="MyProject",
    data_path="/path/to/profiling/data",
    is_new_project=True
)

# 3. Query data
query = DataQuery(client)
top_operators = query.get_top_n_operators(n=10, metric="duration")
memory_summary = query.get_memory_summary()

# 4. Control timeline
timeline = TimelineController(client)
timeline.zoom_to_time(0, 1000, unit="ms")
timeline.pin_swimlanes(["rank 0", "rank 1"])
timeline.compare_ranks(["rank 0", "rank 1"])

# 5. Disconnect
client.disconnect()
```

### Key Methods

#### DataQuery
```python
# Operator queries
query.get_top_n_operators(n=10, metric="duration")
query.get_operator_by_id(operator_id="...")
query.get_operator_statistics()

# Memory queries
query.get_memory_summary()
query.get_memory_timeline()
query.get_memory_leaks()

# Communication queries
query.get_communication_matrix()
query.get_communication_hotspots(n=10)

# Analysis
query.get_bottleneck_analysis()
query.get_optimization_suggestions()
```

#### TimelineController
```python
# Navigation
timeline.zoom_to_time(start=0, end=1000, unit="ms")
timeline.go_to_operator(operator_id="...")
timeline.reset_zoom()

# Swimlane control
timeline.pin_swimlanes(lane_ids=["rank 0", "rank 1"])
timeline.unpin_all_swimlanes()
timeline.filter_swimlanes(filter_type="name", pattern="MatMul")

# Analysis
timeline.compare_ranks(rank_ids=["rank 0", "rank 1"])

# Query
timeline.get_visible_range()
timeline.get_swimlane_list()
```

#### DataImporter
```python
# Import data
importer.import_profiling_data(
    project_name="MyProject",
    data_path="/path/to/data",
    is_new_project=True
)

# Multi-rank
importer.import_multi_rank_data(
    project_name="MyProject",
    data_paths=["/path/to/rank0", "/path/to/rank1"]
)

# History
importer.get_import_history()
```

## Important Notes

### Single Connection Limit
⚠️ **Backend only allows ONE WebSocket connection**
- Close MindStudio Insight GUI before using CLI
- Cannot use CLI and GUI simultaneously

### Data Dependency
⚠️ **Most commands require data to be imported first**
- Import data using `DataImporter.import_profiling_data()`
- Then query and control operations will work

### Protocol Format
Request:
```json
{
  "id": 1,
  "type": "request",
  "moduleName": "timeline",
  "command": "zoomToRange",
  "params": {...}
}
```

Response:
```json
{
  "type": "response",
  "requestId": 1,
  "result": true,
  "body": {...}
}
```

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
1. **Always connect first**: `client.connect()`
2. **Import data before queries**: Most commands need data
3. **Handle connection errors**: Backend might not be running
4. **Close GUI**: Single connection limit
5. **Use context managers**: Automatic cleanup

### Example Agent Workflow

```
User: "帮我分析最慢的算子"

AI Agent:
1. Connect to backend
   client = MindStudioWebSocketClient(port=9000)
   client.connect()

2. Import data (if not already)
   importer = DataImporter(client)
   importer.import_profiling_data(...)

3. Query data
   query = DataQuery(client)
   top_ops = query.get_top_n_operators(n=10)

4. Return results to user
   "最慢的10个算子是：
    1. MatMul_123: 45.23 ms
    2. Conv2d_456: 32.10 ms
    ..."

5. Disconnect
   client.disconnect()
```

## Status

- ✅ **Protocol Layer**: Complete and verified
- ✅ **Control Layer**: Complete (API ready)
- ✅ **Data Import**: Complete
- ✅ **Connection**: Verified (WebSocket + heartbeat)
- ⏳ **Data Testing**: Needs real data validation

**Overall**: 95% complete, core functionality implemented

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
