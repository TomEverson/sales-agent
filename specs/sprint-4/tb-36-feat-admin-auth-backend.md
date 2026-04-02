---
ticket: TB-36
type: feat
title: Admin Authentication - Backend API
sprint: sprint-4
status: done
component: server
depends_on: none
---

# TB-36: Admin Authentication - Backend API

> **Filename:** `tb-36-feat-admin-auth-backend.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: none
- Sprint: sprint-4
- Component: server

## Goal
Add JWT-based authentication for the admin dashboard. Admin credentials are admin@gmail.com / admin123 (bcrypt hashed).

## Files to create / modify
- `server/models/user.py` ← create
- `server/routers/auth.py` ← create
- `server/main.py` ← modify (register router, create admin on startup)
- `server/tests/test_auth.py` ← create

## What to build

### 1. User Model
Create `server/models/user.py`:
- `User` SQLModel table:
  - `id`: Primary key
  - `email`: str (unique, indexed)
  - `hashed_password`: str
  - `is_admin`: bool = True
- `UserCreate` schema for login
- `Token` schema for JWT response

### 2. Auth Router
Create `server/routers/auth.py`:
- `POST /auth/login` - Verify credentials, return JWT token
- `GET /auth/verify` - Verify token, return user info

### 3. Admin Seeding
On app startup, create the default admin user if not exists:
- email: admin@gmail.com
- password: admin123 (bcrypt hashed)

## Acceptance Criteria
- [x] User model exists with correct fields
- [x] POST /auth/login returns JWT token for valid credentials
- [x] POST /auth/login returns 401 for invalid credentials
- [x] GET /auth/verify returns user info for valid token
- [x] GET /auth/verify returns 401 for invalid token

## Test file
`server/tests/test_auth.py`

## Definition of Done
- [x] Test file exists at correct path
- [x] All tests pass: `uv run pytest tests/test_auth.py -v`
- [x] Linted: `uv run ruff check .`
- [x] All acceptance criteria checked