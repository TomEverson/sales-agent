# TB-05: Agent Core — Tool Calling Loop

## Context
Read rules/base.md before starting.
Read rules/bot.md to understand how the agent will be called from the Telegram bot.
Read salebot/mcp_tools.py — all 4 tools must be complete before this story.

## Dependency
TB-01, TB-02, TB-03, TB-04 must be complete before starting this story.
TOOLS list and execute_tool dispatcher must exist in mcp_tools.py with all 4 tools.

---

## Goal
Create agent.py — the brain of the Salebot.
It receives a user message and conversation history, calls Claude API with the 4 MCP tools,
executes tool calls in a loop until Claude produces a final text response,
and returns that final response to the caller.

---

## Files to create
salebot/agent.py
salebot/prompts/system_prompt.md  ← placeholder only, full content in TB-08

---

## What to build

### 1. System Prompt Loader
Create a module-level function: load_system_prompt() -> str

- Read content from salebot/prompts/system_prompt.md
- If file does not exist → return a minimal fallback string:
  "You are Travelbase Assistant, a helpful travel sales agent."
- Cache the result in a module-level variable so the file
  is only read once per process startup
- Never raise an exception — always return a string

### 2. Tool Executor Bridge
Create a function: async def execute_tool_call(tool_name: str, tool_input: dict) -> str

- Import execute_tool from mcp_tools
- Call execute_tool(tool_name, tool_input)
- Wrap in try/except — if any exception occurs return:
  "Tool {tool_name} failed with error: {str(e)}"
- This is the only place in agent.py that touches mcp_tools

### 3. Core Agent Loop
Create the main function: async def run_agent(user_id: int, user_message: str, history: list) -> str

#### Parameters
- user_id: int — Telegram user ID (used for logging only in this story)
- user_message: str — the latest message from the user
- history: list — list of previous messages in Anthropic format
  [{"role": "user"|"assistant", "content": "..."}]

#### Loop behavior
1. Build messages list: history + new user message
2. Call Claude API:
   - model: claude-sonnet-4-5
   - max_tokens: 4096
   - system: load_system_prompt()
   - tools: TOOLS from mcp_tools
   - messages: built messages list
3. Check response stop_reason:
   - If "end_turn" → extract text from response and return it
   - If "tool_use" → execute all tool_use blocks, append results, loop again
   - If anything else → return "I encountered an unexpected error. Please try again."
4. Repeat until stop_reason is "end_turn" or max iterations reached

#### Iteration cap
- Maximum 10 iterations per run_agent call
- If cap is reached → return:
  "I was unable to complete your request in time. Please try again."

#### Message construction for tool results
After executing tool calls, append two messages to the messages list:

First — the assistant message with tool_use blocks:
```python
{
    "role": "assistant",
    "content": response.content  # list of content blocks from Claude
}
```

Second — the user message with tool_result blocks:
```python
{
    "role": "user",
    "content": [
        {
            "type": "tool_result",
            "tool_use_id": tool_use_block.id,
            "content": result_string
        }
        for each tool_use_block
    ]
}
```

#### Text extraction
When stop_reason is "end_turn", extract the final response text:
- Find the first content block where type == "text"
- Return its text field
- If no text block found → return "I have no response. Please try again."

### 4. Placeholder system_prompt.md
Create salebot/prompts/system_prompt.md with this content only:
```
You are Travelbase Assistant, a friendly travel sales agent.
Help users find flights, hotels, activities, and transport for their trips.
Use the available tools to search real inventory.
Never invent prices or availability.
```

Full system prompt will be written in TB-08.

---

## File structure after TB-05
```
salebot/
├── agent.py                    ← created in this story
├── mcp_tools.py                ← unchanged
├── prompts/
│   └── system_prompt.md        ← placeholder created in this story
└── tests/
    ├── __init__.py
    ├── conftest.py             ← add agent fixtures
    └── test_agent.py           ← created in this story
```

---

## Tests to write first
Create salebot/tests/test_agent.py:
```python
class TestLoadSystemPrompt:

    def test_returns_string_when_file_exists(self, tmp_path):
        """TB-05: load_system_prompt returns file content as string per spec"""

    def test_returns_fallback_when_file_missing(self):
        """TB-05: load_system_prompt returns fallback string when file not found per spec"""

    def test_never_raises_exception(self):
        """TB-05: load_system_prompt must never raise an exception per spec"""

    def test_result_is_cached(self, tmp_path):
        """TB-05: system prompt file is only read once per process per spec"""


class TestExecuteToolCall:

    async def test_routes_to_mcp_execute_tool(self, mocker):
        """TB-05: execute_tool_call delegates to mcp_tools.execute_tool per spec"""

    async def test_returns_error_string_on_exception(self, mocker):
        """TB-05: exceptions are caught and returned as error string per spec"""

    async def test_error_string_includes_tool_name(self, mocker):
        """TB-05: error message must include the tool name per spec"""


class TestRunAgent:

    async def test_returns_text_on_end_turn(self, mocker):
        """TB-05: returns extracted text when Claude stop_reason is end_turn per spec"""

    async def test_executes_tool_and_loops_on_tool_use(self, mocker):
        """TB-05: tool_use stop_reason triggers tool execution and second API call per spec"""

    async def test_executes_multiple_tools_in_one_turn(self, mocker):
        """TB-05: multiple tool_use blocks in one response are all executed per spec"""

    async def test_returns_error_on_unexpected_stop_reason(self, mocker):
        """TB-05: unexpected stop_reason returns error string per spec"""

    async def test_respects_max_iteration_cap(self, mocker):
        """TB-05: loop stops after 10 iterations and returns timeout message per spec"""

    async def test_timeout_message_is_correct(self, mocker):
        """TB-05: iteration cap message matches spec exactly"""

    async def test_appends_assistant_message_after_tool_use(self, mocker):
        """TB-05: assistant content blocks are appended to messages after tool_use per spec"""

    async def test_appends_tool_result_message_after_tool_use(self, mocker):
        """TB-05: tool_result user message is appended after tool execution per spec"""

    async def test_history_is_included_in_first_api_call(self, mocker):
        """TB-05: existing history is prepended to messages list per spec"""

    async def test_returns_fallback_when_no_text_block(self, mocker):
        """TB-05: no text block in end_turn response returns fallback message per spec"""

    async def test_user_id_does_not_affect_output(self, mocker):
        """TB-05: user_id is used for logging only and does not change return value per spec"""
```

Add to conftest.py:
```python
@pytest.fixture
def mock_end_turn_response():
    """TB-05: simulates Claude API response with stop_reason end_turn"""
    from unittest.mock import MagicMock
    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [
        MagicMock(type="text", text="Here is your tour package!")
    ]
    return response

@pytest.fixture
def mock_tool_use_response():
    """TB-05: simulates Claude API response with stop_reason tool_use"""
    from unittest.mock import MagicMock
    response = MagicMock()
    response.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "tool_123"
    tool_block.name = "search_flights"
    tool_block.input = {"destination": "Singapore"}
    response.content = [tool_block]
    return response

@pytest.fixture
def sample_history():
    """TB-05: sample conversation history in Anthropic message format"""
    return [
        {"role": "user", "content": "I want to visit Singapore"},
        {"role": "assistant", "content": "Great choice! What is your budget?"}
    ]
```

---

## Acceptance Criteria

- [ ] agent.py is created with no import errors
- [ ] load_system_prompt() exists and returns a string
- [ ] load_system_prompt() returns fallback string when file not found
- [ ] load_system_prompt() never raises an exception under any circumstance
- [ ] System prompt is cached — file is read only once per process
- [ ] execute_tool_call(tool_name, tool_input) exists with exact signature
- [ ] execute_tool_call catches all exceptions and returns error string
- [ ] Error string from execute_tool_call includes the tool name
- [ ] run_agent(user_id, user_message, history) exists with exact signature
- [ ] Uses model: claude-sonnet-4-5
- [ ] Uses max_tokens: 4096
- [ ] Passes TOOLS from mcp_tools to Claude API
- [ ] History is included in the messages list sent to Claude
- [ ] stop_reason "end_turn" → extracts and returns first text block
- [ ] stop_reason "tool_use" → executes all tool_use blocks and loops
- [ ] Multiple tool_use blocks in one response are all executed before looping
- [ ] Assistant message with content blocks appended after tool_use
- [ ] Tool result user message appended after tool execution
- [ ] Unexpected stop_reason returns "I encountered an unexpected error. Please try again."
- [ ] Loop cap is exactly 10 iterations
- [ ] Cap exceeded returns "I was unable to complete your request in time. Please try again."
- [ ] No text block in end_turn returns "I have no response. Please try again."
- [ ] salebot/prompts/system_prompt.md exists with placeholder content
- [ ] All tests in test_agent.py pass
- [ ] All previously passing TB-01 through TB-04 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
import asyncio
from agent import run_agent

async def test():
    # Test 1: basic request — agent should call tools and return a package
    result = await run_agent(
        user_id=12345,
        user_message="I want to visit Singapore this weekend, my budget is $1000",
        history=[]
    )
    print("Test 1 result:")
    print(result)
    print()

    # Test 2: follow-up with history
    history = [
        {"role": "user", "content": "I want to visit Singapore, budget $1000"},
        {"role": "assistant", "content": result}
    ]
    result2 = await run_agent(
        user_id=12345,
        user_message="Can you find me a nicer hotel?",
        history=history
    )
    print("Test 2 result (follow-up):")
    print(result2)

asyncio.run(test())
```

Expected:
- Test 1: A tour package response referencing real inventory
  (agent must have called at least search_flights and search_hotels)
- Test 2: A refined package with a higher-rated hotel
  (agent uses history to understand the original request context)

---

## When done
Print: ✅ TB-05 complete
Do not proceed to TB-06 until all acceptance criteria above are checked.
