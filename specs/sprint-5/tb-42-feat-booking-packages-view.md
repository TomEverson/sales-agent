---
ticket: TB-42
type: feat
title: Booking Packages View
sprint: sprint-5
status: done
component: client
depends_on: TB-36
---

# TB-42: Booking Packages View

> **Filename:** `tb-42-feat-booking-packages-view.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-36 (Admin Authentication)
- Sprint: sprint-5
- Component: client

## Goal
The bookings tab currently shows individual bookings (flights, hotels, activities, transport separately). Group all bookings by their payment/booking reference to show complete packages as users booked them.

## Files to create / modify
- `client/src/pages/Bookings.tsx` ← modify (group bookings by package)
- `client/src/services/api.ts` ← modify (add endpoint to fetch all bookings grouped)
- `client/src/types/index.ts` ← modify (add PackageBooking type)

## What to build

### 1. Backend - Group Bookings by Package
The `booking_reference` links all items in a package. Group bookings by this reference.

Add to `server/routers/bookings.py` or create a new endpoint:
- `GET /bookings/packages` - Returns all bookings grouped by booking_reference

### 2. Client - Group Bookings Display
Modify `client/src/pages/Bookings.tsx`:
- Fetch all bookings (flights, hotels, activities, transport)
- Group them by booking_reference
- Display as packages with:
  - Booking reference
  - All items in the package (flight, hotel, activity, transport)
  - Total cost
  - Status
  - Date created

### 3. Types
Add `PackageBooking` type:
```typescript
interface PackageBooking {
  booking_reference: string
  items: {
    flight?: FlightBooking
    hotel?: HotelBooking
    activity?: ActivityBooking
    transport?: TransportBooking
  }
  total_amount: number
  status: string
  created_at: string
}
```

## Acceptance Criteria
- [x] Bookings tab shows packages instead of individual bookings
- [x] Each package shows all related booking items grouped together
- [x] Package displays booking reference, items, total, status

## Definition of Done
- [x] Backend groups bookings by reference (`GET /bookings/packages`)
- [x] Frontend displays packages view
- [x] Build passes: `npm run build`
- [x] All acceptance criteria checked