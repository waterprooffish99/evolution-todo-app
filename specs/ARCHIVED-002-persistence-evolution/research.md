# Research & Technical Decisions: Persistence Evolution

**Feature**: 002-persistence-evolution
**Date**: 2026-01-01
**Context**: Adding JSON-based persistence to Phase I in-memory todo application

## Research Questions Resolved

### 1. Atomic File Writing Strategy

**Decision**: Write-then-rename using temporary file + `os.replace()`

**Rationale**:
- `os.replace()` is atomic on both POSIX and Windows systems (Python 3.13+)
- Writing to `.tmp` file first prevents partial writes if interrupted
- If crash occurs during write, original file remains intact
- If crash occurs during rename, operation either completes or doesn't (atomicity guarantee)

**Alternatives Considered**:
- Direct write to file: Risk of partial writes, data corruption on crash
- File locking (`fcntl.flock`): Platform-specific, doesn't prevent partial writes
- Write-ahead logging: Over-engineered for single-user application

**Implementation Pattern**:
```python
import json
import os
from pathlib import Path

def save_tasks_atomic(tasks, filepath):
    """Atomically save tasks to JSON file"""
    tmp_path = f"{filepath}.tmp"

    # Write to temporary file
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

    # Atomic rename (replaces existing file)
    os.replace(tmp_path, filepath)
```

**References**:
- Python docs: `os.replace()` is atomic on POSIX and Windows
- Best practice: Used by SQLite, Git, and other data-critical systems

---

### 2. JSON Schema Versioning

**Decision**: Include explicit `version` field in JSON structure for future migration support

**Rationale**:
- Phase II is version "1.0" but future phases may need schema changes
- Explicit version enables automated migration detection
- Minimal overhead (one field) with significant long-term benefit
- Follows industry best practices (database migrations, API versioning)

**Alternatives Considered**:
- No versioning: Future migrations would require heuristics, error-prone
- Separate metadata file: Adds complexity, risk of desynchronization
- Hash-based validation: Doesn't help with migration, only detects corruption

**Schema Format**:
```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "completed": false
    }
  ]
}
```

**Migration Path** (future):
- Load JSON, check version field
- If version < current: run migration functions
- If version > current: error (downgrade not supported)

---

### 3. Corruption Detection & Recovery

**Decision**: Try-catch with `json.JSONDecodeError`, backup corrupted files with timestamp, offer user recovery options

**Rationale**:
- JSON corruption is rare but catastrophic if not handled
- User data preservation is critical (backup before overwrite)
- User choice respects agency: fix manually or start fresh
- Timestamp backup allows multiple corruption events without data loss

**Alternatives Considered**:
- Automatic overwrite: User loses all data, unacceptable
- Automatic recovery to last known good: Requires versioning system, over-engineered
- Silent failure: Violates constitution principle of human-readable design

**Implementation Strategy**:
```python
import json
from datetime import datetime
from pathlib import Path

def load_tasks_with_recovery(filepath):
    """Load tasks with corruption detection and recovery"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('tasks', [])

    except json.JSONDecodeError as e:
        # Backup corrupted file
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        backup_path = f"{filepath}.corrupt.{timestamp}"
        Path(filepath).rename(backup_path)

        # Prompt user for action
        print(f"ERROR: {filepath} is corrupted (backed up to {backup_path})")
        print("Options:")
        print("1. Create fresh empty file")
        print("2. Exit and manually fix the file")

        choice = input("Choose (1/2): ")

        if choice == "1":
            return []  # Start with empty task list
        else:
            exit(1)

    except FileNotFoundError:
        # First run, no file exists yet
        return []
```

**Recovery Options**:
1. Create fresh file → User loses data but can continue working
2. Exit → User can manually inspect/fix backup file

---

### 4. Persistence Layer Architecture

**Decision**: Wrapper pattern - persistence layer wraps Phase I skills without modifying them

**Rationale**:
- Phase I skills remain the source of truth (constitution requirement)
- Persistence is infrastructure concern, not business logic
- Wrapper intercepts mutating operations, adds save hook
- Non-mutating operations (GetTasks) don't trigger saves
- Clean separation of concerns enables future storage backends (SQLite, cloud)

**Alternatives Considered**:
- Modify Phase I skills directly: Violates backward compatibility requirement
- Decorator pattern: Too complex for simple save-after-mutation logic
- Event system: Over-engineered, adds unnecessary abstraction

**Architecture**:
```
┌─────────────────────────────────────┐
│  CLI Layer (menu-driven interface)  │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Persistence Layer (wrapper)       │
│  - load_on_startup()                │
│  - save_after_mutation()            │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Phase I Skills (unchanged)         │
│  - AddTask()                        │
│  - UpdateTask()                     │
│  - DeleteTask()                     │
│  - ToggleTaskStatus()               │
│  - GetTasks()                       │
└─────────────────────────────────────┘
```

**Implementation Pattern**:
- Initialize: Load from JSON, populate Phase I's in-memory store
- Mutating operations: Call Phase I skill → Save to JSON
- Read operations: Call Phase I skill directly (no save)

---

### 5. Task ID Continuity After Restart

**Decision**: On load, set next_id to `max(task.id for task in loaded_tasks) + 1`

**Rationale**:
- Ensures unique IDs across sessions
- Simple algorithm, no state tracking needed
- Handles edge case: empty file → next_id = 1

**Alternatives Considered**:
- Persist next_id in JSON: Adds complexity, risk of desync with actual task IDs
- UUID instead of integers: Violates Phase I spec (integer IDs required)
- Sequential ID without gap handling: Could reuse IDs after delete

**Implementation**:
```python
def initialize_task_id_counter(tasks):
    """Set next task ID based on loaded data"""
    if not tasks:
        return 1
    return max(task['id'] for task in tasks) + 1
```

---

### 6. Error Handling Strategy

**Decision**: Fail fast with user-friendly messages, never silently continue with corrupted state

**Rationale**:
- Constitution principle: "The system must never crash due to invalid user input"
- Extends to file system errors: permission denied, disk full, read-only
- User-friendly errors over technical stack traces
- Graceful degradation: offer recovery paths when possible

**Error Categories & Responses**:

| Error Type | Detection | User Action | System Response |
|------------|-----------|-------------|-----------------|
| Missing file | `FileNotFoundError` | None (expected on first run) | Create empty file, continue |
| Corrupted JSON | `json.JSONDecodeError` | Choose: fresh file or exit | Backup + create fresh or exit |
| Permission denied | `PermissionError` | Fix permissions, rerun | Display error + exit |
| Disk full | `OSError` | Free space, retry | Display error + exit |
| Read-only filesystem | `PermissionError` on write | Remove read-only, retry | Display error + exit |

**Implementation Pattern**:
```python
def handle_file_error(error, operation):
    """User-friendly error messages for file operations"""
    if isinstance(error, PermissionError):
        print(f"ERROR: Permission denied for {operation}")
        print("Fix: Check file/directory permissions")
    elif isinstance(error, OSError) and error.errno == 28:  # ENOSPC
        print(f"ERROR: Disk full during {operation}")
        print("Fix: Free disk space and try again")
    else:
        print(f"ERROR: Unexpected error during {operation}: {error}")
    exit(1)
```

---

### 7. Directory Structure

**Decision**: Create `data/` directory at application root, store `todo_data.json` inside

**Rationale**:
- Separates data from code (best practice)
- Easy to add `.gitignore` for `data/` (user data shouldn't be in version control)
- Scalable: future phases can add `data/backups/`, `data/logs/`, etc.
- Platform-agnostic: works on Linux, macOS, Windows

**Alternatives Considered**:
- Root directory (`./todo_data.json`): Clutters project root
- User home directory (`~/.evolution-todo/`): Over-engineered for learning project
- System temp directory: Data loss on cleanup, inappropriate for persistent storage

**Implementation**:
```python
from pathlib import Path

DATA_DIR = Path(__file__).parent / 'data'
DATA_FILE = DATA_DIR / 'todo_data.json'

def ensure_data_directory():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
```

**Git Ignore**:
```gitignore
# User data (should not be committed)
data/
!data/.gitkeep
```

---

## Technology Stack Confirmation

### Language & Version
**Python 3.13+** (Phase I requirement, unchanged)

### Standard Library Only
No external dependencies (Phase I requirement, unchanged)

**Required Modules**:
- `json`: Serialization/deserialization
- `os`: Atomic file operations (`os.replace()`)
- `pathlib`: Cross-platform path handling
- `datetime`: Timestamp generation for backups

### Testing Framework
**pytest** (Phase I requirement, unchanged)

**New Test Categories for Phase II**:
- Persistence tests: Load/save operations
- Corruption recovery tests: Malformed JSON handling
- File system error tests: Permissions, disk full (mocked)
- Atomicity tests: Interrupt simulation (advanced)

---

## Performance Considerations

### Load Performance
- **Target**: < 1 second for 1,000 tasks
- **Expected**: ~10ms for typical use (< 100 tasks)
- **Limitation**: Full file read on startup, acceptable for target scale

### Save Performance
- **Target**: < 100ms per operation
- **Expected**: ~5-20ms per save (typical task list size)
- **Optimization**: Python's `json.dump()` with `indent=2` for readability

### Memory Usage
- **In-memory**: Task list lives in RAM (Phase I design)
- **File I/O**: Temporary duplication during save (tasks in memory + JSON string)
- **Constraint**: < 100MB total (constitution), easily met for reasonable task counts

### Scaling Limits
- **Comfortable**: Up to 10,000 tasks
- **Warning threshold**: > 10,000 tasks (should suggest migration to database)
- **Hard limit**: Python list size limit (~10^7 items), unrealistic for todo app

---

## Open Questions (for User Clarification)

None. All technical decisions have been made based on:
- Phase I requirements (backward compatibility)
- Constitution Amendment I (persistence principle)
- Industry best practices (atomic writes, versioning, error handling)

---

## Summary

**Phase II adds persistence with minimal complexity**:
- Atomic write-then-rename prevents corruption
- Explicit versioning enables future migrations
- Wrapper architecture preserves Phase I skills
- User-friendly error handling with recovery options
- Standard library only (no dependencies)
- Scales comfortably to 10,000 tasks

**Risk Mitigation**:
- Corruption: Backup + recovery options
- Data loss: Atomic writes guarantee
- Future evolution: Version field + clean architecture

**Next Steps**: Phase 1 Design (data-model.md, contracts, quickstart.md)
