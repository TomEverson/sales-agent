---
ticket: TB-37
type: feat
title: Admin Login Page
sprint: sprint-4
status: done
component: client
depends_on: TB-36
---

# TB-37: Admin Login Page

> **Filename:** `tb-37-feat-admin-login-page.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-36
- Sprint: sprint-4
- Component: client

## Goal
Create the admin login page at /login that authenticates against the backend and stores the JWT token in localStorage.

## Files to create / modify
- `client/src/pages/Login.tsx` ← create
- `client/src/types/index.ts` ← modify (add auth types)
- `client/src/services/api.ts` ← modify (add login/verify functions, add auth interceptor)

## What to build

### 1. Login Page
Create `client/src/pages/Login.tsx`:
- Email/password form
- POST to /auth/login
- On success: store JWT in localStorage, verify token, redirect to home
- Show error message on failure

### 2. API Service
Modify `client/src/services/api.ts`:
- Add `login(credentials)` function
- Add `verifyToken(token)` function
- Add axios interceptor to attach `Authorization: Bearer <token>` to all requests

### 3. TypeScript Types
Modify `client/src/types/index.ts`:
- Add `LoginCredentials` interface
- Add `AuthToken` interface
- Add `AuthUser` interface

## Acceptance Criteria
- [x] Login page accessible at /login
- [x] Form validates email and password
- [x] Successful login stores JWT in localStorage
- [x] Successful login redirects to home
- [x] Failed login shows error message

## Definition of Done
- [x] Build passes: `npm run build`
- [x] All acceptance criteria checked