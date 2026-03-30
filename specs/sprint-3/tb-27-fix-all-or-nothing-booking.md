---
ticket: TB-27
type: fix
title: Booking Flow Should Be All-or-Nothing
sprint: sprint-3
status: todo
component: salebot
depends_on: TB-23
---

# TB-27: Booking Flow Should Be All-or-Nothing

## Context

Currently, the agent books items individually (flight, hotel, activity, transport) as separate transactions. If one item fails (e.g., hotel not available), the already-booked items (flights, activities) are already committed, leading to an inconsistent state.

The expected behavior: **Either all items in the package are booked successfully, or no items are booked at all.**

Read `rules/base.md` and `rules/bot.md` before starting.

---

## Problem

The agent's current booking flow in `system_prompt.md` (Section 9) shows items being booked sequentially with individual confirmations. This can lead to partial bookings:

```
1. User confirms flight → book_flight → success
2. User confirms hotel → book_hotel → FAILED (not available)
3. Result: Flight booked but no hotel = inconsistent package
```

---

## Files to modify

| File | Change |
|------|--------|
| `salebot/prompts/system_prompt.md` | Update booking flow to collect all items first, then book all at once or reject all |
| `salebot/prompts/system_prompt_my.md` | Same update for Burmese version |

---

## What to build

### All-or-Nothing Booking Flow

After presenting a package, the agent should:

1. **Collect all booking details upfront** before making any bookings:
   - Flight: passenger name → email → seats
   - Hotel: guest name → email → check-in → check-out → guests
   - Activity: participant name → email → date → participants
   - Transport: passenger name → email → passengers

2. **Confirm the full booking** with a summary:
   ```
   "Here's your complete booking summary:
   
   ✈️ Flight: Bangkok → Singapore | AirAsia | $85
   🏨 Hotel: The Singapore Suites | 2 nights | $240
   🎯 Activities: Gardens by the Bay Tour | $25
   
   Total: $350
   
   Shall I proceed with all bookings?"
   ```

3. **Book all items only after explicit "yes" confirmation**:
   - Call all book_* tools in sequence
   - If ANY booking fails → stop immediately
   - Inform user: "One of the items couldn't be booked. No bookings have been made. Let's find alternatives."
   - Do NOT show partial confirmation

4. **On all success**:
   - Display all booking confirmations with reference numbers
   - "All bookings confirmed! 🎉"

5. **On partial failure**:
   - "Sorry, [item] is no longer available. Please choose a different option."
   - Do NOT show any partial confirmations

---

## Acceptance Criteria

- [ ] Agent collects all booking details before making any bookings
- [ ] Agent shows full booking summary and asks for single confirmation
- [ ] If any item fails during booking, NO items are committed
- [ ] User is informed of the failure and asked to choose alternatives
- [ ] Successful booking shows all confirmations at once
- [ ] Booking reference numbers shown for all items

---

## Tests to verify

Run: `cd salebot && uv run pytest tests/ -v`

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: confirm full package → one item unavailable → no bookings made