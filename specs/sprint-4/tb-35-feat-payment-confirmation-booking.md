---
ticket: TB-35
type: feat
title: Payment Bot Flow - Confirmation & Booking Creation
sprint: sprint-4
status: done
component: salebot
depends_on: TB-34
---

# TB-35: Payment Bot Flow - Confirmation & Booking Creation

> **Filename:** `tb-35-feat-payment-confirmation-booking.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-34 (Payment Bot Flow - QR Display)
- Sprint: sprint-4
- Component: salebot

## Goal
Handle user's payment screenshot and create actual bookings only after payment is verified.

## Files to create / modify
- `salebot/mcp_tools.py` ← modify (add payment verification tool)
- `salebot/agent.py` ← modify (integrate payment flow with booking creation)
- `salebot/prompts/system_prompt.md` ← modify (update instructions)

## What to build

### 1. Payment Verification Tool
Modify `salebot/mcp_tools.py`:
- Add `confirm_payment` tool:
  - Input: `booking_reference` (str)
  - Calls: `PUT /payments/{booking_reference}/confirm`
  - Returns: status, paid_at
- Add `check_payment_status` tool:
  - Input: `booking_reference` (str)
  - Calls: `GET /payments/{booking_reference}`
  - Returns: status, amount, paid_at

### 2. Booking Creation After Payment
Modify `salebot/agent.py`:
- When user sends a payment screenshot:
  1. Agent acknowledges receipt of screenshot
  2. Agent calls `confirm_payment` with the booking_reference (simulated verification)
  3. On success, create all bookings (flight, hotel, activities, transport)
  4. Send confirmation message with booking references
- Store package selection in memory until payment screenshot received

### 3. Flow Diagram
```
User confirms package
        ↓
Agent calls initiate_payment → gets booking_reference
        ↓
Display QR code + "Send payment screenshot"
        ↓
User sends screenshot
        ↓
Agent calls confirm_payment
        ↓
On success → create all bookings
        ↓
Send confirmation with booking refs
```

### 4. System Prompt Update
Update system prompt to:
- Only create bookings after payment confirmed
- Handle payment failure scenarios
- Provide booking confirmation with references

## Acceptance Criteria
- [ ] confirm_payment tool works
- [ ] Bookings are created only after user sends payment screenshot
- [ ] User receives booking confirmation with references
- [ ] Payment failure is handled gracefully

## Test file
`salebot/tests/test_payment_booking_flow.py`

## Manual test
```python
# Full flow test:
# 1. Confirm package
# 2. Initiate payment
# 3. Confirm payment
# 4. Verify bookings created
```

## Definition of Done
- [ ] Test file exists at correct path
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Linted: `uv run ruff check .`
- [ ] All acceptance criteria checked
