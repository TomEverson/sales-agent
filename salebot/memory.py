from typing import Any

MAX_MESSAGES = 20

# In-memory store: user_id (int) → list of message dicts
_store: dict[int, list[dict[str, Any]]] = {}


def _enforce_cap(user_id: int) -> None:
    history = _store[user_id]
    if len(history) > MAX_MESSAGES:
        _store[user_id] = history[-MAX_MESSAGES:]


def get_history(user_id: int) -> list[dict[str, Any]]:
    """Return a copy of the conversation history for a user."""
    return list(_store.get(user_id, []))


def append_message(user_id: int, role: str, content: str) -> None:
    """Append a single text message to a user's history, capping at MAX_MESSAGES."""
    if role not in ("user", "assistant"):
        raise ValueError("role must be user or assistant")
    if user_id not in _store:
        _store[user_id] = []
    _store[user_id].append({"role": role, "content": content})
    _enforce_cap(user_id)


def append_tool_messages(
    user_id: int,
    assistant_content: list,
    tool_results: list,
) -> None:
    """Append assistant tool-use blocks and their results to a user's history."""
    if user_id not in _store:
        _store[user_id] = []
    _store[user_id].append({"role": "assistant", "content": assistant_content})
    _store[user_id].append({"role": "user", "content": tool_results})
    _enforce_cap(user_id)


def clear_history(user_id: int) -> None:
    """Clear the conversation history for a user."""
    _store.pop(user_id, None)


def get_history_length(user_id: int) -> int:
    """Return the number of stored messages for a user."""
    return len(_store.get(user_id, []))
