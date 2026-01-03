# Quickstart: Full-Stack Web Evolution Implementation

**Feature**: 002-web-evolution
**Audience**: Developers implementing Phase II
**Date**: 2026-01-01

## Overview

This guide walks you through implementing the full-stack web application migration from Phase I console app to a production-ready web application with Next.js frontend, FastAPI backend, Neon PostgreSQL database, and Better Auth authentication.

**Time Estimate**: 8-12 hours (split across backend and frontend)

---

## Prerequisites

### Required Software
- [ ] **Node.js**: 18+ and npm/yarn/pnpm
- [ ] **Python**: 3.13+
- [ ] **PostgreSQL Client**: psql (for database inspection)
- [ ] **Git**: For version control

### Required Accounts
- [ ] **Neon Account**: Create at https://neon.tech (free tier sufficient)
- [ ] **Vercel Account** (optional): For frontend deployment
- [ ] **Fly.io/Railway Account** (optional): For backend deployment

### Verify Prerequisites
```bash
# Check Node.js
node --version  # Should be 18+

# Check Python
python3 --version  # Should be 3.13+

# Check npm/yarn
npm --version

# Confirm you're on the right branch
git branch  # Should show * 002-web-evolution
```

---

## Part 1: Backend Setup (FastAPI + Neon PostgreSQL)

### Step 1: Create Backend Project Structure

```bash
# Create backend directory
mkdir -p backend/app/api
cd backend

# Create necessary files
touch app/__init__.py
touch app/main.py
touch app/auth.py
touch app/models.py
touch app/skills.py
touch app/database.py
touch app/api/__init__.py
touch app/api/tasks.py
touch requirements.txt
touch .env
```

**Project Structure**:
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app initialization
│   ├── auth.py          # JWT verification middleware
│   ├── models.py        # SQLModel schemas (User, Task)
│   ├── skills.py        # Adapted Phase I skills
│   ├── database.py      # Neon connection setup
│   └── api/
│       ├── __init__.py
│       └── tasks.py     # Task CRUD endpoints
├── requirements.txt
├── .env
└── alembic/             # (Created later for migrations)
```

---

### Step 2: Install Python Dependencies

**File**: `backend/requirements.txt`

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
python-dotenv==1.0.1
alembic==1.13.1
pydantic[email]==2.6.0
```

**Install**:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### Step 3: Set Up Neon PostgreSQL Database

1. **Create Neon Project**:
   - Go to https://neon.tech
   - Click "Create Project"
   - Name: `evolution-todo`
   - Region: Choose closest to your location
   - PostgreSQL version: 16+

2. **Get Connection String**:
   - After creation, copy the connection string
   - Format: `postgresql://user:password@ep-xyz.region.aws.neon.tech/dbname?sslmode=require`

3. **Configure Environment Variables**:

**File**: `backend/.env`

```env
# Database
DATABASE_URL=postgresql://user:password@ep-xyz.region.aws.neon.tech/evolution-todo?sslmode=require

# Authentication (shared with frontend)
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long-change-in-production

# CORS (Next.js frontend URL)
ALLOWED_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
```

**Generate a secure secret**:
```bash
# Linux/macOS
openssl rand -base64 32

# Python (any OS)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### Step 4: Implement SQLModel Schemas

**File**: `backend/app/models.py`

```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional, List

class User(SQLModel, table=True):
    """User account (managed by Better Auth)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")


class Task(SQLModel, table=True):
    """Task owned by a user"""
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
```

---

### Step 5: Set Up Database Connection

**File**: `backend/app/database.py`

```python
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv("ENVIRONMENT") == "development" else False,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,
    max_overflow=10
)

def create_db_and_tables():
    """Create all tables (use only in development, use Alembic in production)"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get database session"""
    with Session(engine) as session:
        yield session
```

---

### Step 6: Implement JWT Verification

**File**: `backend/app/auth.py`

```python
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET")
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> int:
    """
    Verify JWT token and extract user_id.

    Returns:
        int: Authenticated user_id

    Raises:
        HTTPException: 401 if token is invalid or expired
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing user_id")
        return user_id
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
```

---

### Step 7: Adapt Phase I Skills to SQLModel

**File**: `backend/app/skills.py`

```python
from sqlmodel import Session, select
from app.models import Task
from fastapi import HTTPException
from datetime import datetime
from typing import List, Optional

def create_task(user_id: int, title: str, description: Optional[str], db: Session) -> Task:
    """
    Adapted from Phase I AddTask skill.
    Creates a new task for the authenticated user.
    """
    # Phase I validation logic preserved
    if not title or title.strip() == "":
        raise ValueError("Title cannot be empty")

    # Create task (adapted to SQLModel)
    new_task = Task(
        user_id=user_id,
        title=title.strip(),
        description=description,
        completed=False
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def get_user_tasks(user_id: int, db: Session) -> List[Task]:
    """
    Adapted from Phase I GetTasks skill.
    Retrieves all tasks for the authenticated user.
    """
    statement = select(Task).where(Task.user_id == user_id)
    return db.exec(statement).all()


def update_task(task_id: int, user_id: int, title: str, description: Optional[str], db: Session) -> Task:
    """
    Adapted from Phase I UpdateTask skill.
    Updates an existing task (with identity check).
    """
    # Phase I validation preserved
    if not title or title.strip() == "":
        raise ValueError("Title cannot be empty")

    # Find task with identity check
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task
    task.title = title.strip()
    task.description = description
    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def delete_task(task_id: int, user_id: int, db: Session) -> None:
    """
    Adapted from Phase I DeleteTask skill.
    Deletes a task (with identity check).
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()


def toggle_task_status(task_id: int, user_id: int, db: Session) -> Task:
    """
    Adapted from Phase I ToggleTaskStatus skill.
    Toggles task completion status (with identity check).
    """
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db.exec(statement).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Toggle completion
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

---

### Step 8: Implement Task API Endpoints

**File**: `backend/app/api/tasks.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.auth import verify_token
from app.skills import (
    create_task,
    get_user_tasks,
    update_task,
    delete_task,
    toggle_task_status
)
from app.models import Task
from pydantic import BaseModel, Field, validator
from typing import Optional, List

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])

# Request models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be whitespace')
        return v


class TaskUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be whitespace')
        return v


@router.get("")
async def get_tasks(
    user_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """Get all tasks for authenticated user"""
    if authenticated_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    tasks = get_user_tasks(user_id, db)
    return {"tasks": tasks}


@router.post("", status_code=201)
async def create_new_task(
    user_id: int,
    task_data: TaskCreate,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """Create a new task"""
    if authenticated_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = create_task(user_id, task_data.title, task_data.description, db)
    return task


@router.put("/{task_id}")
async def update_existing_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """Update an existing task"""
    if authenticated_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = update_task(task_id, user_id, task_data.title, task_data.description, db)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_existing_task(
    user_id: int,
    task_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """Delete a task"""
    if authenticated_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    delete_task(task_id, user_id, db)
    return None


@router.patch("/{task_id}/complete")
async def toggle_completion(
    user_id: int,
    task_id: int,
    authenticated_user_id: int = Depends(verify_token),
    db: Session = Depends(get_session)
):
    """Toggle task completion status"""
    if authenticated_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    task = toggle_task_status(task_id, user_id, db)
    return task
```

---

### Step 9: Initialize FastAPI App

**File**: `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.api.tasks import router as tasks_router
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Evolution Todo API",
    description="Multi-tenant todo application with JWT authentication",
    version="2.0.0"
)

# CORS configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks_router)

@app.on_event("startup")
def on_startup():
    """Create database tables on startup (dev only)"""
    create_db_and_tables()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

### Step 10: Run Backend Server

```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test the API**:
```bash
# Health check (no auth required)
curl http://localhost:8000/health

# View auto-generated API docs
open http://localhost:8000/docs  # Swagger UI
```

---

## Part 2: Frontend Setup (Next.js + Better Auth)

### Step 1: Create Next.js Project

```bash
# Return to project root
cd ..

# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir

cd frontend
```

Answer prompts:
- TypeScript: **Yes**
- ESLint: **Yes**
- Tailwind CSS: **Yes**
- `src/` directory: **No**
- App Router: **Yes**
- Import alias: **@/\***

---

### Step 2: Install Dependencies

```bash
npm install better-auth
npm install jose  # For JWT handling
```

**File**: `frontend/package.json` (should include):
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "better-auth": "^1.0.0",
    "jose": "^5.0.0"
  }
}
```

---

### Step 3: Configure Environment Variables

**File**: `frontend/.env.local`

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Secret (same as backend)
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long-change-in-production

# Better Auth URL
BETTER_AUTH_URL=http://localhost:3000
```

---

### Step 4: Set Up Better Auth

**File**: `frontend/lib/auth.ts`

```typescript
import { BetterAuth } from "better-auth";

export const auth = new BetterAuth({
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.BETTER_AUTH_URL!,
  database: {
    // Better Auth will create tables in the same Neon database
    url: process.env.DATABASE_URL!,
  },
  emailAndPassword: {
    enabled: true,
  },
});

export type Session = typeof auth.$Infer.Session;
```

**File**: `frontend/app/api/auth/[...all]/route.ts`

```typescript
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
```

---

### Step 5: Create API Client

**File**: `frontend/lib/api.ts`

```typescript
interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("auth_token");

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Redirect to login
      window.location.href = "/login";
    }
    const error = await response.json();
    throw new Error(error.detail || "API request failed");
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

// Task API methods
export const taskApi = {
  getAll: (userId: number) =>
    apiClient<{ tasks: Task[] }>(`/api/${userId}/tasks`),

  create: (userId: number, data: { title: string; description?: string }) =>
    apiClient<Task>(`/api/${userId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (userId: number, taskId: number, data: { title: string; description?: string }) =>
    apiClient<Task>(`/api/${userId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (userId: number, taskId: number) =>
    apiClient<void>(`/api/${userId}/tasks/${taskId}`, {
      method: "DELETE",
    }),

  toggleComplete: (userId: number, taskId: number) =>
    apiClient<Task>(`/api/${userId}/tasks/${taskId}/complete`, {
      method: "PATCH",
    }),
};
```

---

### Step 6: Create Task Dashboard

**File**: `frontend/app/dashboard/page.tsx`

```typescript
"use client";

import { useEffect, useState } from "react";
import { taskApi } from "@/lib/api";

interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
}

export default function DashboardPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTitle, setNewTitle] = useState("");
  const [newDescription, setNewDescription] = useState("");
  const userId = 1; // TODO: Get from auth context

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      const { tasks } = await taskApi.getAll(userId);
      setTasks(tasks);
    } catch (error) {
      console.error("Failed to load tasks:", error);
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await taskApi.create(userId, { title: newTitle, description: newDescription });
      setNewTitle("");
      setNewDescription("");
      loadTasks();
    } catch (error) {
      console.error("Failed to create task:", error);
    }
  };

  const handleToggle = async (taskId: number) => {
    try {
      await taskApi.toggleComplete(userId, taskId);
      loadTasks();
    } catch (error) {
      console.error("Failed to toggle task:", error);
    }
  };

  const handleDelete = async (taskId: number) => {
    try {
      await taskApi.delete(userId, taskId);
      loadTasks();
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">My Tasks</h1>

      {/* Create Task Form */}
      <form onSubmit={handleCreate} className="mb-8 space-y-4">
        <input
          type="text"
          placeholder="Task title"
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
        <textarea
          placeholder="Description (optional)"
          value={newDescription}
          onChange={(e) => setNewDescription(e.target.value)}
          className="w-full p-2 border rounded"
        />
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">
          Add Task
        </button>
      </form>

      {/* Task List */}
      <div className="space-y-2">
        {tasks.map((task) => (
          <div key={task.id} className="flex items-center gap-4 p-4 border rounded">
            <input
              type="checkbox"
              checked={task.completed}
              onChange={() => handleToggle(task.id)}
              className="w-5 h-5"
            />
            <div className="flex-1">
              <h3 className={task.completed ? "line-through" : ""}>{task.title}</h3>
              {task.description && <p className="text-sm text-gray-600">{task.description}</p>}
            </div>
            <button
              onClick={() => handleDelete(task.id)}
              className="text-red-500 hover:text-red-700"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

### Step 7: Run Frontend

```bash
cd frontend
npm run dev
```

Open http://localhost:3000/dashboard

---

## Testing the Full Stack

### Manual Testing Checklist

- [ ] Backend health check works: `curl http://localhost:8000/health`
- [ ] API docs accessible: http://localhost:8000/docs
- [ ] Frontend loads: http://localhost:3000
- [ ] Can create a task
- [ ] Can view tasks
- [ ] Can toggle task completion
- [ ] Can delete a task
- [ ] Tasks persist after page refresh

---

## Next Steps

1. **Implement Better Auth login/signup UI**
2. **Add real authentication flow**
3. **Write integration tests**
4. **Set up Alembic for database migrations**
5. **Deploy to production**

---

## Troubleshooting

### Backend won't start
- Check `.env` file exists and has correct `DATABASE_URL`
- Verify Neon database is accessible
- Check Python dependencies are installed

### Frontend won't connect to backend
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS configuration in backend allows `localhost:3000`
- Verify backend is running on port 8000

### Database connection errors
- Verify Neon connection string is correct
- Check if IP is allowed (Neon has IP allowlist feature)
- Ensure `?sslmode=require` is in connection string

---

**Documentation Complete!** You're ready to implement Phase II.
