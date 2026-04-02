---
ticket: TB-43
type: feat
title: Booking Statistics Dashboard
sprint: sprint-5
status: done
component: client
depends_on: TB-36
---

# TB-43: Booking Statistics Dashboard

> **Filename:** `tb-43-feat-booking-statistics.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-36 (Admin Authentication)
- Sprint: sprint-5
- Component: client

## Goal
Show booking statistics on the dashboard/home page so admins can see:
- Total bookings made
- Total users who made bookings
- Total payments received
- Booking breakdown by type (flights, hotels, activities, transport)

## Files to create / modify
- `client/src/pages/Home.tsx` ← modify (add statistics cards)
- `client/src/services/api.ts` ← modify (add stats fetching functions)
- `client/src/types/index.ts` ← modify (add BookingStats type)

## What to build

### 1. Backend - Statistics Endpoint
Add to `server/routers/bookings.py`:
- `GET /bookings/stats` - Returns aggregated statistics:
  - Total booking count
  - Unique user count (by email)
  - Bookings by type (flights, hotels, activities, transport)
  - Total revenue (sum of prices)

Or create `GET /stats/overview`:
```json
{
  "total_bookings": 45,
  "unique_users": 23,
  "total_revenue": 125000.00,
  "by_type": {
    "flights": 20,
    "hotels": 15,
    "activities": 30,
    "transport": 25
  }
}
```

### 2. Client - Statistics Display
Modify `client/src/pages/Home.tsx`:
- Add statistics cards at the top:
  - Total Bookings
  - Total Users
  - Total Revenue
  - Bookings by Type (pie chart or bar)
- Show real-time stats from the API

### 3. Types
Add `BookingStats` type:
```typescript
interface BookingStats {
  total_bookings: number
  unique_users: number
  total_revenue: number
  by_type: {
    flights: number
    hotels: number
    activities: number
    transport: number
  }
}
```

### 4. Payment Stats
Also show payment statistics:
- Total payments initiated
- Total payments confirmed
- Pending payments

## Acceptance Criteria
- [x] Home page shows total booking count
- [x] Home page shows total unique users count
- [x] Home page shows booking breakdown by type
- [x] Stats update from backend API

## Definition of Done
- [x] Backend stats endpoint implemented (`GET /bookings/stats`)
- [x] Frontend displays statistics cards
- [x] Build passes: `npm run build`
- [x] All acceptance criteria checked