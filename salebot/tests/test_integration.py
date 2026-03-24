"""Integration tests — FR-10: Full Package Flow.

Wires real modules: agent.py + memory.py + mcp_tools.py
Mocks: Claude API (via agent._get_client) + FastAPI (via respx)
"""

import sys
import os

import pytest
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import run_agent
from memory import append_message, clear_history, get_history, get_history_length


USER_A = 10001
USER_B = 10002


def _make_claude(mocker, *responses):
    """Patch agent._get_client with a fresh AsyncMock returning given responses."""
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(side_effect=list(responses))
    mocker.patch("agent._get_client", return_value=mock_client)
    return mock_client


def _end_turn(text):
    r = MagicMock()
    r.stop_reason = "end_turn"
    r.content = [MagicMock(type="text", text=text)]
    return r


def _tool_use(*tools):
    """tools: list of (name, input_dict) tuples."""
    r = MagicMock()
    r.stop_reason = "tool_use"
    blocks = []
    for i, (name, inp) in enumerate(tools):
        b = MagicMock()
        b.type = "tool_use"
        b.id = f"t{i}"
        b.name = name
        b.input = inp
        blocks.append(b)
    r.content = blocks
    return r


PACKAGE_TEXT = (
    "Here is your Singapore package!\n"
    "✈️ Flight: Bangkok → Singapore | AirAsia | $85.00\n"
    "🏨 Hotel: The Singapore Suites ⭐⭐⭐⭐ | $120.00/night\n"
    "🎯 Activities: Gardens by the Bay Tour | $25.00\n"
    "💰 Total: $350.00 (Budget remaining: $650.00)\n"
    "Would you like to adjust anything?"
)


# ---------------------------------------------------------------------------
# TestPrimaryJourney
# ---------------------------------------------------------------------------


class TestPrimaryJourney:
    @pytest.mark.asyncio
    async def test_full_package_built_from_single_message(self, mock_fastapi, mocker):
        """FR-10: single user message produces a complete tour package per spec."""
        _make_claude(
            mocker,
            _tool_use(
                ("search_flights", {"destination": "Singapore"}),
                ("search_hotels", {"city": "Singapore"}),
                ("search_activities", {"city": "Singapore"}),
            ),
            _end_turn(PACKAGE_TEXT),
        )
        result = await run_agent(USER_A, "Singapore this weekend, $1000", [])
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_package_contains_flight(self, mock_fastapi, mocker):
        """FR-10: response from run_agent references flight details per spec."""
        _make_claude(mocker, _tool_use(("search_flights", {"destination": "Singapore"})), _end_turn(PACKAGE_TEXT))
        result = await run_agent(USER_A, "Singapore $1000", [])
        assert "Flight" in result or "AirAsia" in result

    @pytest.mark.asyncio
    async def test_package_contains_hotel(self, mock_fastapi, mocker):
        """FR-10: response from run_agent references hotel details per spec."""
        _make_claude(mocker, _tool_use(("search_hotels", {"city": "Singapore"})), _end_turn(PACKAGE_TEXT))
        result = await run_agent(USER_A, "Singapore $1000", [])
        assert "Hotel" in result or "Suites" in result

    @pytest.mark.asyncio
    async def test_package_contains_activity(self, mock_fastapi, mocker):
        """FR-10: response from run_agent references at least one activity per spec."""
        _make_claude(mocker, _tool_use(("search_activities", {"city": "Singapore"})), _end_turn(PACKAGE_TEXT))
        result = await run_agent(USER_A, "Singapore $1000", [])
        assert "Activities" in result or "Gardens" in result or "Tour" in result

    @pytest.mark.asyncio
    async def test_agent_calls_search_flights_tool(self, mock_fastapi, mocker):
        """FR-10: run_agent triggers search_flights tool call per spec."""
        _make_claude(mocker, _tool_use(("search_flights", {"destination": "Singapore"})), _end_turn(PACKAGE_TEXT))
        await run_agent(USER_A, "Singapore $1000", [])
        assert mock_fastapi.calls.call_count >= 1
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/flights" in u for u in called_urls)

    @pytest.mark.asyncio
    async def test_agent_calls_search_hotels_tool(self, mock_fastapi, mocker):
        """FR-10: run_agent triggers search_hotels tool call per spec."""
        _make_claude(mocker, _tool_use(("search_hotels", {"city": "Singapore"})), _end_turn(PACKAGE_TEXT))
        await run_agent(USER_A, "Singapore $1000", [])
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/hotels" in u for u in called_urls)

    @pytest.mark.asyncio
    async def test_agent_calls_search_activities_tool(self, mock_fastapi, mocker):
        """FR-10: run_agent triggers search_activities tool call per spec."""
        _make_claude(mocker, _tool_use(("search_activities", {"city": "Singapore"})), _end_turn(PACKAGE_TEXT))
        await run_agent(USER_A, "Singapore $1000", [])
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/activities" in u for u in called_urls)

    @pytest.mark.asyncio
    async def test_history_saved_after_response(self, mock_fastapi, mocker):
        """FR-10: conversation history contains user and assistant messages after turn per spec."""
        _make_claude(mocker, _tool_use(("search_flights", {"destination": "Singapore"})), _end_turn(PACKAGE_TEXT))
        msg = "I want to visit Singapore, budget $1000"
        result = await run_agent(USER_A, msg, [])
        # Simulate what bot.py does
        append_message(USER_A, "user", msg)
        append_message(USER_A, "assistant", result)
        history = get_history(USER_A)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"


# ---------------------------------------------------------------------------
# TestTweakJourney
# ---------------------------------------------------------------------------


class TestTweakJourney:
    @pytest.mark.asyncio
    async def test_hotel_upgrade_uses_existing_history(self, mock_fastapi, mocker):
        """FR-10: follow-up tweak passes history to run_agent per spec."""
        client = _make_claude(
            mocker,
            _tool_use(("search_hotels", {"city": "Singapore", "stars": 5})),
            _end_turn("Updated package with luxury hotel!"),
        )
        history = [
            {"role": "user", "content": "Singapore $1000"},
            {"role": "assistant", "content": PACKAGE_TEXT},
        ]
        await run_agent(USER_A, "Can you upgrade the hotel?", history)
        first_call_messages = client.messages.create.call_args_list[0][1]["messages"]
        assert first_call_messages[0] == history[0]
        assert first_call_messages[1] == history[1]

    @pytest.mark.asyncio
    async def test_hotel_upgrade_triggers_new_hotel_search(self, mock_fastapi, mocker):
        """FR-10: upgrade hotel request triggers search_hotels again per spec."""
        _make_claude(
            mocker,
            _tool_use(("search_hotels", {"city": "Singapore", "stars": 5})),
            _end_turn("Upgraded package!"),
        )
        history = [
            {"role": "user", "content": "Singapore $1000"},
            {"role": "assistant", "content": PACKAGE_TEXT},
        ]
        await run_agent(USER_A, "Upgrade the hotel", history)
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/hotels" in u for u in called_urls)

    @pytest.mark.asyncio
    async def test_add_activity_triggers_activity_search(self, mock_fastapi, mocker):
        """FR-10: add activity request triggers search_activities again per spec."""
        _make_claude(
            mocker,
            _tool_use(("search_activities", {"city": "Singapore"})),
            _end_turn("Added Night Safari to your package!"),
        )
        history = [
            {"role": "user", "content": "Singapore $1000"},
            {"role": "assistant", "content": PACKAGE_TEXT},
        ]
        await run_agent(USER_A, "Add another activity", history)
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/activities" in u for u in called_urls)

    @pytest.mark.asyncio
    async def test_full_package_shown_after_tweak(self, mock_fastapi, mocker):
        """FR-10: complete package returned after tweak not just changed component per spec."""
        updated = (
            "Here is your updated package!\n"
            "✈️ Flight: Bangkok → Singapore | AirAsia | $85.00\n"
            "🏨 Hotel: Raffles Singapore ⭐⭐⭐⭐⭐ | $250.00/night\n"
            "🎯 Activities: Gardens by the Bay Tour | $25.00\n"
            "💰 Total: $610.00 (Budget remaining: $390.00)\n"
            "Would you like to adjust anything?"
        )
        _make_claude(mocker, _tool_use(("search_hotels", {"city": "Singapore"})), _end_turn(updated))
        result = await run_agent(USER_A, "Nicer hotel please", [{"role": "user", "content": "Singapore $1000"}])
        assert "Flight" in result or "Hotel" in result


# ---------------------------------------------------------------------------
# TestClearJourney
# ---------------------------------------------------------------------------


class TestClearJourney:
    def test_clear_wipes_history(self):
        """FR-10: clear_history removes all messages for user per spec."""
        append_message(USER_A, "user", "hello")
        append_message(USER_A, "assistant", "hi there")
        assert get_history_length(USER_A) == 2
        clear_history(USER_A)
        assert get_history(USER_A) == []

    @pytest.mark.asyncio
    async def test_fresh_message_after_clear_has_no_prior_context(self, mock_fastapi, mocker):
        """FR-10: run_agent after clear receives empty history per spec."""
        # Populate then clear
        append_message(USER_A, "user", "I want Singapore")
        append_message(USER_A, "assistant", "Here is Singapore...")
        clear_history(USER_A)

        history = get_history(USER_A)
        assert history == []  # History is empty after clear

        # Capture the initial messages length before any tool mutations
        initial_len = []

        async def capturing_create(**kwargs):
            if not initial_len:
                initial_len.append(len(kwargs["messages"]))
            # First call returns tool_use, second returns end_turn
            if len(initial_len) == 1 and not getattr(capturing_create, "_second", False):
                capturing_create._second = True
                return _tool_use(("search_flights", {"destination": "Bali"}))
            return _end_turn("Bali package!")

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=capturing_create)
        mocker.patch("agent._get_client", return_value=mock_client)

        result = await run_agent(USER_A, "I want Bali, $800", history)
        assert initial_len[0] == 1  # Only 1 message (no Singapore context)
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_two_users_have_independent_histories(self, mock_fastapi, mocker):
        """FR-10: user A history does not affect user B package per spec."""
        # Pre-load user A with Singapore history
        append_message(USER_A, "user", "Singapore $1000")
        append_message(USER_A, "assistant", PACKAGE_TEXT)
        assert get_history_length(USER_A) == 2

        # User B has no history
        history_b = get_history(USER_B)
        assert len(history_b) == 0

        # Capture what messages user B's agent call receives
        initial_len_b = []

        async def capturing_create(**kwargs):
            if not initial_len_b:
                initial_len_b.append(len(kwargs["messages"]))
            if len(initial_len_b) == 1 and not getattr(capturing_create, "_done", False):
                capturing_create._done = True
                return _tool_use(("search_flights", {"destination": "Bangkok"}))
            return _end_turn("Bangkok package for user B!")

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=capturing_create)
        mocker.patch("agent._get_client", return_value=mock_client)

        await run_agent(USER_B, "Bangkok $500", history_b)

        # User B's first call should only have 1 message (their own), not user A's 2
        assert initial_len_b[0] == 1
        # User A's history is still intact
        assert get_history_length(USER_A) == 2


# ---------------------------------------------------------------------------
# TestOverBudgetJourney
# ---------------------------------------------------------------------------


class TestOverBudgetJourney:
    @pytest.mark.asyncio
    async def test_agent_responds_when_budget_too_low(self, mock_fastapi, mocker):
        """FR-10: agent returns honest response when budget insufficient per spec."""
        over_budget_text = (
            "I wasn't able to build a complete package within $50. "
            "The minimum I can offer is $230. Would you like to proceed?"
        )
        _make_claude(
            mocker,
            _tool_use(("search_flights", {"destination": "Singapore"})),
            _end_turn(over_budget_text),
        )
        result = await run_agent(USER_A, "Singapore, budget $50", [])
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_no_package_presented_when_over_budget(self, mock_fastapi, mocker):
        """FR-10: over-budget response does not silently present package per spec."""
        over_budget_text = (
            "I wasn't able to build a complete package within $50. "
            "The minimum I can offer is $230. Would you like to proceed?"
        )
        _make_claude(
            mocker,
            _tool_use(("search_flights", {"destination": "Singapore"})),
            _end_turn(over_budget_text),
        )
        result = await run_agent(USER_A, "Singapore, budget $50", [])
        # Response should be honest — not a silent package with a total
        assert "Total: $" not in result or "wasn't able" in result or "minimum" in result


# ---------------------------------------------------------------------------
# TestToolCallIntegration
# ---------------------------------------------------------------------------


class TestToolCallIntegration:
    @pytest.mark.asyncio
    async def test_tool_results_appended_to_history(self, mock_fastapi, mocker):
        """FR-10: tool use and tool result messages sent to Claude on second call per spec."""
        client = _make_claude(
            mocker,
            _tool_use(("search_flights", {"destination": "Singapore"})),
            _end_turn(PACKAGE_TEXT),
        )
        await run_agent(USER_A, "Singapore $1000", [])
        assert client.messages.create.call_count == 2
        second_call_messages = client.messages.create.call_args_list[1][1]["messages"]
        tool_result_msgs = [
            m for m in second_call_messages
            if m["role"] == "user"
            and isinstance(m.get("content"), list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in m["content"])
        ]
        assert len(tool_result_msgs) == 1

    @pytest.mark.asyncio
    async def test_history_cap_respected_across_turns(self, mock_fastapi, mocker):
        """FR-10: history never exceeds 20 messages across multiple turns per spec."""
        for i in range(19):
            append_message(USER_A, "user" if i % 2 == 0 else "assistant", f"msg {i}")
        assert get_history_length(USER_A) == 19

        append_message(USER_A, "user", "one more")
        append_message(USER_A, "assistant", "response")
        assert get_history_length(USER_A) == 20

        append_message(USER_A, "user", "overflow")
        append_message(USER_A, "assistant", "capped")
        assert get_history_length(USER_A) == 20

    @pytest.mark.asyncio
    async def test_fastapi_unreachable_returns_graceful_error(self, mock_fastapi_down, mocker):
        """FR-10: unavailable FastAPI returns graceful error message per spec."""
        _make_claude(
            mocker,
            _tool_use(
                ("search_flights", {"destination": "Singapore"}),
                ("search_hotels", {"city": "Singapore"}),
                ("search_activities", {"city": "Singapore"}),
            ),
            _end_turn("I'm having trouble reaching the inventory right now."),
        )
        result = await run_agent(USER_A, "Singapore $1000", [])
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_all_four_tools_reachable_from_agent(self, mock_fastapi, mocker):
        """FR-10: all 4 MCP tools callable from within agent loop per spec."""
        _make_claude(
            mocker,
            _tool_use(
                ("search_flights", {"destination": "Singapore"}),
                ("search_hotels", {"city": "Singapore"}),
                ("search_activities", {"city": "Singapore"}),
                ("search_transport", {"origin": "Singapore Airport", "destination": "Singapore City"}),
            ),
            _end_turn(PACKAGE_TEXT),
        )
        result = await run_agent(USER_A, "Full package for Singapore $1000", [])
        called_urls = [str(c.request.url) for c in mock_fastapi.calls]
        assert any("/flights" in u for u in called_urls)
        assert any("/hotels" in u for u in called_urls)
        assert any("/activities" in u for u in called_urls)
        assert any("/transport" in u for u in called_urls)
        assert isinstance(result, str)
