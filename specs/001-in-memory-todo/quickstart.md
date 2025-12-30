# Quickstart: In-Memory Console Todo Application

**Feature**: 001-in-memory-todo
**Created**: 2025-12-29

## Prerequisites

- Python 3.13 or higher
- No external dependencies required

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd evolution-todo-app

# Verify Python version
python3 --version  # Should show 3.13+
```

## Running the Application

```bash
python3 src/app.py
```

## Menu Options

The application presents a menu-driven interface:

```
=== Todo Application ===
1. Add a new task
2. View all tasks
3. Update a task
4. Delete a task
5. Toggle task completion
6. Exit

Enter your choice (1-6):
```

### Option 1: Add a New Task

```
Enter task title: Buy groceries
Enter description (optional): Milk, eggs, bread
Task added successfully! (ID: 1)
```

### Option 2: View All Tasks

```
=== Tasks ===
1. [ ] Buy groceries
   Description: Milk, eggs, bread

No tasks yet.
```

### Option 3: Update a Task

```
Enter task ID to update: 1
Enter new title (leave empty to keep current):
Enter new description (leave empty to keep current): Milk, eggs, bread, cheese
Task updated successfully!
```

### Option 4: Delete a Task

```
Enter task ID to delete: 1
Task deleted successfully!
```

### Option 5: Toggle Task Completion

```
Enter task ID to toggle: 1
Task marked as complete!
```

## Testing

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run skill tests only
python3 -m pytest tests/unit/test_skills.py -v

# Run integration tests only
python3 -m pytest tests/integration/test_cli.py -v
```

## Project Structure

```
src/
├── app.py           # Entry point
├── models/
│   └── task.py      # Task data class
├── skills/
│   └── task_skills.py  # Core business logic
└── cli/
    └── todo_menu.py # CLI orchestrator

tests/
├── unit/
│   └── test_skills.py   # Skills tests
└── integration/
    └── test_cli.py      # CLI integration tests
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│         src/app.py                  │
│         (Entry Point)               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        src/cli/todo_menu.py         │
│        (CLI Orchestrator)           │
│  - Displays menu                    │
│  - Collects user input              │
│  - Validates basic input            │
│  - Delegates to skills              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│       src/skills/task_skills.py     │
│       (Reusable Skills)             │
│  - AddTask                          │
│  - GetTasks                         │
│  - UpdateTask                       │
│  - DeleteTask                       │
│  - ToggleTaskStatus                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│        src/models/task.py           │
│        (Data Model)                 │
│  - Task dataclass                   │
│  - Validation rules                 │
└─────────────────────────────────────┘
```

## Key Principles

1. **Skills are independent**: Core functions can be called directly without CLI
2. **No persistence**: Data is session-only, lost on exit
3. **No file I/O**: All data stays in memory
4. **Human-readable**: Clear output, simple flows
