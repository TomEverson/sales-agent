---
ticket: TB-38
type: feat
title: Protected Routes
sprint: sprint-4
status: done
component: client
depends_on: TB-37
---

# TB-38: Protected Routes

> **Filename:** `tb-38-feat-protected-routes.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-37
- Sprint: sprint-4
- Component: client

## Goal
Protect all routes except /login. Redirect unauthenticated users to /login. Add logout functionality in navbar.

## Files to create / modify
- `client/src/context/AuthContext.tsx` ← create
- `client/src/App.tsx` ← modify (add AuthProvider, PrivateRoute wrapper)
- `client/src/components/ui/Navbar.tsx` ← modify (add logout button)

## What to build

### 1. Auth Context
Create `client/src/context/AuthContext.tsx`:
- React context providing: user, token, isLoading, setAuth(), logout()
- On mount: verify stored JWT token
- Functions to manage auth state and localStorage

### 2. Private Routes
Modify `client/src/App.tsx`:
- Wrap app in AuthProvider
- Add PrivateRoute component that:
  - Shows loading while checking auth
  - Redirects to /login if not authenticated
  - Renders children if authenticated
- Protect all routes except /login

### 3. Logout Button
Modify `client/src/components/ui/Navbar.tsx`:
- Add logout button (visible when user is authenticated)
- On click: clear token, redirect to /login

## Acceptance Criteria
- [x] Unauthenticated users redirected to /login when accessing protected routes
- [x] Authenticated users can access all protected routes
- [x] Logout button visible in navbar when authenticated
- [x] Logout clears token and redirects to /login

## Definition of Done
- [x] Build passes: `npm run build`
- [x] All acceptance criteria checked