"""Tests for salebot/memory.py — FR-6: Per-User Conversation History."""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import memory
from memory import (
    get_history,
    append_message,
    append_tool_messages,
    clear_history,
    get_history_length,
)


# ---------------------------------------------------------------------------
# TestGetHistory
# ---------------------------------------------------------------------------


class TestGetHistory:
    def test_returns_empty_list_for_new_user(self, user_id_a):
        """FR-6: unknown user_id returns empty list per spec."""
        assert get_history(user_id_a) == []

    def test_returns_stored_messages(self, user_id_a):
        """FR-6: stored messages are returned correctly per spec."""
        append_message(user_id_a, "user", "hello")
        result = get_history(user_id_a)
        assert result == [{"role": "user", "content": "hello"}]

    def test_returns_copy_not_reference(self, user_id_a):
        """FR-6: mutating returned list must not affect internal store per spec."""
        append_message(user_id_a, "user", "hello")
        result = get_history(user_id_a)
        result.append({"role": "user", "content": "injected"})
        assert get_history_length(user_id_a) == 1

    def test_returns_empty_list_after_clear(self, user_id_a):
        """FR-6: get_history returns empty list after clear_history per spec."""
        append_message(user_id_a, "user", "hello")
        clear_history(user_id_a)
        assert get_history(user_id_a) == []


# ---------------------------------------------------------------------------
# TestAppendMessage
# ---------------------------------------------------------------------------


class TestAppendMessage:
    def test_appends_user_message(self, user_id_a):
        """FR-6: user role message is appended correctly per spec."""
        append_message(user_id_a, "user", "hi there")
        assert get_history(user_id_a)[0] == {"role": "user", "content": "hi there"}

    def test_appends_assistant_message(self, user_id_a):
        """FR-6: assistant role message is appended correctly per spec."""
        append_message(user_id_a, "assistant", "How can I help?")
        assert get_history(user_id_a)[0] == {"role": "assistant", "content": "How can I help?"}

    def test_creates_new_list_for_new_user(self, user_id_a):
        """FR-6: new user_id creates a new history list per spec."""
        assert get_history_length(user_id_a) == 0
        append_message(user_id_a, "user", "first message")
        assert get_history_length(user_id_a) == 1

    def test_invalid_role_raises_value_error(self, user_id_a):
        """FR-6: invalid role raises ValueError per spec."""
        with pytest.raises(ValueError):
            append_message(user_id_a, "system", "hack")

    def test_invalid_role_error_message(self, user_id_a):
        """FR-6: ValueError message matches spec exactly."""
        with pytest.raises(ValueError, match="role must be user or assistant"):
            append_message(user_id_a, "system", "hack")

    def test_cap_enforced_at_20_messages(self, user_id_a):
        """FR-6: history never exceeds 20 messages per spec."""
        for i in range(25):
            append_message(user_id_a, "user", f"msg {i}")
        assert get_history_length(user_id_a) == 20

    def test_oldest_messages_dropped_first(self, user_id_a):
        """FR-6: messages are dropped from front not end per spec."""
        for i in range(25):
            append_message(user_id_a, "user", f"msg {i}")
        # After 25 messages capped to 20, the oldest 5 (0-4) are gone
        assert get_history(user_id_a)[0]["content"] == "msg 5"

    def test_cap_drops_correct_number_of_messages(self, user_id_a):
        """FR-6: exactly enough messages dropped to reach 20 per spec."""
        for i in range(23):
            append_message(user_id_a, "user", f"msg {i}")
        assert get_history_length(user_id_a) == 20
        assert get_history(user_id_a)[0]["content"] == "msg 3"

    def test_message_format_is_correct(self, user_id_a):
        """FR-6: stored message has role and content keys per spec."""
        append_message(user_id_a, "user", "test")
        msg = get_history(user_id_a)[0]
        assert "role" in msg
        assert "content" in msg
        assert msg["role"] == "user"
        assert msg["content"] == "test"


# ---------------------------------------------------------------------------
# TestAppendToolMessages
# ---------------------------------------------------------------------------


class TestAppendToolMessages:
    def _make_tool_data(self):
        assistant_content = [{"type": "tool_use", "id": "t1", "name": "search_flights", "input": {}}]
        tool_results = [{"type": "tool_result", "tool_use_id": "t1", "content": "[]"}]
        return assistant_content, tool_results

    def test_appends_two_messages(self, user_id_a):
        """FR-6: append_tool_messages always adds exactly 2 messages per spec."""
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history_length(user_id_a) == 2

    def test_first_message_is_assistant(self, user_id_a):
        """FR-6: first appended message has role assistant per spec."""
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history(user_id_a)[0]["role"] == "assistant"

    def test_second_message_is_user(self, user_id_a):
        """FR-6: second appended message has role user per spec."""
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history(user_id_a)[1]["role"] == "user"

    def test_assistant_content_is_stored_as_list(self, user_id_a):
        """FR-6: assistant_content list is stored directly without modification per spec."""
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history(user_id_a)[0]["content"] == ac

    def test_tool_results_stored_as_content(self, user_id_a):
        """FR-6: tool_results list stored as content of user message per spec."""
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history(user_id_a)[1]["content"] == tr

    def test_cap_enforced_after_appending_two(self, user_id_a):
        """FR-6: 20 message cap is enforced after both messages are appended per spec."""
        # Fill to 19 messages
        for i in range(19):
            append_message(user_id_a, "user", f"msg {i}")
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history_length(user_id_a) == 20

    def test_cap_drops_from_front_when_adding_two(self, user_id_a):
        """FR-6: oldest messages dropped from front when cap exceeded by 2 per spec."""
        # Fill to 20 messages
        for i in range(20):
            append_message(user_id_a, "user", f"msg {i}")
        ac, tr = self._make_tool_data()
        append_tool_messages(user_id_a, ac, tr)
        assert get_history_length(user_id_a) == 20
        # The two oldest plain messages were dropped
        assert get_history(user_id_a)[0]["content"] == "msg 2"


# ---------------------------------------------------------------------------
# TestClearHistory
# ---------------------------------------------------------------------------


class TestClearHistory:
    def test_clears_existing_history(self, user_id_a):
        """FR-6: clear_history removes all messages for user_id per spec."""
        append_message(user_id_a, "user", "hello")
        clear_history(user_id_a)
        assert get_history(user_id_a) == []

    def test_clear_nonexistent_user_does_nothing(self, user_id_a):
        """FR-6: clear_history on unknown user_id does not raise per spec."""
        try:
            clear_history(user_id_a)
        except Exception:
            pytest.fail("clear_history raised an exception for unknown user_id")

    def test_clear_does_not_affect_other_users(self, user_id_a, user_id_b):
        """FR-6: clearing one user does not affect another user's history per spec."""
        append_message(user_id_a, "user", "user A message")
        append_message(user_id_b, "user", "user B message")
        clear_history(user_id_a)
        assert get_history_length(user_id_b) == 1


# ---------------------------------------------------------------------------
# TestGetHistoryLength
# ---------------------------------------------------------------------------


class TestGetHistoryLength:
    def test_returns_zero_for_new_user(self, user_id_a):
        """FR-6: unknown user_id returns 0 per spec."""
        assert get_history_length(user_id_a) == 0

    def test_returns_correct_count(self, user_id_a):
        """FR-6: returns exact number of stored messages per spec."""
        append_message(user_id_a, "user", "one")
        append_message(user_id_a, "assistant", "two")
        assert get_history_length(user_id_a) == 2

    def test_returns_zero_after_clear(self, user_id_a):
        """FR-6: returns 0 after clear_history per spec."""
        append_message(user_id_a, "user", "hello")
        clear_history(user_id_a)
        assert get_history_length(user_id_a) == 0

    def test_returns_max_20_after_cap(self, user_id_a):
        """FR-6: never returns more than 20 per spec."""
        for i in range(30):
            append_message(user_id_a, "user", f"msg {i}")
        assert get_history_length(user_id_a) == 20


# ---------------------------------------------------------------------------
# TestIsolation
# ---------------------------------------------------------------------------


class TestIsolation:
    def test_different_users_have_independent_histories(self, user_id_a, user_id_b):
        """FR-6: two user_ids store and retrieve independent histories per spec."""
        append_message(user_id_a, "user", "user A")
        append_message(user_id_b, "user", "user B")
        assert get_history(user_id_a)[0]["content"] == "user A"
        assert get_history(user_id_b)[0]["content"] == "user B"

    def test_store_is_module_level_dict(self):
        """FR-6: _store is a dict at module level per spec."""
        assert isinstance(memory._store, dict)
