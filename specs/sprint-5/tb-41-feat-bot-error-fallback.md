---
ticket: TB-41
type: feat
title: Bot Error Fallback with Operator Contact
sprint: sprint-5
status: done
component: salebot
depends_on: none
---

# TB-41: Bot Error Fallback with Operator Contact

> **Filename:** `tb-41-feat-bot-error-fallback.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: none
- Sprint: sprint-5
- Component: salebot

## Goal
When the bot encounters an error it cannot resolve (API failures, booking conflicts, payment issues), it should gracefully provide operator contact information so the user can get human help.

## Files to create / modify
- `salebot/prompts/system_prompt.md` ← modify (add error fallback instructions)
- `salebot/mcp_tools.py` ← modify (add operator_contact tool)

## What to build

### 1. Operator Contact Tool
Add a tool in `mcp_tools.py`:
- `get_operator_contact` - Returns operator phone, email, Telegram

### 2. Error Handling Flow
When the bot hits an unrecoverable error:
1. Catch the error
2. Provide a helpful message acknowledging the issue
3. Offer to connect them with a human operator
4. Show operator contact details

### 3. System Prompt Update
Update `salebot/prompts/system_prompt.md`:
- Add section on error fallback behavior
- Include operator contact details to share with users
- Define conditions for escalating to human (API down, repeated failures, etc.)

### 4. Specific Error Scenarios
- API/connectivity errors → Suggest trying again, offer operator
- Booking conflicts → Offer operator to resolve manually
- Payment failures → Provide operator contact for manual payment
- Repeated failed attempts → Automatically suggest operator

## Acceptance Criteria
- [x] Bot provides operator contact on unrecoverable errors
- [x] Error messages are user-friendly (not technical)
- [x] Escalation logic works for API failures
- [x] Escalation logic works for booking failures

## Definition of Done
- [x] Error fallback implemented in agent loop
- [x] get_operator_contact tool added
- [x] System prompt updated with escalation instructions
- [x] Tests pass: `uv run pytest tests/ -v`
- [x] Linted: `uv run ruff check .`
- [x] All acceptance criteria checked