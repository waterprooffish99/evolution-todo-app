# Data Model: Full-Stack Web Evolution

**Feature**: 002-web-evolution
**Date**: 2026-01-01
**Status**: Phase 1 Design

## Overview

Phase II introduces a multi-tenant web application with user authentication and cloud database persistence. The data model extends Phase I's Task entity with user ownership and adds a User entity managed by Better Auth.

---

## Entities

### User (Better Auth Managed)

**Definition**: Represents an authenticated user account. Managed by Better Auth but referenced in the database.

**Attributes**:

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | int | Yes | > 0 | Auto-increment | Primary key, unique identifier |
| `email` | str | Yes | Valid email format | N/A | Unique, used for login |
| `password_hash` | str | Yes | Bcrypt hash | N/A | Managed by Better Auth |
| `created_at` | datetime | Yes | Valid timestamp | `datetime.utcnow()` | Account creation time |
| `updated_at` | datetime | Yes | Valid timestamp | `datetime.utcnow()` | Last update time |

**Invariants**:
- `email` must be unique across all users
- `password_hash` is never exposed in API responses
- `id` is used as foreign key in Task entity

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
```

**Indexes**:
- Primary key: `id`
- Unique index: `email`

**Example**:
```json
{
  "id": 123,
  "email": "user@example.com",
  "created_at": "2026-01-01T10:00:00Z",
  "updated_at": "2026-01-01T10:00:00Z"
}
```

**Note**: `password_hash` is never included in API responses.

---

### Task (Extended from Phase I)

**Definition**: Represents a single todo item owned by a user. Extended from Phase I with user ownership and timestamps.

**Attributes**:

| Field | Type | Required | Validation | Default | Notes |
|-------|------|----------|------------|---------|-------|
| `id` | int | Yes | > 0 | Auto-increment | Primary key, unique identifier |
| `user_id` | int | Yes | Valid User.id | N/A | Foreign key to User (THE IDENTITY LAW) |
| `title` | str | Yes | 1-255 chars, non-whitespace | N/A | Task description |
| `description` | str | No | 0-1000 chars | `None` | Optional details |
| `completed` | bool | Yes | True/False | `False` | Completion status |
| `created_at` | datetime | Yes | Valid timestamp | `datetime.utcnow()` | Task creation time |
| `updated_at` | datetime | Yes | Valid timestamp | `datetime.utcnow()` | Last modification time |

**Invariants**:
- `user_id` must reference a valid User
- `title` cannot be empty or whitespace-only
- `completed` is always a boolean (no null states)
- `created_at` <= `updated_at`

**State Transitions**:
```
[New Task] --POST /api/{user_id}/tasks--> [Incomplete]
    ↓
[Incomplete] --PATCH /complete--> [Complete]
    ↑                                  ↓
    └─────────PATCH /complete──────────┘

[Any State] --PUT--> [Same State, modified title/description, updated_at changed]
[Any State] --DELETE--> [Removed from database]
```

**SQLModel Definition**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
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

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 123,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "created_at": "2026-01-01T10:00:00Z",
                "updated_at": "2026-01-01T10:00:00Z"
            }
        }
```

**Indexes**:
- Primary key: `id`
- Foreign key index: `user_id` (for efficient user-based queries)
- Composite index: `(user_id, id)` for identity-filtered lookups

**Database Constraints**:
```sql
-- Foreign key constraint (enforced by SQLModel)
ALTER TABLE tasks
ADD CONSTRAINT fk_tasks_user_id
FOREIGN KEY (user_id) REFERENCES user(id)
ON DELETE CASCADE;

-- Check constraint for title
ALTER TABLE tasks
ADD CONSTRAINT check_title_not_empty
CHECK (LENGTH(TRIM(title)) > 0);
```

**Example**:
```json
{
  "id": 42,
  "user_id": 123,
  "title": "Complete Phase II specification",
  "description": "Write comprehensive data model documentation",
  "completed": false,
  "created_at": "2026-01-01T10:30:00Z",
  "updated_at": "2026-01-01T10:30:00Z"
}
```

---

## Pydantic Request/Response Models

### Task Creation Request

**Used for**: POST /api/{user_id}/tasks

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Optional task description")

    @validator('title')
    def title_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread"
            }
        }
```

---

### Task Update Request

**Used for**: PUT /api/{user_id}/tasks/{id}

```python
class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    class Config:
        schema_extra = {
            "example": {
                "title": "Buy groceries (updated)",
                "description": "Milk, eggs, bread, cheese"
            }
        }
```

---

### Task Response

**Used for**: All task endpoints (GET, POST, PUT, PATCH)

```python
from datetime import datetime

class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
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
```

---

### Tasks List Response

**Used for**: GET /api/{user_id}/tasks

```python
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
                    },
                    {
                        "id": 2,
                        "user_id": 123,
                        "title": "Write report",
                        "description": None,
                        "completed": True,
                        "created_at": "2026-01-01T11:00:00Z",
                        "updated_at": "2026-01-01T12:00:00Z"
                    }
                ]
            }
        }
```

---

## Relationships

### One-to-Many: User → Tasks

**Relationship**: One User has many Tasks

**Cardinality**: 1:N

**Foreign Key**: `tasks.user_id` references `user.id`

**Cascade Behavior**: `ON DELETE CASCADE` (deleting a user deletes all their tasks)

**SQLModel Relationship**:
```python
# User side
class User(SQLModel, table=True):
    tasks: List["Task"] = Relationship(back_populates="user")

# Task side
class Task(SQLModel, table=True):
    user: Optional[User] = Relationship(back_populates="tasks")
```

**Query Examples**:
```python
# Get all tasks for a user
user = db.query(User).filter(User.id == user_id).first()
tasks = user.tasks  # SQLModel loads related tasks

# Or direct query (preferred for The Identity Law)
tasks = db.query(Task).filter(Task.user_id == user_id).all()
```

---

## Database Schema (PostgreSQL DDL)

```sql
-- Users table
CREATE TABLE user (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Index on email for faster login lookups
CREATE INDEX idx_user_email ON user(email);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Foreign key constraint
    CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id)
        REFERENCES user(id)
        ON DELETE CASCADE,

    -- Check constraint
    CONSTRAINT check_title_not_empty
        CHECK (LENGTH(TRIM(title)) > 0)
);

-- Indexes for efficient queries
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_user_id_id ON tasks(user_id, id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
```

---

## Validation Rules

### Task Validation

**Title**:
- **Required**: Yes
- **Min length**: 1 (after trimming whitespace)
- **Max length**: 255 characters
- **Regex**: `^(?!\s*$).+` (not empty or whitespace-only)
- **Error**: `400 Bad Request` with message "Title cannot be empty"

**Description**:
- **Required**: No (optional)
- **Min length**: 0
- **Max length**: 1000 characters
- **Null allowed**: Yes

**Completed**:
- **Type**: Boolean
- **Default**: `false`
- **Allowed values**: `true`, `false`

---

### User Validation

**Email**:
- **Required**: Yes
- **Format**: Valid email (RFC 5322)
- **Unique**: Yes (enforced by database)
- **Max length**: 255 characters
- **Regex**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`

**Password** (handled by Better Auth):
- **Min length**: 8 characters
- **Requirements**: At least one uppercase, one lowercase, one number
- **Hashing**: Bcrypt with cost factor 12

---

## Data Access Patterns

### The Identity Law (Mandatory)

**Every query MUST filter by authenticated user_id**:

```python
# ✅ CORRECT - Always filter by user_id
def get_user_tasks(user_id: int, db: Session):
    return db.query(Task).filter(Task.user_id == user_id).all()

def get_user_task(task_id: int, user_id: int, db: Session):
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id  # Critical for security
    ).first()

# ❌ WRONG - Missing user_id filter (SECURITY VIOLATION)
def get_task_wrong(task_id: int, db: Session):
    return db.query(Task).filter(Task.id == task_id).first()  # NO!
```

---

### Common Query Patterns

**1. Get all tasks for a user**:
```python
tasks = db.query(Task).filter(Task.user_id == user_id).all()
```

**2. Get a specific task (with identity check)**:
```python
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id
).first()

if not task:
    raise HTTPException(status_code=404, detail="Task not found")
```

**3. Create a task**:
```python
new_task = Task(
    user_id=user_id,
    title=task_data.title,
    description=task_data.description,
    completed=False
)
db.add(new_task)
db.commit()
db.refresh(new_task)
return new_task
```

**4. Update a task**:
```python
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id
).first()

if not task:
    raise HTTPException(status_code=404, detail="Task not found")

task.title = task_data.title
task.description = task_data.description
task.updated_at = datetime.utcnow()
db.commit()
db.refresh(task)
return task
```

**5. Toggle task completion**:
```python
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id
).first()

if not task:
    raise HTTPException(status_code=404, detail="Task not found")

task.completed = not task.completed
task.updated_at = datetime.utcnow()
db.commit()
db.refresh(task)
return task
```

**6. Delete a task**:
```python
task = db.query(Task).filter(
    Task.id == task_id,
    Task.user_id == user_id
).first()

if not task:
    raise HTTPException(status_code=404, detail="Task not found")

db.delete(task)
db.commit()
return {"message": "Task deleted"}
```

---

## Error Cases & HTTP Status Codes

| Scenario | HTTP Status | Response Body |
|----------|-------------|---------------|
| Task created successfully | 201 Created | TaskResponse |
| Task retrieved successfully | 200 OK | TaskResponse |
| Tasks list retrieved | 200 OK | TasksResponse |
| Task updated successfully | 200 OK | TaskResponse |
| Task deleted successfully | 204 No Content | Empty |
| Task toggled successfully | 200 OK | TaskResponse |
| Missing JWT token | 401 Unauthorized | `{"detail": "Unauthorized"}` |
| Invalid JWT token | 401 Unauthorized | `{"detail": "Invalid token"}` |
| URL user_id != JWT user_id | 403 Forbidden | `{"detail": "Forbidden"}` |
| Task not found or wrong user | 404 Not Found | `{"detail": "Task not found"}` |
| Invalid input (empty title) | 400 Bad Request | `{"detail": "Title cannot be empty"}` |
| Server error | 500 Internal Server Error | `{"detail": "Internal server error"}` |

---

## Testing Data Scenarios

### Happy Path
1. **User with no tasks**: Empty tasks list
2. **User with one task**: Single task returned
3. **User with multiple tasks**: All tasks for user returned
4. **Task completion toggle**: Status changes correctly
5. **Task update**: Title/description change correctly

### Edge Cases
1. **Empty title**: Rejected with 400
2. **Whitespace-only title**: Rejected with 400
3. **Very long title** (256+ chars): Rejected with 400
4. **Very long description** (1001+ chars): Rejected with 400
5. **Null description**: Accepted (optional field)
6. **Special characters in title**: Accepted (Unicode support)
7. **Concurrent updates**: Last write wins (updated_at changes)

### Security Cases
1. **User A tries to access User B's task**: 404 Not Found
2. **User A tries to update User B's task**: 404 Not Found
3. **User A tries to delete User B's task**: 404 Not Found
4. **No JWT provided**: 401 Unauthorized
5. **Invalid JWT**: 401 Unauthorized
6. **Expired JWT**: 401 Unauthorized
7. **URL user_id doesn't match JWT user_id**: 403 Forbidden

---

## Migration Strategy

### From Phase I to Phase II

**Phase I Model** (in-memory):
```python
@dataclass
class Task:
    id: int
    title: str
    description: str | None
    completed: bool
```

**Phase II Model** (SQLModel):
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")  # NEW
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)  # NEW
    updated_at: datetime = Field(default_factory=datetime.utcnow)  # NEW
```

**Key Changes**:
- **Added**: `user_id` (foreign key)
- **Added**: `created_at` timestamp
- **Added**: `updated_at` timestamp
- **Changed**: `id` is now `Optional[int]` (auto-generated by database)
- **Changed**: `description` is now `Optional[str]` (Pydantic/SQLModel convention)

**Migration Script** (Alembic):
```python
# alembic/versions/001_initial_schema.py
def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('completed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE')
    )

    op.create_index('idx_user_email', 'user', ['email'])
    op.create_index('idx_tasks_user_id', 'tasks', ['user_id'])

def downgrade():
    op.drop_table('tasks')
    op.drop_table('user')
```

---

## Summary

**Phase II Data Model**:
- **2 entities**: User, Task
- **1 relationship**: User → Tasks (1:N)
- **User isolation**: All queries filtered by `user_id` (The Identity Law)
- **Timestamps**: `created_at`, `updated_at` on all entities
- **Validation**: Pydantic models for input/output
- **SQLModel**: Type-safe ORM with automatic validation

**Database**: PostgreSQL (Neon Serverless)
**ORM**: SQLModel
**Migrations**: Alembic

**Next Step**: Generate API contracts (OpenAPI specification)
