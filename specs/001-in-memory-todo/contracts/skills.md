# Skills Contracts: In-Memory Console Todo Application

**Feature**: 001-in-memory-todo
**Created**: 2025-12-29

## Core Skills Overview

Each skill is a deterministic, reusable function independent of the CLI layer. Skills operate on in-memory state and follow consistent patterns for error handling.

## AddTask

Creates a new task with a unique identifier.

### Signature

```python
def AddTask(
    title: str,
    description: str | None,
    tasks: list[Task],
    next_id: int
) -> tuple[Task, list[Task], int]:
    """Add a new task to the in-memory task list.

    Args:
        title: Non-empty string describing the task.
        description: Optional detailed description of the task.
        tasks: Current list of tasks (in-memory state).
        next_id: Next available identifier for task assignment.

    Returns:
        tuple: (new_task, updated_tasks_list, updated_next_id)

    Side Effects:
        - Appends new task to tasks list
        - Increments next_id counter
    """
```

### Contract

| Aspect | Value |
|--------|-------|
| Input Validation | Title must be non-empty (caller responsibility) |
| Output | New Task object, updated list, updated counter |
| Side Effects | Modifies tasks list and next_id |
| Idempotent | No (creates new task each call) |
| Error Handling | Raises ValueError if title is empty/whitespace |

## GetTasks

Returns all tasks without modifying state.

### Signature

```python
def GetTasks(tasks: list[Task]) -> list[Task]:
    """Retrieve all tasks from in-memory storage.

    Args:
        tasks: Current list of tasks (in-memory state).

    Returns:
        Copy of the current tasks list.

    Side Effects:
        None (read-only operation)
    """
```

### Contract

| Aspect | Value |
|--------|-------|
| Input Validation | None required |
| Output | Copy of tasks list |
| Side Effects | None |
| Idempotent | Yes |
| Error Handling | Returns empty list if no tasks |

## UpdateTask

Modifies an existing task's title and/or description.

### Signature

```python
def UpdateTask(
    task_id: int,
    title: str | None,
    description: str | None,
    tasks: list[Task]
) -> tuple[Task | None, list[Task]]:
    """Update an existing task by identifier.

    Args:
        task_id: Unique identifier of task to update.
        title: New title (None to keep existing).
        description: New description (None to keep existing).
        tasks: Current list of tasks (in-memory state).

    Returns:
        tuple: (updated_task_or_none, updated_tasks_list)

    Side Effects:
        Modifies task in tasks list if found
    """
```

### Contract

| Aspect | Value |
|--------|-------|
| Input Validation | task_id must exist in tasks (caller responsibility) |
| Output | Updated Task object or None if not found |
| Side Effects | Modifies task in place if found |
| Idempotent | Yes (multiple identical updates produce same result) |
| Error Handling | Returns None if task_id not found |

## DeleteTask

Removes a task by identifier.

### Signature

```python
def DeleteTask(
    task_id: int,
    tasks: list[Task]
) -> tuple[bool, list[Task]]:
    """Delete a task by identifier.

    Args:
        task_id: Unique identifier of task to delete.
        tasks: Current list of tasks (in-memory state).

    Returns:
        tuple: (deletion_successful, updated_tasks_list)

    Side Effects:
        Removes task from tasks list if found
    """
```

### Contract

| Aspect | Value |
|--------|-------|
| Input Validation | task_id must exist in tasks (caller responsibility) |
| Output | (True, updated_list) or (False, original_list) |
| Side Effects | Removes task from list if found |
| Idempotent | Yes (deleting non-existent task returns False) |
| Error Handling | Returns (False, original_list) if not found |

## ToggleTaskStatus

Switches a task's completion status between complete and incomplete.

### Signature

```python
def ToggleTaskStatus(
    task_id: int,
    tasks: list[Task]
) -> tuple[Task | None, list[Task]]:
    """Toggle task completion status.

    Args:
        task_id: Unique identifier of task to toggle.
        tasks: Current list of tasks (in-memory state).

    Returns:
        tuple: (updated_task_or_none, updated_tasks_list)

    Side Effects:
        Modifies task's completed field if found
    """
```

### Contract

| Aspect | Value |
|--------|-------|
| Input Validation | task_id must exist in tasks (caller responsibility) |
| Output | Updated Task object or None if not found |
| Side Effects | Flips completed boolean if found |
| Idempotent | Yes (calling twice returns to original state) |
| Error Handling | Returns None if task_id not found |

## State Management

### In-Memory State Structure

```python
class TaskState:
    """Container for all in-memory state."""
    tasks: list[Task]
    next_id: int
```

### State Flow

```
CLI Input
    │
    ▼
CLI Validation (title non-empty, task_id exists)
    │
    ▼
Skill Call (with current state)
    │
    ▼
Skill Returns (modified state)
    │
    ▼
CLI Displays Result
```

## File Reference

All skills implemented in: `src/skills/task_skills.py`
Task model defined in: `src/models/task.py`
