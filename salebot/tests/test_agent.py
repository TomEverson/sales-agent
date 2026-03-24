"""Tests for salebot/agent.py — FR-5: Agent Core."""

import sys
import os

import pytest
from unittest.mock import MagicMock, AsyncMock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import agent


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _reset_prompt_cache():
    """Reset module-level prompt cache so each test starts clean."""
    agent._system_prompt = None


# ---------------------------------------------------------------------------
# TestLoadSystemPrompt
# ---------------------------------------------------------------------------


class TestLoadSystemPrompt:
    def setup_method(self):
        _reset_prompt_cache()

    def teardown_method(self):
        _reset_prompt_cache()

    def test_returns_string_when_file_exists(self):
        """FR-5: load_system_prompt returns file content as string per spec."""
        result = agent.load_system_prompt()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_fallback_when_file_missing(self, mocker):
        """FR-5: load_system_prompt returns fallback string when file not found per spec."""
        mocker.patch("pathlib.Path.read_text", side_effect=FileNotFoundError)
        result = agent.load_system_prompt()
        assert result == "You are Travelbase Assistant, a helpful travel sales agent."

    def test_never_raises_exception(self, mocker):
        """FR-5: load_system_prompt must never raise an exception per spec."""
        mocker.patch("pathlib.Path.read_text", side_effect=PermissionError("denied"))
        try:
            result = agent.load_system_prompt()
        except Exception:
            pytest.fail("load_system_prompt raised an exception")
        assert isinstance(result, str)

    def test_result_is_cached(self, mocker):
        """FR-5: system prompt file is only read once per process per spec."""
        mock_read = mocker.patch("pathlib.Path.read_text", return_value="cached content")
        agent.load_system_prompt()
        agent.load_system_prompt()
        assert mock_read.call_count == 1


# ---------------------------------------------------------------------------
# TestExecuteToolCall
# ---------------------------------------------------------------------------


class TestExecuteToolCall:
    @pytest.mark.asyncio
    async def test_routes_to_mcp_execute_tool(self, mocker):
        """FR-5: execute_tool_call delegates to mcp_tools.execute_tool per spec."""
        mock = mocker.patch("agent.execute_tool", new_callable=AsyncMock, return_value="result")
        result = await agent.execute_tool_call("search_flights", {"destination": "Singapore"})
        mock.assert_called_once_with("search_flights", {"destination": "Singapore"})
        assert result == "result"

    @pytest.mark.asyncio
    async def test_returns_error_string_on_exception(self, mocker):
        """FR-5: exceptions are caught and returned as error string per spec."""
        mocker.patch("agent.execute_tool", new_callable=AsyncMock, side_effect=Exception("boom"))
        result = await agent.execute_tool_call("search_flights", {})
        assert "failed with error" in result

    @pytest.mark.asyncio
    async def test_error_string_includes_tool_name(self, mocker):
        """FR-5: error message must include the tool name per spec."""
        mocker.patch("agent.execute_tool", new_callable=AsyncMock, side_effect=Exception("boom"))
        result = await agent.execute_tool_call("search_hotels", {})
        assert "search_hotels" in result


# ---------------------------------------------------------------------------
# TestRunAgent
# ---------------------------------------------------------------------------


class TestRunAgent:
    def _setup_client(self, mocker, *responses):
        """Patch _get_client and execute_tool_call, returning a mock client."""
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=list(responses))
        mocker.patch("agent._get_client", return_value=mock_client)
        mocker.patch(
            "agent.execute_tool_call",
            new_callable=AsyncMock,
            return_value='{"flights": []}',
        )
        return mock_client

    @pytest.mark.asyncio
    async def test_returns_text_on_end_turn(self, mocker, mock_end_turn_response):
        """FR-5: returns extracted text when Claude stop_reason is end_turn per spec."""
        self._setup_client(mocker, mock_end_turn_response)
        result = await agent.run_agent(1, "Hello", [])
        assert result == "Here is your tour package!"

    @pytest.mark.asyncio
    async def test_executes_tool_and_loops_on_tool_use(
        self, mocker, mock_tool_use_response, mock_end_turn_response
    ):
        """FR-5: tool_use stop_reason triggers tool execution and second API call per spec."""
        client = self._setup_client(mocker, mock_tool_use_response, mock_end_turn_response)
        result = await agent.run_agent(1, "Find flights", [])
        assert client.messages.create.call_count == 2
        assert result == "Here is your tour package!"

    @pytest.mark.asyncio
    async def test_executes_multiple_tools_in_one_turn(self, mocker, mock_end_turn_response):
        """FR-5: multiple tool_use blocks in one response are all executed per spec."""
        multi_tool_response = MagicMock()
        multi_tool_response.stop_reason = "tool_use"
        block1 = MagicMock(type="tool_use", id="t1", name="search_flights", input={"destination": "Singapore"})
        block2 = MagicMock(type="tool_use", id="t2", name="search_hotels", input={"city": "Singapore"})
        multi_tool_response.content = [block1, block2]

        self._setup_client(mocker, multi_tool_response, mock_end_turn_response)
        mock_execute = mocker.patch(
            "agent.execute_tool_call", new_callable=AsyncMock, return_value="ok"
        )
        await agent.run_agent(1, "Plan my trip", [])
        assert mock_execute.call_count == 2

    @pytest.mark.asyncio
    async def test_returns_error_on_unexpected_stop_reason(self, mocker):
        """FR-5: unexpected stop_reason returns error string per spec."""
        bad_response = MagicMock()
        bad_response.stop_reason = "max_tokens"
        bad_response.content = []
        self._setup_client(mocker, bad_response)
        result = await agent.run_agent(1, "Hello", [])
        assert result == "I encountered an unexpected error. Please try again."

    @pytest.mark.asyncio
    async def test_respects_max_iteration_cap(self, mocker, mock_tool_use_response):
        """FR-5: loop stops after 10 iterations and returns timeout message per spec."""
        client = self._setup_client(mocker, *([mock_tool_use_response] * 11))
        result = await agent.run_agent(1, "Hello", [])
        assert client.messages.create.call_count == 10
        assert result == "I was unable to complete your request in time. Please try again."

    @pytest.mark.asyncio
    async def test_timeout_message_is_correct(self, mocker, mock_tool_use_response):
        """FR-5: iteration cap message matches spec exactly."""
        self._setup_client(mocker, *([mock_tool_use_response] * 11))
        result = await agent.run_agent(1, "Hello", [])
        assert result == "I was unable to complete your request in time. Please try again."

    @pytest.mark.asyncio
    async def test_appends_assistant_message_after_tool_use(
        self, mocker, mock_tool_use_response, mock_end_turn_response
    ):
        """FR-5: assistant content blocks are appended to messages after tool_use per spec."""
        client = self._setup_client(mocker, mock_tool_use_response, mock_end_turn_response)
        await agent.run_agent(1, "Find flights", [])
        second_call_messages = client.messages.create.call_args_list[1][1]["messages"]
        # The assistant message with tool_use content should be in the messages
        assistant_msgs = [m for m in second_call_messages if m["role"] == "assistant"]
        assert len(assistant_msgs) >= 1

    @pytest.mark.asyncio
    async def test_appends_tool_result_message_after_tool_use(
        self, mocker, mock_tool_use_response, mock_end_turn_response
    ):
        """FR-5: tool_result user message is appended after tool execution per spec."""
        client = self._setup_client(mocker, mock_tool_use_response, mock_end_turn_response)
        await agent.run_agent(1, "Find flights", [])
        second_call_messages = client.messages.create.call_args_list[1][1]["messages"]
        # Find the user message that contains tool_result
        tool_result_msgs = [
            m for m in second_call_messages
            if m["role"] == "user"
            and isinstance(m["content"], list)
            and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in m["content"])
        ]
        assert len(tool_result_msgs) == 1

    @pytest.mark.asyncio
    async def test_history_is_included_in_first_api_call(
        self, mocker, mock_end_turn_response, sample_history
    ):
        """FR-5: existing history is prepended to messages list per spec."""
        client = self._setup_client(mocker, mock_end_turn_response)
        await agent.run_agent(1, "New message", sample_history)
        first_call_messages = client.messages.create.call_args_list[0][1]["messages"]
        assert first_call_messages[0] == sample_history[0]
        assert first_call_messages[1] == sample_history[1]

    @pytest.mark.asyncio
    async def test_returns_fallback_when_no_text_block(self, mocker):
        """FR-5: no text block in end_turn response returns fallback message per spec."""
        no_text_response = MagicMock()
        no_text_response.stop_reason = "end_turn"
        no_text_response.content = [MagicMock(type="image")]
        self._setup_client(mocker, no_text_response)
        result = await agent.run_agent(1, "Hello", [])
        assert result == "I have no response. Please try again."

    @pytest.mark.asyncio
    async def test_user_id_does_not_affect_output(
        self, mocker, mock_end_turn_response
    ):
        """FR-5: user_id is used for logging only and does not change return value per spec."""
        self._setup_client(mocker, mock_end_turn_response)
        result_a = await agent.run_agent(111, "Hello", [])

        mocker.patch("agent._get_client", return_value=MagicMock(
            messages=MagicMock(create=AsyncMock(return_value=mock_end_turn_response))
        ))
        result_b = await agent.run_agent(999, "Hello", [])
        assert result_a == result_b


# ---------------------------------------------------------------------------
# TestRunAgentContentSerialisation — FR-13
# ---------------------------------------------------------------------------


class TestRunAgentContentSerialisation:
    def _tool_response_then_end_turn(self, text="Done"):
        """Build a tool_use response followed by an end_turn response."""
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "t1"
        tool_block.name = "search_flights"
        tool_block.input = {"destination": "Singapore"}

        tool_response = MagicMock()
        tool_response.stop_reason = "tool_use"
        tool_response.content = [tool_block]

        end_response = MagicMock()
        end_response.stop_reason = "end_turn"
        end_response.content = [MagicMock(type="text", text=text)]
        return tool_response, end_response

    @pytest.mark.asyncio
    async def test_assistant_message_content_is_list_of_dicts(self, mocker):
        """FR-13: assistant content blocks in messages list are plain dicts not SDK objects."""
        tool_resp, end_resp = self._tool_response_then_end_turn()
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_resp, end_resp])
        mocker.patch("agent._get_client", return_value=mock_client)
        mocker.patch("agent.execute_tool", return_value="[]")

        await agent.run_agent(1, "test", [])

        # Second call's messages list must have an assistant entry whose
        # content is a list of plain dicts
        second_call_messages = mock_client.messages.create.call_args_list[1][1]["messages"]
        assistant_entry = next(m for m in second_call_messages if m["role"] == "assistant")
        content = assistant_entry["content"]
        assert isinstance(content, list)
        for block in content:
            assert isinstance(block, dict), f"Expected dict, got {type(block)}"

    @pytest.mark.asyncio
    async def test_tool_use_block_dict_has_required_keys(self, mocker):
        """FR-13: serialised tool_use dict has type, id, name, input keys per spec."""
        tool_resp, end_resp = self._tool_response_then_end_turn()
        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_resp, end_resp])
        mocker.patch("agent._get_client", return_value=mock_client)
        mocker.patch("agent.execute_tool", return_value="[]")

        await agent.run_agent(1, "test", [])

        second_call_messages = mock_client.messages.create.call_args_list[1][1]["messages"]
        assistant_entry = next(m for m in second_call_messages if m["role"] == "assistant")
        tool_dicts = [b for b in assistant_entry["content"] if b.get("type") == "tool_use"]
        assert len(tool_dicts) == 1
        td = tool_dicts[0]
        assert "type" in td
        assert "id" in td
        assert "name" in td
        assert "input" in td

    @pytest.mark.asyncio
    async def test_text_block_dict_has_required_keys(self, mocker):
        """FR-13: serialised text dict has type and text keys per spec."""
        text_block = MagicMock()
        text_block.type = "text"
        text_block.text = "Thinking..."
        tool_block = MagicMock()
        tool_block.type = "tool_use"
        tool_block.id = "t1"
        tool_block.name = "search_flights"
        tool_block.input = {"destination": "Singapore"}

        tool_resp = MagicMock()
        tool_resp.stop_reason = "tool_use"
        tool_resp.content = [text_block, tool_block]

        end_resp = MagicMock()
        end_resp.stop_reason = "end_turn"
        end_resp.content = [MagicMock(type="text", text="Done")]

        mock_client = MagicMock()
        mock_client.messages.create = AsyncMock(side_effect=[tool_resp, end_resp])
        mocker.patch("agent._get_client", return_value=mock_client)
        mocker.patch("agent.execute_tool", return_value="[]")

        await agent.run_agent(1, "test", [])

        second_call_messages = mock_client.messages.create.call_args_list[1][1]["messages"]
        assistant_entry = next(m for m in second_call_messages if m["role"] == "assistant")
        text_dicts = [b for b in assistant_entry["content"] if b.get("type") == "text"]
        assert len(text_dicts) == 1
        assert "type" in text_dicts[0]
        assert "text" in text_dicts[0]


# ---------------------------------------------------------------------------
# TestAgentPublicInterface — FR-13
# ---------------------------------------------------------------------------


class TestAgentPublicInterface:
    def test_handle_message_does_not_exist(self):
        """FR-13: handle_message must not exist in agent.py per spec."""
        assert not hasattr(agent, "handle_message")

    def test_run_agent_loop_does_not_exist(self):
        """FR-13: _run_agent_loop must not exist in agent.py per spec."""
        assert not hasattr(agent, "_run_agent_loop")

    def test_run_agent_exists(self):
        """FR-13: run_agent function must still exist per FR-5 spec."""
        assert hasattr(agent, "run_agent")
        assert callable(agent.run_agent)

    def test_execute_tool_call_exists(self):
        """FR-13: execute_tool_call function must still exist per FR-5 spec."""
        assert hasattr(agent, "execute_tool_call")
        assert callable(agent.execute_tool_call)

    def test_load_system_prompt_exists(self):
        """FR-13: load_system_prompt function must still exist per FR-5 spec."""
        assert hasattr(agent, "load_system_prompt")
        assert callable(agent.load_system_prompt)
