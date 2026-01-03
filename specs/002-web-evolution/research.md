# Research & Technical Decisions: Full-Stack Web Evolution

**Feature**: 002-web-evolution
**Date**: 2026-01-01
**Context**: Migrating Phase I console todo app to full-stack web application with Next.js, FastAPI, Neon PostgreSQL, and Better Auth

## Research Questions Resolved

### 1. Frontend Framework: Next.js 16+ with App Router

**Decision**: Next.js 16+ using App Router (not Pages Router)

**Rationale**:
- **App Router** is the recommended approach for new Next.js projects (since v13+)
- Built-in server components for better performance
- Simplified data fetching with async/await in components
- Better file-system based routing with layouts and loading states
- Native support for streaming and Suspense
- Better SEO with server-side rendering by default

**Alternatives Considered**:
- **Pages Router**: Older, more verbose, less performant
- **Remix**: Good alternative but smaller ecosystem
- **Create React App**: No SSR, requires separate backend routing
- **Vue/Nuxt**: Different ecosystem, team not familiar

**Implementation Pattern**:
```
app/
├── page.tsx                    # Home/login page (public)
├── dashboard/
│   └── page.tsx                # Task dashboard (protected)
├── api/
│   └── auth/[...all]/route.ts  # Better Auth API routes
└── layout.tsx                  # Root layout with providers
```

**References**:
- Next.js App Router: https://nextjs.org/docs/app
- React Server Components: https://react.dev/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023

---

### 2. Authentication: Better Auth + JWT

**Decision**: Better Auth for frontend authentication with JWT tokens

**Rationale**:
- **Type-safe** authentication library built for TypeScript
- **Zero-config** JWT token management
- Built-in session handling and refresh tokens
- Supports multiple providers (email/password, OAuth)
- Generates JWT with custom claims (user_id, email, roles)
- Easy integration with Next.js API routes

**Alternatives Considered**:
- **NextAuth.js**: More complex configuration, less type-safe
- **Auth0**: Third-party service, vendor lock-in, costs money
- **Supabase Auth**: Requires Supabase ecosystem
- **Custom JWT**: Reinventing the wheel, security risks

**JWT Structure**:
```json
{
  "user_id": 123,
  "email": "user@example.com",
  "exp": 1704153600,
  "iat": 1704067200,
  "iss": "better-auth"
}
```

**Secret Sharing Strategy**:
- Both frontend (Better Auth) and backend (FastAPI) share the same `BETTER_AUTH_SECRET`
- Frontend signs JWTs, backend verifies them
- Secret stored in environment variables (`.env.local` and `.env`)

**References**:
- Better Auth: https://better-auth.com
- JWT Best Practices: https://tools.ietf.org/html/rfc8725

---

### 3. Backend Framework: FastAPI

**Decision**: Python FastAPI for backend REST API

**Rationale**:
- **Fast** (built on Starlette and Pydantic)
- **Type-safe** with Python type hints
- **Automatic API documentation** (Swagger UI, ReDoc)
- **Async support** for concurrent requests
- **Easy JWT verification** with python-jose
- **Familiar to Python developers** (similar to Flask but modern)
- **Excellent SQLModel integration** (same author: Tiangolo)

**Alternatives Considered**:
- **Flask**: Older, slower, lacks async support, less type-safe
- **Django**: Too heavy for REST API, includes ORM we won't use
- **Node.js/Express**: Different language, team prefers Python
- **Go/Gin**: Different language, steeper learning curve

**Implementation Pattern**:
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Evolution Todo API")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT verification dependency
async def verify_jwt_token(token: str = Depends(oauth2_scheme)):
    # Verify with BETTER_AUTH_SECRET
    pass
```

**References**:
- FastAPI: https://fastapi.tiangolo.com
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/

---

### 4. Database: Neon Serverless PostgreSQL

**Decision**: Neon Serverless PostgreSQL with connection pooling

**Rationale**:
- **Serverless**: Auto-scaling, pay-per-use, no infrastructure management
- **PostgreSQL**: Industry-standard, ACID compliant, feature-rich
- **Fast cold starts**: < 1 second (important for serverless)
- **Connection pooling**: Built-in Pgbouncer for connection efficiency
- **Branching**: Create database branches for testing (like Git)
- **Generous free tier**: 0.5 GB storage, 10 GB transfer/month

**Alternatives Considered**:
- **Supabase**: Heavier ecosystem, more features we don't need
- **PlanetScale**: MySQL-based, less familiar, different features
- **AWS RDS**: Requires always-on instance, more expensive
- **SQLite**: Not suitable for multi-tenant web application

**Connection String Format**:
```
postgresql://user:password@ep-xyz.region.aws.neon.tech/dbname?sslmode=require
```

**Best Practices**:
- Use connection pooling (Neon's Pgbouncer)
- Set `pool_size` and `max_overflow` in SQLModel
- Use `pool_pre_ping=True` to handle stale connections

**References**:
- Neon Documentation: https://neon.tech/docs
- PostgreSQL Connection Pooling: https://www.postgresql.org/docs/current/runtime-config-connection.html

---

### 5. ORM: SQLModel

**Decision**: SQLModel for database operations (not raw SQL or SQLAlchemy directly)

**Rationale**:
- **Combines SQLAlchemy + Pydantic**: Type-safe models, validation, and ORM
- **Single model definition**: Use same model for DB and API (DRY)
- **Automatic validation**: Pydantic validates data before DB insert
- **Type hints everywhere**: Full IDE autocomplete and type checking
- **FastAPI integration**: Native support (same author)
- **Async support**: Works with FastAPI async endpoints

**Alternatives Considered**:
- **SQLAlchemy directly**: More verbose, no automatic Pydantic models
- **Raw SQL**: Error-prone, no type safety, SQL injection risks
- **Django ORM**: Tied to Django framework
- **Tortoise ORM**: Smaller ecosystem, less mature

**Model Example**:
```python
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    title: str = Field(max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    user: Optional["User"] = Relationship(back_populates="tasks")
```

**References**:
- SQLModel: https://sqlmodel.tiangolo.com
- SQLModel with FastAPI: https://sqlmodel.tiangolo.com/tutorial/fastapi/

---

### 6. JWT Verification Strategy (Backend)

**Decision**: Use `python-jose` for JWT verification in FastAPI

**Rationale**:
- **Standard library** for JWT in Python
- **Supports multiple algorithms** (HS256, RS256, etc.)
- **Easy integration** with FastAPI security utilities
- **Validates expiration**, issuer, audience automatically
- **Extracts claims** for user_id extraction

**Implementation Pattern**:
```python
from jose import jwt, JWTError
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        payload = jwt.decode(
            credentials.credentials,
            BETTER_AUTH_SECRET,
            algorithms=["HS256"]
        )
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Security Considerations**:
- **Always verify signature** with shared secret
- **Check expiration** (exp claim)
- **Validate issuer** (iss claim) if set
- **Use HTTPS in production** to prevent token interception

**References**:
- python-jose: https://python-jose.readthedocs.io
- JWT Security Best Practices: https://curity.io/resources/learn/jwt-best-practices/

---

### 7. Identity Law Enforcement Strategy

**Decision**: Middleware-based JWT extraction + query-level filtering

**Rationale**:
- **Centralized authentication**: Middleware verifies JWT once per request
- **Automatic user_id injection**: Attach user_id to request context
- **Query-level filtering**: Every SQLModel query MUST filter by user_id
- **Defense in depth**: Multiple layers prevent data leakage

**Implementation Pattern**:
```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public routes
        if request.url.path in ["/", "/health", "/docs"]:
            return await call_next(request)

        # Extract and verify JWT
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ")[1]
        user_id = verify_token(token)  # Raises 401 if invalid

        # Attach user_id to request state
        request.state.user_id = user_id

        return await call_next(request)
```

**Query Pattern** (ALWAYS filter by user_id):
```python
from fastapi import Request

@app.get("/api/{user_id}/tasks")
async def get_tasks(user_id: int, request: Request, db: Session = Depends(get_db)):
    # Verify URL user_id matches authenticated user_id
    if request.state.user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Query with user_id filter (THE IDENTITY LAW)
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return {"tasks": tasks}
```

**References**:
- FastAPI Middleware: https://fastapi.tiangolo.com/advanced/middleware/
- Multi-Tenancy Patterns: https://docs.microsoft.com/en-us/azure/architecture/guide/multitenant/

---

### 8. CORS Configuration

**Decision**: Strict CORS with explicit Next.js frontend URL

**Rationale**:
- **Security**: Prevent unauthorized domains from making requests
- **Development**: Allow localhost:3000 (Next.js dev server)
- **Production**: Allow only production frontend domain
- **Credentials**: Allow cookies/auth headers with `credentials: true`

**Configuration**:
```python
from fastapi.middleware.cors import CORSMiddleware

# Development
ALLOWED_ORIGINS = ["http://localhost:3000"]

# Production
# ALLOWED_ORIGINS = ["https://todo.example.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)
```

**References**:
- CORS Explained: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

---

### 9. Frontend State Management

**Decision**: React Context + useState (no Redux/Zustand yet)

**Rationale**:
- **Simple requirements**: CRUD operations don't need complex state
- **Server state**: Most state lives in database, not frontend
- **React Context**: Good for auth state (user, token)
- **Component state**: `useState` for form inputs, loading states
- **Defer complexity**: Add Redux/Zustand only if needed later

**Pattern**:
```typescript
// lib/auth-context.tsx
'use client';

import { createContext, useContext, useState } from 'react';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  // ... implementation

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
```

**References**:
- React Context: https://react.dev/reference/react/useContext
- Next.js Client Components: https://nextjs.org/docs/app/building-your-application/rendering/client-components

---

### 10. API Client Strategy (Frontend)

**Decision**: Custom fetch wrapper with JWT auto-injection

**Rationale**:
- **Simple**: Native fetch API, no additional dependencies
- **Type-safe**: TypeScript interfaces for request/response
- **JWT auto-injection**: Automatically add Authorization header
- **Error handling**: Centralized error parsing and display
- **Retry logic**: Optional retry for network failures

**Implementation**:
```typescript
// lib/api.ts
import { useAuth } from './auth-context';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { token } = useAuth();

  const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...options.headers,
    },
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, redirect to login
      window.location.href = '/login';
    }
    const error = await response.json();
    throw new Error(error.detail || 'API request failed');
  }

  return response.json();
}

// Usage
const tasks = await apiClient<{ tasks: Task[] }>('/api/123/tasks');
```

**Alternatives Considered**:
- **Axios**: Additional dependency, overkill for simple needs
- **React Query**: Good for caching, but adds complexity
- **SWR**: Similar to React Query, deferred for now

**References**:
- Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API
- Next.js Environment Variables: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables

---

### 11. Database Migration Strategy

**Decision**: Alembic for database migrations (SQLModel/SQLAlchemy compatible)

**Rationale**:
- **Industry standard** for SQLAlchemy migrations
- **Version control** for database schema
- **Automatic migration generation** from model changes
- **Rollback support** for failed migrations
- **Works with Neon** (standard PostgreSQL)

**Setup**:
```bash
# Initialize Alembic
alembic init alembic

# Generate migration from models
alembic revision --autogenerate -m "Create tasks table"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**Alternatives Considered**:
- **SQLModel built-in**: Limited, no migration history
- **Manual SQL scripts**: Error-prone, no versioning
- **Django migrations**: Tied to Django

**References**:
- Alembic: https://alembic.sqlalchemy.org
- Alembic with FastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/#migrations

---

### 12. Error Handling & Validation

**Decision**: Pydantic models for validation + FastAPI exception handlers

**Rationale**:
- **Automatic validation**: Pydantic validates all inputs
- **Type safety**: TypeScript-like validation in Python
- **Custom error responses**: Format errors consistently
- **HTTP status codes**: Use correct codes (400, 401, 403, 404, 500)

**Pattern**:
```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)

    @validator('title')
    def title_not_whitespace(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

# FastAPI endpoint
@app.post("/api/{user_id}/tasks", status_code=201)
async def create_task(
    user_id: int,
    task_data: TaskCreate,  # Pydantic validation happens here
    request: Request,
    db: Session = Depends(get_db)
):
    # If we reach here, validation passed
    pass
```

**References**:
- Pydantic: https://docs.pydantic.dev
- FastAPI Validation: https://fastapi.tiangolo.com/tutorial/body/

---

## Summary of Key Decisions

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| Frontend | Next.js 16+ (App Router) | Modern, performant, built-in SSR |
| Auth Frontend | Better Auth | Type-safe, zero-config JWT |
| Backend | FastAPI | Fast, type-safe, async, auto-docs |
| Database | Neon Serverless PostgreSQL | Serverless, fast, PostgreSQL standard |
| ORM | SQLModel | Type-safe, Pydantic+SQLAlchemy combo |
| JWT Verification | python-jose | Standard library, easy integration |
| Migrations | Alembic | Industry standard, version control |
| State Management | React Context + useState | Simple, sufficient for CRUD |
| API Client | Custom fetch wrapper | Lightweight, type-safe |
| CORS | Strict whitelist | Security best practice |
| Identity Law | Middleware + query filtering | Defense in depth |

---

## Open Questions (Resolved)

None remaining. All technical decisions finalized for implementation.

---

## Next Steps

- **Phase 1**: Generate data-model.md (Task, User entities)
- **Phase 1**: Generate API contracts (OpenAPI spec)
- **Phase 1**: Generate quickstart.md (setup instructions)
- **Phase 2**: Generate tasks.md (implementation checklist)
- **Implementation**: Backend setup → Frontend setup → Integration
