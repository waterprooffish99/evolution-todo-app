"""
SQLModel database schemas for Evolution Todo Application (Phase II)

This module defines the User and Task models using SQLModel, which combines
SQLAlchemy (ORM) and Pydantic (validation) for type-safe database operations.
"""

from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    """
    User account model (managed by Better Auth).

    Attributes:
        id: Auto-incrementing primary key
        email: Unique user email (used for login)
        password_hash: Bcrypt hashed password (never exposed in API)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        tasks: Relationship to user's tasks (one-to-many)
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """
    Task model with user ownership (The Identity Law).

    Attributes:
        id: Auto-incrementing primary key
        user_id: Foreign key to User (owner of this task)
        title: Task title (1-255 characters, non-empty)
        description: Optional task description (up to 1000 characters)
        completed: Completion status (default: False)
        created_at: Task creation timestamp
        updated_at: Last modification timestamp
        user: Relationship to task owner
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)
    title: str = Field(max_length=255, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional[User] = Relationship(back_populates="tasks")
