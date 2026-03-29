# TB-13: Clean Up agent.py — Remove Dead Code and Fix Content Serialisation

## Context
Read rules/base.md before starting.
Read specs/sprint-1/tb-05-agent-tool-calling-loop.md — defines exactly which functions should exist in agent.py.
Read salebot/agent.py — contains two non-spec functions (handle_message, _run_agent_loop)
that are never called by bot.py, plus a content serialisation inconsistency in run_agent.
Read salebot/bot.py — confirms that handle_message is never imported or called;
only run_agent is used.

## Dependency
TB-11 and TB-12 must be complete.
All tests must be passing before this cleanup story starts:
  uv run pytest tests/ -v   ← must show 0 failures

---

## Goal
Remove handle_message and _run_agent_loop from agent.py (dead code not in TB-05 spec,
never called by bot.py). Fix run_agent to serialise Claude API content-block objects
into plain Python dicts before appending the assistant message to the messages list,
matching the intent of the TB-05 spec and the correct behaviour already in _run_agent_loop.

---

## Files to modify
- salebot/agent.py — remove two functions; fix one code block in run_agent
- salebot/tests/test_agent.py — append two new test classes

---

## What to build

### 1. Remove handle_message from agent.py

Delete the entire async def handle_message(user_id: int, user_text: str) -> str function.

Why: bot.py calls run_agent and manages memory itself. handle_message is never imported
or called anywhere in the codebase and contains a redundant memory-management path
that duplicates bot.py logic. Its presence violates the TB-05 spec which defines only
run_agent as the public entry point.

### 2. Remove _run_agent_loop from agent.py

Delete the entire async def _run_agent_loop(...) -> str private function.

Why: _run_agent_loop was the implementation body called by handle_message. With
handle_message removed, _run_agent_loop has no caller and must also be removed.

### 3. Fix content-block serialisation in run_agent

Current code (wrong — appends raw SDK objects):
```python
if response.stop_reason == "tool_use":
    messages.append({"role": "assistant", "content": response.content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            ...
```

Replace the assistant-message append with explicit serialisation (correct):
```python
if response.stop_reason == "tool_use":
    assistant_content: list[dict[str, Any]] = []
    for block in response.content:
        if block.type == "text":
            assistant_content.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            assistant_content.append({
                "type": "tool_use",
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    messages.append({"role": "assistant", "content": assistant_content})
    tool_results = []
    for block in response.content:
        if block.type == "tool_use":
            ...
```

Why: The Anthropic API requires message history to contain plain Python dicts.
Passing raw SDK content-block objects back into a subsequent messages.create call
is fragile — it happens to work because the SDK re-serialises them, but it is not
the intended usage and will break if the SDK changes. The deleted _run_agent_loop
already had the correct implementation; this fix brings run_agent in line.

---

## Tests to write first

Add to salebot/tests/test_agent.py before making any changes to agent.py:

```python
class TestRunAgentContentSerialisation:

    @pytest.mark.asyncio
    async def test_assistant_message_content_is_list_of_dicts(self, mocker):
        """TB-13: assistant content blocks in messages list are plain dicts not SDK objects."""

    @pytest.mark.asyncio
    async def test_tool_use_block_dict_has_required_keys(self, mocker):
        """TB-13: serialised tool_use dict has type, id, name, input keys per spec."""

    @pytest.mark.asyncio
    async def test_text_block_dict_has_required_keys(self, mocker):
        """TB-13: serialised text dict has type and text keys per spec."""


class TestAgentPublicInterface:

    def test_handle_message_does_not_exist(self):
        """TB-13: handle_message must not exist in agent.py per spec."""

    def test_run_agent_loop_does_not_exist(self):
        """TB-13: _run_agent_loop must not exist in agent.py per spec."""

    def test_run_agent_exists(self):
        """TB-13: run_agent function must still exist per TB-05 spec."""

    def test_execute_tool_call_exists(self):
        """TB-13: execute_tool_call function must still exist per TB-05 spec."""

    def test_load_system_prompt_exists(self):
        """TB-13: load_system_prompt function must still exist per TB-05 spec."""
```

Note on TestRunAgentContentSerialisation: capture the messages list built inside
run_agent by patching _get_client and inspecting the calls made to
client.messages.create. After the first (tool_use) call returns, the second call's
messages argument should contain an assistant entry whose "content" value is a list
of plain dicts with string keys.

---

## Additions to conftest.py

No new fixtures required for this story.

---

## Acceptance Criteria

- [ ] handle_message function no longer exists in agent.py
- [ ] _run_agent_loop function no longer exists in agent.py
- [ ] run_agent still exists with exact signature: run_agent(user_id: int, user_message: str, history: list) -> str
- [ ] execute_tool_call still exists with exact signature per TB-05 spec
- [ ] load_system_prompt still exists
- [ ] _get_client still exists
- [ ] In run_agent, the assistant message appended for tool_use responses contains a list of plain dicts
- [ ] Each dict in the assistant content list has correct keys:
      text blocks: {"type": "text", "text": "..."}
      tool_use blocks: {"type": "tool_use", "id": "...", "name": "...", "input": {...}}
- [ ] test_handle_message_does_not_exist passes
- [ ] test_run_agent_loop_does_not_exist passes
- [ ] test_assistant_message_content_is_list_of_dicts passes
- [ ] test_tool_use_block_dict_has_required_keys passes
- [ ] All previously passing test_agent.py tests still pass (no regression)
- [ ] All previously passing tests across all test files still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test script

```python
import agent, inspect

# Test 1: dead code removed
assert not hasattr(agent, "handle_message"), "handle_message should not exist"
assert not hasattr(agent, "_run_agent_loop"), "_run_agent_loop should not exist"
print("Test 1: dead code removed ✅")

# Test 2: spec functions still present
assert hasattr(agent, "run_agent"), "run_agent must exist"
assert hasattr(agent, "execute_tool_call"), "execute_tool_call must exist"
assert hasattr(agent, "load_system_prompt"), "load_system_prompt must exist"
print("Test 2: spec functions present ✅")

# Test 3: run_agent signature unchanged
sig = inspect.signature(agent.run_agent)
params = list(sig.parameters.keys())
assert params == ["user_id", "user_message", "history"], f"Unexpected params: {params}"
print("Test 3: run_agent signature correct ✅")

# Test 4: execute_tool_call signature unchanged
sig2 = inspect.signature(agent.execute_tool_call)
params2 = list(sig2.parameters.keys())
assert params2 == ["tool_name", "tool_input"], f"Unexpected params: {params2}"
print("Test 4: execute_tool_call signature correct ✅")
```

Expected:
- Test 1: no AttributeError, confirmation printed
- Test 2: all three functions found
- Test 3: params = ["user_id", "user_message", "history"]
- Test 4: params = ["tool_name", "tool_input"]

---

## When done
Print: ✅ TB-13 complete — agent.py is clean and spec-compliant.
Run the full test suite one final time to confirm zero failures:
  uv run pytest tests/ -v
  uv run ruff check .
