---
ticket: TB-44
type: feat
title: Persistent Memory for Bot
sprint: sprint-5
status: done
component: salebot
depends_on: none
---

# TB-44: Persistent Memory for Bot

> **Filename:** `tb-44-feat-persistent-memory.md`
> **Types:** `feat` new feature · `fix` bug fix · `chore` cleanup/refactor · `test` test coverage

## Context
- Depends on: none
- Sprint: sprint-5
- Component: salebot

## Goal
The bot currently stores conversation history, language preferences, and pending payments in an in-memory Python dict. This means all data is lost on bot restart. Persist this data to disk (JSON or SQLite).

## Files to create / modify
- `salebot/memory.py` ← modify (add file-based persistence)
- `salebot/.env` ← modify (if needed for path config)

## What to build

### Current In-Memory State
The `memory.py` module stores:
- `_store`: dict[int, list[dict]] — conversation history per user
- `_language_prefs`: dict[int, str] — language preference per user
- `_pending_payment`: dict[int, dict] — pending payment info per user

### Persistence Strategy
Use JSON files in the `salebot/data/` directory:
- `conversations.json` — stores all user conversation histories
- `preferences.json` — stores language prefs and pending payments

Load from JSON on startup, write to JSON on every mutation (append/clear/set).

### Implementation Details

#### 1. Load on startup
On module import, load existing data from JSON files if they exist.

#### 2. Save on every mutation
After any change (append_message, clear_history, set_language, set_pending_payment, etc.), write the full state back to JSON.

#### 3. File structure
```
salebot/data/
  ├── conversations.json  # {"12345": [{"role": "user", "content": "..."}], ...}
  └── preferences.json   # {"lang": {"12345": "en"}, "pending_payment": {"12345": {"booking_reference": "PAY-XXX"}}}
```

### Backward Compatibility
- Functions should have the same signatures
- Same return types
- Existing tests should pass unchanged

## Acceptance Criteria
- [x] Bot restart does not lose conversation history
- [x] Bot restart does not lose language preferences
- [x] Bot restart does not lose pending payments
- [x] Data is persisted immediately after any change
- [x] Existing tests pass

## Definition of Done
- [x] memory.py updated with file-based persistence
- [x] Bot works across restarts
- [x] Tests pass: `uv run pytest tests/ -v` (297/297)
- [x] All acceptance criteria checked