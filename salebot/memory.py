from typing import Any

MAX_MESSAGES = 20

# In-memory store: user_id (int) → list of message dicts
_store: dict[int, list[dict[str, Any]]] = {}


def get_history(user_id: int) -> list[dict[str, Any]]:
    """Return the conversation history for a user."""
    return _store.get(user_id, [])


def append_message(user_id: int, message: dict[str, Any]) -> None:
    """Append a message to a user's history, capping at MAX_MESSAGES."""
    if user_id not in _store:
        _store[user_id] = []
    _store[user_id].append(message)
    # Keep only the most recent MAX_MESSAGES entries
    if len(_store[user_id]) > MAX_MESSAGES:
        _store[user_id] = _store[user_id][-MAX_MESSAGES:]


def clear_history(user_id: int) -> None:
    """Clear the conversation history for a user."""
    _store.pop(user_id, None)
