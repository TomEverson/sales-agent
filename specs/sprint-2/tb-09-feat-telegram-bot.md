# TB-09: Telegram Bot — Entry Point

## Context
Read rules/base.md before starting.
Read rules/bot.md to understand the full bot architecture.
Read salebot/agent.py from TB-05 — bot.py calls run_agent().
Read salebot/memory.py from TB-06 — bot.py calls get_history(),
append_message(), append_tool_messages(), and clear_history().

## Dependency
TB-05, TB-06, TB-07, and TB-08 must be complete before starting this story.
All of the following must exist and be working:
- salebot/agent.py with run_agent()
- salebot/memory.py with all 5 memory functions
- salebot/package_builder.py with all dataclasses and formatters
- salebot/prompts/system_prompt.md with full content

---

## Goal
Create bot.py — the Telegram entry point that wires everything together.
It receives messages from Telegram users, passes them through the agent,
stores conversation history, and sends responses back.

---

## File to create
salebot/bot.py

---

## What to build

### 1. Environment Loading
At module top:
```python
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
```

- If TELEGRAM_BOT_TOKEN is None → raise RuntimeError:
  "TELEGRAM_BOT_TOKEN is not set in .env"
- If ANTHROPIC_API_KEY is None → raise RuntimeError:
  "ANTHROPIC_API_KEY is not set in .env"
- Validation happens at startup, not at message time

### 2. /start Handler
Create an async function: start_handler(update, context) -> None

Sends this exact message when user sends /start:
```
👋 Welcome to *Travelbase Assistant*!

I can build a personalised tour package for you — flights, hotels, activities, and transport — all within your budget.

Just tell me something like:
_"I want to visit Singapore this weekend, my budget is $1000"_

Or ask me anything about travelling in Southeast Asia.

Type /clear to start a fresh conversation.
```

- Use Telegram ParseMode.MARKDOWN_V2
- Do not store /start in conversation history

### 3. /clear Handler
Create an async function: clear_handler(update, context) -> None

- Call clear_history(user_id) from memory.py
- Send this exact message:
  "🗑 Conversation cleared. Let's start fresh — where would you like to go?"
- Do not store /clear in conversation history

### 4. Message Handler
Create an async function: message_handler(update, context) -> None

This is the core handler — called for every non-command text message.

#### Step-by-step flow:
1. Extract user_id from update.effective_user.id
2. Extract user_message from update.message.text
3. Send typing action: await context.bot.send_chat_action(
     chat_id=update.effective_chat.id,
     action=ChatAction.TYPING
   )
4. Load history: history = get_history(user_id)
5. Call agent: response = await run_agent(user_id, user_message, history)
6. Store user message: append_message(user_id, "user", user_message)
7. Store assistant response: append_message(user_id, "assistant", response)
8. Send response to Telegram with ParseMode.MARKDOWN_V2
9. If any exception occurs → send fallback message:
   "Sorry, something went wrong. Please try again in a moment."

#### Markdown safety:
Telegram MarkdownV2 requires escaping special characters.
Create a helper function: escape_markdown(text: str) -> str
that escapes these characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
by prefixing each with a backslash.

Apply escape_markdown to the agent response before sending.

### 5. Error Handler
Create an async function: error_handler(update, context) -> None

- Log the error: logger.error(f"Update {update} caused error {context.error}")
- If update and update.effective_message exist → send to user:
  "An unexpected error occurred. Please try again."
- Never let an unhandled error crash the bot process

### 6. Bot Startup
Create the main function: main() -> None
```python
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("clear", clear_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    app.add_error_handler(error_handler)

    logger.info("Travelbase bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
```

### 7. Logging Setup
At module top, configure logging:
```python
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)
```

Log these events:
- Bot startup: "Travelbase bot is running..."
- Each incoming message: "Message from user {user_id}: {user_message[:50]}"
- Each agent response: "Response to user {user_id}: {response[:50]}"
- Each /clear: "History cleared for user {user_id}"
- Each error: "Update {update} caused error {context.error}"

---

## File structure after TB-09
```
salebot/
├── bot.py                      ← created in this story
├── agent.py                    ← unchanged
├── memory.py                   ← unchanged
├── mcp_tools.py                ← unchanged
├── package_builder.py          ← unchanged
├── prompts/
│   └── system_prompt.md        ← unchanged
├── .env                        ← must exist with both tokens
└── tests/
    ├── __init__.py
    ├── conftest.py             ← add bot fixtures
    └── test_bot.py             ← created in this story
```

---

## Tests to write first
Create salebot/tests/test_bot.py:
```python
class TestEnvironmentValidation:

    def test_raises_if_telegram_token_missing(self, monkeypatch):
        """TB-09: RuntimeError raised if TELEGRAM_BOT_TOKEN not set per spec"""

    def test_raises_if_anthropic_key_missing(self, monkeypatch):
        """TB-09: RuntimeError raised if ANTHROPIC_API_KEY not set per spec"""

    def test_telegram_error_message_exact(self, monkeypatch):
        """TB-09: RuntimeError message matches spec exactly for missing token"""

    def test_anthropic_error_message_exact(self, monkeypatch):
        """TB-09: RuntimeError message matches spec exactly for missing key"""


class TestEscapeMarkdown:

    def test_escapes_underscore(self):
        """TB-09: underscore is escaped with backslash per spec"""

    def test_escapes_asterisk(self):
        """TB-09: asterisk is escaped with backslash per spec"""

    def test_escapes_period(self):
        """TB-09: period is escaped with backslash per spec"""

    def test_escapes_hyphen(self):
        """TB-09: hyphen is escaped with backslash per spec"""

    def test_escapes_all_special_chars(self):
        """TB-09: all 19 special chars are escaped per spec"""

    def test_plain_text_unchanged(self):
        """TB-09: text with no special chars is returned unchanged per spec"""

    def test_empty_string_unchanged(self):
        """TB-09: empty string returns empty string per spec"""


class TestStartHandler:

    async def test_sends_welcome_message(self, mocker):
        """TB-09: /start sends welcome message to user per spec"""

    async def test_welcome_contains_travelbase(self, mocker):
        """TB-09: welcome message contains Travelbase name per spec"""

    async def test_welcome_contains_clear_instruction(self, mocker):
        """TB-09: welcome message mentions /clear command per spec"""

    async def test_start_not_stored_in_history(self, mocker):
        """TB-09: /start command is not added to conversation history per spec"""


class TestClearHandler:

    async def test_calls_clear_history(self, mocker):
        """TB-09: /clear calls clear_history with correct user_id per spec"""

    async def test_sends_confirmation_message(self, mocker):
        """TB-09: /clear sends confirmation message to user per spec"""

    async def test_clear_not_stored_in_history(self, mocker):
        """TB-09: /clear command is not added to conversation history per spec"""


class TestMessageHandler:

    async def test_sends_typing_action(self, mocker):
        """TB-09: typing action sent before calling agent per spec"""

    async def test_calls_run_agent_with_correct_args(self, mocker):
        """TB-09: run_agent called with user_id, message, and history per spec"""

    async def test_loads_history_before_agent_call(self, mocker):
        """TB-09: get_history called before run_agent per spec"""

    async def test_stores_user_message_after_agent(self, mocker):
        """TB-09: append_message called with user role after agent responds per spec"""

    async def test_stores_assistant_response_after_agent(self, mocker):
        """TB-09: append_message called with assistant role after agent responds per spec"""

    async def test_sends_agent_response_to_telegram(self, mocker):
        """TB-09: agent response is sent back to Telegram user per spec"""

    async def test_sends_fallback_on_exception(self, mocker):
        """TB-09: fallback message sent if any exception occurs per spec"""

    async def test_fallback_message_exact(self, mocker):
        """TB-09: fallback message matches spec exactly"""

    async def test_response_is_escaped_before_sending(self, mocker):
        """TB-09: escape_markdown applied to agent response before sending per spec"""


class TestErrorHandler:

    async def test_logs_error(self, mocker):
        """TB-09: error is logged with update and error info per spec"""

    async def test_sends_message_to_user_when_update_exists(self, mocker):
        """TB-09: error message sent to user when update is available per spec"""

    async def test_does_not_crash_when_update_is_none(self, mocker):
        """TB-09: error handler does not raise when update is None per spec"""
```

Add to conftest.py:
```python
@pytest.fixture
def mock_update():
    """TB-09: mock Telegram Update object for handler tests"""
    from unittest.mock import MagicMock, AsyncMock
    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    update.message.text = "I want to visit Singapore, budget $1000"
    update.message.reply_text = AsyncMock()
    return update

@pytest.fixture
def mock_context():
    """TB-09: mock Telegram CallbackContext for handler tests"""
    from unittest.mock import MagicMock, AsyncMock
    context = MagicMock()
    context.bot.send_chat_action = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.error = Exception("test error")
    return context

@pytest.fixture
def mock_env(monkeypatch):
    """TB-09: set required environment variables for bot tests"""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key_456")
```

---

## Acceptance Criteria

- [ ] bot.py is created with no import errors
- [ ] TELEGRAM_BOT_TOKEN loaded from .env
- [ ] ANTHROPIC_API_KEY loaded from .env
- [ ] RuntimeError raised at startup if TELEGRAM_BOT_TOKEN is None
- [ ] RuntimeError raised at startup if ANTHROPIC_API_KEY is None
- [ ] RuntimeError messages match spec exactly
- [ ] escape_markdown(text) exists with exact signature
- [ ] escape_markdown escapes all 19 special MarkdownV2 characters
- [ ] escape_markdown returns plain text unchanged
- [ ] start_handler sends welcome message with Travelbase name
- [ ] start_handler welcome message mentions /clear
- [ ] /start not stored in conversation history
- [ ] clear_handler calls clear_history(user_id) from memory.py
- [ ] clear_handler sends confirmation message
- [ ] /clear not stored in conversation history
- [ ] message_handler sends typing action before calling agent
- [ ] message_handler calls get_history before run_agent
- [ ] message_handler calls run_agent with user_id, user_message, history
- [ ] message_handler calls append_message for user message after response
- [ ] message_handler calls append_message for assistant response after response
- [ ] message_handler applies escape_markdown before sending response
- [ ] message_handler sends fallback message on any exception
- [ ] Fallback message matches spec exactly
- [ ] error_handler logs error with update and error details
- [ ] error_handler sends message to user when update is available
- [ ] error_handler does not crash when update is None
- [ ] Logging configured with correct format at module level
- [ ] All 5 log events are present in correct handlers
- [ ] main() registers all 3 handlers and error handler
- [ ] Bot starts with: uv run python bot.py
- [ ] All tests in test_bot.py pass
- [ ] All previously passing TB-01 through TB-08 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, do a smoke test:

1. Create .env with real tokens:
```
TELEGRAM_BOT_TOKEN=your_real_token
ANTHROPIC_API_KEY=your_real_key
```

2. Make sure FastAPI server is running:
```bash
cd server && uv run uvicorn main:app --reload
```

3. Start the bot:
```bash
cd salebot && uv run python bot.py
```

4. Open Telegram and test these in order:
```
/start
→ expect: welcome message with Travelbase name and /clear instruction

I want to visit Singapore this weekend, my budget is $1000
→ expect: typing indicator, then a full tour package with flight + hotel + activities

Can you find me a nicer hotel?
→ expect: updated package with higher star hotel, same flight and activities

/clear
→ expect: confirmation message

I want to visit Bali for 3 days, budget $800
→ expect: fresh package with no memory of Singapore conversation
```

Expected:
- /start: welcome message renders correctly
- First message: full package within $1000 using real inventory
- Follow-up: refined package with upgraded hotel
- /clear: confirmation, history wiped
- Fresh message: new package for Bali with no Singapore context leaking

---

## When done
Print: ✅ TB-09 complete
Do not proceed to TB-10 until all acceptance criteria above are checked.
