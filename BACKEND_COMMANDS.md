# MindStudio Insight Backend Command Reference

**Status**: Research in progress - Mapping backend handlers to CLI commands

## Overview

MindStudio Insight backend has **115+ handlers** implementing specific query commands.
The CLI Control Layer API was designed independently and **does not match** backend actual commands.

## Backend Command Categories

### 1. Timeline Module
**Import/Parse**:
- `import/action` - Import profiling data
- `parse/cards` - Parse analysis cards

**Timeline Queries**:
- `operator/names` - Get operator names list
- `duration/list` - Get duration data
- `thread/traces` - Query thread traces
- `thread/detail` - Get thread details
- `flow/category/list` - List flow categories
- `flow/category/events` - Get flow events
- `search/slice` - Search timeline slices
- `search/allSlices` - Search all slices
- `group` - Timeline grouping

### 2. Memory Module
**Memory Analysis**:
- `mem/scope/allocation` - Memory scope allocation
- `mem/scope/block` - Memory block data
- `mem/scope/event` - Memory events
- `mem/snapshot/allocation` - Memory snapshot
- `mem/snapshot/block` - Snapshot blocks
- `details/memory/graph` - Memory graph
- `details/memory/table` - Memory table

### 3. Operator Module
**Operator Analysis**:
- `kernel/detail` - Kernel details
- `op/detail/info` - Operator details
- `op/statistic/info` - Operator statistics
- `op/category/info` - Operator categories
- `communication/kernel` - Communication kernel info

### 4. Communication Module
**Communication Analysis**:
- `communication/matrix/list` - Communication matrix
- `communication/matrix/sortOpNames` - Sorted operator names
- `communication/operator/details` - Communication details
- `communication/operator/lists` - Communication lists

### 5. Global Module
**Project Management**:
- `heartCheck` - Heartbeat
- `moduleConfig/get` - Get module config
- `files/getProjectExplorer` - Get project list
- `project/explorer/info` - Project info
- `project/valid` - Validate project

## Command Format

Backend commands follow this format:
```json
{
  "id": 1,
  "type": "request",
  "moduleName": "timeline|memory|operator|communication|global",
  "command": "operator/names",
  "fileId": "",
  "projectName": "MyProject",
  "params": {
    // Command-specific parameters
  }
}
```

## CLI Implementation Status

### ✅ Working (Protocol Layer)
- WebSocket connection
- Request/Response format
- Heartbeat
- Basic queries (`heartCheck`, `moduleConfig/get`, `files/getProjectExplorer`)

### ⏳ Not Implemented (Control Layer Mismatch)
The following were designed but **do not exist in backend**:
- `getTopNOperators` → Should use `op/statistic/info`
- `getMemorySummary` → Should use `mem/scope/*` commands
- `zoomToRange` → Backend has no direct timeline zoom command
- `getSwimlaneList` → Should use `thread/traces` or similar

### 🔄 Needs Reimplementation
**Control Layer API must be redesigned** to map to actual backend commands:

**TimelineController**:
- ~~`zoomToTime()`~~ - Not supported directly
- `getThreadTraces()` - Map to `thread/traces`
- `searchSlices()` - Map to `search/slice`
- `getOperatorNames()` - Map to `operator/names`

**DataQuery**:
- ~~`getTopNOperators()`~~ - Use `op/statistic/info` with filters
- ~~`getMemorySummary()`~~ - Use `mem/scope/*` commands
- `getCommunicationMatrix()` - Map to `communication/matrix/list`
- `getKernelDetails()` - Map to `kernel/detail`

## Next Steps

1. **Map each backend command** to CLI Control Layer API
2. **Document parameters** for each command (requires backend team input)
3. **Implement Control Layer** with actual commands
4. **Test with real data** to verify functionality
5. **Update SKILL.md** with actual capabilities

## References

- Backend source: `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/*/handler/*.cpp`
- Protocol definitions: `/*/protocol/*Protocol.cpp`
- Handler count: 115+ handlers across 6 modules
