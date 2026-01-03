"""
REST API endpoints for task management with JWT authentication and The Identity Law enforcement.

This module implements the 5 REST endpoints for task CRUD operations:
- GET /api/{user_id}/tasks - Get all tasks for a user
- POST /api/{user_id}/tasks - Create a new task for a user
- PUT /api/{user_id}/tasks/{task_id} - Update an existing task
- DELETE /api/{user_id}/tasks/{task_id} - Delete a task
- PATCH /api/{user_id}/tasks/{task_id}/complete - Toggle task completion status

All endpoints require valid JWT authentication and enforce The Identity Law
by ensuring URL user_id matches JWT user_id.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from app.database import get_session
from app.auth import verify_token, check_user_authorization
from app.models import Task
from app.skills import (
    create_task as create_task_skill,
    get_user_tasks as get_user_tasks_skill,
    update_task as update_task_skill,
    delete_task as delete_task_skill,
    toggle_task_status as toggle_task_status_skill
)


# Pydantic models for request/response validation
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional task description")

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: str | None = Field(None, max_length=1000, description="Optional task description")

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries (updated)",
                "description": "Milk, eggs, bread, cheese"
            }
        }


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True  # Allow creation from SQLModel objects
        schema_extra = {
            "example": {
                "id": 42,
                "user_id": 123,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-01T10:30:00Z",
                "updated_at": "2026-01-01T10:30:00Z"
            }
        }


class TasksResponse(BaseModel):
    tasks: List[TaskResponse]

    class Config:
        schema_extra = {
            "example": {
                "tasks": [
                    {
                        "id": 1,
                        "user_id": 123,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-01-01T10:00:00Z",
                        "updated_at": "2026-01-01T10:00:00Z"
                    }
                ]
            }
        }


# API Router
router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


@router.get("/", response_model=TasksResponse)
def get_tasks(
    user_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Get all tasks for the specified user.

    Args:
        user_id: The ID of the user whose tasks to retrieve (from URL)
        authenticated_user_id: The ID of the authenticated user (from JWT)
        db: Database session

    Returns:
        TasksResponse containing list of user's tasks

    Raises:
        HTTPException(403): If URL user_id doesn't match JWT user_id
    """
    # Enforce The Identity Law: URL user_id must match JWT user_id
    check_user_authorization(authenticated_user_id, user_id)

    # Get user's tasks from database
    tasks = get_user_tasks_skill(user_id, db)

    # Convert to response format
    task_responses = [TaskResponse.from_orm(task) for task in tasks]
    return TasksResponse(tasks=task_responses)


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    user_id: int,
    task_data: TaskCreate,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Create a new task for the specified user.

    Args:
        user_id: The ID of the user creating the task (from URL)
        task_data: Task creation data (title, description)
        authenticated_user_id: The ID of the authenticated user (from JWT)
        db: Database session

    Returns:
        TaskResponse containing the created task

    Raises:
        HTTPException(400): If title is invalid
        HTTPException(403): If URL user_id doesn't match JWT user_id
    """
    # Enforce The Identity Law: URL user_id must match JWT user_id
    check_user_authorization(authenticated_user_id, user_id)

    try:
        # Create task in database
        task = create_task_skill(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            db=db
        )
        return TaskResponse.from_orm(task)
    except ValueError as e:
        # Title validation failed
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Update an existing task for the specified user.

    Args:
        user_id: The ID of the user (from URL)
        task_id: The ID of the task to update
        task_data: Task update data (title, description)
        authenticated_user_id: The ID of the authenticated user (from JWT)
        db: Database session

    Returns:
        TaskResponse containing the updated task

    Raises:
        HTTPException(400): If title is invalid
        HTTPException(403): If URL user_id doesn't match JWT user_id
        HTTPException(404): If task not found
    """
    # Enforce The Identity Law: URL user_id must match JWT user_id
    check_user_authorization(authenticated_user_id, user_id)

    # Update task in database
    task = update_task_skill(
        task_id=task_id,
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        db=db
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.from_orm(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    user_id: int,
    task_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Delete a task for the specified user.

    Args:
        user_id: The ID of the user (from URL)
        task_id: The ID of the task to delete
        authenticated_user_id: The ID of the authenticated user (from JWT)
        db: Database session

    Raises:
        HTTPException(403): If URL user_id doesn't match JWT user_id
        HTTPException(404): If task not found
    """
    # Enforce The Identity Law: URL user_id must match JWT user_id
    check_user_authorization(authenticated_user_id, user_id)

    # Delete task from database
    deleted = delete_task_skill(task_id=task_id, user_id=user_id, db=db)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def toggle_task_completion(
    user_id: int,
    task_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """
    Toggle the completion status of a task for the specified user.

    Args:
        user_id: The ID of the user (from URL)
        task_id: The ID of the task to toggle
        authenticated_user_id: The ID of the authenticated user (from JWT)
        db: Database session

    Returns:
        TaskResponse containing the task with toggled completion status

    Raises:
        HTTPException(403): If URL user_id doesn't match JWT user_id
        HTTPException(404): If task not found
    """
    # Enforce The Identity Law: URL user_id must match JWT user_id
    check_user_authorization(authenticated_user_id, user_id)

    # Toggle task completion in database
    task = toggle_task_status_skill(task_id=task_id, user_id=user_id, db=db)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse.from_orm(task)