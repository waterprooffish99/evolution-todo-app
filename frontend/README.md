# Evolution Todo Frontend

Next.js 16+ frontend for Evolution Todo application with Better Auth authentication.

## Prerequisites

- Node.js 18+ installed
- PostgreSQL database (Neon Serverless PostgreSQL recommended)
- Backend API running (FastAPI)

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Copy `.env.example` to `.env.local` and fill in your values:

```bash
cp .env.example .env.local
```

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string (same as backend)
- `BETTER_AUTH_SECRET` - JWT secret (at least 32 characters, same as backend)
- `BETTER_AUTH_URL` - Frontend URL (http://localhost:3000 for dev)
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8000 for dev)

**Important**: `DATABASE_URL` and `BETTER_AUTH_SECRET` must match backend exactly!

### 3. Test Database Connectivity

```bash
node test-db-connection.js
```

This script verifies:
- Environment variables are loaded from `.env.local`
- DATABASE_URL is accessible
- Better Auth configuration is valid
- Database adapter can connect

**Expected Output:**
```
============================================================
Better Auth Database Connectivity Test
============================================================
1. Checking environment variables...
   ✅ DATABASE_URL: postgresql://***@ep-***.aws.neon.tech/neondb?sslmode=require
   ✅ BETTER_AUTH_SECRET: set (65 characters)
   ✅ BETTER_AUTH_URL: http://localhost:3000

2. Testing Better Auth configuration...
   ✅ Better Auth configured successfully
   ✅ Database provider: postgres
   ✅ Email/password auth: enabled
   ✅ Session expiration: 24 hours

3. Testing database connection...
   ✅ Database adapter accessible
   ℹ️  Table "users" will be auto-created on first use

============================================================
✅ All checks passed!
============================================================
```

### 4. Start Development Server

```bash
npm run dev
```

Application will be available at http://localhost:3000

### 5. (In separate terminal) Start Backend

```bash
cd ../backend
.venv/bin/python -m uvicorn app.main:app --reload
```

Backend API will be available at http://localhost:8000

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Next.js Frontend (localhost:3000)     │
│  ├── Better Auth (JWT generation)        │
│  ├── Task Dashboard UI                  │
│  └── API Client (with JWT injection)    │
└──────────────────┬────────────────────────┘
                 │
                 │ HTTPS
                 │ Authorization: Bearer <JWT>
                 ▼
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (localhost:8000)      │
│  ├── JWT Verification (python-jose)       │
│  ├── Task CRUD Endpoints                │
│  └── SQLModel ORM                      │
└──────────────────┬────────────────────────┘
                 │
                 │ SQLModel
                 ▼
┌─────────────────────────────────────────────────┐
│  Neon PostgreSQL                       │
│  ├── users table (Better Auth managed)     │
│  └── tasks table (FastAPI managed)       │
└─────────────────────────────────────────────────┘
```

## Available Scripts

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Lint code
npm run lint

# Test database connectivity
node test-db-connection.js
```

## Pages

- `/` - Home page (redirects based on auth state)
- `/login` - Login form
- `/signup` - Signup form
- `/dashboard` - Protected task management interface

## API Routes

- `/api/auth/[...all]` - Better Auth authentication endpoints

## Authentication Flow

### 1. Signup

1. User visits `/signup`
2. Fills email/password form
3. Form submits to `/api/auth/sign-up`
4. Better Auth creates user in `users` table
5. Redirects to `/login`

### 2. Login

1. User visits `/login`
2. Fills email/password form
3. Form submits to `/api/auth/sign-in`
4. Better Auth verifies credentials
5. Generates JWT token with `user_id`, `email`, `exp` claims
6. JWT stored in `localStorage`
7. User redirected to `/dashboard`

### 3. JWT Usage

1. Frontend reads JWT from `localStorage`
2. Adds `Authorization: Bearer <JWT>` header to API requests
3. Backend verifies JWT with `BETTER_AUTH_SECRET`
4. Extracts `user_id` from token
5. Filters all database queries by `user_id` (The Identity Law)

## Database Schema

### Users Table (Better Auth managed)

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Managed by**: Better Auth (frontend)
**Accessed by**: FastAPI backend (read-only for JWT verification)

### Tasks Table (FastAPI managed)

```sql
CREATE TABLE tasks (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Managed by**: FastAPI backend
**Linked to users table**: via `user_id` foreign key

## Build Behavior

### Expected Warning During Build

When running `npm run build`, you may see:

```
[Error [BetterAuthError]: Failed to initialize database adapter] {
  cause: undefined
}
```

**This is NORMAL and EXPECTED** because:

1. Next.js builds happen in CI/CD without database access
2. Better Auth loads during build → tries to connect → fails
3. **Build still completes successfully** (error is non-blocking)
4. Better Auth initializes correctly at **runtime**

**Build succeeds with this error** - you can ignore it for now.

### When It Matters

The error only matters at **runtime**:
- If you see it during `npm run dev`, database connection is failing
- Check `DATABASE_URL` in `.env.local`
- Verify Neon database is accessible
- Run `node test-db-connection.js` to debug

## Troubleshooting

### Database Connection Issues

1. **Check .env.local exists**:
   ```bash
   ls -la .env.local
   ```

2. **Verify DATABASE_URL is correct**:
   ```bash
   grep DATABASE_URL .env.local
   ```

3. **Test connection manually**:
   ```bash
   node test-db-connection.js
   ```

4. **Check Neon console**:
   - Verify database branch is active
   - Check connection string is correct
   - Verify user has correct permissions

### Authentication Issues

1. **Check JWT secret matches**:
   Frontend `.env.local`: `BETTER_AUTH_SECRET`
   Backend `.env`: `BETTER_AUTH_SECRET`
   **Must be identical!**

2. **Clear browser storage**:
   ```javascript
   // Browser console
   localStorage.clear()
   ```

3. **Check CORS**:
   Backend `.env`: `ALLOWED_ORIGINS` should match frontend URL
   Dev: `http://localhost:3000`
   Prod: `https://your-domain.com`

### Signup Issues

**"Email already in use"**:
- This means email collision detection is working correctly
- User should try a different email
- Or login if they already have an account

**"Signup failed" (generic)**:
- Check network connectivity
- Verify DATABASE_URL is correct
- Check Better Auth configuration in `lib/auth.ts`

## Development Workflow

### Typical Development Session

```bash
# Terminal 1: Backend
cd backend
.venv/bin/python -m uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Monitor database (optional)
# Use Neon console SQL Editor
```

### Making Changes

1. Modify source code
2. Frontend hot-reloads automatically
3. Backend auto-reloads with `--reload` flag
4. Database changes: run migrations in backend

## Deployment

### Environment Variables

Set these in your deployment platform (Vercel, Netlify, etc.):

- `DATABASE_URL` - Production Neon database URL
- `BETTER_AUTH_SECRET` - Generate with `openssl rand -base64 32`
- `BETTER_AUTH_URL` - Production frontend URL
- `NEXT_PUBLIC_API_URL` - Production backend API URL
- `ALLOWED_ORIGINS` (backend only) - Production frontend URL

### Build Command

```bash
npm run build
```

### Deploy Output

- `/.next/` - Production build files
- Deploy this directory to hosting platform

## Documentation

- [Better Auth Setup Guide](./BETTER_AUTH_SETUP.md) - Detailed Better Auth configuration
- [Backend README](../backend/README.md) - Backend API documentation
- [Project Spec](../specs/002-web-evolution/spec.md) - Feature specifications

## Security Notes

- ⚠️ **Never commit** `.env.local` or `.env` files
- ✅ Use `.env.example` as template for developers
- ✅ Rotate `BETTER_AUTH_SECRET` regularly in production
- ✅ Use HTTPS in production
- ✅ Restrict CORS to production frontend domain only
- ✅ All database connections use SSL (`sslmode=require`)

## License

See project root LICENSE file.

## Support

For issues or questions:
1. Check [Better Auth Setup Guide](./BETTER_AUTH_SETUP.md)
2. Run `node test-db-connection.js` for diagnostics
3. Check backend logs for API errors
4. Check browser console for frontend errors
