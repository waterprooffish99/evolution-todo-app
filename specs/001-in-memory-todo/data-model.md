# Data Model: In-Memory Console Todo Application

**Feature**: 001-in-memory-todo
**Created**: 2025-12-29

## Task Entity

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Unique, non-null, sequential | Unique identifier assigned at creation |
| `title` | String | Non-empty, non-whitespace-only | Brief task description |
| `description` | String | Optional (nullable) | Detailed task information |
| `completed` | Boolean | Default: False | Completion status |

### Validation Rules

| Rule | Enforcement Point | Error Message |
|------|-------------------|---------------|
| Title must not be empty | CLI input validation | "Title cannot be empty" |
| Title must not be whitespace-only | CLI input validation | "Title cannot be only whitespace" |

### State Transitions

| From State | Action | To State |
|------------|--------|----------|
| incomplete | toggle_status() | complete |
| complete | toggle_status() | incomplete |

No other state transitions occur for the Task entity.

## In-Memory Storage Structure

### Tasks Collection

```python
tasks: List[Task]  # Ordered list, index not used for lookup
```

Unique identifier assignment uses a counter:

```python
next_id: int = 1  # Increments on each task creation
```

### Storage Operations

| Operation | Data Structure | Complexity |
|-----------|----------------|------------|
| Add task | list.append() | O(1) |
| Get all tasks | list iteration | O(n) |
| Find by ID | list iteration | O(n) |
| Update task | list iteration + assignment | O(n) |
| Delete task | list removal | O(n) |
| Toggle status | list iteration + assignment | O(n) |

Note: O(n) complexity is acceptable for Phase I scope (single user, typical task count < 100).

## File Structure

```
src/
└── models/
    └── task.py      # Task dataclass and validation
```

## Code Reference

See `src/models/task.py` for the Task dataclass implementation.
See `src/skills/task_skills.py` for storage operations.
