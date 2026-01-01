# Data Model: Persistence Evolution

**Feature**: 002-persistence-evolution
**Date**: 2026-01-01
**Status**: Phase 1 Design

## Overview

Phase II extends Phase I's in-memory data model with persistent storage. The core Task entity remains unchanged to maintain backward compatibility.

---

## Entities

### Task (Phase I - Unchanged)

**Definition**: Represents a single todo item with unique identifier, title, optional description, and completion status.

**Attributes**:

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | int | Yes | > 0 | Auto-assigned | Sequential, unique across all tasks |
| `title` | str | Yes | Non-empty, no leading/trailing whitespace | N/A | Primary task description |
| `description` | str | No | Any string | `""` (empty string) | Additional details |
| `completed` | bool | Yes | True or False | `False` | Completion status |

**Invariants**:
- `id` must be unique across all tasks (enforced by Phase I AddTask skill)
- `title` cannot be empty or whitespace-only
- `completed` is always a boolean (no null/undefined states)

**State Transitions**:
```
[New Task] --AddTask--> [Incomplete] --ToggleTaskStatus--> [Complete]
                             ↑                                   |
                             |--------ToggleTaskStatus-----------|

[Any State] --UpdateTask--> [Same State, modified title/description]
[Any State] --DeleteTask--> [Removed]
```

**Example**:
```python
{
    "id": 1,
    "title": "Implement persistence layer",
    "description": "Add JSON storage with atomic writes",
    "completed": False
}
```

---

### TaskCollection (Phase II - New Concept)

**Definition**: The complete set of tasks with metadata for persistence and versioning.

**Structure**:
```python
{
    "version": str,     # Schema version (e.g., "1.0")
    "tasks": List[Task] # List of Task dictionaries
}
```

**Attributes**:

| Field | Type | Required | Validation | Notes |
|-------|------|----------|------------|-------|
| `version` | str | Yes | Semantic version format (e.g., "1.0") | Enables future schema migrations |
| `tasks` | list | Yes | List of Task dictionaries | Empty list `[]` is valid |

**Invariants**:
- `version` must be present and non-empty
- `tasks` must be a list (not null/undefined)
- Each item in `tasks` must be a valid Task dictionary
- No duplicate task IDs within `tasks` list

**Example**:
```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": 1,
      "title": "Learn Python",
      "description": "Complete tutorial",
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

---

## Persistence Layer State

### Runtime State (In-Memory)

**Global State** (Phase I design, unchanged):
```python
tasks = []          # List of task dictionaries
next_task_id = 1    # Counter for assigning new task IDs
```

**Initialization** (Phase II addition):
1. On application startup, load `data/todo_data.json`
2. Populate `tasks` list from loaded TaskCollection
3. Set `next_task_id = max(task['id'] for task in tasks) + 1`

### File State (Persistent)

**Location**: `data/todo_data.json`

**Format**: JSON (UTF-8 encoding)

**Structure**: TaskCollection (see above)

**Update Triggers** (auto-save after these operations):
- AddTask: New task created
- UpdateTask: Task title/description modified
- DeleteTask: Task removed
- ToggleTaskStatus: Task completion status changed

**Read Operations** (no save triggered):
- GetTasks: Returns task list, no mutations

---

## Data Flow

### Application Startup
```
1. Application starts
2. Persistence layer checks for data/todo_data.json
3. If file exists:
   a. Read and parse JSON → TaskCollection
   b. Load tasks into in-memory list
   c. Set next_task_id based on max ID
4. If file missing/corrupt:
   a. Handle error (backup if corrupt, create if missing)
   b. Initialize with empty task list
   c. Set next_task_id = 1
5. Application ready for user interaction
```

### Mutation Operation Flow
```
1. User initiates action (e.g., Add Task)
2. CLI layer validates input
3. CLI calls Phase I skill (e.g., AddTask)
4. Phase I skill updates in-memory state
5. Phase I skill returns result
6. Persistence layer saves tasks to JSON
   a. Serialize TaskCollection to JSON string
   b. Write to data/todo_data.json.tmp
   c. Atomically rename .tmp to .json
7. CLI displays result to user
```

### Read Operation Flow
```
1. User initiates read action (e.g., View Tasks)
2. CLI calls Phase I skill (GetTasks)
3. Phase I skill returns in-memory task list
4. CLI formats and displays tasks
(No persistence layer involvement - read-only)
```

---

## Validation Rules

### On Load (from JSON)

**Structural Validation**:
- JSON must be valid (parseable)
- Root object must have `version` and `tasks` keys
- `tasks` must be a list

**Task Validation**:
- Each task must have: `id`, `title`, `completed`
- `id` must be positive integer
- `title` must be non-empty string
- `completed` must be boolean
- `description` is optional (defaults to empty string if missing)

**Duplicate ID Check**:
- Scan all loaded tasks, ensure unique IDs
- If duplicates found: log warning, keep first occurrence

**Failure Handling**:
- If validation fails: treat as corruption
- Backup file, offer recovery options

### On Save (to JSON)

**Pre-Save Checks**:
- Ensure `tasks` list is valid (not None)
- Ensure all tasks have required fields
- No duplicate IDs (enforced by Phase I logic)

**Post-Save Verification** (optional, for critical applications):
- Read back saved file, verify parseable
- Compare task count (sanity check)
- If verification fails: log error, keep .tmp file

---

## Error Handling

### Corruption Recovery

**Scenario**: JSON file is corrupted (invalid syntax)

**Detection**: `json.JSONDecodeError` on load

**Response**:
1. Backup corrupted file: `todo_data.json.corrupt.YYYY-MM-DDTHH-MM-SS`
2. Display error to user with backup location
3. Offer options:
   - Create fresh empty file (lose corrupted data)
   - Exit and manually fix backup file

### Missing File

**Scenario**: `data/todo_data.json` does not exist (first run)

**Detection**: `FileNotFoundError` on load

**Response**:
1. Create `data/` directory if missing
2. Create empty TaskCollection file
3. Initialize with 0 tasks
4. Continue normally

### Permission Denied

**Scenario**: Application lacks read/write permissions

**Detection**: `PermissionError` on read or write

**Response**:
1. Display user-friendly error message
2. Instruct user to fix permissions
3. Exit gracefully (cannot continue without access)

### Disk Full

**Scenario**: No space available during save

**Detection**: `OSError` with errno 28 (ENOSPC)

**Response**:
1. Display error: "Disk full, changes not saved"
2. Instruct user to free space
3. Rollback: keep .tmp file, don't replace .json
4. Exit or retry (user choice)

---

## Schema Versioning

### Current Version: 1.0

**Fields**:
- `version`: String, always "1.0"
- `tasks`: List of Task dictionaries

### Future Migration Path

**Version Detection**:
```python
def get_schema_version(data):
    return data.get('version', '0.0')  # Default for legacy data

def migrate_if_needed(data):
    version = get_schema_version(data)

    if version == '1.0':
        return data  # Current version, no migration
    elif version == '0.0':
        # Legacy data (no version field), migrate to 1.0
        return {'version': '1.0', 'tasks': data}
    else:
        # Future version (e.g., 2.0), unsupported
        raise ValueError(f"Schema version {version} not supported")
```

**Future Extensions** (examples for Phase III+):
- Version 1.1: Add `created_at`, `updated_at` timestamps to Task
- Version 2.0: Add `tags` list to Task
- Version 3.0: Nested task hierarchy (parent-child relationships)

---

## Indexes and Lookups

### Primary Access Pattern: By ID

**Phase I Design** (unchanged):
- Tasks stored in list
- Lookup by ID: Linear search `O(n)`
- Acceptable for < 10,000 tasks

**Future Optimization** (Phase III+):
- Add in-memory index: `task_by_id = {task['id']: task}`
- Lookup becomes `O(1)`
- Trade-off: Additional memory, complexity

### Secondary Access Patterns

**Not implemented in Phase II**, but schema supports:
- Filter by completion status: `[t for t in tasks if t['completed']]`
- Search by title: `[t for t in tasks if query in t['title'].lower()]`
- Sort by ID: `sorted(tasks, key=lambda t: t['id'])`

---

## Data Constraints Summary

| Constraint | Enforced By | Consequence of Violation |
|------------|-------------|--------------------------|
| Task ID uniqueness | Phase I AddTask | Duplicate ID error |
| Task title non-empty | Phase I validation | Task creation rejected |
| JSON file atomicity | Persistence layer (atomic writes) | File either fully written or unchanged |
| Schema version present | Persistence layer load | Treated as legacy/corrupted data |
| Tasks list is list type | Python type system | TypeError on invalid operations |

---

## Testing Data Scenarios

### Happy Path
1. **Empty state**: No tasks, fresh start
2. **Single task**: One incomplete task
3. **Multiple tasks**: Mix of complete/incomplete
4. **All complete**: All tasks completed
5. **All incomplete**: All tasks pending

### Edge Cases
1. **Empty description**: Task with no description field
2. **Very long title**: 1000+ character title
3. **Special characters**: Unicode, emojis in title/description
4. **Large ID numbers**: Task ID > 1,000,000
5. **10,000 tasks**: Performance boundary

### Error Cases
1. **Corrupted JSON**: Invalid syntax (missing bracket, trailing comma)
2. **Missing version field**: Legacy data without version
3. **Invalid task structure**: Missing required fields
4. **Duplicate IDs**: Two tasks with same ID
5. **Type mismatches**: ID as string, completed as string "true"

---

## Summary

**Phase II Data Model Additions**:
- TaskCollection wrapper for versioning
- Persistent JSON storage structure
- Error handling for corruption/missing files
- Atomic write strategy for data integrity

**Phase I Compatibility**:
- Task entity unchanged
- In-memory operations identical
- Phase I skills unaware of persistence

**Extensibility**:
- Version field enables future migrations
- JSON format easy to extend with new fields
- Architecture supports alternate storage backends (SQLite, cloud)
