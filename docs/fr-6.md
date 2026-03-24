# FR-6: Memory — Per-User Conversation History

## Context
Read rules/base.md before starting.
Read salebot/agent.py from FR-5 — memory.py will be called from here.
Read rules/bot.md to understand how user_id flows from Telegram into the memory system.

## Dependency
FR-5 must be complete before starting this story.
run_agent(user_id, user_message, history) must exist in agent.py.

---

## Goal
Create memory.py — the per-user conversation store.
The bot will use it to load history before calling run_agent
and save the updated history after each response.
Memory persists across multiple messages in the same session
but is lost when the server restarts (in-memory only, no DB).

---

## File to create
salebot/memory.py

---

## What to build

### 1. Storage
Define a single module-level dict as the store:
```python
_store: dict[int, list[dict]] = {}
```

- Keys are Telegram user_id (int)
- Values are lists of messages in Anthropic format:
  [{"role": "user"|"assistant", "content": "..."}]
- This dict is the only storage mechanism — no file, no DB, no cache

### 2. get_history
Create a function: get_history(user_id: int) -> list[dict]

- Return a copy of the message list for user_id
- If user_id has no history → return empty list []
- Must return a copy, not a reference to the internal list
  (caller mutations must not affect the store)

### 3. append_message
Create a function: append_message(user_id: int, role: str, content: str) -> None

- Append {"role": role, "content": content} to the user's history
- If user_id does not exist in store → create a new list for them
- After appending, enforce the 20 message cap:
  if len(history) > 20 → drop the oldest messages until len == 20
  Always drop from the front (index 0), never from the end
- role must be one of: "user", "assistant"
- If role is anything else → raise ValueError("role must be user or assistant")

### 4. append_tool_messages
Create a function: append_tool_messages(user_id: int, assistant_content: list, tool_results: list) -> None

- Used to store tool use + tool result message pairs in history
- Appends two raw message dicts directly to the store (no role validation):

First message:
```python
{"role": "assistant", "content": assistant_content}
```

Second message:
```python
{"role": "user", "content": tool_results}
```

- assistant_content is the raw content block list from Claude API response
- tool_results is the list of tool_result dicts built in agent.py
- After appending both, enforce the 20 message cap same as append_message
- This function exists separately because tool messages contain structured
  content blocks, not plain strings

### 5. clear_history
Create a function: clear_history(user_id: int) -> None

- Remove all history for user_id from the store
- If user_id does not exist → do nothing, no error

### 6. get_history_length
Create a function: get_history_length(user_id: int) -> int

- Return the number of messages currently stored for user_id
- If user_id has no history → return 0

---

## Cap enforcement rule
The 20 message cap applies after every append operation.
Drop from the front until len == 20.
This rule applies in both append_message and append_tool_messages.

Example:
- History has 19 messages
- append_message adds 1 → now 20 → no drop needed
- append_message adds 1 more → now 21 → drop index 0 → back to 20

For append_tool_messages (adds 2 at once):
- History has 19 messages
- append_tool_messages adds 2 → now 21 → drop index 0 → back to 20
- History has 20 messages
- append_tool_messages adds 2 → now 22 → drop index 0, 1 → back to 20

---

## File structure after FR-6
```
salebot/
├── agent.py               ← unchanged
├── memory.py              ← created in this story
├── mcp_tools.py           ← unchanged
├── prompts/
│   └── system_prompt.md   ← unchanged
└── tests/
    ├── __init__.py
    ├── conftest.py        ← add memory fixtures
    └── test_memory.py     ← created in this story
```

---

## Tests to write first
Create salebot/tests/test_memory.py:
```python
class TestGetHistory:

    def test_returns_empty_list_for_new_user(self):
        """FR-6: unknown user_id returns empty list per spec"""

    def test_returns_stored_messages(self):
        """FR-6: stored messages are returned correctly per spec"""

    def test_returns_copy_not_reference(self):
        """FR-6: mutating returned list must not affect internal store per spec"""

    def test_returns_empty_list_after_clear(self):
        """FR-6: get_history returns empty list after clear_history per spec"""


class TestAppendMessage:

    def test_appends_user_message(self):
        """FR-6: user role message is appended correctly per spec"""

    def test_appends_assistant_message(self):
        """FR-6: assistant role message is appended correctly per spec"""

    def test_creates_new_list_for_new_user(self):
        """FR-6: new user_id creates a new history list per spec"""

    def test_invalid_role_raises_value_error(self):
        """FR-6: invalid role raises ValueError per spec"""

    def test_invalid_role_error_message(self):
        """FR-6: ValueError message matches spec exactly"""

    def test_cap_enforced_at_20_messages(self):
        """FR-6: history never exceeds 20 messages per spec"""

    def test_oldest_messages_dropped_first(self):
        """FR-6: messages are dropped from front not end per spec"""

    def test_cap_drops_correct_number_of_messages(self):
        """FR-6: exactly enough messages dropped to reach 20 per spec"""

    def test_message_format_is_correct(self):
        """FR-6: stored message has role and content keys per spec"""


class TestAppendToolMessages:

    def test_appends_two_messages(self):
        """FR-6: append_tool_messages always adds exactly 2 messages per spec"""

    def test_first_message_is_assistant(self):
        """FR-6: first appended message has role assistant per spec"""

    def test_second_message_is_user(self):
        """FR-6: second appended message has role user per spec"""

    def test_assistant_content_is_stored_as_list(self):
        """FR-6: assistant_content list is stored directly without modification per spec"""

    def test_tool_results_stored_as_content(self):
        """FR-6: tool_results list stored as content of user message per spec"""

    def test_cap_enforced_after_appending_two(self):
        """FR-6: 20 message cap is enforced after both messages are appended per spec"""

    def test_cap_drops_from_front_when_adding_two(self):
        """FR-6: oldest messages dropped from front when cap exceeded by 2 per spec"""


class TestClearHistory:

    def test_clears_existing_history(self):
        """FR-6: clear_history removes all messages for user_id per spec"""

    def test_clear_nonexistent_user_does_nothing(self):
        """FR-6: clear_history on unknown user_id does not raise per spec"""

    def test_clear_does_not_affect_other_users(self):
        """FR-6: clearing one user does not affect another user's history per spec"""


class TestGetHistoryLength:

    def test_returns_zero_for_new_user(self):
        """FR-6: unknown user_id returns 0 per spec"""

    def test_returns_correct_count(self):
        """FR-6: returns exact number of stored messages per spec"""

    def test_returns_zero_after_clear(self):
        """FR-6: returns 0 after clear_history per spec"""

    def test_returns_max_20_after_cap(self):
        """FR-6: never returns more than 20 per spec"""


class TestIsolation:

    def test_different_users_have_independent_histories(self):
        """FR-6: two user_ids store and retrieve independent histories per spec"""

    def test_store_is_module_level_dict(self):
        """FR-6: _store is a dict at module level per spec"""
```

Add to conftest.py:
```python
@pytest.fixture(autouse=True)
def clear_memory_store():
    """FR-6: reset the memory store before each test to ensure isolation"""
    from memory import _store
    _store.clear()
    yield
    _store.clear()

@pytest.fixture
def user_id_a():
    """FR-6: sample user_id for primary test user"""
    return 111111

@pytest.fixture
def user_id_b():
    """FR-6: sample user_id for secondary test user (isolation tests)"""
    return 222222

@pytest.fixture
def sample_messages():
    """FR-6: list of sample messages for populating history in tests"""
    return [
        {"role": "user", "content": f"Message {i}"}
        for i in range(25)
    ]
```

---

## Acceptance Criteria

- [ ] memory.py is created with no import errors
- [ ] _store is defined as a module-level dict[int, list[dict]]
- [ ] get_history(user_id) exists with exact signature
- [ ] get_history returns [] for unknown user_id
- [ ] get_history returns a copy, not a reference to internal list
- [ ] append_message(user_id, role, content) exists with exact signature
- [ ] append_message creates new list for unknown user_id
- [ ] append_message raises ValueError for invalid role
- [ ] ValueError message is exactly "role must be user or assistant"
- [ ] append_message enforces 20 message cap by dropping from front
- [ ] append_tool_messages(user_id, assistant_content, tool_results) exists with exact signature
- [ ] append_tool_messages appends exactly 2 messages
- [ ] First message role is "assistant" with assistant_content as content
- [ ] Second message role is "user" with tool_results as content
- [ ] append_tool_messages enforces 20 message cap after both are appended
- [ ] clear_history(user_id) exists with exact signature
- [ ] clear_history removes all messages for the given user_id
- [ ] clear_history on unknown user_id does nothing and does not raise
- [ ] clear_history does not affect other users' history
- [ ] get_history_length(user_id) exists with exact signature
- [ ] get_history_length returns 0 for unknown user_id
- [ ] get_history_length never returns more than 20
- [ ] Two different user_ids have fully independent histories
- [ ] autouse fixture in conftest.py clears _store before each test
- [ ] All tests in test_memory.py pass
- [ ] All previously passing FR-1 through FR-5 tests still pass (no regression)
- [ ] uv run ruff check . passes with no errors

---

## Manual test
After generating, verify with this script:
```python
from memory import (
    get_history, append_message, append_tool_messages,
    clear_history, get_history_length
)

# Test 1: new user returns empty history
print("Test 1:", get_history(999))  # []

# Test 2: append and retrieve
append_message(1, "user", "I want to visit Singapore")
append_message(1, "assistant", "Great! What is your budget?")
print("Test 2:", get_history(1))  # 2 messages

# Test 3: copy not reference
history = get_history(1)
history.append({"role": "user", "content": "injected"})
print("Test 3 length unchanged:", get_history_length(1))  # 2

# Test 4: 20 message cap
for i in range(25):
    append_message(2, "user", f"msg {i}")
print("Test 4 capped at 20:", get_history_length(2))  # 20
print("Test 4 oldest dropped:", get_history(2)[0]["content"])  # msg 5

# Test 5: clear history
clear_history(1)
print("Test 5 cleared:", get_history(1))  # []
print("Test 5 length:", get_history_length(1))  # 0

# Test 6: clear nonexistent user — no error
clear_history(9999)
print("Test 6: no error")

# Test 7: invalid role
try:
    append_message(1, "system", "hack")
except ValueError as e:
    print("Test 7 ValueError:", e)  # role must be user or assistant

# Test 8: isolation
append_message(10, "user", "user 10 message")
append_message(20, "user", "user 20 message")
print("Test 8 user 10:", get_history(10)[0]["content"])  # user 10 message
print("Test 8 user 20:", get_history(20)[0]["content"])  # user 20 message
clear_history(10)
print("Test 8 user 20 unaffected:", get_history_length(20))  # 1

# Test 9: append_tool_messages
from unittest.mock import MagicMock
assistant_blocks = [MagicMock(type="tool_use", id="t1", name="search_flights")]
tool_results = [{"type": "tool_result", "tool_use_id": "t1", "content": "[]"}]
append_tool_messages(3, assistant_blocks, tool_results)
print("Test 9 two messages added:", get_history_length(3))  # 2
print("Test 9 first role:", get_history(3)[0]["role"])   # assistant
print("Test 9 second role:", get_history(3)[1]["role"])  # user
```

Expected:
- Test 1: []
- Test 2: 2 messages with correct roles
- Test 3: length still 2 (copy confirmed)
- Test 4: capped at 20, oldest message is "msg 5"
- Test 5: empty list, length 0
- Test 6: no error raised
- Test 7: ValueError with correct message
- Test 8: independent histories, user 20 unaffected by clearing user 10
- Test 9: 2 messages, first is assistant, second is user

---

## When done
Print: ✅ FR-6 complete
Do not proceed to FR-7 until all acceptance criteria above are checked.