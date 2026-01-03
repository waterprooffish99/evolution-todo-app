# Better Auth Setup Guide

This document explains how Better Auth database adapter initialization works and how to configure it correctly.

## Architecture Overview

Better Auth uses a **shared PostgreSQL database** between frontend and backend:

```
┌─────────────────────────────────────────────────────────┐
│              Neon PostgreSQL Database                │
│                                                 │
│  ┌──────────────┐  ┌────────────────┐  │
│  │ users table   │  │ tasks table   │  │
│  │ (Better Auth) │  │ (Backend)    │  │
│  └──────┬───────┘  └───────┬───────┘  │
│         │ user_id(FK)       │ user_id(FK) │
└─────────┼────────────────────┼──────────────┘
          │                    │
          │                    │
┌─────────┴────────────────────┴──────────────┐
│  Frontend (Next.js + Better Auth)          │
│  - Creates/Manages users in `users` table   │
│  - Generates JWT tokens                     │
│  - Stores sessions                           │
└────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────┐
│  Backend (FastAPI)                         │
│  - Uses shared `users` table (read-only)      │
│  - Owns `tasks` table                     │
│  - Verifies JWT tokens from Better Auth       │
└──────────────────────────────────────────────────┘
```

## Configuration Requirements

### 1. Shared Database URL

**CRITICAL**: Both frontend and backend MUST use the **SAME** database URL.

**Frontend** (`.env.local`):
```env
# Better Auth uses this to create/manage user table
DATABASE_URL=postgresql://neondb_owner:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require
```

**Backend** (`.env`):
```env
# Backend reads from users table for JWT verification
DATABASE_URL=postgresql://neondb_owner:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require
```

### 2. Shared JWT Secret

**CRITICAL**: Both frontend and backend MUST use the **SAME** `BETTER_AUTH_SECRET`.

**Frontend** (`.env.local`):
```env
# Better Auth uses this to SIGN JWT tokens
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long-change-in-production
```

**Backend** (`.env`):
```env
# Backend uses this to VERIFY JWT tokens
BETTER_AUTH_SECRET=your-super-secret-key-min-32-characters-long-change-in-production
```

### 3. Base URLs

**Frontend** (`.env.local`):
```env
# URL where Better Auth API is hosted (Next.js frontend itself)
BETTER_AUTH_URL=http://localhost:3000

# Production: https://todo.yourapp.com
```

**Backend** (`.env`):
```env
# Frontend URL for CORS (allows requests from frontend)
ALLOWED_ORIGINS=http://localhost:3000

# Production: https://todo.yourapp.com
```

## Build-Time Behavior

### Expected Error During Build

You may see this error during `npm run build`:

```
[Error [BetterAuthError]: Failed to initialize database adapter] {
  cause: undefined
}
```

**This is NORMAL and EXPECTED** because:

1. Next.js builds happen in a CI/CD environment
2. Database may not be accessible during build
3. Build still completes successfully
4. Better Auth initializes correctly at **runtime**

### Why This Happens

Better Auth configuration (in `lib/auth.ts`) is loaded during:
- **Build time**: Evaluates config, tries to connect to DB → fails
- **Runtime**: Server starts, environment vars are available → succeeds

The error appears in build logs but doesn't affect functionality.

## Runtime Verification

To verify Better Auth is working correctly at runtime:

### 1. Start Frontend Dev Server
```bash
cd frontend
npm run dev
```

### 2. Check Database Connection

Better Auth will automatically create the `users` table if it doesn't exist.

Verify in Neon console:
```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- Should see:
-- users (created by Better Auth)
-- tasks (created by backend)
```

### 3. Test Signup Flow

1. Navigate to `http://localhost:3000/signup`
2. Fill email/password
3. Submit form
4. Should redirect to `/login` on success

**If error occurs**:
- "Email already in use" → Duplicate email detection working
- "Signup failed" → Check DATABASE_URL in `.env.local`
- Network error → Check Neon database is accessible

### 4. Test Login Flow

1. Navigate to `http://localhost:3000/login`
2. Use the same email/password from signup
3. Submit form
4. Should redirect to `/dashboard`

**If error occurs**:
- Check JWT token in localStorage:
  ```javascript
  localStorage.getItem("auth_token")
  ```
- Should contain JWT with `user_id` and `email` claims

## Database Schema

Better Auth creates this table automatically:

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

## Backend Integration

Backend **reads** from the `users` table but **doesn't own** it:

```python
# backend/app/models.py
class User(SQLModel, table=True):
    """
    User account model (managed by Better Auth).

    Better Auth creates/updates this table.
    Backend only reads from it for JWT verification.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Backend owns tasks table, not users
    tasks: List["Task"] = Relationship(back_populates="user")
```

Backend **owns** the `tasks` table:

```python
# backend/app/models.py
class Task(SQLModel, table=True):
    """
    Task model with user ownership (The Identity Law).
    """
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True, nullable=False)
    title: str = Field(max_length=255, min_length=1)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to user (managed by Better Auth)
    user: Optional[User] = Relationship(back_populates="tasks")
```

## Troubleshooting

### Error: "Failed to initialize database adapter"

**Build time** (expected):
```
✓ Build continues successfully
→ Ignore this error
```

**Runtime** (not expected):
```
✗ Check DATABASE_URL in .env.local
✗ Verify Neon database is accessible
✗ Check network connectivity
✗ Ensure database user has correct permissions
```

### Error: "Email already in use"

**This is CORRECT behavior** - email collision detection working:

```typescript
// frontend/lib/auth-context.tsx
if (
  errorData.message?.toLowerCase().includes("email") ||
  errorData.message?.toLowerCase().includes("already") ||
  response.status === 409
) {
  throw new Error("Email already in use");
}
```

### Error: "Signup failed" (generic)

**Debug steps**:
1. Check console for actual error message
2. Verify DATABASE_URL is correct in `.env.local`
3. Check Neon console for connection logs
4. Test database connection directly:
   ```bash
   psql "postgresql://neondb_owner:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require"
   ```

## Security Checklist

- [ ] DATABASE_URL matches between frontend and backend
- [ ] BETTER_AUTH_SECRET matches between frontend and backend
- [ ] BETTER_AUTH_SECRET is at least 32 characters long
- [ ] Database uses SSL (`sslmode=require`)
- [ ] ALLOWED_ORIGINS in backend matches BETTER_AUTH_URL
- [ ] .env.local is in .gitignore (never commit secrets!)
- [ ] .env is in .gitignore (never commit secrets!)
- [ ] Production secrets are rotated and stored in deployment platform (Vercel, Fly.io)

## Production Deployment

### Environment Variables

**Vercel (Frontend)**:
```bash
# In Vercel dashboard → Settings → Environment Variables
BETTER_AUTH_SECRET=<production-secret-32+-chars>
DATABASE_URL=<neon-production-url>
BETTER_AUTH_URL=https://todo.yourapp.com
NEXT_PUBLIC_API_URL=https://api.todo.yourapp.com
```

**Fly.io/Railway (Backend)**:
```bash
# In deployment platform → Environment Variables
DATABASE_URL=<neon-production-url>
BETTER_AUTH_SECRET=<production-secret-32+-chars>
ALLOWED_ORIGINS=https://todo.yourapp.com
ENVIRONMENT=production
```

### Database Migration

When deploying to production:

1. Create a new Neon branch for production:
   ```bash
   # In Neon console → Branches → Create Branch
   Name: production
   Parent: main
   ```

2. Update DATABASE_URL in both frontend and backend:
   ```env
   DATABASE_URL=postgresql://neondb_owner:password@ep-xyz.region.aws.neon.tech/neondb?sslmode=require&pgbouncer=true
   ```

3. Run backend migrations:
   ```bash
   cd backend
   .venv/bin/alembic upgrade head
   ```

4. Better Auth will auto-create users table in new branch

## References

- Better Auth: https://better-auth.com/docs
- Neon PostgreSQL: https://neon.tech/docs
- Next.js Environment Variables: https://nextjs.org/docs/app/building-your-application/configuring/environment-variables
- FastAPI Security: https://fastapi.tiangolo.com/tutorial/security/
