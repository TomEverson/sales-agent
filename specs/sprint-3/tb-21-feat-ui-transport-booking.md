---
ticket: TB-21
type: feat
title: UI — Transport Booking Form
sprint: sprint-3
status: todo
component: client
depends_on: TB-17, TB-18
---

# TB-21: UI — Transport Booking Form

## Context
Read `rules/client.md` and `rules/base.md` before starting.
Read `client/src/components/booking/BookingModal.tsx` from TB-18 — reuse it.
Read `client/src/components/booking/BookingConfirmation.tsx` from TB-18 — reuse it.
Read `client/src/types/index.ts` — `TransportBooking` and `CreateTransportBooking` already exist from TB-18.

## Dependency
TB-17 (server transport booking endpoint) must be complete.
TB-18 (BookingModal + BookingConfirmation + booking types) must be complete.

---

## Goal
Add a transport booking flow to `TransportCard`.

Each `TransportCard` gets a **"Book"** button. Clicking it opens the shared `BookingModal`
containing a `TransportBookingForm`. The form collects passenger name, email, and number
of passengers. On success shows `BookingConfirmation`.

Transport uses `capacity` (not `seats_available`) — the Book button should be disabled
when `capacity === 0`.

---

## Files to create / modify

| File | Action |
|------|--------|
| `client/src/services/api.ts` | modify — add bookTransport |
| `client/src/components/transport/TransportBookingForm.tsx` | create |
| `client/src/components/transport/TransportCard.tsx` | modify — add Book button |

---

## What to build

### 1. API — add to `client/src/services/api.ts`

```typescript
export async function bookTransport(data: CreateTransportBooking): Promise<TransportBooking> {
  const { data: res } = await api.post<TransportBooking>('/bookings/transport', data)
  return res
}
```

- On 422 → throw with message `"Not enough capacity available."`
- On 404 → throw with message `"Transport not found."`

### 2. TransportBookingForm — `client/src/components/transport/TransportBookingForm.tsx`

```typescript
interface TransportBookingFormProps {
  transport: Transport
  onSuccess: (booking: TransportBooking) => void
  onCancel: () => void
}
```

Fields:
| Field | Type | Label | Validation |
|-------|------|-------|------------|
| `passenger_name` | text | Passenger Name | required |
| `contact_email` | email | Email Address | required, valid email |
| `passengers` | number | Passengers | required, min 1, max transport.capacity |

Layout:
- Read-only transport summary at top:
  `🚗 Car | Singapore Airport → Singapore City`
  `Departs: Sat 08:00 → Arrives: Sat 08:45 | $30.00`
- `passengers` field capped at `transport.capacity`
- Show `Capacity: {transport.capacity}` as muted hint below the passengers field
- Submit button: `Book Transport` — sky-500, full width
- Loading: `Booking...` + disabled
- Error banner for API errors
- Cancel link

On success: call `onSuccess(booking)`.

### 3. TransportCard — modify `client/src/components/transport/TransportCard.tsx`

- Add **"Book"** button (sky-500, bottom-right)
- Button is **disabled** when `transport.capacity === 0`, with label `Full`
- On click: open `BookingModal` with title `Book Transport` and `TransportBookingForm`
- On success: show `BookingConfirmation`
  - `summary`: `"Car | Singapore Airport → Singapore City | 1 passenger"`
- On confirmation close: modal closes, card shows decremented `capacity`

---

## Acceptance Criteria

- [ ] `bookTransport(data)` exists in `api.ts`, POSTs to `/bookings/transport`
- [ ] 422/404 produce human-readable thrown errors
- [ ] `TransportBookingForm` renders with all 3 fields
- [ ] `passengers` field max is capped at `transport.capacity`
- [ ] Loading state shown during submission
- [ ] API errors shown in error banner
- [ ] Book button disabled with label `Full` when `capacity === 0`
- [ ] `BookingConfirmation` shown on success
- [ ] `capacity` decremented on card after booking closes
- [ ] No TypeScript errors: `npm run build` passes
- [ ] Tailwind style matches existing client

---

## Manual test

1. Navigate to `/transport`
2. Click **Book** on any transport card → modal opens with route summary
3. Set passengers > capacity → verify field is capped
4. Fill valid fields and submit → `BookingConfirmation` shown
5. Verify `capacity` decremented on the card after close
6. Find a transport with capacity 0 (or book until full) → button shows `Full` and is disabled

---

## When done
Print: ✅ TB-21 complete
