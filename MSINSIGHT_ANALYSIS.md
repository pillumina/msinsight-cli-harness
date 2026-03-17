# MindStudio Insight (msinsight) - Codebase Analysis

## Overview

**MindStudio Insight** is a visual performance tuning tool for Ascend AI applications. It's a web-based GUI application with a C++ backend server and TypeScript frontend modules.

## Architecture

### Backend Engine
- **Language**: C++ 17
- **Server Type**: WebSocket Server (WsServer)
- **Protocol**: Custom binary protocol with JSON payloads
- **Build System**: CMake
- **Entry Point**: `server/src/entry/server/bin/main.cpp`

### Frontend
- **Language**: TypeScript/JavaScript
- **Framework**: Custom modular architecture
- **Build**: npm/pnpm
- **Modules**: cluster, compute, memory, operator, timeline, leaks, statistic, reinforcement-learning

## Data Model

### Supported File Formats

1. **Database Files (.db)**
   - SQLite databases containing profiling data
   - Used for system tuning, service optimization

2. **JSON Files**
   - `profiler_metadata.json` - metadata and parallel strategy info
   - `communication_group.json` - communication group configuration
   - `cluster_communication_matrix.json` - communication matrix data
   - `cluster_communication.json` - communication time data
   - Various configuration files

3. **CSV Files**
   - `cluster_step_trace_time.csv` - step trace timing data
   - `kernel_details.csv` - kernel execution details

4. **Binary Files (.bin)**
   - Profiling binary data
   - Operator performance data

### Project State Representation
- No traditional project file format
- State managed through WebSocket session
- Data loaded from profiling output directories
- Session-based analysis workflow

## Existing CLI Interface

### Server CLI Parameters
The backend server accepts the following command-line arguments:

```bash
msinsight-server \
  --wsPort=<port>          # WebSocket port (9000-9100)
  --wsHost=<ip>            # WebSocket host (default: 127.0.0.1)
  --logPath=<path>         # Log file directory
  --logSize=<bytes>        # Max log file size
  --logLevel=<level>       # Log level (INFO, DEBUG, etc.)
  --eventDir=<path>        # Event directory
  --scanPort=<port>        # Scan for available ports
```

### Example Usage
```bash
# Start server on default port
./msinsight-server --wsPort=9000

# Start with custom configuration
./msinsight-server --wsPort=9001 --wsHost=0.0.0.0 --logPath=/var/log/msinsight
```

## Backend Modules (API Domains)

### 1. **Source Module** (`server/src/modules/source/`)
- File loading and parsing
- Data import from profiling directories
- Format detection and validation

### 2. **Timeline Module** (`server/src/modules/timeline/`)
- Timeline visualization data
- Event processing and filtering
- Time-series analysis

### 3. **Summary Module** (`server/src/modules/summary/`)
- Overview statistics
- Performance summaries
- Aggregate metrics

### 4. **Communication Module** (`server/src/modules/communication/`)
- Cluster communication analysis
- Network performance metrics
- Inter-node communication patterns

### 5. **Memory Module** (`server/src/modules/memory/`)
- Memory allocation tracking
- Memory leak detection
- Memory usage patterns

### 6. **Memscope Module** (`server/src/modules/memscope/`)
- Detailed memory analysis
- Memory lifecycle tracking

### 7. **Operator Module** (`server/src/modules/operator/`)
- Operator performance analysis
- Kernel execution details
- Compute optimization

### 8. **RL Module** (`server/src/modules/rl/`)
- Reinforcement learning performance
- Training step analysis

### 9. **Servitization Module** (`server/src/modules/servitization/`)
- Service deployment analysis
- Inference performance

### 10. **Advisor Module** (`server/src/modules/advisor/`)
- Performance recommendations
- Optimization suggestions

### 11. **Triton Module** (`server/src/modules/triton/`)
- Triton inference server integration

## GUI Actions to API Mapping

| GUI Action | WebSocket Request | Backend Handler |
|------------|-------------------|-----------------|
| Load profiling data | File selection dialog | SourceModule::LoadFile |
| View timeline | Timeline render request | TimelineModule::GetTimelineData |
| Analyze memory | Memory analysis request | MemoryModule::GetMemoryData |
| Check communication | Communication query | CommunicationModule::GetCommData |
| Export report | Export request | Various modules + export handlers |
| Filter operators | Filter request | OperatorModule::FilterOperators |
| Zoom timeline | Zoom request | TimelineModule::ZoomRange |

## Communication Protocol

### WebSocket Protocol
- **Transport**: WebSocket (ws://)
- **Message Format**: Binary protocol with JSON payloads
- **Request/Response Pattern**: Asynchronous message handling
- **Protocol Classes**: `ProtocolMessage`, `ProtocolMessageBuffer`

### Message Flow
1. Client sends request via WebSocket
2. Server routes to appropriate module handler
3. Handler processes request
4. Server sends response via WebSocket
5. Client renders results in GUI

## Data Processing Pipeline

1. **Data Ingestion**
   - User selects profiling directory
   - SourceModule detects file formats
   - Parsers convert to internal format

2. **Data Storage**
   - SQLite database for structured data
   - In-memory cache for frequently accessed data
   - Temporary files for large datasets

3. **Analysis**
   - Module-specific analysis algorithms
   - Statistical computations
   - Performance metric calculations

4. **Visualization**
   - Frontend requests visualization data
   - Backend prepares chart/trace data
   - WebSocket streams results

## Key Technologies

### Backend Dependencies
- C++ STL
- WebSocket library
- SQLite
- JSON parser (rapidjson or similar)
- Logging framework

### Frontend Dependencies
- TypeScript/JavaScript
- npm/pnpm package manager
- Chart visualization libraries
- WebSocket client

## System Requirements

### From README
- **Platforms**: Windows, Linux, macOS
- **Hardware**: Ascend AI processors (for data collection)
- **CANN Version**: 8.5.0 and earlier
- **File Size Limits**:
  - JSON: up to 20GB
  - Binary: up to 20GB
  - DB: up to 20GB (system tuning), 10GB (service)
  - CSV: up to 2GB

## Identified CLI Opportunities

### Missing CLI Capabilities
1. **No headless operation mode** - requires GUI/web interface
2. **No batch processing** - can't process multiple files automatically
3. **No scriptable export** - can't export reports via command line
4. **No automation support** - AI agents cannot use the tool

### Potential CLI Command Groups
1. **Project Management**: create, open, info, close
2. **Data Import**: load-profiling, import-db, validate
3. **Analysis**: analyze-system, analyze-operator, analyze-memory, analyze-communication
4. **Export**: export-report, export-timeline, export-metrics
5. **Query**: query-operators, query-memory, query-communication
6. **Session**: status, history, undo, redo

## Command/Undo System

- No explicit undo/redo system identified in backend
- State managed through WebSocket session
- Operations are primarily read-only (analysis)
- No mutation of source profiling data

## Summary

MindStudio Insight is a sophisticated performance analysis tool with:
- **Backend**: C++ WebSocket server with modular architecture
- **Frontend**: TypeScript web application
- **Data**: Profiling files (DB, JSON, CSV, BIN)
- **API**: WebSocket-based request/response protocol
- **Current CLI**: Limited to server startup parameters

The tool lacks a comprehensive CLI for:
- Headless operation
- Batch processing
- Automated analysis
- Report generation
- AI agent integration

This presents an opportunity to build a CLI harness that wraps the backend server and provides command-line access to all analysis capabilities.
