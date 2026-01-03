"""Core skills for the in-memory Todo application.

This module implements reusable, deterministic business logic for task management.
All skills follow the contracts defined in /specs/001-in-memory-todo/contracts/skills.md

These skills are designed to be MCP-ready:
- Deterministic (same inputs always produce same outputs)
- Explicit inputs and outputs
- No direct user input/output
- Independently callable without CLI dependency
"""

from typing import List

from src.models.task import Task


def AddTask(
    title: str,
    description: str | None,
    tasks: List[Task],
    next_id: int
) -> tuple[Task, List[Task], int]:
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

    Example:
        >>> tasks = []
        >>> new_task, updated_tasks, next_id = AddTask("Buy milk", "2% preferred", [], 1)
        >>> new_task.id
        1
        >>> len(updated_tasks)
        1
    """
    # Create the new task with the next available ID
    new_task = Task(
        id=next_id,
        title=title,
        description=description,
        completed=False
    )

    # Add to the tasks list
    updated_tasks = tasks + [new_task]

    # Increment the ID counter
    updated_next_id = next_id + 1

    return new_task, updated_tasks, updated_next_id


def GetTasks(tasks: List[Task]) -> List[Task]:
    """Retrieve all tasks from in-memory storage.

    Args:
        tasks: Current list of tasks (in-memory state).

    Returns:
        Copy of the current tasks list.

    Side Effects:
        None (read-only operation)

    Example:
        >>> tasks = [Task(id=1, title="Task 1")]
        >>> GetTasks(tasks)
        [Task(id=1, title='Task 1', completed=False)]
    """
    # Return a copy to prevent accidental modification
    return list(tasks)


def UpdateTask(
    task_id: int,
    title: str | None,
    description: str | None,
    tasks: List[Task]
) -> tuple[Task | None, List[Task]]:
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

    Example:
        >>> task = Task(id=1, title="Old title")
        >>> updated, new_list = UpdateTask(1, "New title", None, [task])
        >>> updated.title
        'New title'
    """
    # Find the task by ID
    for i, task in enumerate(tasks):
        if task.id == task_id:
            # Create updated task with new values (keep existing if None)
            new_title = title if title is not None else task.title
            new_description = description if description is not None else task.description

            updated_task = Task(
                id=task.id,
                title=new_title,
                description=new_description,
                completed=task.completed
            )

            # Create new list with updated task
            updated_tasks = tasks.copy()
            updated_tasks[i] = updated_task

            return updated_task, updated_tasks

    # Task not found
    return None, tasks


def DeleteTask(
    task_id: int,
    tasks: List[Task]
) -> tuple[bool, List[Task]]:
    """Delete a task by identifier.

    Args:
        task_id: Unique identifier of task to delete.
        tasks: Current list of tasks (in-memory state).

    Returns:
        tuple: (deletion_successful, updated_tasks_list)

    Side Effects:
        Removes task from tasks list if found

    Example:
        >>> task = Task(id=1, title="To delete")
        >>> success, new_list = DeleteTask(1, [task])
        >>> success
        True
        >>> len(new_list)
        0
    """
    # Find and remove the task
    for i, task in enumerate(tasks):
        if task.id == task_id:
            # Create new list without the task
            updated_tasks = tasks[:i] + tasks[i+1:]
            return True, updated_tasks

    # Task not found
    return False, list(tasks)


def ToggleTaskStatus(
    task_id: int,
    tasks: List[Task]
) -> tuple[Task | None, List[Task]]:
    """Toggle task completion status.

    Args:
        task_id: Unique identifier of task to toggle.
        tasks: Current list of tasks (in-memory state).

    Returns:
        tuple: (updated_task_or_none, updated_tasks_list)

    Side Effects:
        Flips completed boolean if found

    Example:
        >>> task = Task(id=1, title="Task", completed=False)
        >>> toggled, new_list = ToggleTaskStatus(1, [task])
        >>> toggled.completed
        True
    """
    # Find the task by ID
    for i, task in enumerate(tasks):
        if task.id == task_id:
            # Create updated task with toggled status
            updated_task = Task(
                id=task.id,
                title=task.title,
                description=task.description,
                completed=not task.completed
            )

            # Create new list with updated task
            updated_tasks = tasks.copy()
            updated_tasks[i] = updated_task

            return updated_task, updated_tasks

    # Task not found
    return None, list(tasks)
