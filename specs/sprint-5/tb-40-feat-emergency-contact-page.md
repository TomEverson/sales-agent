---
ticket: TB-40
type: feat
title: Emergency Contact Page
sprint: sprint-5
status: done
component: client
depends_on: TB-38
---

# TB-40: Emergency Contact Page

> **Filename:** `tb-40-feat-emergency-contact-page.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-38 (Protected Routes)
- Sprint: sprint-5
- Component: client

## Goal
Create a support/contact page where users can reach operators when something goes wrong with their bookings. This gives users a clear way to get help rather than being stuck.

## Files to create / modify
- `client/src/pages/Support.tsx` ← create
- `client/src/App.tsx` ← modify (add /support route)

## What to build

### 1. Support Page
Create `client/src/pages/Support.tsx`:
- Display operator contact information:
  - Phone/WhatsApp number
  - Email address
  - Telegram handle
- Common issue categories (Booking Issues, Payment Problems, Changes/Cancellations)
- Simple contact form or direct links
- Link back to home

### 2. Navigation
Add "Support" link to navbar (next to Logout)

### 3. Error State Integration
Consider showing a "Contact Support" link/button on booking error states in existing pages

## Acceptance Criteria
- [x] Support page accessible at /support
- [x] Contact information is clearly displayed
- [x] Navbar includes Support link

## Definition of Done
- [x] Support page implemented
- [x] Build passes: `npm run build`
- [x] All acceptance criteria checked