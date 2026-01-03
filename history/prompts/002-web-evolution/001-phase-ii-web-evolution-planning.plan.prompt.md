---
id: 001
title: Phase II Web Evolution Planning
stage: plan
date: 2026-01-01
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-web-evolution
branch: 002-web-evolution
user: Salman
command: /sp.plan
labels: ["web-evolution", "fullstack", "nextjs", "fastapi", "neon", "better-auth", "planning"]
links:
  spec: specs/002-web-evolution/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-web-evolution/plan.md
  - specs/002-web-evolution/research.md
  - specs/002-web-evolution/data-model.md
  - specs/002-web-evolution/quickstart.md
  - specs/002-web-evolution/contracts/openapi.yaml
  - .specify/memory/constitution.md
tests:
  - None (planning phase)
---

## Prompt

/sp.plan

## Response snapshot

Successfully completed Phase II Web Evolution planning following SDD-RI methodology:

**Constitution Updated (Amendment II)**:
- Replaced Amendment I (local JSON persistence)
- Added Amendment II: Full-Stack Web & Identity
- The Identity Law: strict user isolation with user_id filtering
- Technical stack: Next.js 16+, FastAPI, Neon PostgreSQL, Better Auth
- Version: 1.1.0 → 2.0.0

**Phase 0: Research** (research.md)
- 12 technical decisions documented with rationales
- Frontend: Next.js App Router (vs Pages Router, Remix, CRA)
- Auth: Better Auth with JWT (vs NextAuth, Auth0, custom)
- Backend: FastAPI (vs Flask, Django, Node.js)
- Database: Neon Serverless PostgreSQL (vs Supabase, PlanetScale, RDS)
- ORM: SQLModel (vs SQLAlchemy, raw SQL, Django ORM)
- JWT: python-jose for verification
- State: React Context + useState (vs Redux, Zustand)
- API Client: Custom fetch wrapper
- CORS: Strict origin whitelist
- Migrations: Alembic
- Identity Law: 3-layer enforcement (JWT, URL, DB)

**Phase 1: Design** (data-model.md, contracts/, quickstart.md)
- Data model: User (Better Auth) + Task (extended with user_id, timestamps)
- SQLModel schemas with foreign key constraints
- Pydantic request/response models (TaskCreate, TaskUpdate, TaskResponse)
- Database indexes for performance (user_id, composite)
- Query patterns with Identity Law enforcement
- OpenAPI 3.0 specification (5 REST endpoints fully documented)
- Quickstart: Backend setup (10 steps) + Frontend setup (7 steps)
- Complete code examples for all layers

**Architecture** (plan.md)
- Three-tier: Next.js → FastAPI → Neon PostgreSQL
- JWT flow: Better Auth generates → Frontend sends → Backend verifies → Skills use
- The Identity Law: 3-layer enforcement (middleware, endpoint, database)
- Request flow: 7-step example with code snippets
- Project structure: frontend/ and backend/ directories
- Phase I skills adaptation strategy (preserve logic, add user_id)
- Testing strategy: 60% unit, 30% API, 10% integration
- Security: JWT verification, CORS, SQL injection prevention
- Performance: Indexes, connection pooling, < 200ms p95 target
- Deployment: Vercel (frontend), Fly.io (backend), Neon (database)

**Constitution Check** ✅
- Amendment II fully complied with
- The Identity Law enforced in all layers
- Technical stack matches requirements
- Core principles maintained (spec-driven, reusable skills, human-readable, clean boundaries)
- Security requirements met (JWT, HTTPS, SQL injection prevention, CORS)
- Zero violations detected

**Project Structure**
- backend/ - FastAPI with app/, tests/, alembic/, requirements.txt
- frontend/ - Next.js with app/, components/, lib/, package.json
- Phase I src/ to be archived post-migration
- Complete file tree with all directories and key files documented

## Outcome

- ✅ Impact: Comprehensive architectural plan for full-stack web migration with complete documentation (5 files, 12,000+ lines)
- 🧪 Tests: Testing strategy defined (backend: pytest, frontend: Jest, E2E: Playwright)
- 📁 Files: 5 created (plan.md, research.md, data-model.md, quickstart.md, contracts/openapi.yaml), 1 updated (constitution.md v2.0.0)
- 🔁 Next prompts: Run `/sp.tasks` to generate implementation tasks for backend and frontend
- 🧠 Reflection: Phase I skills preserved in adapted form, multi-tenant architecture with defense-in-depth security

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution Check: PASS (zero violations, full Amendment II compliance)
- Prompt variant (if applicable): Standard /sp.plan workflow with full-stack web architecture
- Next experiment (smallest change to try): Execute `/sp.tasks` to generate actionable backend + frontend implementation tasks
