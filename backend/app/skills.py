"""
Adapted Phase I skills for SQLModel database operations (Phase II).

This module contains the same business logic as Phase I but adapted to work
with SQLModel database operations instead of in-memory lists. The core behaviors
are preserved while adding user_id ownership and The Identity Law enforcement.
"""

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from app.models import Task


def create_task(user_id: int, title: str, description: Optional[str], db: Session) -> Task:
    """
    Create a new task for the specified user.

    Args:
        user_id: The ID of the user creating the task
        title: The task title
        description: Optional task description
        db: Database session

    Returns:
        The created Task object

    Raises:
        ValueError: If title is empty or whitespace-only
    """
    # Validate title (same logic as Phase I)
    if not title.strip():
        raise ValueError("Title cannot be empty or whitespace-only")

    # Create new task with user_id (The Identity Law)
    new_task = Task(
        user_id=user_id,
        title=title.strip(),
        description=description,
        completed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Add to database
    db.add(new_task)
    db.commit()
    db.refresh(new_task)  # Refresh to get the auto-generated ID

    return new_task


def get_user_tasks(user_id: int, db: Session) -> List[Task]:
    """
    Get all tasks for the specified user.

    Args:
        user_id: The ID of the user whose tasks to retrieve
        db: Database session

    Returns:
        List of Task objects belonging to the user
    """
    # Filter by user_id (The Identity Law enforcement)
    statement = select(Task).where(Task.user_id == user_id)
    tasks = db.exec(statement).all()
    return tasks


def update_task(task_id: int, user_id: int, title: str, description: Optional[str], db: Session) -> Optional[Task]:
    """
    Update an existing task for the specified user.

    Args:
        task_id: The ID of the task to update
        user_id: The ID of the user (for identity verification)
        title: New task title
        description: New task description
        db: Database session

    Returns:
        Updated Task object, or None if task not found

    Raises:
        ValueError: If title is empty or whitespace-only
    """
    # Validate title (same logic as Phase I)
    if not title.strip():
        raise ValueError("Title cannot be empty or whitespace-only")

    # Get task with user_id filter (The Identity Law enforcement)
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        return None

    # Update task properties
    task.title = title.strip()
    task.description = description
    task.updated_at = datetime.utcnow()

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def delete_task(task_id: int, user_id: int, db: Session) -> bool:
    """
    Delete a task for the specified user.

    Args:
        task_id: The ID of the task to delete
        user_id: The ID of the user (for identity verification)
        db: Database session

    Returns:
        True if task was deleted, False if task not found
    """
    # Get task with user_id filter (The Identity Law enforcement)
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        return False

    # Delete the task
    db.delete(task)
    db.commit()

    return True


def toggle_task_status(task_id: int, user_id: int, db: Session) -> Optional[Task]:
    """
    Toggle the completion status of a task for the specified user.

    Args:
        task_id: The ID of the task to toggle
        user_id: The ID of the user (for identity verification)
        db: Database session

    Returns:
        Updated Task object with toggled completion status, or None if task not found
    """
    # Get task with user_id filter (The Identity Law enforcement)
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        return None

    # Toggle completion status
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()

    # Commit changes
    db.add(task)
    db.commit()
    db.refresh(task)

    return task