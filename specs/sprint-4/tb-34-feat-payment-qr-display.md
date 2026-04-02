---
ticket: TB-34
type: feat
title: Payment Bot Flow - QR Display
sprint: sprint-4
status: done
component: salebot
depends_on: TB-33
---

# TB-34: Payment Bot Flow - QR Display

> **Filename:** `tb-34-feat-payment-qr-display.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: TB-33 (Payment Backend)
- Sprint: sprint-4
- Component: salebot

## Goal
After user confirms a tour package, display a QR code for payment and ask user to confirm when they've paid.

## Files to create / modify
- `salebot/mcp_tools.py` ← modify (add payment tool)
- `salebot/prompts/system_prompt.md` ← modify (add payment handling instructions)

## What to build

### 1. Payment Tool Schema
Modify `salebot/mcp_tools.py`:
- Add `initiate_payment` tool:
  - Input: `amount` (float)
  - Calls: `POST /payments`
  - Returns: booking_reference, amount, status

### 2. Payment Flow in Agent
After package is confirmed by user:
1. Agent calls `initiate_payment` with total package price
2. Agent displays static QR code image to user
3. Agent asks user to send a screenshot of their payment ("Please send a screenshot of your payment confirmation")

### 3. QR Code Display
- Use a static placeholder QR code image (e.g., generic payment QR)
- Display inline in Telegram using photo message
- Include instruction: "Scan this QR to pay, then send me a screenshot of your payment confirmation"

### 4. System Prompt Update
Update system prompt to:
- Recognize payment confirmation intents ("I've paid", "paid", "payment done")
- Guide user through payment flow

## Acceptance Criteria
- [ ] initiate_payment tool works and calls backend API
- [ ] After package confirmation, QR code is shown
- [ ] User is prompted to send payment screenshot
- [ ] System prompt handles payment-related messages

## Test file
`salebot/tests/test_payment_flow.py`

## Manual test
```python
# Test payment tool directly
from salebot.mcp_tools import get_tools
tools = get_tools()
# Find initiate_payment tool and call it
```

## Definition of Done
- [ ] Test file exists at correct path
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] Linted: `uv run ruff check .`
- [ ] All acceptance criteria checked
