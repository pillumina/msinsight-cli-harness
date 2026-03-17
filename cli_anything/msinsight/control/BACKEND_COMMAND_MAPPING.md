# Backend Command Mapping

**Purpose**: Map CLI Control Layer methods to actual backend WebSocket commands

**Generated**: 2026-03-17
**Source**: `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/defs/ProtocolDefs.h`

## Command Categories

### 1. Data Import (Priority: CRITICAL)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `import_data()` | `import/action` | timeline | Import profiling data |
| `get_import_cards()` | `parse/cards` | timeline | Get parsed analysis cards |

### 2. Summary Analysis (Priority: HIGH)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `get_top_n_data()` | `summary/queryTopData` | summary | Get top N performance data |
| `get_statistics()` | `summary/statistic` | summary | Get performance statistics |
| `get_compute_details()` | `summary/queryComputeDetail` | summary | Get compute details |
| `get_communication_details()` | `summary/queryCommunicationDetail` | summary | Get communication details |
| `get_model_info()` | `summary/queryModelInfo` | summary | Get model information |
| `get_expert_hotspot()` | `summary/queryExpertHotspot` | summary | Get expert hotspot analysis |
| `import_expert_data()` | `summary/importExpertData` | summary | Import expert analysis data |

### 3. Operator Analysis (Priority: HIGH)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `get_operator_category()` | `operator/category` | operator | Get operator categories |
| `get_operator_statistic()` | `operator/statistic` | operator | Get operator statistics |
| `get_operator_details()` | `operator/details` | operator | Get operator details |
| `get_operator_more_info()` | `operator/more_info` | operator | Get additional operator info |
| `export_operator_details()` | `operator/exportDetails` | operator | Export operator details |

### 4. Memory Analysis (Priority: MEDIUM)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `get_memory_view()` | `Memory/view/memoryUsage` | memory | Get memory usage view |
| `get_memory_type()` | `Memory/view/type` | memory | Get memory type info |
| `get_memory_operator()` | `Memory/view/operator` | memory | Get memory operator info |
| `get_memory_component()` | `Memory/view/component` | memory | Get memory component info |
| `get_memory_operator_size()` | `Memory/view/operatorSize` | memory | Get operator memory size |
| `find_memory_slice()` | `Memory/find/slice` | memory | Find memory slice |

### 5. Communication Analysis (Priority: MEDIUM)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `get_communication_matrix_group()` | `communication/matrix/group` | communication | Get communication matrix group |
| `get_communication_bandwidth()` | `communication/bandwidth` | communication | Get communication bandwidth |
| `get_communication_operator_details()` | `communication/operatorDetails` | communication | Get operator communication details |
| `get_communication_operator_lists()` | `communication/operatorLists` | communication | Get operator communication lists |

### 6. Timeline Navigation (Priority: LOW)

| CLI Method | Backend Command | Module | Description |
|------------|----------------|--------|-------------|
| `get_unit_threads()` | `unit/threads` | timeline | Get thread information |
| `get_unit_flows()` | `unit/flows` | timeline | Get flow information |
| `get_unit_system_view()` | `unit/systemView` | timeline | Get system view |
| `search_slice()` | `search/slice` | timeline | Search timeline slice |
| `search_all_slices()` | `search/all/slices` | timeline | Search all slices |

## Implementation Priority

### Phase 1: Core Commands (Day 1-2)
- Data import (`import/action`)
- Summary statistics (`summary/statistic`)
- Operator analysis (`operator/*`)

### Phase 2: Analysis Commands (Day 3-4)
- Memory analysis (`Memory/view/*`)
- Communication analysis (`communication/*`)

### Phase 3: Advanced Commands (Day 5)
- Timeline navigation (`unit/*`, `search/*`)
- Expert analysis (`advisor/*`, `expertAnalysis/*`)

## Request Format

All commands follow this JSON format:

```json
{
  "id": <unique_id>,
  "type": "request",
  "moduleName": "<module>",
  "command": "<command>",
  "fileId": "",
  "projectName": "<project>",
  "params": {
    // Command-specific parameters
  }
}
```

## Response Format

```json
{
  "type": "response",
  "requestId": <id>,
  "result": true/false,
  "command": "<command>",
  "moduleName": "<module>",
  "error": {  // Optional, only if result=false
    "code": <error_code>,
    "message": "<error_message>"
  },
  "body": {
    // Response data
  }
}
```

## Next Steps

1. Analyze Request parameter structures from Protocol files
2. Implement Python methods for each command
3. Create test cases for each command
4. Update SKILL.md with actual capabilities
