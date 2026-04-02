# Sprint 5

## Tickets

| Ticket | Type | Title | Status |
|--------|------|-------|--------|
| TB-39 | test | Playwright E2E Test Setup | done |
| TB-40 | feat | Emergency Contact Page | done |
| TB-41 | feat | Bot Error Fallback with Operator Contact | done |
| TB-42 | feat | Booking Packages View | done |
| TB-43 | feat | Booking Statistics Dashboard | done |
| TB-44 | feat | Persistent Memory for Bot | done |

## Goals

- **Automated Testing**: Add Playwright for E2E testing
  - TB-39: Set up Playwright with tests for login, navigation, and inventory viewing
- **Operator Support**: Add ways for users to reach operators when issues occur
  - TB-40: Support/contact page in the dashboard for help
  - TB-41: Bot gracefully hands off to human operator on errors
- **Dashboard Improvements**: Better booking views and statistics
  - TB-42: Show bookings as packages instead of individual items
  - TB-43: Show booking statistics (users, payments, revenue)
- **Bot Improvements**: Make bot more reliable
  - TB-44: Persist conversation history and preferences across restarts