---
ticket: TB-19
type: feat
title: UI — Hotel Booking Form
sprint: sprint-3
status: todo
component: client
depends_on: TB-15, TB-18
---

# TB-19: UI — Hotel Booking Form

## Context
Read `rules/client.md` and `rules/base.md` before starting.
Read `client/src/components/booking/BookingModal.tsx` from TB-18 — reuse it.
Read `client/src/components/booking/BookingConfirmation.tsx` from TB-18 — reuse it.
Read `client/src/types/index.ts` — `HotelBooking` and `CreateHotelBooking` already exist from TB-18.
Read `client/src/services/api.ts` — you will be adding `bookHotel`.

## Dependency
TB-15 (server hotel booking endpoint) must be complete.
TB-18 (BookingModal + BookingConfirmation + booking types) must be complete.

---

## Goal
Add a hotel booking flow to `HotelCard`.

Each `HotelCard` gets a **"Book"** button. Clicking it opens the shared `BookingModal`
containing a `HotelBookingForm`. The form collects guest name, email, check-in date,
check-out date, and number of guests. Nights are calculated automatically from the dates.
On success shows `BookingConfirmation`.

---

## Files to create / modify

| File | Action |
|------|--------|
| `client/src/services/api.ts` | modify — add bookHotel |
| `client/src/components/hotels/HotelBookingForm.tsx` | create |
| `client/src/components/hotels/HotelCard.tsx` | modify — add Book button |

---

## What to build

### 1. API — add to `client/src/services/api.ts`

```typescript
export async function bookHotel(data: CreateHotelBooking): Promise<HotelBooking> {
  const { data: res } = await api.post<HotelBooking>('/bookings/hotels', data)
  return res
}
```

- On 422 → throw with message `"Not enough rooms available."`
- On 404 → throw with message `"Hotel not found."`

### 2. HotelBookingForm — `client/src/components/hotels/HotelBookingForm.tsx`

```typescript
interface HotelBookingFormProps {
  hotel: Hotel
  onSuccess: (booking: HotelBooking) => void
  onCancel: () => void
}
```

Fields:
| Field | Type | Label | Validation |
|-------|------|-------|------------|
| `guest_name` | text | Guest Name | required |
| `contact_email` | email | Email Address | required, valid email |
| `check_in_date` | date | Check-in Date | required, must not be in the past |
| `check_out_date` | date | Check-out Date | required, must be after check_in_date |
| `guests` | number | Guests | required, min 1 |

Derived field (not a form input — computed and displayed):
- `nights` = number of days between check_in_date and check_out_date
- Show below the dates: `2 nights` in muted text
- `nights` is computed client-side and sent in the payload

Layout:
- Read-only hotel summary at top: `The Singapore Suites | ⭐⭐⭐⭐ | $120.00/night`
- Date inputs side by side on desktop, stacked on mobile
- `Nights: N` shown between the date row and the guests field
- Submit button: `Book Hotel` — sky-500, full width
- Loading: `Booking...` + disabled
- Error banner for API errors
- Cancel link below button

On submit: call `bookHotel` with `nights` derived from the date diff.
On success: call `onSuccess(booking)`.

### 3. HotelCard — modify `client/src/components/hotels/HotelCard.tsx`

- Add **"Book"** button (same style as FlightCard: sky-500, bottom-right)
- On click: open `BookingModal` with title `Book Hotel` and `HotelBookingForm` inside
- On booking success: replace form with `BookingConfirmation`
  - `summary`: `"The Singapore Suites | ⭐⭐⭐⭐ | 28 Mar → 30 Mar (2 nights)"`
- On confirmation close: modal closes, card shows decremented `rooms_available`

---

## Acceptance Criteria

- [ ] `bookHotel(data)` exists in `api.ts`, POSTs to `/bookings/hotels`
- [ ] 422/404 produce human-readable thrown errors
- [ ] `HotelBookingForm` renders with all 5 fields
- [ ] `nights` is computed from dates and sent in payload — never a manual input
- [ ] `check_out_date` validation rejects dates ≤ `check_in_date`
- [ ] `check_in_date` validation rejects past dates
- [ ] Loading state disables button and shows `Booking...`
- [ ] API errors shown in error banner
- [ ] `HotelCard` Book button opens modal with `HotelBookingForm`
- [ ] `BookingConfirmation` shown on success
- [ ] No TypeScript errors: `npm run build` passes
- [ ] Tailwind style matches existing client

---

## Manual test

1. Navigate to `/hotels`
2. Click **Book** on any hotel card
3. Select check-in: tomorrow, check-out: day after → verify `Nights: 1` appears
4. Select check-out before check-in → verify validation error
5. Fill all fields and submit → verify `BookingConfirmation` shown
6. Verify `rooms_available` decremented on the card after close

---

## When done
Print: ✅ TB-19 complete
