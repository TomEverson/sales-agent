"""Tests for salebot/bot.py — FR-9: Telegram Bot Entry Point."""

import sys
import os

import pytest
from unittest.mock import AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bot
from bot import escape_markdown


# ---------------------------------------------------------------------------
# TestEnvironmentValidation
# ---------------------------------------------------------------------------


class TestEnvironmentValidation:
    def test_raises_if_telegram_token_missing(self, monkeypatch):
        """FR-9: RuntimeError raised if TELEGRAM_BOT_TOKEN not set per spec."""
        monkeypatch.setattr(bot, "TELEGRAM_BOT_TOKEN", None)
        monkeypatch.setattr(bot, "ANTHROPIC_API_KEY", "key")
        with pytest.raises(RuntimeError):
            bot._validate_env()

    def test_raises_if_anthropic_key_missing(self, monkeypatch):
        """FR-9: RuntimeError raised if ANTHROPIC_API_KEY not set per spec."""
        monkeypatch.setattr(bot, "TELEGRAM_BOT_TOKEN", "token")
        monkeypatch.setattr(bot, "ANTHROPIC_API_KEY", None)
        with pytest.raises(RuntimeError):
            bot._validate_env()

    def test_telegram_error_message_exact(self, monkeypatch):
        """FR-9: RuntimeError message matches spec exactly for missing token."""
        monkeypatch.setattr(bot, "TELEGRAM_BOT_TOKEN", None)
        monkeypatch.setattr(bot, "ANTHROPIC_API_KEY", "key")
        with pytest.raises(RuntimeError, match="TELEGRAM_BOT_TOKEN is not set in .env"):
            bot._validate_env()

    def test_anthropic_error_message_exact(self, monkeypatch):
        """FR-9: RuntimeError message matches spec exactly for missing key."""
        monkeypatch.setattr(bot, "TELEGRAM_BOT_TOKEN", "token")
        monkeypatch.setattr(bot, "ANTHROPIC_API_KEY", None)
        with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY is not set in .env"):
            bot._validate_env()


# ---------------------------------------------------------------------------
# TestEscapeMarkdown
# ---------------------------------------------------------------------------


class TestEscapeMarkdown:
    def test_escapes_underscore(self):
        """FR-9: underscore is escaped with backslash per spec."""
        assert escape_markdown("hello_world") == "hello\\_world"

    def test_escapes_asterisk(self):
        """FR-9: asterisk is escaped with backslash per spec."""
        assert escape_markdown("hello*world") == "hello\\*world"

    def test_escapes_period(self):
        """FR-9: period is escaped with backslash per spec."""
        assert escape_markdown("hello.world") == "hello\\.world"

    def test_escapes_hyphen(self):
        """FR-9: hyphen is escaped with backslash per spec."""
        assert escape_markdown("hello-world") == "hello\\-world"

    def test_escapes_all_special_chars(self):
        """FR-9: all 19 special chars are escaped per spec."""
        special = "\\_*[]()~`>#+-=|{}.!"
        result = escape_markdown(special)
        for ch in special:
            assert f"\\{ch}" in result

    def test_plain_text_unchanged(self):
        """FR-9: text with no special chars is returned unchanged per spec."""
        text = "Hello world this is plain text 123"
        assert escape_markdown(text) == text

    def test_empty_string_unchanged(self):
        """FR-9: empty string returns empty string per spec."""
        assert escape_markdown("") == ""


# ---------------------------------------------------------------------------
# TestStartHandler
# ---------------------------------------------------------------------------


class TestStartHandler:
    @pytest.mark.asyncio
    async def test_sends_welcome_message(self, mock_update, mock_context):
        """FR-9: /start sends welcome message to user per spec."""
        await bot.start_handler(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_welcome_contains_travelbase(self, mock_update, mock_context):
        """FR-9: welcome message contains Travelbase name per spec."""
        await bot.start_handler(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "Travelbase" in call_args

    @pytest.mark.asyncio
    async def test_welcome_contains_clear_instruction(self, mock_update, mock_context):
        """FR-9: welcome message mentions /clear command per spec."""
        await bot.start_handler(mock_update, mock_context)
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert "/clear" in call_args

    @pytest.mark.asyncio
    async def test_start_not_stored_in_history(self, mock_update, mock_context, mocker):
        """FR-9: /start command is not added to conversation history per spec."""
        mock_append = mocker.patch("bot.append_message")
        await bot.start_handler(mock_update, mock_context)
        mock_append.assert_not_called()


# ---------------------------------------------------------------------------
# TestClearHandler
# ---------------------------------------------------------------------------


class TestClearHandler:
    @pytest.mark.asyncio
    async def test_calls_clear_history(self, mock_update, mock_context, mocker):
        """FR-9: /clear calls clear_history with correct user_id per spec."""
        mock_clear = mocker.patch("bot.clear_history")
        await bot.clear_handler(mock_update, mock_context)
        mock_clear.assert_called_once_with(mock_update.effective_user.id)

    @pytest.mark.asyncio
    async def test_sends_confirmation_message(self, mock_update, mock_context, mocker):
        """FR-9: /clear sends confirmation message to user per spec."""
        mocker.patch("bot.clear_history")
        await bot.clear_handler(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()
        msg = mock_update.message.reply_text.call_args[0][0]
        assert "cleared" in msg.lower() or "fresh" in msg.lower()

    @pytest.mark.asyncio
    async def test_clear_not_stored_in_history(self, mock_update, mock_context, mocker):
        """FR-9: /clear command is not added to conversation history per spec."""
        mocker.patch("bot.clear_history")
        mock_append = mocker.patch("bot.append_message")
        await bot.clear_handler(mock_update, mock_context)
        mock_append.assert_not_called()


# ---------------------------------------------------------------------------
# TestMessageHandler
# ---------------------------------------------------------------------------


class TestMessageHandler:
    @pytest.mark.asyncio
    async def test_sends_typing_action(self, mock_update, mock_context, mocker):
        """FR-9: typing action sent before calling agent per spec."""
        mocker.patch("bot.get_history", return_value=[])
        mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value="Response!")
        mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        mock_context.bot.send_chat_action.assert_called_once()

    @pytest.mark.asyncio
    async def test_calls_run_agent_with_correct_args(self, mock_update, mock_context, mocker):
        """FR-9: run_agent called with user_id, message, and history per spec."""
        history = [{"role": "user", "content": "prev"}]
        mocker.patch("bot.get_history", return_value=history)
        mock_agent = mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value="OK")
        mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        mock_agent.assert_called_once_with(
            mock_update.effective_user.id,
            mock_update.message.text,
            history,
        )

    @pytest.mark.asyncio
    async def test_loads_history_before_agent_call(self, mock_update, mock_context, mocker):
        """FR-9: get_history called before run_agent per spec."""
        call_order = []
        mocker.patch("bot.get_history", side_effect=lambda uid: call_order.append("get_history") or [])
        mocker.patch(
            "bot.run_agent",
            new_callable=AsyncMock,
            side_effect=lambda *a, **k: call_order.append("run_agent") or "OK",
        )
        mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        assert call_order.index("get_history") < call_order.index("run_agent")

    @pytest.mark.asyncio
    async def test_stores_user_message_after_agent(self, mock_update, mock_context, mocker):
        """FR-9: append_message called with user role after agent responds per spec."""
        mocker.patch("bot.get_history", return_value=[])
        mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value="Response!")
        mock_append = mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        calls = [c.args for c in mock_append.call_args_list]
        assert any(c[1] == "user" for c in calls)

    @pytest.mark.asyncio
    async def test_stores_assistant_response_after_agent(self, mock_update, mock_context, mocker):
        """FR-9: append_message called with assistant role after agent responds per spec."""
        mocker.patch("bot.get_history", return_value=[])
        mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value="Response!")
        mock_append = mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        calls = [c.args for c in mock_append.call_args_list]
        assert any(c[1] == "assistant" for c in calls)

    @pytest.mark.asyncio
    async def test_sends_agent_response_to_telegram(self, mock_update, mock_context, mocker):
        """FR-9: agent response is sent back to Telegram user per spec."""
        mocker.patch("bot.get_history", return_value=[])
        mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value="Here is your package!")
        mocker.patch("bot.append_message")
        await bot.message_handler(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_sends_fallback_on_exception(self, mock_update, mock_context, mocker):
        """FR-9: fallback message sent if any exception occurs per spec."""
        mocker.patch("bot.get_history", side_effect=Exception("unexpected error"))
        await bot.message_handler(mock_update, mock_context)
        mock_update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_fallback_message_exact(self, mock_update, mock_context, mocker):
        """FR-9: fallback message matches spec exactly."""
        mocker.patch("bot.get_history", side_effect=Exception("unexpected error"))
        await bot.message_handler(mock_update, mock_context)
        msg = mock_update.message.reply_text.call_args[0][0]
        assert msg == "Sorry, something went wrong. Please try again in a moment."

    @pytest.mark.asyncio
    async def test_response_is_escaped_before_sending(self, mock_update, mock_context, mocker):
        """FR-9: escape_markdown applied to agent response before sending per spec."""
        raw_response = "Price: $100.00 — great_deal!"
        mocker.patch("bot.get_history", return_value=[])
        mocker.patch("bot.run_agent", new_callable=AsyncMock, return_value=raw_response)
        mocker.patch("bot.append_message")
        mock_escape = mocker.patch("bot.escape_markdown", wraps=escape_markdown)
        await bot.message_handler(mock_update, mock_context)
        mock_escape.assert_called_once_with(raw_response)


# ---------------------------------------------------------------------------
# TestErrorHandler
# ---------------------------------------------------------------------------


class TestErrorHandler:
    @pytest.mark.asyncio
    async def test_logs_error(self, mock_update, mock_context, mocker):
        """FR-9: error is logged with update and error info per spec."""
        mock_log = mocker.patch("bot.logger")
        await bot.error_handler(mock_update, mock_context)
        mock_log.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_sends_message_to_user_when_update_exists(self, mock_update, mock_context):
        """FR-9: error message sent to user when update is available per spec."""
        from telegram import Update as TelegramUpdate
        mock_update.__class__ = TelegramUpdate
        mock_update.effective_message.reply_text = AsyncMock()
        await bot.error_handler(mock_update, mock_context)
        mock_update.effective_message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_does_not_crash_when_update_is_none(self, mock_context):
        """FR-9: error handler does not raise when update is None per spec."""
        try:
            await bot.error_handler(None, mock_context)
        except Exception:
            pytest.fail("error_handler raised when update was None")
