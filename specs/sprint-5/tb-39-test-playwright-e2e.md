---
ticket: TB-39
type: test
title: Playwright E2E Test Setup
sprint: sprint-5
status: done
component: client
depends_on: none
---

# TB-39: Playwright E2E Test Setup

> **Filename:** `tb-39-test-playwright-e2e.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: none
- Sprint: sprint-5
- Component: client

## Goal
Set up Playwright for end-to-end testing. Create tests for critical user flows: admin login, navigation, and viewing inventory (flights, hotels, activities).

## Files to create / modify
- `client/package.json` ← modify (add playwright and test dependencies)
- `client/playwright.config.ts` ← create
- `client/tests/e2e.spec.ts` ← create
- `client/tests/login.spec.ts` ← create

## What to build

### 1. Install Playwright
Modify `client/package.json`:
- Add `@playwright/test` as dev dependency
- Add `playwright` as dev dependency
- Add test script: `"test:e2e": "playwright test"`

### 2. Playwright Config
Create `client/playwright.config.ts`:
- Base URL: `http://localhost:5173`
- Use `webServer` to start dev server automatically
- Configure `trace` and `screenshot` on failure
- Set `testDir: './tests'`
- Set `timeout: 30000`

### 3. E2E Test Suite
Create `client/tests/e2e.spec.ts`:
- Test 1: Home page loads successfully
- Test 2: Navigation to Flights page
- Test 3: Navigation to Hotels page
- Test 4: Navigation to Activities page
- Test 5: Navigation to Transport page
- Test 6: Navigation to Bookings page

### 4. Login Test Suite
Create `client/tests/login.spec.ts`:
- Test 1: Login page renders correctly
- Test 2: Login with invalid credentials shows error
- Test 3: Login with valid credentials redirects to home (requires server running)

## Acceptance Criteria
- [x] Playwright installed and configured
- [x] `npm run test:e2e` runs without errors
- [x] E2E tests cover all main navigation routes
- [x] Login page tests pass

## Test file
- `client/tests/e2e.spec.ts`
- `client/tests/login.spec.ts`

## Manual test
```bash
# Run tests (webServer in playwright.config.ts starts both backend and frontend)
cd client && npm run test:e2e
```

## Definition of Done
- [x] Test files exist at correct paths
- [x] Tests pass: `npm run test:e2e` (15/15 passing)
- [x] Linted: `uv run ruff check .` on server
- [x] All acceptance criteria checked