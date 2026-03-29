---
ticket: TB-22
type: feat
title: UI — My Bookings Page
sprint: sprint-3
status: todo
component: client
depends_on: TB-18, TB-19, TB-20, TB-21
---

# TB-22: UI — My Bookings Page

## Context
Read `rules/client.md` and `rules/base.md` before starting.
Read `client/src/types/index.ts` — all 4 booking types already exist from TB-18.
Read `client/src/services/api.ts` — you will be adding 4 getter functions.
Read `client/src/App.tsx` — you will add the `/bookings` route.
Read `client/src/components/ui/Navbar.tsx` — you will add a Bookings nav link.

## Dependency
TB-18 through TB-21 must be complete (all booking types and API functions exist).

---

## Goal
Add a **My Bookings** page at `/bookings`.

The user enters their email address and the page fetches and displays all their bookings
across all 4 types (flights, hotels, activities, transport) in a unified view,
each with its booking reference, status, and key details.

---

## Files to create / modify

| File | Action |
|------|--------|
| `client/src/services/api.ts` | modify — add 4 getXxxBookings functions |
| `client/src/components/booking/BookingCard.tsx` | create — unified booking display card |
| `client/src/pages/Bookings.tsx` | create — My Bookings page |
| `client/src/App.tsx` | modify — add `/bookings` route |
| `client/src/components/ui/Navbar.tsx` | modify — add Bookings nav link |

---

## What to build

### 1. API — add to `client/src/services/api.ts`

```typescript
export async function getFlightBookings(email: string): Promise<FlightBooking[]> {
  const { data } = await api.get<FlightBooking[]>('/bookings/flights', { params: { email } })
  return data
}

export async function getHotelBookings(email: string): Promise<HotelBooking[]> {
  const { data } = await api.get<HotelBooking[]>('/bookings/hotels', { params: { email } })
  return data
}

export async function getActivityBookings(email: string): Promise<ActivityBooking[]> {
  const { data } = await api.get<ActivityBooking[]>('/bookings/activities', { params: { email } })
  return data
}

export async function getTransportBookings(email: string): Promise<TransportBooking[]> {
  const { data } = await api.get<TransportBooking[]>('/bookings/transport', { params: { email } })
  return data
}
```

- All 4 functions: on error → log to console and return `[]`

### 2. BookingCard — `client/src/components/booking/BookingCard.tsx`

A single card component that can display any booking type.

```typescript
type AnyBooking =
  | (FlightBooking & { kind: 'flight' })
  | (HotelBooking & { kind: 'hotel' })
  | (ActivityBooking & { kind: 'activity' })
  | (TransportBooking & { kind: 'transport' })

interface BookingCardProps {
  booking: AnyBooking
}
```

Layout per type:

**Flight booking card:**
```
✈️  Flight Booking
Reference: TB-20260328-A3F7   [copy]
Passenger: John Smith
Seats: 1 | Status: confirmed
Booked: 28 Mar 2026
```

**Hotel booking card:**
```
🏨  Hotel Booking
Reference: TB-20260328-B2K9   [copy]
Guest: John Smith
Check-in: 28 Mar → Check-out: 30 Mar (2 nights)
Status: confirmed
```

**Activity booking card:**
```
🎯  Activity Booking
Reference: TB-20260328-C5T1   [copy]
Participant: John Smith
Date: 29 Mar 2026 | Participants: 1
Status: confirmed
```

**Transport booking card:**
```
🚗  Transport Booking
Reference: TB-20260328-D7R3   [copy]
Passenger: John Smith
Passengers: 1 | Status: confirmed
Booked: 28 Mar 2026
```

Design:
- White card, subtle border, rounded-xl, shadow-sm
- Type icon + label in the card header (sky-500 tint background for header strip)
- Reference in monospace with copy-to-clipboard icon
- Status badge: green pill for `confirmed`, gray for anything else
- Consistent spacing matching existing cards in the app

### 3. Bookings Page — `client/src/pages/Bookings.tsx`

Layout:
```
[Page title: My Bookings]

[Email input + Search button]

[Loading spinner while fetching]

[Results — sorted by created_at descending, most recent first]

  ✈️ Flights (N)
  [FlightBookingCard list]

  🏨 Hotels (N)
  [HotelBookingCard list]

  🎯 Activities (N)
  [ActivityBookingCard list]

  🚗 Transport (N)
  [TransportBookingCard list]

[Empty state if all 4 return [] — "No bookings found for this email."]
```

Behaviour:
- Email input with a **Search** button — does not auto-fetch on load
- On search: fetch all 4 types in parallel using `Promise.all`
- Show spinner during fetch
- Each section only rendered if it has at least 1 result
- If all sections are empty → show empty state message
- Email input persists in URL query param: `/bookings?email=john@example.com`
  so the page is shareable/refreshable
- On page load, if `?email=` param exists → pre-fill and auto-search

### 4. App.tsx — add route

```typescript
import Bookings from './pages/Bookings'

// add inside <Routes>:
<Route path="/bookings" element={<Bookings />} />
```

### 5. Navbar.tsx — add link

Add `Bookings` to the navigation links, between `Transport` and the end:
```
Home  Flights  Hotels  Activities  Transport  Bookings
```

---

## File structure after TB-22
```
client/src/
├── components/
│   ├── booking/
│   │   ├── BookingModal.tsx          ← from TB-18
│   │   ├── BookingConfirmation.tsx   ← from TB-18
│   │   └── BookingCard.tsx           ← created
│   └── ui/
│       └── Navbar.tsx                ← modified (Bookings link added)
├── pages/
│   └── Bookings.tsx                  ← created
├── services/
│   └── api.ts                        ← modified (4 getter functions added)
└── App.tsx                           ← modified (/bookings route added)
```

---

## Acceptance Criteria

### API
- [ ] All 4 `getXxxBookings(email)` functions exist in `api.ts`
- [ ] All 4 use `email` as a query param
- [ ] Errors return `[]` and log to console

### BookingCard
- [ ] Renders correctly for all 4 booking types
- [ ] Type icon and label shown in header
- [ ] Reference displayed in monospace with copy-to-clipboard
- [ ] Status badge is green for `confirmed`
- [ ] No `any` types used

### Bookings Page
- [ ] Email input and Search button render on load
- [ ] Clicking Search fetches all 4 booking types in parallel
- [ ] Spinner shown during fetch
- [ ] Each section shown only when it has results
- [ ] Empty state shown when all 4 return empty
- [ ] `?email=` query param pre-fills and auto-searches on load
- [ ] Results sorted most-recent-first within each section

### Navigation
- [ ] `/bookings` route registered in `App.tsx`
- [ ] `Bookings` link added to Navbar

### General
- [ ] No TypeScript errors: `npm run build` passes
- [ ] Tailwind style matches existing client (white, slate, sky-500)

---

## Manual test

1. Make some bookings via the cards (TB-18 through TB-21)
2. Navigate to `/bookings`
3. Enter the email used in those bookings → click Search
4. Verify all booking types appear in their sections
5. Verify reference copy button works
6. Open `/bookings?email=john@example.com` directly → page pre-fills and auto-searches
7. Enter an unknown email → `No bookings found for this email.` shown
8. Verify Bookings link in Navbar navigates to `/bookings`

---

## When done
Print: ✅ TB-22 complete
All booking UI stories are complete (TB-18 through TB-22).
Run `npm run build` — must complete with zero TypeScript errors.
