# Feature Specification: Persistence Evolution (Phase II)

**Feature Branch**: `002-persistence-evolution`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User description: "Add persistent JSON storage to Phase I in-memory todo application, ensuring all state changes persist to data/todo_data.json with auto-load on startup and auto-save on every mutation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Persistent Task Storage (Priority: P0)

As a user, I want all my tasks to be automatically saved to a file so that my task list is preserved when I close and reopen the application.

**Why this priority**: Without persistence, all task data is lost between sessions, making the application unusable for real-world task management.

**Independent Test**: Can be fully tested by adding tasks, closing the application, restarting it, and verifying all tasks are restored with correct data and status.

**Acceptance Scenarios**:

1. **Given** I add a new task, **When** the task is created, **Then** it is immediately written to `data/todo_data.json`.
2. **Given** I have tasks in the system, **When** I restart the application, **Then** all tasks are loaded from `data/todo_data.json` with their original state intact.
3. **Given** the `data/todo_data.json` file does not exist, **When** I start the application, **Then** it creates an empty file and initializes with zero tasks.
4. **Given** I perform any task operation (add/update/delete/toggle), **When** the operation completes, **Then** the changes are immediately persisted to `data/todo_data.json`.

---

### User Story 2 - Corrupted Data Recovery (Priority: P1)

As a user, I want the application to handle corrupted data files gracefully so that a malformed JSON file doesn't prevent me from using the application.

**Why this priority**: File corruption can occur due to power failures, disk errors, or manual editing. The application must remain usable even when the data file is damaged.

**Independent Test**: Can be fully tested by intentionally corrupting the JSON file with invalid syntax and verifying the application starts with clear error messaging and recovery options.

**Acceptance Scenarios**:

1. **Given** the `data/todo_data.json` file contains invalid JSON syntax, **When** I start the application, **Then** I see a clear error message indicating the file is corrupted.
2. **Given** the data file is corrupted, **When** the error is displayed, **Then** the application offers options to: (a) create a fresh empty file, or (b) exit and manually fix the file.
3. **Given** I choose to create a fresh file, **When** the operation completes, **Then** the corrupted file is backed up with a timestamp suffix and a new empty `data/todo_data.json` is created.
4. **Given** the data file contains valid JSON but unexpected structure, **When** I start the application, **Then** it attempts to migrate or initializes with an empty task list and logs a warning.

---

### User Story 3 - Atomic Write Operations (Priority: P1)

As a user, I want all file write operations to be atomic so that my data is never partially written or corrupted during save operations.

**Why this priority**: Non-atomic writes can leave the data file in an inconsistent state if the application crashes or is interrupted during a save operation.

**Independent Test**: Can be simulated by testing write operations and verifying the file is either fully written or not modified at all (no partial writes).

**Acceptance Scenarios**:

1. **Given** a task operation is in progress, **When** the system writes to the file, **Then** it writes to a temporary file first and then atomically renames it to `todo_data.json`.
2. **Given** a write operation is interrupted (simulated), **When** the application restarts, **Then** the data file is either the old complete state or the new complete state, never a partial write.

---

### User Story 4 - Backward Compatibility with Phase I Skills (Priority: P0)

As a developer, I want all Phase I skills (AddTask, GetTasks, UpdateTask, DeleteTask, ToggleTaskStatus) to remain unchanged in their signatures so that the persistence layer is transparent to the core logic.

**Why this priority**: Maintaining skill signatures ensures that Phase I's design remains valid and that persistence is an enhancement, not a rewrite.

**Independent Test**: Can be fully tested by running all Phase I tests against the Phase II implementation and verifying 100% pass rate.

**Acceptance Scenarios**:

1. **Given** the Phase II implementation, **When** I call any Phase I skill, **Then** its function signature, inputs, and outputs remain identical to Phase I.
2. **Given** the Phase II implementation, **When** I run all Phase I tests, **Then** they all pass without modification.
3. **Given** a task operation completes, **When** the skill returns, **Then** the persistence layer has already auto-saved the changes without the skill being aware of it.

---

### Edge Cases

- What happens if the `data/` directory does not exist when the application starts?
- What happens if the `data/todo_data.json` file is read-only or the application lacks write permissions?
- What happens if the disk is full during a save operation?
- What happens if two instances of the application run simultaneously (future consideration)?
- How does the application handle very large JSON files (10,000+ tasks)?
- What happens if the JSON file contains non-UTF-8 characters?
- How does the system handle task IDs after loading from a file (does it resume from max ID + 1)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST store all task data in `data/todo_data.json` in valid JSON format.
- **FR-002**: The system MUST automatically load all tasks from `data/todo_data.json` on application startup.
- **FR-003**: The system MUST automatically save the current task state to `data/todo_data.json` after every Create, Update, Delete, or Toggle operation.
- **FR-004**: The system MUST create the `data/` directory and `data/todo_data.json` file if they do not exist on startup.
- **FR-005**: The system MUST detect corrupted JSON files on startup and display a user-friendly error message with recovery options.
- **FR-006**: The system MUST back up corrupted files with a timestamp suffix (e.g., `todo_data.json.corrupt.2026-01-01T12-00-00`) before creating a fresh file.
- **FR-007**: All file write operations MUST be atomic to prevent partial writes and data corruption.
- **FR-008**: The system MUST use a write-then-rename strategy (write to `.tmp` file, then rename) to ensure atomicity.
- **FR-009**: Phase I skill signatures (AddTask, GetTasks, UpdateTask, DeleteTask, ToggleTaskStatus) MUST remain unchanged.
- **FR-010**: The persistence layer MUST be implemented as a separate module/layer that is invisible to Phase I skills.
- **FR-011**: The system MUST handle file system errors (permissions, disk full, read-only) gracefully without crashing.
- **FR-012**: The system MUST resume task ID generation from the maximum ID found in the loaded data file plus one.
- **FR-013**: The JSON file structure MUST support future extensibility (e.g., adding timestamps, tags, etc.).

### Key Entities

- **Task** (unchanged from Phase I):
  - `id` (integer): Unique identifier assigned at creation time
  - `title` (string): Non-empty string describing the task
  - `description` (string, optional): Additional details about the task
  - `completed` (boolean): Whether the task has been completed

- **PersistenceLayer** (new):
  - Responsible for loading tasks from `data/todo_data.json` on startup
  - Responsible for saving tasks to `data/todo_data.json` after every mutation
  - Handles file system errors and corruption detection
  - Implements atomic write operations

### JSON File Format

```json
{
  "version": "1.0",
  "tasks": [
    {
      "id": 1,
      "title": "Example Task",
      "description": "This is an example",
      "completed": false
    },
    {
      "id": 2,
      "title": "Another Task",
      "description": "",
      "completed": true
    }
  ]
}
```

### Assumptions

- The application runs on a POSIX-compliant file system (Linux, macOS) or Windows with Python 3.13+ standard library file operations.
- Task data files are small enough to fit in memory (reasonable limit: < 10MB or ~100,000 tasks).
- Only one instance of the application runs at a time (multi-instance locking is deferred to a future phase).
- The `data/` directory is relative to the application's working directory.
- File operations use UTF-8 encoding.
- Phase I skills remain the source of truth for business logic; the persistence layer is purely infrastructural.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of Phase I tests pass without modification against the Phase II implementation.
- **SC-002**: All task operations (add, update, delete, toggle) persist to `data/todo_data.json` immediately upon completion.
- **SC-003**: Application startup successfully loads all tasks from `data/todo_data.json` in < 1 second for files containing up to 1,000 tasks.
- **SC-004**: Corrupted JSON files are detected on startup with a user-friendly error message and recovery options are provided.
- **SC-005**: Atomic write operations ensure that the data file is never left in a partially written state.
- **SC-006**: The application gracefully handles missing directories, missing files, and file system errors without crashing.
- **SC-007**: The persistence layer is implemented as a separate module that does not modify Phase I skill signatures.
- **SC-008**: Task ID generation correctly resumes from the maximum ID in the loaded data file plus one.
- **SC-009**: The JSON file structure supports the `version` field for future schema migrations.
- **SC-010**: The application can handle edge cases (empty files, read-only files, disk full) with appropriate error messages and recovery paths.

## Non-Goals *(explicit exclusions)*

- Multi-instance concurrency control (file locking, conflict resolution)
- Cloud synchronization or remote storage
- Database integration (PostgreSQL, SQLite, etc.)
- Backup and restore features beyond corruption recovery
- Undo/redo functionality
- Performance optimization for > 10,000 tasks
- Encryption or data security features
- Import/export to other formats (CSV, XML, etc.)

## Technical Architecture Notes

### Persistence Strategy

The persistence layer will be implemented as a wrapper around Phase I skills:

1. **Initialization**: On application startup, load `data/todo_data.json` into memory and initialize Phase I's in-memory data structure.
2. **Interception**: Wrap each mutating operation (AddTask, UpdateTask, DeleteTask, ToggleTaskStatus) with a persistence hook that saves the state after the operation completes.
3. **Atomic Writes**: Use `json.dumps()` to serialize, write to `data/todo_data.json.tmp`, then `os.replace()` to atomically rename the file.
4. **Error Handling**: Catch `json.JSONDecodeError` for corruption detection, `PermissionError` and `OSError` for file system issues.

### File Structure

```
data/
  todo_data.json              # Current task data
  todo_data.json.corrupt.*    # Backup of corrupted files (timestamped)
```

### Compatibility with Phase I

Phase I skills will remain unchanged. The persistence layer will:
- Initialize the in-memory data structure by loading from the file
- Automatically save after every mutation without modifying skill signatures
- Be implemented as a separate module (e.g., `persistence.py`) that imports and wraps Phase I skills

## Open Questions

1. Should the application prompt the user before overwriting a corrupted file, or is automatic backup sufficient?
2. What is the maximum acceptable file size before we need to warn the user about performance degradation?
3. Should the version field in the JSON file trigger automatic migrations in future phases?

## Dependencies

- Phase I implementation (001-in-memory-todo) must be complete and tested
- Python 3.13+ standard library only (no external dependencies)
- `json` module for serialization/deserialization
- `os` and `pathlib` modules for file operations
- `datetime` module for timestamp generation in backup file names

## References

- Phase I Specification: `specs/001-in-memory-todo/spec.md`
- Constitution Amendment I: `.specify/memory/constitution.md` (Section: Amendments)
