# Persistence API Contracts

**Feature**: 002-persistence-evolution
**Date**: 2026-01-01
**Type**: Internal API (Python module interface)

## Overview

This document defines the interface contracts for the persistence layer. These are internal Python function signatures, not REST/HTTP APIs.

---

## Module: `persistence.py`

### Purpose
Handles loading and saving task data to/from `data/todo_data.json` with error handling and atomic writes.

### Public Interface

---

#### `initialize_persistence() -> None`

**Purpose**: Initialize persistence layer, load existing data, setup in-memory state.

**Called By**: Application startup (main entry point)

**Behavior**:
1. Create `data/` directory if missing
2. Check for `data/todo_data.json`
3. If file exists: Load and parse JSON
4. If file missing: Create empty file with initial structure
5. If file corrupted: Backup and handle recovery
6. Initialize Phase I global state (`tasks` list, `next_task_id` counter)

**Side Effects**:
- Creates `data/` directory (filesystem)
- Creates `data/todo_data.json` if missing (filesystem)
- Initializes global variables: `tasks`, `next_task_id`
- May create backup files if corruption detected

**Exceptions**:
- `PermissionError`: Cannot read/write data directory
- `OSError`: Disk full or other filesystem error
- `SystemExit`: User chose to exit during corruption recovery

**Returns**: `None`

**Example Usage**:
```python
# In main.py
from persistence import initialize_persistence

if __name__ == "__main__":
    initialize_persistence()
    # ... rest of application logic
```

**Postconditions**:
- `tasks` list is populated from file (or empty if no data)
- `next_task_id` is set correctly (max ID + 1 or 1 if empty)
- `data/todo_data.json` exists and is valid JSON

---

#### `save_tasks() -> None`

**Purpose**: Atomically save current task state to JSON file.

**Called By**: After every mutating operation (AddTask, UpdateTask, DeleteTask, ToggleTaskStatus)

**Behavior**:
1. Serialize current `tasks` list to JSON string
2. Write JSON to temporary file `data/todo_data.json.tmp`
3. Atomically rename `.tmp` to `todo_data.json` (replaces existing file)

**Side Effects**:
- Writes to filesystem (`data/todo_data.json.tmp`)
- Replaces `data/todo_data.json` with new content
- Temporary file `.tmp` is removed after rename

**Exceptions**:
- `PermissionError`: Cannot write to data directory
- `OSError`: Disk full, filesystem read-only

**Returns**: `None`

**Example Usage**:
```python
# After mutating operation
from phase1_skills import AddTask
from persistence import save_tasks

task = AddTask("Buy groceries", "Milk, eggs, bread")
save_tasks()  # Persist the change immediately
```

**Preconditions**:
- `tasks` list must be valid (not None, all tasks have required fields)

**Postconditions**:
- `data/todo_data.json` reflects current `tasks` state
- File contains valid JSON with correct schema version

---

#### `load_tasks() -> List[Dict[str, Any]]`

**Purpose**: Load tasks from JSON file (used internally by `initialize_persistence`).

**Called By**: Internal (called by `initialize_persistence`)

**Behavior**:
1. Read `data/todo_data.json`
2. Parse JSON into Python dictionary
3. Validate schema (version, tasks list)
4. Return list of task dictionaries

**Side Effects**:
- None (read-only operation)

**Exceptions**:
- `FileNotFoundError`: File does not exist (handled by returning empty list)
- `json.JSONDecodeError`: File is corrupted (triggers recovery flow)
- `ValueError`: Schema validation failed (treated as corruption)

**Returns**: `List[Dict[str, Any]]` - List of task dictionaries

**Example**:
```python
tasks = load_tasks()
# tasks = [{'id': 1, 'title': 'Task 1', 'description': '', 'completed': False}, ...]
```

**Postconditions**:
- Returned list contains only valid Task dictionaries
- No duplicate task IDs in returned list

---

#### `handle_corrupted_file(filepath: str) -> List[Dict[str, Any]]`

**Purpose**: Handle corrupted JSON file with user recovery options.

**Called By**: Internal (called by `load_tasks` when `JSONDecodeError` occurs)

**Behavior**:
1. Backup corrupted file with timestamp: `todo_data.json.corrupt.YYYY-MM-DDTHH-MM-SS`
2. Display error message to user with backup location
3. Prompt user for action:
   - Option 1: Create fresh empty file (lose corrupted data)
   - Option 2: Exit and manually fix backup
4. Execute user choice

**Side Effects**:
- Creates backup file (filesystem)
- May create fresh empty JSON file (if user chooses option 1)
- May exit application (if user chooses option 2)

**Exceptions**:
- `PermissionError`: Cannot create backup file
- `SystemExit`: User chose to exit (exception code 1)

**Returns**: `List[Dict[str, Any]]` - Empty list if user chose fresh start

**Example Flow**:
```
ERROR: data/todo_data.json is corrupted (backed up to todo_data.json.corrupt.2026-01-01T14-30-00)

Options:
1. Create fresh empty file (you will lose corrupted data)
2. Exit and manually fix the backup file

Choose (1/2): 1

Fresh file created. Starting with empty task list.
```

**Postconditions**:
- Corrupted file is backed up (never lost)
- User has made informed decision (fresh start or manual fix)

---

#### `ensure_atomic_write(data: Dict[str, Any], filepath: str) -> None`

**Purpose**: Write data to file atomically to prevent partial writes.

**Called By**: Internal (called by `save_tasks`)

**Behavior**:
1. Serialize `data` to JSON string with indentation
2. Write to temporary file `{filepath}.tmp`
3. Atomically rename temp file to target filepath (replaces existing)

**Side Effects**:
- Writes to filesystem (temp file)
- Replaces target file (atomic operation)

**Exceptions**:
- `OSError`: Disk full, permission denied, filesystem error

**Returns**: `None`

**Example**:
```python
data = {'version': '1.0', 'tasks': [...]}
ensure_atomic_write(data, 'data/todo_data.json')
# File is now atomically updated
```

**Guarantees**:
- Target file is either fully updated or unchanged
- No partial writes (atomic rename ensures this)
- If interrupted, temp file may remain (can be cleaned up)

---

## Module: Phase I Skills (Unchanged)

Phase I skills (`AddTask`, `UpdateTask`, `DeleteTask`, `ToggleTaskStatus`, `GetTasks`) remain unchanged. Their signatures and behavior are documented in Phase I spec.

**Persistence Integration**:
- CLI layer calls Phase I skill
- After mutating skills, CLI calls `save_tasks()`
- Read-only skills (`GetTasks`) do not trigger saves

**Example Integration**:
```python
from phase1_skills import AddTask, GetTasks
from persistence import save_tasks

# Mutating operation
task = AddTask("New task", "Description")
save_tasks()  # Persist immediately

# Read operation
all_tasks = GetTasks()
# No save needed
```

---

## Error Handling Contracts

### Error Categories

| Error Type | Handling Strategy | User Experience | System Response |
|------------|-------------------|-----------------|-----------------|
| Missing file (first run) | Auto-create | Silent, seamless | Create empty JSON |
| Corrupted JSON | Backup + prompt | User chooses recovery | Backup file, offer options |
| Permission denied | Fail with message | Clear error, action required | Display error, exit |
| Disk full | Fail with message | Clear error, action required | Display error, keep old file |
| Unexpected error | Fail with traceback | Technical error shown | Display error, exit |

### Error Message Templates

**Permission Denied**:
```
ERROR: Permission denied when accessing data/todo_data.json

Fix: Ensure the application has read/write permissions for the data directory.

Run: chmod 755 data/ && chmod 644 data/todo_data.json
```

**Disk Full**:
```
ERROR: Disk full - cannot save changes

Fix: Free up disk space and restart the application.

Note: Last successful save is preserved in data/todo_data.json
```

**Corrupted File**:
```
ERROR: data/todo_data.json is corrupted (backed up to todo_data.json.corrupt.2026-01-01T14-30-00)

Options:
1. Create fresh empty file (you will lose corrupted data)
2. Exit and manually fix the backup file

Choose (1/2):
```

---

## File Format Contract

### JSON Schema (Version 1.0)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "tasks"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^[0-9]+\\.[0-9]+$",
      "description": "Schema version (e.g., '1.0')"
    },
    "tasks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "title", "completed"],
        "properties": {
          "id": {
            "type": "integer",
            "minimum": 1,
            "description": "Unique task identifier"
          },
          "title": {
            "type": "string",
            "minLength": 1,
            "description": "Task title (non-empty)"
          },
          "description": {
            "type": "string",
            "description": "Optional task description"
          },
          "completed": {
            "type": "boolean",
            "description": "Task completion status"
          }
        }
      }
    }
  }
}
```

### Example Valid File

```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": 1,
      "title": "Learn Python",
      "description": "Complete online tutorial",
      "completed": false
    },
    {
      "id": 2,
      "title": "Build todo app",
      "description": "",
      "completed": true
    }
  ]
}
```

### Example Invalid Files

**Missing version field**:
```json
{
  "tasks": [...]
}
```
→ Treated as legacy/corrupted, triggers migration or recovery

**Invalid task structure**:
```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": "1",  // Should be integer, not string
      "title": "Task 1",
      "completed": false
    }
  ]
}
```
→ Validation fails, treated as corrupted

**Duplicate IDs**:
```json
{
  "version": "1.0",
  "tasks": [
    {"id": 1, "title": "Task 1", "completed": false},
    {"id": 1, "title": "Task 2", "completed": true}  // Duplicate ID
  ]
}
```
→ Log warning, keep first occurrence, discard duplicate

---

## Testing Contracts

### Unit Test Requirements

**Persistence Layer Tests**:
1. `test_initialize_persistence_creates_directory()`
2. `test_initialize_persistence_creates_empty_file()`
3. `test_initialize_persistence_loads_existing_data()`
4. `test_save_tasks_writes_valid_json()`
5. `test_save_tasks_is_atomic()`
6. `test_load_tasks_returns_empty_list_on_missing_file()`
7. `test_load_tasks_handles_corrupted_json()`
8. `test_handle_corrupted_file_creates_backup()`
9. `test_ensure_atomic_write_uses_temp_file()`

**Integration Tests** (Phase I + Persistence):
1. `test_add_task_persists_immediately()`
2. `test_update_task_persists_changes()`
3. `test_delete_task_persists_removal()`
4. `test_toggle_status_persists_state()`
5. `test_restart_loads_previous_session()`
6. `test_task_id_continuity_after_restart()`

**Error Handling Tests**:
1. `test_permission_error_displays_message()`
2. `test_disk_full_preserves_old_file()`
3. `test_corrupted_file_offers_recovery()`
4. `test_missing_directory_is_created()`

### Mock Requirements

**File System Mocks** (for error simulation):
- `mock_permission_error()`: Simulate PermissionError
- `mock_disk_full()`: Simulate OSError (errno 28)
- `mock_corrupted_json()`: Return invalid JSON string

**User Input Mocks** (for recovery testing):
- `mock_user_choice_fresh_file()`: Simulate user choosing option 1
- `mock_user_choice_exit()`: Simulate user choosing option 2

---

## Performance Contracts

### Load Time (Startup)

**Target**: < 1 second for 1,000 tasks

**Measurement**:
```python
import time
start = time.time()
initialize_persistence()
elapsed = time.time() - start
assert elapsed < 1.0, f"Load time {elapsed}s exceeds 1s"
```

**Acceptance**:
- 100 tasks: < 50ms
- 1,000 tasks: < 500ms
- 10,000 tasks: < 5s (warning threshold)

### Save Time (Per Operation)

**Target**: < 100ms per save

**Measurement**:
```python
import time
from persistence import save_tasks

start = time.time()
save_tasks()
elapsed = time.time() - start
assert elapsed < 0.1, f"Save time {elapsed}s exceeds 100ms"
```

**Acceptance**:
- 100 tasks: < 20ms
- 1,000 tasks: < 100ms
- 10,000 tasks: < 1s (warning threshold)

---

## Summary

**Persistence API provides**:
- Initialization with error recovery
- Atomic save operations
- Transparent integration with Phase I skills
- Comprehensive error handling

**Guarantees**:
- Data integrity (atomic writes)
- Backward compatibility (Phase I skills unchanged)
- User agency (recovery options, not silent failures)

**Next Steps**: Implement persistence.py following these contracts
