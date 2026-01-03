<!--
================================================================================
SYNC IMPACT REPORT
================================================================================
Version change: N/A → 1.0.0 (new document)

Modified Principles:
  - N/A (new document)

Added Sections:
  - Phase I Purpose
  - Core Principles (4 principles from user input)
  - Phase I Scope (Explicit)
  - Technical Guardrails
  - Development Constraints
  - Success Definition (Phase I)

Removed Sections:
  - N/A (new document)

Templates Status:
  - .specify/templates/plan.md ✅ No changes needed - Constitution Check section already references constitution
  - .specify/templates/spec.md ✅ No changes needed - already aligned with spec-driven approach
  - .specify/templates/tasks.md ✅ No changes needed - already flexible for any methodology
  - .specify/templates/phr-template.prompt.md ✅ No changes needed

Follow-up TODOs:
  - None
================================================================================
-->

# The Evolution of Todo Constitution

## Core Principles

### I. Spec-Driven First
No implementation is generated without a written and refined specification.
Specifications are the single source of truth.

### II. Reusable Intelligence
Core behaviors are implemented as well-defined, reusable functions ("skills").
These skills must be simple, deterministic, and future-extensible.

### III. Human-Readable Design
The system must be understandable by beginners and AI systems alike.
Clear naming, simple flows, and predictable behavior are mandatory.

### IV. Clean Phase Boundaries
Phase I contains no web, database, agent, or AI logic.
All decisions must remain valid when extended in later phases.

## Phase I Scope (Explicit)

This phase **must support only** the following features:
- Add a task (title and description)
- View all tasks with completion status
- Update an existing task
- Delete a task by identifier
- Mark a task as complete or incomplete

No additional features are permitted in Phase I.

## Technical Guardrails

- **Language**: Python 3.13+
- **Runtime**: Console / CLI only
- **Persistence**: In-memory data structures only
- **Architecture**: Menu-driven, deterministic flow
- **No file system usage**
- **No external services or databases**

## Development Constraints

- **No manual coding is allowed.**
- All implementation must be generated via Claude Code based on refined specifications.
- Specifications may be iterated until the generated output is correct.

## Success Definition (Phase I)

Phase I is successful when:
- The console application works reliably
- All required features are implemented
- The codebase is clean and readable
- The project is ready to evolve into Phase II without refactoring

## Amendments

### Amendment II: Full-Stack Web & Identity (Phase II)
**Effective**: 2026-01-01
**Supersedes**: Amendment I (local JSON persistence)

**Principle**: The Evolution of Todo transitions to a full-stack web application with multi-user identity management and cloud-based persistence.

**The Identity Law (User Isolation)**:
- Every task **MUST** be linked to a `user_id`
- The Backend **MUST** verify the `Authorization: Bearer <JWT>` header using a shared `BETTER_AUTH_SECRET`
- Every database query **MUST** be filtered by the authenticated `user_id`
- **No user shall ever see another user's data** (strict tenant isolation)

**Rationale**: Phase II evolves the console application into a production-ready web application with proper authentication, authorization, and multi-tenant data isolation. This amendment maintains Phase I's core skills while adapting them to modern web architecture.

**Technical Stack**:
- **Frontend**: Next.js 16+ (App Router)
- **Backend**: Python FastAPI
- **Database**: Neon Serverless PostgreSQL (using SQLModel ORM)
- **Authentication**: Better Auth (Frontend) + JWT verification (Backend)
- **API**: RESTful endpoints at `/api/{user_id}/tasks`

**Technical Changes**:
- Phase I skills adapted to use SQLModel instead of in-memory lists
- All task operations require valid JWT authentication
- Database queries filtered by authenticated user_id
- RESTful API endpoints for CRUD operations
- Completion toggle via PATCH endpoint

**Constraints**:
- Phase I skill logic must be preserved (business logic unchanged)
- All endpoints must return 401 Unauthorized if JWT is missing or invalid
- Database schema must enforce user_id foreign key constraints
- Frontend must never expose other users' data

**Security Requirements**:
- JWT secret shared between Better Auth and FastAPI backend
- HTTPS required in production
- SQL injection prevention via SQLModel parameterized queries
- CORS configured for Next.js frontend only

## Governance

This constitution supersedes all other development practices.
Amendments require documentation of the change and rationale.
All implementation work must verify compliance with these principles.

**Version**: 2.0.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-01-01
