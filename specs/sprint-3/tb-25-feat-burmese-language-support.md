---
ticket: TB-25
type: feat
title: Burmese Language Support — Ask Preference + Auto-Detect
sprint: sprint-3
status: todo
component: salebot
depends_on: TB-05, TB-09
---

# TB-25: Burmese Language Support

## Context
Read `rules/base.md` before starting.
Read `rules/bot.md` — agent and bot code must remain async.
Read `salebot/memory.py` — you will extend user state storage.
Read `salebot/agent.py` — you will add language-based prompt selection.
Read `salebot/bot.py` — you will add a language selection callback handler.
Read `salebot/prompts/system_prompt.md` — you will create a Burmese translation.

---

## Goal
Allow users to choose Burmese (ျမန္မာ) or English when starting a conversation.
The bot presents a language choice on first interaction. If the user skips or
the preference is not detected, fall back to auto-detecting the language from
their first message. Once set, all agent responses are in the selected language.

---

## Files to create / modify

| File | Action |
|------|--------|
| `salebot/prompts/system_prompt_my.md` | create — Burmese translation of system prompt |
| `salebot/memory.py` | modify — add language preference getter/setter |
| `salebot/bot.py` | modify — add language selection on first message + inline buttons |
| `salebot/agent.py` | modify — load correct prompt based on language preference |
| `salebot/tests/test_language.py` | create — language selection tests |
| `salebot/tests/conftest.py` | modify — add language fixtures if needed |

---

## What to build

### 1. Language Preference Store — `salebot/memory.py`

Add an in-memory dict for language preferences (separate from message history):

```python
_language_prefs: dict[int, str] = {}  # user_id → "en" | "my"

def set_language(user_id: int, lang: str) -> None:
    if lang not in ("en", "my"):
        raise ValueError("lang must be 'en' or 'my'")
    _language_prefs[user_id] = lang

def get_language(user_id: int) -> str | None:
    """Return 'en', 'my', or None if not yet set."""
    return _language_prefs.get(user_id)

def clear_language(user_id: int) -> None:
    _language_prefs.pop(user_id, None)
```

Update `clear_history` to also call `clear_language` so `/start` resets language.

---

### 2. Burmese System Prompt — `salebot/prompts/system_prompt_my.md`

Translate the full `system_prompt.md` into Burmese (Unicode).
Preserve all structural sections, rules, and booking flows exactly.
Only the natural-language instructions change — JSON field names, tool names,
and technical identifiers stay English.

Keep the section numbering identical (Section 1–9).

---

### 3. Language Selection Flow — `salebot/bot.py`

#### 3a. On `/start` command
Show the welcome message with two inline buttons:
- `English 🇬🇧`
- `ျမန္မာ 🇲🇲`

Use `telegram.InlineKeyboardButton` and `InlineKeyboardMarkup`.

#### 3b. On first message (no language set)
When `get_language(user_id)` returns `None`:
- Show language selection inline buttons (same as `/start`)
- Do NOT forward to agent yet
- Wait for callback

#### 3c. Callback handler
Add a `CallbackQueryHandler` that listens for `lang_en` and `lang_my` data:
- Call `set_language(user_id, lang)`
- Reply with confirmation in selected language
  - English: "Language set to English. How can I help you today?"
  - Burmese: "ဘာသာစကားကို ျမန္မာအျဖစ္ သတ္မွတ္ျပီးပါျပီ။ ဘယ္လိုကူညီႏုိင္မလဲ?"
- Then prompt user to send their travel query

#### 3d. Auto-detect fallback
If user sends a message before selecting a language (e.g. they dismiss buttons),
detect the language:
- If the text contains Burmese Unicode characters (U+1000–U+109F range),
  set language to `"my"`
- Otherwise set to `"en"`
- Then proceed with agent response in detected language

#### 3e. `/clear` command
Already calls `clear_history` — extend to also clear language preference.

---

### 4. Prompt Selection — `salebot/agent.py`

Modify `load_system_prompt` to accept an optional `lang` parameter:

```python
_prompt_cache: dict[str, str] = {}

def load_system_prompt(lang: str = "en") -> str:
    if lang not in _prompt_cache:
        filename = "system_prompt.md" if lang == "en" else "system_prompt_my.md"
        try:
            path = Path(__file__).parent / "prompts" / filename
            _prompt_cache[lang] = path.read_text(encoding="utf-8")
        except Exception:
            _prompt_cache[lang] = _FALLBACK_PROMPT
    return _prompt_cache[lang]
```

Modify `run_agent` to accept `lang` parameter and pass it to `load_system_prompt`:

```python
async def run_agent(user_id: int, user_message: str, history: list, lang: str = "en") -> str:
    ...
    system = load_system_prompt(lang)
    ...
```

---

### 5. Wire it together — `salebot/bot.py`

In `message_handler`:
1. Check `get_language(user_id)` — if `None`, show language buttons and return
2. If language is set, pass `lang` to `run_agent(user_id, user_message, history, lang=language)`

---

## File structure after TB-25

```
salebot/
├── prompts/
│   ├── system_prompt.md       ← unchanged
│   └── system_prompt_my.md    ← created (Burmese)
├── memory.py                  ← modified (language prefs)
├── agent.py                   ← modified (prompt selection)
├── bot.py                     ← modified (lang flow + auto-detect)
└── tests/
    └── test_language.py       ← created
```

---

## Tests to write first

### `salebot/tests/test_language.py`

```python
class TestLanguagePreference:

    def test_set_and_get_language(self):
        """TB-25: set_language stores preference, get_language returns it."""

    def test_set_invalid_language_raises(self):
        """TB-25: set_language rejects anything other than en/my."""

    def test_get_language_returns_none_when_not_set(self):
        """TB-25: get_language returns None for unknown user."""

    def test_clear_history_also_clears_language(self):
        """TB-25: clear_history resets language preference."""


class TestPromptSelection:

    def test_load_english_prompt(self):
        """TB-25: load_system_prompt('en') loads English prompt."""

    def test_load_burmese_prompt(self):
        """TB-25: load_system_prompt('my') loads Burmese prompt."""

    def test_caches_prompts(self):
        """TB-25: prompts are cached after first load."""

    def test_burmese_prompt_contains_burmese_text(self):
        """TB-25: Burmese prompt file contains actual Burmese characters."""


class TestAutoDetect:

    def test_burmese_text_detected(self):
        """TB-25: text with Burmese Unicode chars triggers my detection."""

    def test_english_text_detected(self):
        """TB-25: ASCII-only text triggers en detection."""

    def test_mixed_text_defaults_to_burmese(self):
        """TB-25: text containing any Burmese chars detected as my."""


class TestBotLanguageFlow:

    def test_first_message_shows_language_buttons(self, bot_mock):
        """TB-25: first message without language shows selection buttons."""

    def test_callback_sets_language(self, bot_mock):
        """TB-25: pressing English button sets language to en."""

    def test_burmese_callback_sets_language(self, bot_mock):
        """TB-25: pressing Burmese button sets language to my."""

    def test_subsequent_messages_skip_selection(self, bot_mock):
        """TB-25: after language is set, messages go to agent directly."""

    def test_auto_detect_burmese_on_message(self, bot_mock):
        """TB-25: Burmese text auto-detected and set before agent call."""
```

---

## Acceptance Criteria

### Memory
- [ ] `set_language(user_id, lang)` stores preference
- [ ] `get_language(user_id)` returns `"en"`, `"my"`, or `None`
- [ ] `clear_language(user_id)` removes preference
- [ ] `clear_history` also clears language preference
- [ ] Invalid `lang` value raises `ValueError`

### Burmese Prompt
- [ ] `system_prompt_my.md` exists and is valid Burmese Unicode
- [ ] All 9 sections are present and structurally identical to English
- [ ] Tool names and JSON fields remain in English
- [ ] Natural-language instructions are translated to Burmese

### Agent
- [ ] `load_system_prompt(lang="en")` returns English prompt
- [ ] `load_system_prompt(lang="my")` returns Burmese prompt
- [ ] Prompts are cached per language
- [ ] `run_agent` accepts `lang` parameter and passes to prompt loader

### Bot
- [ ] `/start` shows language selection with inline buttons
- [ ] First message without language shows selection buttons
- [ ] Pressing English button sets language and confirms in English
- [ ] Pressing Burmese button sets language and confirms in Burmese
- [ ] Messages after language is set go directly to agent
- [ ] Burmese Unicode text auto-detects to `"my"`
- [ ] ASCII-only text auto-detects to `"en"`
- [ ] `/clear` resets language preference
- [ ] Agent responds in correct language after selection

### Tests
- [ ] All tests in `test_language.py` pass
- [ ] `uv run pytest tests/ -v` passes with no regressions
- [ ] `uv run ruff check .` passes with no errors

---

## Definition of Done
- [ ] All acceptance criteria checked off
- [ ] All tests pass: `cd salebot && uv run pytest tests/ -v`
- [ ] Lint clean: `cd salebot && uv run ruff check .`
- [ ] Manual Telegram flow tested end-to-end:
  - English path: select English, ask about Singapore
  - Burmese path: select Burmese, ask about Singapore (in Burmese)
  - Auto-detect path: type Burmese without selecting language
  - /clear resets language, shows selection again
