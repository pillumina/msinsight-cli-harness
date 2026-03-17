# MindStudio Insight CLI - Test Plan and Results

## Test Inventory Plan

| Test File | Description | Estimated Tests |
|-----------|-------------|-----------------|
| `test_core.py` | Unit tests for core modules | 25 tests |
| `test_full_e2e.py` | End-to-end tests with real data | 15 tests |
| **Total** | | **40 tests** |

## Unit Test Plan (`test_core.py`)

### 1. Project Management Module (`core/project.py`)

**Functions to test:**
- `create_project()`
- `open_project()`
- `save_project()`
- `get_project_info()`
- `close_project()`

**Test cases (8 tests):**
1. `test_create_project_default` - Create project with default parameters
2. `test_create_project_with_name` - Create project with custom name
3. `test_create_project_save_to_file` - Create and save project to file
4. `test_open_project_valid_file` - Open existing valid project file
5. `test_open_project_file_not_found` - Error when file doesn't exist
6. `test_open_project_invalid_json` - Error when JSON is malformed
7. `test_save_project` - Save project modifications
8. `test_get_project_info` - Get project information

**Edge cases:**
- Invalid file paths
- Permission errors
- Large project files (>10MB)
- Unicode in project names
- Empty project names

### 2. Data Import Module (`core/import_data.py`)

**Functions to test:**
- `validate_data()`
- `list_profiling_files()`

**Test cases (6 tests):**
1. `test_validate_data_valid_directory` - Validate directory with all file types
2. `test_validate_data_invalid_path` - Error when path doesn't exist
3. `test_validate_data_empty_directory` - Validate empty directory
4. `test_list_profiling_files_json` - List JSON files
5. `test_list_profiling_files_mixed` - List mixed file types
6. `test_list_profiling_files_empty` - List files in empty directory

**Edge cases:**
- Directory with thousands of files
- Files with unusual names
- Symbolic links
- Permission denied errors

### 3. Session Management Module (`core/session.py`)

**Functions to test:**
- `Session.__init__`
- `Session.set_project`
- `Session.get_status`
- `Session.add_to_history`
- `Session.get_history`

**Test cases (6 tests):**
1. `test_session_init` - Initialize empty session
2. `test_session_set_project` - Set project
3. `test_session_status` - Get session status
4. `test_session_history` - Command history tracking
5. `test_session_config` - Set and get configuration
6. `test_session_clear_cache` - Clear session cache

### 4. Backend Integration (`utils/msinsight_backend.py`)

**Functions to test:**
- `find_available_port()`
- `is_server_running()`
- `MsInsightBackendError`

**Test cases (5 tests):**
1. `test_find_available_port` - Find available port in range
2. `test_find_available_port_all_used` - Error when all ports used
3. `test_is_server_running_false` - Check non-running server
4. `test_backend_error_message` - Error message formatting
5. `test_backend_binary_not_found` - Error when binary missing

**Note**: Testing actual server startup and WebSocket communication will be in E2E tests.

## E2E Test Plan (`test_full_e2e.py`)

### 1. Project Workflow Tests

**Test cases (3 tests):**
1. `test_full_project_workflow` - Create → Save → Open → Modify → Save
   - Create new project
   - Save to file
   - Close project
   - Re-open project
   - Verify all data persisted
   - Modify project
   - Save again

2. `test_project_json_roundtrip` - JSON serialization/deserialization
   - Create project with all fields
   - Save to JSON
   - Load from JSON
   - Verify identical

3. `test_multiple_projects` - Handle multiple projects
   - Create several projects
   - Switch between them
   - Verify independent state

### 2. Data Import Workflow Tests

**Test cases (3 tests):**
1. `test_import_validate_profiling_data` - Validate real profiling directory
   - Create temporary directory with sample files
   - Validate directory
   - Verify file counts
   - Check file types detected

2. `test_import_list_files` - List profiling files
   - Create directory with various file types
   - List files
   - Verify all files found
   - Check file metadata

3. `test_import_mixed_formats` - Import with mixed valid/invalid files
   - Create directory with valid and invalid files
   - Validate should succeed
   - List should return all files

### 3. CLI Subprocess Tests

**Test cases (6 tests):**
1. `test_cli_help` - CLI --help command
   ```python
   result = subprocess.run(["cli-anything-msinsight", "--help"])
   assert result.returncode == 0
   ```

2. `test_cli_version` - CLI --version command
   ```python
   result = subprocess.run(["cli-anything-msinsight", "--version"])
   assert result.returncode == 0
   assert "1.0.0" in result.stdout
   ```

3. `test_cli_project_new_json` - Create project via CLI with JSON output
   ```python
   result = subprocess.run([
       "cli-anything-msinsight", "--json",
       "project", "new", "-o", "test.json"
   ])
   assert result.returncode == 0
   data = json.loads(result.stdout)
   assert data["status"] == "success"
   ```

4. `test_cli_project_open` - Open project via CLI
   ```python
   # Create project first
   subprocess.run(["cli-anything-msinsight", "project", "new", "-o", "test.json"])
   # Open project
   result = subprocess.run([
       "cli-anything-msinsight", "--json",
       "--project", "test.json",
       "project", "info"
   ])
   assert result.returncode == 0
   ```

5. `test_cli_import_validate` - Validate data via CLI
   ```python
   result = subprocess.run([
       "cli-anything-msinsight", "--json",
       "import", "validate", test_data_dir
   ])
   assert result.returncode == 0
   data = json.loads(result.stdout)
   assert data["status"] == "success"
   ```

6. `test_cli_full_workflow` - Complete workflow via CLI
   ```python
   # Create project
   subprocess.run([...])
   # Load data
   subprocess.run([...])
   # Get status
   result = subprocess.run([...])
   assert result.returncode == 0
   ```

### 4. Realistic Workflow Scenarios

#### Scenario 1: Performance Analysis Pipeline
**Simulates**: Analyzing profiling data from training run

**Operations**:
1. Create new project
2. Load profiling directory
3. Validate data integrity
4. Get project info
5. Save project

**Verified**:
- All commands execute successfully
- Project file is valid JSON
- Data source recorded in project

#### Scenario 2: Batch Analysis
**Simulates**: Processing multiple profiling runs

**Operations**:
1. For each directory in list:
   - Create new project
   - Load profiling data
   - Validate
   - Save project with unique name

**Verified**:
- All projects created successfully
- No conflicts between projects
- Each project has correct data

#### Scenario 3: AI Agent Integration
**Simulates**: AI agent using CLI programmatically

**Operations**:
1. Create project with --json output
2. Load data with --json output
3. Get status with --json output
4. Parse all JSON responses
5. Verify machine-readable format

**Verified**:
- All JSON is valid
- Response structure is consistent
- No human-readable text in JSON mode

## Test Data Requirements

### Sample Profiling Directory

```
test_data/
├── valid_profiling/
│   ├── profiler_metadata.json    (100 KB)
│   ├── msprof_0.db                (1 MB)
│   ├── msprof_1.db                (1 MB)
│   ├── operator_info.bin          (500 KB)
│   ├── memory_info.bin            (500 KB)
│   └── kernel_details.csv         (200 KB)
├── empty_directory/
├── mixed_files/
│   ├── valid.json
│   ├── invalid.json
│   ├── data.db
│   └── readme.txt
└── invalid_data/
    └── corrupt.db
```

### Test Project Files

- `small_project.json` - Minimal project (<1 KB)
- `large_project.json` - Project with many data sources (100 KB)
- `invalid_project.json` - Malformed JSON
- `wrong_version.json` - Wrong version number

## Test Execution Strategy

### 1. Unit Tests (No External Dependencies)
```bash
cd agent-harness
pytest cli_anything/msinsight/tests/test_core.py -v --tb=short
```

**Expected**: All 25 tests pass
**Time**: <5 seconds
**Coverage**: >80% of core modules

### 2. E2E Tests (With Test Data)
```bash
cd agent-harness
pytest cli_anything/msinsight/tests/test_full_e2e.py -v --tb=short
```

**Expected**: All 15 tests pass
**Time**: <30 seconds
**Requires**: Test data directory

### 3. Subprocess Tests (With Installed CLI)
```bash
cd agent-harness
CLI_ANYTHING_FORCE_INSTALLED=1 pytest cli_anything/msinsight/tests/test_full_e2e.py::TestCLISubprocess -v -s
```

**Expected**: All subprocess tests pass
**Time**: <60 seconds
**Requires**: `pip install -e .` run first

## Test Coverage Goals

| Module | Target Coverage |
|--------|----------------|
| core/project.py | 90% |
| core/import_data.py | 85% |
| core/session.py | 80% |
| utils/msinsight_backend.py | 70% |
| **Overall** | **80%** |

## Known Limitations

1. **Backend Integration**: E2E tests cannot test actual WebSocket communication without running backend server
2. **Analysis Commands**: Timeline, memory, operator analysis requires backend - not testable in unit tests
3. **Export**: Report generation requires backend - placeholder tests only

## Test Maintenance

- Update tests when adding new commands
- Add regression tests for bugs
- Keep test data minimal but representative
- Ensure tests run in <1 minute total

---

## Test Results

*Test results will be appended here after running pytest in Phase 6*
