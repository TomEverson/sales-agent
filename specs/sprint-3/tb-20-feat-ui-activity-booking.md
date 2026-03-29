---
ticket: TB-20
type: feat
title: UI — Activity Booking Form
sprint: sprint-3
status: todo
component: client
depends_on: TB-16, TB-18
---

# TB-20: UI — Activity Booking Form

## Context
Read `rules/client.md` and `rules/base.md` before starting.
Read `client/src/components/booking/BookingModal.tsx` from TB-18 — reuse it.
Read `client/src/components/booking/BookingConfirmation.tsx` from TB-18 — reuse it.
Read `client/src/types/index.ts` — `ActivityBooking` and `CreateActivityBooking` already exist from TB-18.

## Dependency
TB-16 (server activity booking endpoint) must be complete.
TB-18 (BookingModal + BookingConfirmation + booking types) must be complete.

---

## Goal
Add an activity booking flow to `ActivityCard`.

Each `ActivityCard` gets a **"Book"** button. Clicking it opens the shared `BookingModal`
containing an `ActivityBookingForm`. The form collects participant name, email, activity
date, and number of participants.

**Key difference from other booking types:** Activities have no capacity limit — the Book
button should never be disabled due to availability, and there is no 422 case to handle.

---

## Files to create / modify

| File | Action |
|------|--------|
| `client/src/services/api.ts` | modify — add bookActivity |
| `client/src/components/activities/ActivityBookingForm.tsx` | create |
| `client/src/components/activities/ActivityCard.tsx` | modify — add Book button |

---

## What to build

### 1. API — add to `client/src/services/api.ts`

```typescript
export async function bookActivity(data: CreateActivityBooking): Promise<ActivityBooking> {
  const { data: res } = await api.post<ActivityBooking>('/bookings/activities', data)
  return res
}
```

- On 404 → throw with message `"Activity not found."`
- No 422 case — activities have no capacity limit

### 2. ActivityBookingForm — `client/src/components/activities/ActivityBookingForm.tsx`

```typescript
interface ActivityBookingFormProps {
  activity: Activity
  onSuccess: (booking: ActivityBooking) => void
  onCancel: () => void
}
```

Fields:
| Field | Type | Label | Validation |
|-------|------|-------|------------|
| `participant_name` | text | Your Name | required |
| `contact_email` | email | Email Address | required, valid email |
| `activity_date` | date | Activity Date | required, must not be in the past |
| `participants` | number | Participants | required, min 1 |

Layout:
- Read-only activity summary at top:
  `Gardens by the Bay Tour | 🌿 Nature | 3hrs | $25.00`
- Show `availability` field value as a small badge (e.g. `daily`, `weekends`)
- Fields below with clear labels
- Submit button: `Book Activity` — sky-500, full width
- Loading: `Booking...` + disabled
- Error banner for API errors (404 only — no seat/room errors)
- Cancel link

On success: call `onSuccess(booking)`.

### 3. ActivityCard — modify `client/src/components/activities/ActivityCard.tsx`

- Add **"Book"** button (sky-500, bottom-right, same style as other cards)
- Book button is **always enabled** — activities have no availability count to check
- On click: open `BookingModal` with title `Book Activity` and `ActivityBookingForm`
- On success: show `BookingConfirmation`
  - `summary`: `"Gardens by the Bay Tour | 29 Mar 2026 | 1 participant"`
- On confirmation close: modal closes
- Note: `ActivityCard` does NOT need to update any availability count after booking

---

## Acceptance Criteria

- [ ] `bookActivity(data)` exists in `api.ts`, POSTs to `/bookings/activities`
- [ ] No 422 handling in `bookActivity` — activities have no capacity
- [ ] `ActivityBookingForm` renders with all 4 fields
- [ ] `activity_date` rejects past dates
- [ ] Loading state shown during submission
- [ ] API errors shown in error banner
- [ ] `ActivityCard` Book button is always enabled (no capacity check)
- [ ] `BookingConfirmation` shown on success
- [ ] No TypeScript errors: `npm run build` passes
- [ ] Tailwind style matches existing client

---

## Manual test

1. Navigate to `/activities`
2. Click **Book** on any activity card → modal opens
3. Set past date → verify validation error
4. Fill valid fields and submit → `BookingConfirmation` shown
5. Close and click Book again on the same activity → should work again (no capacity limit)

---

## When done
Print: ✅ TB-20 complete
