# Feature Specification: Full-Stack Web Evolution (Phase II)

**Feature Branch**: `002-web-evolution`
**Created**: 2026-01-01
**Status**: Draft
**Input**: User requirement: "Migrate Phase I console todo app to full-stack web application with Next.js frontend, FastAPI backend, Neon PostgreSQL database, and Better Auth authentication with strict user isolation"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User Authentication & Authorization (Priority: P0)

As a user, I want to sign up and log in securely so that my tasks are private and only accessible to me.

**Why this priority**: Without authentication, there is no user identity and no way to implement multi-tenant data isolation. This is the foundational requirement for a web application.

**Independent Test**: Can be fully tested by creating multiple users, logging in with each, and verifying that each user only sees their own tasks.

**Acceptance Scenarios**:

1. **Given** I am a new user, **When** I visit the application, **Then** I see options to sign up or log in.
2. **Given** I provide valid credentials during sign up, **When** I submit the form, **Then** my account is created and I am redirected to my task dashboard.
3. **Given** I am a registered user, **When** I log in with valid credentials, **Then** I receive a JWT token and am redirected to my task dashboard.
4. **Given** I am a registered user, **When** I log in with invalid credentials, **Then** I see an error message and remain on the login page.
5. **Given** I am logged in, **When** I make API requests, **Then** my JWT token is included in the Authorization header.
6. **Given** I am not logged in, **When** I try to access the task dashboard, **Then** I am redirected to the login page.
7. **Given** I am not logged in, **When** I make API requests without a JWT, **Then** I receive a 401 Unauthorized response.

---

### User Story 2 - Multi-Tenant Task Isolation (Priority: P0)

As a user, I want to ensure that only I can see and modify my tasks, and no other user can access my data.

**Why this priority**: The Identity Law requires strict tenant isolation. Without this, the application violates data privacy and security principles.

**Independent Test**: Can be fully tested by creating tasks for User A, then logging in as User B and verifying User B cannot see or modify User A's tasks.

**Acceptance Scenarios**:

1. **Given** I am User A with tasks, **When** User B logs in and views tasks, **Then** User B sees only their own tasks (empty if none created).
2. **Given** I am User A, **When** I create a task, **Then** the task is linked to my `user_id` in the database.
3. **Given** I am User A, **When** I fetch tasks via API, **Then** the backend filters results by my authenticated `user_id`.
4. **Given** I am User A, **When** I try to access a task with an ID belonging to User B, **Then** I receive a 404 Not Found or 403 Forbidden response.
5. **Given** I am User A, **When** I try to modify or delete a task belonging to User B, **Then** the operation is rejected with a 403 Forbidden response.

---

### User Story 3 - RESTful Task API (Priority: P1)

As a frontend developer, I want a consistent RESTful API to manage tasks so that I can build a responsive user interface.

**Why this priority**: The API is the contract between frontend and backend. A well-designed API enables independent frontend and backend development.

**Independent Test**: Can be fully tested by making HTTP requests to each endpoint and verifying correct responses, status codes, and data format.

**Acceptance Scenarios**:

1. **Given** I am authenticated, **When** I GET `/api/{user_id}/tasks`, **Then** I receive a JSON array of all my tasks.
2. **Given** I am authenticated, **When** I POST `/api/{user_id}/tasks` with valid data, **Then** a new task is created and returned with a 201 Created status.
3. **Given** I am authenticated, **When** I PUT `/api/{user_id}/tasks/{id}` with valid data, **Then** the task is updated and returned with a 200 OK status.
4. **Given** I am authenticated, **When** I DELETE `/api/{user_id}/tasks/{id}`, **Then** the task is deleted and I receive a 204 No Content status.
5. **Given** I am authenticated, **When** I PATCH `/api/{user_id}/tasks/{id}/complete`, **Then** the task's completion status is toggled and returned with a 200 OK status.
6. **Given** I am authenticated, **When** I make a request with invalid data, **Then** I receive a 400 Bad Request with validation errors.
7. **Given** I am not authenticated, **When** I make any API request, **Then** I receive a 401 Unauthorized response.

---

### User Story 4 - Web Task Management Interface (Priority: P1)

As a user, I want a modern web interface to manage my tasks so that I can add, view, update, delete, and complete tasks easily from any device.

**Why this priority**: The web interface is the primary user interaction point. Without it, users cannot access the application.

**Independent Test**: Can be fully tested by performing all CRUD operations through the web UI and verifying the UI updates correctly.

**Acceptance Scenarios**:

1. **Given** I am logged in, **When** I view my task dashboard, **Then** I see all my tasks with their titles, descriptions, and completion status.
2. **Given** I am on the task dashboard, **When** I click "Add Task" and provide a title and description, **Then** the task is created and appears in the list.
3. **Given** I have an existing task, **When** I click "Edit" and update the title or description, **Then** the task is updated in the list.
4. **Given** I have an existing task, **When** I click "Delete", **Then** the task is removed from the list.
5. **Given** I have an incomplete task, **When** I click "Mark Complete", **Then** the task is visually marked as complete.
6. **Given** I have a complete task, **When** I click "Mark Incomplete", **Then** the task is visually marked as incomplete.
7. **Given** I have multiple tasks, **When** the page loads, **Then** all tasks are displayed without pagination (for now).

---

### User Story 5 - Database Persistence (Priority: P0)

As a system, I want all task data to be persisted in a PostgreSQL database so that data is durable and scalable.

**Why this priority**: The database is the single source of truth for all task data. Without it, data is lost on server restart.

**Independent Test**: Can be fully tested by creating tasks, restarting the backend server, and verifying tasks are still present.

**Acceptance Scenarios**:

1. **Given** a task is created via API, **When** the database is queried, **Then** the task exists with the correct `user_id`, `title`, `description`, and `completed` status.
2. **Given** a task is updated via API, **When** the database is queried, **Then** the task reflects the updated values.
3. **Given** a task is deleted via API, **When** the database is queried, **Then** the task no longer exists.
4. **Given** the backend server restarts, **When** I fetch tasks via API, **Then** all previously created tasks are returned.
5. **Given** the database schema is created, **When** I inspect the `tasks` table, **Then** it has columns: `id`, `user_id`, `title`, `description`, `completed`, `created_at`, `updated_at`.
6. **Given** a task is inserted with a `user_id` that doesn't exist, **When** the database enforces foreign key constraints, **Then** the insert is rejected.

---

### Edge Cases

**Authentication & Authorization**:
- What happens if a JWT token expires during a session?
- What happens if a user tries to access `/api/{different_user_id}/tasks`?
- What happens if the `BETTER_AUTH_SECRET` is missing or incorrect?

**API & Data Validation**:
- What happens if a user provides an empty title when creating a task?
- What happens if a user tries to update a task that doesn't exist?
- What happens if a user tries to delete a task that doesn't exist?
- What happens if a user provides a task ID that belongs to another user?

**Database & Concurrency**:
- How does the system handle concurrent requests from the same user?
- What happens if the database connection is lost during a request?
- How does the system handle SQL injection attempts?

**Frontend & UX**:
- How does the frontend display errors from the API?
- What happens if the frontend loses network connectivity?
- How does the frontend handle slow API responses (loading states)?

---

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication & Authorization
- **FR-001**: The system MUST implement user authentication using Better Auth in the Next.js frontend.
- **FR-002**: The system MUST generate a JWT token upon successful login containing `user_id`, `email`, and `exp` (expiration).
- **FR-003**: The system MUST include the JWT token in the `Authorization: Bearer <token>` header for all API requests.
- **FR-004**: The Backend MUST verify the JWT signature using the shared `BETTER_AUTH_SECRET`.
- **FR-005**: The Backend MUST extract `user_id` from the verified JWT for all database queries.
- **FR-006**: The system MUST return 401 Unauthorized for requests with missing or invalid JWT tokens.

#### API Endpoints
- **FR-007**: The system MUST implement `GET /api/{user_id}/tasks` to retrieve all tasks for the authenticated user.
- **FR-008**: The system MUST implement `POST /api/{user_id}/tasks` to create a new task for the authenticated user.
- **FR-009**: The system MUST implement `PUT /api/{user_id}/tasks/{id}` to update an existing task for the authenticated user.
- **FR-010**: The system MUST implement `DELETE /api/{user_id}/tasks/{id}` to delete an existing task for the authenticated user.
- **FR-011**: The system MUST implement `PATCH /api/{user_id}/tasks/{id}/complete` to toggle task completion status.
- **FR-012**: All endpoints MUST return 403 Forbidden if the authenticated `user_id` does not match the `{user_id}` in the URL.
- **FR-013**: All endpoints MUST return 404 Not Found if the requested task does not exist or does not belong to the authenticated user.

#### Data Validation
- **FR-014**: The system MUST reject task creation if the title is empty or contains only whitespace (400 Bad Request).
- **FR-015**: The system MUST allow optional description fields (empty or null is valid).
- **FR-016**: The system MUST validate that `user_id` in the URL is a valid UUID or integer (depending on schema).
- **FR-017**: The system MUST validate that task `id` is a valid integer (400 Bad Request if invalid).

#### Database & Persistence
- **FR-018**: The system MUST store all tasks in a PostgreSQL database using Neon Serverless.
- **FR-019**: The system MUST use SQLModel ORM for all database operations.
- **FR-020**: The database MUST enforce a foreign key constraint between `tasks.user_id` and `users.id`.
- **FR-021**: All database queries MUST filter by the authenticated `user_id` (The Identity Law).
- **FR-022**: The database MUST store `created_at` and `updated_at` timestamps for each task.
- **FR-023**: The system MUST use parameterized queries to prevent SQL injection.

#### Frontend Requirements
- **FR-024**: The frontend MUST be built with Next.js 16+ using the App Router.
- **FR-025**: The frontend MUST display a login page for unauthenticated users.
- **FR-026**: The frontend MUST display a task dashboard for authenticated users.
- **FR-027**: The frontend MUST provide forms to add, edit, and delete tasks.
- **FR-028**: The frontend MUST display task completion status visually (e.g., checkbox or strikethrough).
- **FR-029**: The frontend MUST handle API errors gracefully and display user-friendly messages.

### Key Entities

#### User (Better Auth managed)
- `id` (UUID or integer): Unique identifier
- `email` (string): User's email address
- `password_hash` (string): Hashed password (managed by Better Auth)
- `created_at` (timestamp): Account creation time

#### Task (SQLModel schema)
- `id` (integer, primary key): Unique identifier assigned at creation time
- `user_id` (UUID or integer, foreign key): Owner of the task
- `title` (string, required): Non-empty string describing the task
- `description` (string, optional): Additional details about the task
- `completed` (boolean, default False): Whether the task has been completed
- `created_at` (timestamp): Task creation time
- `updated_at` (timestamp): Last modification time

---

### API Specification

#### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.evolution-todo.com`

#### Authentication Header
All requests (except login/signup) must include:
```
Authorization: Bearer <JWT_TOKEN>
```

---

#### Endpoint: GET /api/{user_id}/tasks

**Description**: Retrieve all tasks for the authenticated user.

**Request**:
```http
GET /api/123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 123,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-01T10:00:00Z",
      "updated_at": "2026-01-01T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": 123,
      "title": "Write report",
      "description": null,
      "completed": true,
      "created_at": "2026-01-01T11:00:00Z",
      "updated_at": "2026-01-01T12:00:00Z"
    }
  ]
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Authenticated user_id does not match URL user_id

---

#### Endpoint: POST /api/{user_id}/tasks

**Description**: Create a new task for the authenticated user.

**Request**:
```http
POST /api/123/tasks HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "New Task",
  "description": "Optional description"
}
```

**Response (201 Created)**:
```json
{
  "id": 3,
  "user_id": 123,
  "title": "New Task",
  "description": "Optional description",
  "completed": false,
  "created_at": "2026-01-01T13:00:00Z",
  "updated_at": "2026-01-01T13:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input (empty title, etc.)
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Authenticated user_id does not match URL user_id

---

#### Endpoint: PUT /api/{user_id}/tasks/{id}

**Description**: Update an existing task for the authenticated user.

**Request**:
```http
PUT /api/123/tasks/3 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "title": "Updated Task Title",
  "description": "Updated description"
}
```

**Response (200 OK)**:
```json
{
  "id": 3,
  "user_id": 123,
  "title": "Updated Task Title",
  "description": "Updated description",
  "completed": false,
  "created_at": "2026-01-01T13:00:00Z",
  "updated_at": "2026-01-01T14:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to authenticated user
- `404 Not Found`: Task does not exist

---

#### Endpoint: DELETE /api/{user_id}/tasks/{id}

**Description**: Delete an existing task for the authenticated user.

**Request**:
```http
DELETE /api/123/tasks/3 HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (204 No Content)**: Empty body

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to authenticated user
- `404 Not Found`: Task does not exist

---

#### Endpoint: PATCH /api/{user_id}/tasks/{id}/complete

**Description**: Toggle task completion status for the authenticated user.

**Request**:
```http
PATCH /api/123/tasks/3/complete HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "id": 3,
  "user_id": 123,
  "title": "Updated Task Title",
  "description": "Updated description",
  "completed": true,
  "created_at": "2026-01-01T13:00:00Z",
  "updated_at": "2026-01-01T14:30:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid JWT
- `403 Forbidden`: Task does not belong to authenticated user
- `404 Not Found`: Task does not exist

---

### Assumptions

- Better Auth is configured in the Next.js frontend with a shared `BETTER_AUTH_SECRET`
- FastAPI backend has access to the same `BETTER_AUTH_SECRET` via environment variable
- Neon PostgreSQL connection string is provided via `DATABASE_URL` environment variable
- Phase I skill logic (AddTask, UpdateTask, etc.) can be adapted to use SQLModel queries
- Frontend and backend are deployed separately (not monolithic)
- CORS is configured to allow requests from the Next.js frontend domain

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can sign up and log in via Better Auth with JWT token generation.
- **SC-002**: All API endpoints require valid JWT authentication (401 if missing).
- **SC-003**: User A cannot access, modify, or delete User B's tasks (403 or 404 responses).
- **SC-004**: All CRUD operations work correctly through the API and update the database.
- **SC-005**: Task completion can be toggled via PATCH endpoint.
- **SC-006**: Frontend displays tasks correctly and updates in real-time after API calls.
- **SC-007**: Database enforces foreign key constraints (tasks linked to users).
- **SC-008**: Backend filters all queries by authenticated `user_id` (The Identity Law).
- **SC-009**: API returns appropriate error codes (400, 401, 403, 404) for invalid requests.
- **SC-010**: Phase I skill logic is preserved and adapted to use SQLModel (no business logic rewrite).

---

## Non-Goals *(explicit exclusions)*

- Real-time collaboration (multiple users editing same task)
- Task sharing between users
- Role-based access control (admin, viewer, etc.)
- Task tags or categories (deferred to Phase III)
- Task search or filtering (deferred to Phase III)
- Email notifications
- Mobile app (native iOS/Android)
- Offline support (PWA)
- Task attachments or file uploads
- Task comments or activity history

---

## Technical Architecture Notes

### Project Structure

```
evolution-todo-app/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI app initialization
│   │   ├── auth.py            # JWT verification middleware
│   │   ├── models.py          # SQLModel database models
│   │   ├── skills.py          # Adapted Phase I skills
│   │   ├── api/
│   │   │   └── tasks.py       # Task API endpoints
│   │   └── database.py        # Neon PostgreSQL connection
│   ├── requirements.txt
│   └── .env                   # BETTER_AUTH_SECRET, DATABASE_URL
├── frontend/                   # Next.js 16+ frontend
│   ├── app/
│   │   ├── page.tsx           # Home/login page
│   │   ├── dashboard/
│   │   │   └── page.tsx       # Task dashboard
│   │   └── api/
│   │       └── auth/[...all].ts  # Better Auth routes
│   ├── components/
│   │   ├── TaskList.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskItem.tsx
│   ├── lib/
│   │   ├── auth.ts            # Better Auth setup
│   │   └── api.ts             # API client with JWT
│   ├── package.json
│   └── .env.local             # BETTER_AUTH_SECRET, NEXT_PUBLIC_API_URL
└── src/                        # Phase I (console app - to be archived)
    └── ...
```

### Adaptation Strategy

**Phase I Skills → Phase II SQLModel**:
- `AddTask(title, description, tasks, next_id)` → `create_task(user_id, title, description, db)`
- `GetTasks(tasks)` → `get_tasks(user_id, db)`
- `UpdateTask(task_id, title, description, tasks)` → `update_task(task_id, user_id, title, description, db)`
- `DeleteTask(task_id, tasks)` → `delete_task(task_id, user_id, db)`
- `ToggleTaskStatus(task_id, tasks)` → `toggle_task_status(task_id, user_id, db)`

**Key Adaptation**:
- Add `user_id` parameter to all functions
- Replace in-memory list operations with SQLModel queries
- Preserve business logic (validation, error handling)

---

## Open Questions

1. Should Better Auth use OAuth providers (Google, GitHub) or just email/password?
2. What should the JWT expiration time be (1 hour, 24 hours, 7 days)?
3. Should the API support pagination for tasks (e.g., 50 tasks per page)?
4. Should we add rate limiting to prevent abuse?
5. How should we handle database migrations (Alembic, SQLModel built-in)?

---

## Dependencies

- **Frontend**: Next.js 16+, Better Auth, React, TypeScript
- **Backend**: FastAPI, SQLModel, PyJWT, python-dotenv, psycopg2
- **Database**: Neon Serverless PostgreSQL
- **Deployment**: Vercel (frontend), Fly.io or Railway (backend)

---

## References

- Phase I Specification: `specs/001-in-memory-todo/spec.md`
- Constitution Amendment II: `.specify/memory/constitution.md`
- Better Auth Documentation: https://better-auth.com
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLModel Documentation: https://sqlmodel.tiangolo.com
- Neon Documentation: https://neon.tech/docs
