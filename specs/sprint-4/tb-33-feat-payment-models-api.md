---
ticket: TB-33
type: feat
title: Payment Backend - Models & API
sprint: sprint-4
status: todo
component: server
depends_on: none
---

# TB-33: Payment Backend - Models & API

> **Filename:** `tb-33-feat-payment-models-api.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: none
- Sprint: sprint-4
- Component: server

## Goal
Add backend support for payment tracking. Payment is initiated after user confirms a package, and bookings are only created after payment is confirmed.

## Files to create / modify
- `server/models/payment.py` ← create
- `server/routers/payments.py` ← create
- `server/main.py` ← modify (register router)

## What to build

### 1. Payment Model
Create `server/models/payment.py`:
- `Payment` SQLModel table:
  - `id`: Primary key
  - `booking_reference`: str (links to booking ref that will be created)
  - `amount`: float
  - `status`: str = "pending" (pending → paid)
  - `payment_method`: str = "qr"
  - `created_at`: datetime
  - `paid_at`: datetime | None
- `PaymentCreate` schema for creating payment intent

### 2. Payment Router
Create `server/routers/payments.py`:
- `POST /payments` - Create payment intent (amount, returns booking_reference)
- `GET /payments/{booking_reference}` - Get payment status
- `PUT /payments/{booking_reference}/confirm` - Mark as paid (called after user confirms payment)

### 3. Register Router
Modify `server/main.py` to include the payments router.

## Acceptance Criteria
- [ ] Payment model exists with correct fields
- [ ] POST /payments creates a pending payment
- [ ] GET /payments/{ref} returns payment status
- [ ] PUT /payments/{ref}/confirm marks payment as paid

## Test file
`server/tests/test_payments.py`

## Manual test
```bash
# Test create payment
curl -X POST http://localhost:8000/payments \
  -H "Content-Type: application/json" \
  -d '{"amount": 1500.00}'

# Test get payment
curl http://localhost:8000/payments/TB-20250402-ABCD

# Test confirm payment
curl -X PUT http://localhost:8000/payments/TB-20250402-ABCD/confirm
```

## Definition of Done
- [ ] Test file exists at correct path
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Linted: `uv run ruff check .`
- [ ] All acceptance criteria checked
