---
ticket: TB-18
type: feat
title: UI — Flight Booking Form
sprint: sprint-3
status: todo
component: client
depends_on: TB-14
---

# TB-18: UI — Flight Booking Form

## Context
Read `rules/client.md` — stack is React + Vite + TypeScript + Tailwind + Axios.
Read `client/src/types/index.ts` — you will be adding booking types here.
Read `client/src/services/api.ts` — you will be adding booking API functions here.
Read `client/src/components/flights/FlightCard.tsx` — you will add a Book button.
Read `rules/base.md` before starting.

## Dependency
TB-14 (server flight booking endpoint) must be complete and running.
`POST /bookings/flights` must exist at `http://localhost:8000`.

---

## Goal
Add a flight booking flow to the client.

Each `FlightCard` gets a **"Book"** button. Clicking it opens a `BookingModal` containing
a `FlightBookingForm`. The user fills in name, email, and seat count, submits, and sees
a `BookingConfirmation` with the reference number on success.

This ticket also creates the shared `BookingModal` and `BookingConfirmation` components
that TB-19 through TB-21 will reuse.

---

## Files to create / modify

| File | Action |
|------|--------|
| `client/src/types/index.ts` | modify — add all 4 booking types + create types |
| `client/src/services/api.ts` | modify — add bookFlight (+ stubs for TB-19–21) |
| `client/src/components/booking/BookingModal.tsx` | create — shared modal shell |
| `client/src/components/booking/BookingConfirmation.tsx` | create — shared success view |
| `client/src/components/flights/FlightBookingForm.tsx` | create — flight-specific form |
| `client/src/components/flights/FlightCard.tsx` | modify — add Book button |

---

## What to build

### 1. Types — add to `client/src/types/index.ts`

```typescript
// Booking response types (returned by server)
export interface FlightBooking {
  id: number
  flight_id: number
  passenger_name: string
  contact_email: string
  booking_reference: string
  status: string
  seats_booked: number
  created_at: string
}

export interface HotelBooking {
  id: number
  hotel_id: number
  guest_name: string
  contact_email: string
  check_in_date: string
  check_out_date: string
  nights: number
  guests: number
  booking_reference: string
  status: string
  created_at: string
}

export interface ActivityBooking {
  id: number
  activity_id: number
  participant_name: string
  contact_email: string
  activity_date: string
  participants: number
  booking_reference: string
  status: string
  created_at: string
}

export interface TransportBooking {
  id: number
  transport_id: number
  passenger_name: string
  contact_email: string
  passengers: number
  booking_reference: string
  status: string
  created_at: string
}

// Booking create types (sent to server)
export interface CreateFlightBooking {
  flight_id: number
  passenger_name: string
  contact_email: string
  seats_booked: number
}

export interface CreateHotelBooking {
  hotel_id: number
  guest_name: string
  contact_email: string
  check_in_date: string
  check_out_date: string
  nights: number
  guests: number
}

export interface CreateActivityBooking {
  activity_id: number
  participant_name: string
  contact_email: string
  activity_date: string
  participants: number
}

export interface CreateTransportBooking {
  transport_id: number
  passenger_name: string
  contact_email: string
  passengers: number
}
```

### 2. API — add to `client/src/services/api.ts`

```typescript
export async function bookFlight(data: CreateFlightBooking): Promise<FlightBooking> {
  const { data: res } = await api.post<FlightBooking>('/bookings/flights', data)
  return res
}
```

- On 422 (no seats) → throw with message `"Not enough seats available."`
- On 404 → throw with message `"Flight not found."`
- Let other errors propagate — the form handles them

### 3. BookingModal — `client/src/components/booking/BookingModal.tsx`

A reusable modal shell used by all 4 booking forms.

```typescript
interface BookingModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}
```

Behaviour:
- Renders a full-screen semi-transparent overlay (`bg-black/50`) when `isOpen` is true
- Centered white card: `max-w-md w-full`, `rounded-2xl`, `shadow-xl`, `p-6`
- Title bar: title text on the left, `×` close button on the right
- Clicking the overlay background calls `onClose`
- Pressing `Escape` calls `onClose`
- Does not render (returns null) when `isOpen` is false
- Traps scroll on `<body>` while open

### 4. BookingConfirmation — `client/src/components/booking/BookingConfirmation.tsx`

Shown inside `BookingModal` after a successful booking.

```typescript
interface BookingConfirmationProps {
  reference: string
  summary: string        // e.g. "Bangkok → Singapore | AirAsia | Economy"
  email: string
  onClose: () => void
}
```

Layout:
```
✅  (large green checkmark icon or emoji)
Booking Confirmed!
Reference: TB-20260328-A3F7   ← monospace, copyable
[summary line]
Confirmation sent to: [email]
[Close button — sky-500]
```

- Reference number displayed in a monospace code block with a copy-to-clipboard button
- `onClose` wired to the Close button

### 5. FlightBookingForm — `client/src/components/flights/FlightBookingForm.tsx`

```typescript
interface FlightBookingFormProps {
  flight: Flight
  onSuccess: (booking: FlightBooking) => void
  onCancel: () => void
}
```

Fields:
| Field | Type | Label | Validation |
|-------|------|-------|------------|
| `passenger_name` | text | Passenger Name | required |
| `contact_email` | email | Email Address | required, valid email |
| `seats_booked` | number | Seats | required, min 1, max seats_available |

Layout:
- Show a read-only flight summary at the top of the form:
  `Bangkok → Singapore | AirAsia | Economy | $85.00`
- Form fields below with clear labels
- Inline validation errors beneath each field (shown on blur or submit attempt)
- Submit button: `Book Flight` — sky-500, full width, disabled while loading
- Loading state: button shows `Booking...` and is disabled
- Error banner at top of form for API errors (e.g. "Not enough seats available.")
- Cancel link below the button

On successful submit → call `onSuccess(booking)`.

### 6. FlightCard — modify `client/src/components/flights/FlightCard.tsx`

Add a **"Book"** button to each card:
- Position: bottom-right of the card
- Style: `sky-500` background, white text, small rounded button
- On click: open `BookingModal` with `FlightBookingForm` inside
- When booking is confirmed: show `BookingConfirmation` inside the same modal
- After confirmation is closed: modal closes, card shows updated `seats_available` (re-fetch or optimistic decrement)

---

## File structure after TB-18
```
client/src/
├── types/
│   └── index.ts                          ← modified (booking types added)
├── services/
│   └── api.ts                            ← modified (bookFlight added)
├── components/
│   ├── booking/
│   │   ├── BookingModal.tsx              ← created
│   │   └── BookingConfirmation.tsx       ← created
│   └── flights/
│       ├── FlightCard.tsx                ← modified (Book button added)
│       └── FlightBookingForm.tsx         ← created
```

---

## Acceptance Criteria

### Types
- [ ] All 4 booking response types exported from `types/index.ts`
- [ ] All 4 booking create types exported from `types/index.ts`
- [ ] No `any` types used anywhere

### API
- [ ] `bookFlight(data)` exists in `api.ts` and POSTs to `/bookings/flights`
- [ ] 422 and 404 responses produce thrown errors with human-readable messages

### BookingModal
- [ ] Modal renders only when `isOpen` is true
- [ ] Overlay click and Escape key both call `onClose`
- [ ] Title and children rendered correctly
- [ ] Body scroll locked while modal is open

### BookingConfirmation
- [ ] Shows reference number in monospace/code style
- [ ] Copy-to-clipboard works on reference number
- [ ] Shows email address
- [ ] Close button calls `onClose`

### FlightBookingForm
- [ ] All 3 fields render with correct labels
- [ ] Validation fires on blur and on submit attempt
- [ ] `seats_booked` max is capped at `flight.seats_available`
- [ ] Submit calls `bookFlight` with correct payload
- [ ] Loading state disables button and shows `Booking...`
- [ ] API error shown in error banner
- [ ] `onSuccess` called with booking on 201 response

### FlightCard
- [ ] Book button visible on each card
- [ ] Clicking Book opens BookingModal with FlightBookingForm
- [ ] After successful booking, BookingConfirmation is shown
- [ ] After confirmation closed, modal closes

### General
- [ ] No TypeScript errors: `npm run build` passes cleanly
- [ ] No `console.error` in happy path
- [ ] Tailwind design matches existing client style (white, slate, sky-500 accent)

---

## Manual test

1. Start server: `cd server && uv run uvicorn main:app --reload`
2. Start client: `cd client && npm run dev`
3. Navigate to `/flights`
4. Click **Book** on any flight card
5. Verify modal opens with flight summary and form
6. Submit with empty fields → validation errors shown
7. Fill in valid data and submit
8. Verify `BookingConfirmation` shown with reference `TB-XXXXXXXX-XXXX`
9. Click copy icon on reference → confirm copied to clipboard
10. Close modal → verify `seats_available` decremented on the card

---

## When done
Print: ✅ TB-18 complete
Do not proceed to TB-19 until all acceptance criteria above are checked.
