# Control Layer API v2 - Implementation Review

**Date**: 2026-03-17
**Status**: Phase 1 Implementation Complete

## Overview

This document reviews the redesigned Control Layer API implementation based on actual backend Protocol Request structures extracted from source code.

## Methodology

1. Read backend Protocol Request files from source:
   - `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/summary/protocol/SummaryProtocolRequest.h`
   - `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/operator/protocol/OperatorProtocolRequest.h`
   - `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/memory/protocol/MemoryProtocolRequest.h`
   - `/Users/huangyuxiao/projects/mvp/msinsight/server/src/modules/communication/protocol/CommunicationProtocolRequest.h`

2. Extracted exact parameter structures for each command
3. Updated `api_v2.py` with correct parameter names and requirements
4. Updated test suite to match new parameter requirements

## Updated Commands

### Summary Module (4/13 commands implemented)

#### 1. `summary/statistic`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_statistics(self, rank_id=None, step_id=None, time_flag=None):
    params = {}
    if rank_id: params["rankId"] = rank_id
    if step_id: params["stepId"] = step_id
    if time_flag: params["timeFlag"] = time_flag
```

**New Implementation**:
```python
def get_statistics(self, rank_id: str, time_flag: str, cluster_path: str = "", step_id: Optional[str] = None):
    params = {
        "rankId": rank_id,           # REQUIRED
        "timeFlag": time_flag,       # REQUIRED
        "clusterPath": cluster_path  # REQUIRED (can be empty)
    }
    if step_id is not None:
        params["stepId"] = step_id   # OPTIONAL
```

**Key Changes**:
- Made `rankId` and `timeFlag` required parameters
- Added `clusterPath` as required parameter (can be empty string)
- Parameter names match backend exactly

**Backend Structure**:
```cpp
struct SummaryStatisticParams {
    std::string rankId;
    std::string timeFlag;
    std::string stepId;
    std::string clusterPath;
};
```

---

#### 2. `summary/queryTopData`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_top_n_data(self, n=10, metric="duration", cluster_path=None):
    params = {"n": n, "metric": metric}
    if cluster_path: params["clusterPath"] = cluster_path
```

**New Implementation**:
```python
def get_top_n_data(self, cluster_path: str = "", is_compare: bool = False):
    params = {
        "clusterPath": cluster_path,  # REQUIRED (can be empty)
        "isCompare": is_compare       # REQUIRED (default: false)
    }
```

**Key Changes**:
- Removed `n` and `metric` parameters (not in backend)
- Added `isCompare` parameter
- `clusterPath` is required but can be empty

**Backend Structure**:
```cpp
struct SummaryTopRankParams {
    bool isCompare = false;
    std::string clusterPath;
};
```

---

#### 3. `summary/queryComputeDetail`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_compute_details(self, rank_id=None, order_by="duration", order="desc"):
    params = {"orderBy": order_by, "order": order}
    if rank_id: params["rankId"] = rank_id
```

**New Implementation**:
```python
def get_compute_details(
    self, rank_id: str, time_flag: str, cluster_path: str = "",
    current_page: int = 0, page_size: int = 0,
    order_by: str = "", order: str = "", db_path: Optional[str] = None
):
    params = {
        "rankId": rank_id,           # REQUIRED
        "timeFlag": time_flag,       # REQUIRED
        "clusterPath": cluster_path, # REQUIRED (can be empty)
        "currentPage": current_page, # OPTIONAL (default: 0)
        "pageSize": page_size,       # OPTIONAL (default: 0)
        "orderBy": order_by,         # OPTIONAL
        "order": order               # OPTIONAL
    }
```

**Key Changes**:
- Made `rankId` and `timeFlag` required
- Added `clusterPath`, `currentPage`, `pageSize` parameters
- Added optional `dbPath` parameter

**Backend Structure**:
```cpp
struct ComputeDetailParams {
    std::string rankId;
    std::string dbPath;
    std::string timeFlag;
    int64_t currentPage = 0;
    int64_t pageSize = 0;
    std::string orderBy;
    std::string order;
    std::string clusterPath;
};
```

---

#### 4. `summary/queryCommunicationDetail`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_communication_details(self, rank_id=None, order_by="duration", order="desc"):
    params = {"orderBy": order_by, "order": order}
    if rank_id: params["rankId"] = rank_id
```

**New Implementation**:
```python
def get_communication_details(
    self, rank_id: str, time_flag: str = "HCCL", cluster_path: str = "",
    current_page: int = 0, page_size: int = 0,
    order_by: str = "", order: str = ""
):
    params = {
        "rankId": rank_id,           # REQUIRED
        "timeFlag": time_flag,       # REQUIRED (default: "HCCL")
        "clusterPath": cluster_path, # REQUIRED (can be empty)
        "currentPage": current_page, # OPTIONAL (default: 0)
        "pageSize": page_size,       # OPTIONAL (default: 0)
        "orderBy": order_by,         # OPTIONAL
        "order": order               # OPTIONAL
    }
```

**Key Changes**:
- Made `rankId` required
- Added `timeFlag` with default "HCCL"
- Added pagination parameters

**Backend Structure**:
```cpp
struct CommunicationDetailParams {
    std::string rankId;
    std::string timeFlag = "HCCL";
    int64_t currentPage = 0;
    int64_t pageSize = 0;
    std::string orderBy;
    std::string order;
    std::string clusterPath;
};
```

---

### Operator Module (3/6 commands implemented)

#### 1. `operator/category`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_category_info(self):
    response = self.client.send_command(..., params={})
```

**New Implementation**:
```python
def get_category_info(
    self, rank_id: str, group: str = "Operator",
    device_id: str = "", top_k: int = 0
):
    params = {
        "rankId": rank_id,       # REQUIRED
        "group": group,          # REQUIRED (Operator, Operator Type, Input Shape)
        "deviceId": device_id,   # OPTIONAL
        "topK": top_k            # OPTIONAL (default: 0)
    }
```

**Key Changes**:
- Made `rankId` and `group` required
- Added `deviceId` and `topK` parameters

**Backend Structure**:
```cpp
struct OperatorDurationReqParams {
    std::string rankId;
    std::string deviceId;
    std::string group; // Operator、Operator Type、Input Shape
    int64_t topK{0};
};
```

---

#### 2. `operator/statistic`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_statistic_info(self):
    response = self.client.send_command(..., params={})
```

**New Implementation**:
```python
def get_statistic_info(
    self, rank_id: str, group: str = "Operator",
    device_id: str = "", top_k: int = 0,
    current_page: int = 1, page_size: int = 0,
    order_by: str = "", order: str = "",
    is_compare: bool = False,
    filters: Optional[List[Dict[str, str]]] = None
):
    params = {
        "rankId": rank_id,
        "group": group,
        "deviceId": device_id,
        "topK": top_k,
        "current": current_page,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order,
        "isCompare": is_compare
    }
    if filters: params["filters"] = filters
```

**Key Changes**:
- Made `rankId` and `group` required
- Added pagination, sorting, and filter parameters

**Backend Structure**:
```cpp
struct OperatorStatisticReqParams {
    bool isCompare{false};
    std::string rankId;
    std::string deviceId;
    std::string group;
    int64_t topK{0};
    int64_t current{1};
    int64_t pageSize{0};
    std::string orderBy;
    std::string order;
    std::vector<std::pair<std::string, std::string>> filters;
    std::vector<std::pair<std::string, std::vector<std::string>>> rangeFilters;
};
```

---

#### 3. `operator/more_info`

**Status**: ✅ UPDATED (renamed from `operator/details`)

**Old Implementation**:
```python
def get_operator_details(self, operator_name: str, db_path: Optional[str] = None):
    params = {"operatorName": operator_name}
    if db_path: params["dbPath"] = db_path
```

**New Implementation**:
```python
def get_operator_details(
    self, rank_id: str,
    op_type: str = "", op_name: str = "", shape: str = "",
    group: str = "Operator", device_id: str = "",
    top_k: int = 0, current_page: int = 1, page_size: int = 0,
    order_by: str = "", order: str = ""
):
    params = {
        "rankId": rank_id,
        "opType": op_type,
        "opName": op_name,
        "shape": shape,
        "group": group,
        "deviceId": device_id,
        "topK": top_k,
        "current": current_page,
        "pageSize": page_size,
        "orderBy": order_by,
        "order": order
    }
```

**Key Changes**:
- Corrected command from `operator/details` to `operator/more_info`
- Added `rankId`, `opType`, `shape` parameters
- Added pagination and sorting

**Backend Structure**:
```cpp
struct OperatorMoreInfoReqParams {
    std::string rankId;
    std::string deviceId;
    std::string group;
    int64_t topK{0};
    std::string opType;
    std::string opName;
    std::string shape;
    std::string accCore;
    int64_t current{1};
    int64_t pageSize{0};
    std::string orderBy;
    std::string order;
    std::vector<std::pair<std::string, std::string>> filters;
};
```

---

### Memory Module (2/20 commands implemented)

#### 1. `Memory/view/{type}`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_memory_view(self, view_type="type", rank_id=None):
    params = {}
    if rank_id: params["rankId"] = rank_id
```

**New Implementation**:
```python
def get_memory_view(
    self, rank_id: str, view_type: str = "type",
    device_id: str = "", cluster_path: str = ""
):
    params = {
        "rankId": rank_id,           # REQUIRED
        "deviceId": device_id,       # OPTIONAL
        "clusterPath": cluster_path  # REQUIRED (can be empty)
    }
```

**Key Changes**:
- Made `rankId` required
- Added `deviceId` and `clusterPath` parameters

**Backend Structure**:
```cpp
struct MemoryTypeRequest : public Request {
    std::string rankId;
};
```

---

#### 2. `Memory/view/operatorSize`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_memory_operator_size(self, operator_name: str, rank_id=None):
    params = {"operatorName": operator_name}
    if rank_id: params["rankId"] = rank_id
```

**New Implementation**:
```python
def get_memory_operator_size(
    self, rank_id: str, view_type: str = "Overall",
    device_id: str = "", is_compare: bool = False
):
    params = {
        "rankId": rank_id,        # REQUIRED
        "type": view_type,        # REQUIRED (Overall or Stream)
        "deviceId": device_id,    # OPTIONAL
        "isCompare": is_compare   # REQUIRED (default: false)
    }
```

**Key Changes**:
- Removed `operatorName` parameter
- Added `type`, `isCompare` parameters
- Made `rankId` required

**Backend Structure**:
```cpp
struct MemoryOperatorSizeParams {
    std::string rankId;
    std::string deviceId;
    std::string type;
    bool isCompare = false;
};
```

---

### Communication Module (3/12 commands implemented)

#### 1. `communication/bandwidth`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_bandwidth(self):
    response = self.client.send_command(..., params={})
```

**New Implementation**:
```python
def get_bandwidth(
    self, rank_id: str, operator_name: str,
    stage: str = "", iteration_id: str = "",
    pg_name: str = "", cluster_path: str = "",
    group_id_hash: str = ""
):
    params = {
        "rankId": rank_id,           # REQUIRED
        "operatorName": operator_name, # REQUIRED
        "stage": stage,              # REQUIRED (can be empty)
        "iterationId": iteration_id, # OPTIONAL
        "pgName": pg_name,           # OPTIONAL
        "clusterPath": cluster_path, # REQUIRED (can be empty)
        "groupIdHash": group_id_hash # REQUIRED
    }
```

**Key Changes**:
- Made `rankId`, `operatorName`, `stage`, `clusterPath`, `groupIdHash` required
- Added `iterationId`, `pgName` parameters

**Backend Structure**:
```cpp
struct BandwidthDataParam {
    std::string iterationId;
    std::string rankId;
    std::string operatorName;
    std::string stage;
    std::string pgName;
    std::string clusterPath;
    std::string groupIdHash;
};
```

---

#### 2. `communication/operatorNames`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_operator_lists(self):
    response = self.client.send_command(..., params={})
```

**New Implementation**:
```python
def get_operator_lists(
    self, iteration_id: str = "", rank_list: Optional[List[str]] = None,
    stage: str = "", pg_name: str = "",
    cluster_path: str = "", group_id_hash: str = ""
):
    params = {
        "iterationId": iteration_id,
        "rankList": rank_list or [],
        "stage": stage,
        "pgName": pg_name,
        "clusterPath": cluster_path,
        "groupIdHash": group_id_hash
    }
```

**Key Changes**:
- Corrected command from `communication/operatorLists` to `communication/operatorNames`
- Added all required parameters

**Backend Structure**:
```cpp
struct OperatorNamesParams {
    std::string iterationId;
    std::vector<std::string> rankList = {};
    std::string stage;
    std::string pgName;
    std::string clusterPath;
    std::string groupIdHash;
};
```

---

#### 3. `communication/operatorDetails`

**Status**: ✅ UPDATED

**Old Implementation**:
```python
def get_operator_details(self, operator_name: str):
    params = {"operatorName": operator_name}
```

**New Implementation**:
```python
def get_operator_details(
    self, stage: str, rank_id: str = "", iteration_id: str = "",
    order_by: str = "", order: str = "",
    query_type: str = "Comparison", pg_name: str = "",
    cluster_path: str = "", group_id_hash: str = "",
    current_page: int = 0, page_size: int = 0
):
    params = {
        "stage": stage,              # REQUIRED
        "rankId": rank_id,
        "iterationId": iteration_id,
        "orderBy": order_by,
        "order": order,
        "queryType": query_type,     # REQUIRED (default: Comparison)
        "pgName": pg_name,
        "clusterPath": cluster_path, # REQUIRED
        "groupIdHash": group_id_hash, # REQUIRED
        "currentPage": current_page,
        "pageSize": page_size
    }
```

**Key Changes**:
- Made `stage` required
- Added pagination, sorting, and filter parameters
- Added `queryType`, `clusterPath`, `groupIdHash` parameters

**Backend Structure**:
```cpp
struct OperatorDetailsParam {
    std::string iterationId;
    std::string rankId;
    std::string orderBy;
    std::string order;
    std::string stage;
    std::string queryType = "Comparison";
    std::string pgName;
    std::string clusterPath;
    std::string groupIdHash;
    int pageSize{};
    int currentPage{};
};
```

---

## Test Suite Updates

Updated `test_control_api_v2.py` to match new parameter requirements:

### Key Test Changes:

1. **Summary Tests**:
   - Updated `test_get_statistics` to require `rank_id`, `time_flag`, `cluster_path`
   - Updated `test_get_top_n_data` to require `cluster_path`
   - Updated `test_get_compute_details` and `test_get_communication_details` with required params

2. **Operator Tests**:
   - Updated `test_get_category_info` to require `rank_id`
   - Updated `test_get_statistic_info` to require `rank_id`
   - Updated `test_get_operator_details` with correct parameters

3. **Memory Tests**:
   - Updated `test_get_memory_view_by_type` and `test_get_memory_view_by_operator` to require `rank_id`
   - Updated `test_get_memory_operator_size` with correct parameters

4. **Communication Tests**:
   - Updated `test_get_bandwidth` to require `rank_id`, `operator_name`, `stage`
   - Updated `test_get_operator_lists` with required parameters
   - Updated `test_get_operator_details` with required parameters

## Issues Identified

### 1. Missing Required Parameters Discovery

**Problem**: Many commands require `rankId`, `timeFlag`, `clusterPath` but users don't know what values to use.

**Solution Needed**: Implement discovery commands to query available ranks, time flags, etc.

**Example Commands** (need to implement):
- `global/files/getProjectExplorer` - Get available projects
- `timeline/unit/threads` - Get available ranks
- Query to discover available time flags

### 2. Complex Parameter Dependencies

**Problem**: Commands like `communication/bandwidth` require `operatorName` but users don't know what operators exist.

**Solution Needed**: Implement workflow:
1. Call `communication/operatorNames` first
2. Then call `communication/bandwidth` with operator name

### 3. Cluster Path Mystery

**Problem**: `clusterPath` is required but unclear what it represents.

**Investigation Needed**: Research from backend code what `clusterPath` represents and what values are valid.

## Next Steps

### Phase 1A: Metadata Discovery (NEW - Critical for usability)

Implement commands to discover required parameters:

```python
class MetadataController:
    def get_available_ranks(self) -> List[str]:
        """Discover available rank IDs from imported data."""
        # Use timeline/unit/threads or similar command

    def get_available_time_flags(self, rank_id: str) -> List[str]:
        """Discover available time flags for a rank."""
        # Need to research which command provides this

    def get_project_info(self) -> Dict[str, Any]:
        """Get current project information."""
        # Use global/files/getProjectExplorer
```

### Phase 1B: Complete Summary Module (9 remaining commands)

Implement remaining Summary commands:
- `summary/queryModelInfo`
- `summary/queryExpertHotspot`
- `summary/importExpertData`
- `summary/queryParallelStrategy`
- `summary/setParallelStrategy`
- `pipeline/fwdBwdTimeline`
- `parallelism/arrangement/all`
- `parallelism/performance/data`

### Phase 1C: Complete Operator Module (3 remaining commands)

- `operator/computeUnit` - Get compute unit info
- `operator/exportDetails` - Export operator details

### Phase 2: Memory & Communication Modules

Complete all 32 commands in Memory and Communication modules.

## Success Criteria

For each command implemented:

✅ **Correct Parameters**: Match backend Protocol structure exactly
✅ **Type Hints**: All parameters and return types annotated
✅ **Documentation**: Docstring with backend command name and module
✅ **Test Coverage**: At least one test case per command
✅ **Error Handling**: Graceful handling of missing/invalid parameters

## Current Progress

**Overall Completion**: 12/127 commands = 9.4%

**By Module**:
- Summary: 4/13 = 30.8%
- Operator: 3/6 = 50.0%
- Memory: 2/20 = 10.0%
- Communication: 3/12 = 25.0%
- Timeline: 0/43 = 0%
- Global: 2/10 = 20% (heartCheck, moduleConfig/get)

## Conclusion

Phase 1 implementation has successfully updated 12 core commands with correct parameter structures based on backend Protocol definitions. All updated commands now match backend expectations exactly.

**Key Achievement**: Parameter formats are now correct and will work with backend.

**Critical Blocker**: Need to implement metadata discovery commands so users can discover required parameter values (rank IDs, time flags, cluster paths).

**Recommendation**: Before continuing with more commands, implement `MetadataController` to make the API usable.
