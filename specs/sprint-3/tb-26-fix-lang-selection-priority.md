---
ticket: TB-26
type: fix
title: Language Selection as First Priority on Bot Start
sprint: sprint-3
status: todo
component: salebot
depends_on: TB-25
---

# TB-26: Language Selection as First Priority on Bot Start

## Context

Currently when a user first messages the bot, the language is auto-detected from their message text and the agent responds immediately. This bypasses the language selection UI.

The expected flow should be:
1. User opens bot → sees language selection (English / Burmese) immediately
2. User picks language → confirmation shown → THEN they can chat

The auto-detect fallback should only trigger if the user somehow sends a message without selecting a language (e.g. dismisses the buttons).

Read `rules/base.md` and `rules/bot.md` before starting.

---

## Problem

In `salebot/bot.py` `message_handler` (lines 137-177):

```python
lang = get_language(user_id)
if lang is None:
    detected = _detect_language(user_message)
    set_language(user_id, detected)
    lang = detected
    logger.info(f"User {user_id} auto-detected language: {lang}")
```

This auto-detects and immediately proceeds to the agent on first message. It should instead show language selection buttons and wait for the callback.

---

## Files to modify

| File | Change |
|------|--------|
| `salebot/bot.py` | `message_handler` — when `lang is None`, show language buttons instead of auto-detecting |

---

## What to build

### Fix `message_handler` in `salebot/bot.py`

When `get_language(user_id)` returns `None`:
1. Send language selection inline buttons (same as `/start`)
2. Return early — do NOT call `run_agent`
3. Auto-detect is now only a fallback for edge cases

**Current behavior (wrong):**
```
User: "Hello"
→ auto-detect lang → run agent → response
```

**Expected behavior:**
```
User: "Hello"
→ show language selection → wait for button press
User clicks English
→ set language → confirmation → then proceed
```

### Auto-detect fallback (only if needed)

If user somehow sends a message before selecting a language (edge case), you MAY auto-detect and proceed. But the primary path is explicit selection via buttons.

### Welcome message after language selection

After user selects a language via button callback, send the welcome message in the selected language before the ready prompt:

```python
if data == "lang_en":
    set_language(user_id, "en")
    await query.edit_message_text(EN_CONFIRM, parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=WELCOME,  # ← welcome message in English
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.info(f"User {user_id} set language to English")
elif data == "lang_my":
    set_language(user_id, "my")
    await query.edit_message_text(MY_CONFIRM, parse_mode=ParseMode.MARKDOWN_V2)
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=WELCOME_MY,  # ← welcome message in Burmese
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.info(f"User {user_id} set language to Burmese")
```

Add `WELCOME_MY` constant for the Burmese welcome message translation.

---

## Acceptance Criteria

- [ ] First message without language set shows language selection buttons
- [ ] Agent is NOT called until language is selected
- [ ] After language selection, welcome message is sent in selected language
- [ ] After language selection, subsequent messages go directly to agent
- [ ] Auto-detect fallback still works for edge cases (e.g. user types in Burmese before selecting)
- [ ] `/start` still shows language selection followed by welcome message

---

## Tests to verify

Run: `cd salebot && uv run pytest tests/ -v`

---

## Definition of Done

- [ ] All acceptance criteria checked off
- [ ] `uv run pytest tests/ -v` passes
- [ ] `uv run ruff check .` passes
- [ ] Manual test: send first message → see language buttons → select English → bot responds