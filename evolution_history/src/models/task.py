"""Task data model for the in-memory Todo application.

This module defines the Task dataclass that represents a single task
in the todo list. It follows the data model specification in
/specs/001-in-memory-todo/data-model.md
"""


from dataclasses import dataclass


@dataclass
class Task:
    """Represents a single task in the todo list.

    Attributes:
        id: Unique identifier assigned at creation time.
        title: Brief task description (must be non-empty).
        description: Optional detailed task information.
        completed: Completion status (False by default).

    Example:
        >>> task = Task(id=1, title="Buy groceries", description="Milk, eggs", completed=False)
        >>> print(task.title)
        Buy groceries
    """
    id: int
    title: str
    description: str | None = None
    completed: bool = False
