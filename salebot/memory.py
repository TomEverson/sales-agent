from typing import Any

MAX_MESSAGES = 20

# In-memory store: user_id (int) → list of message dicts
_store: dict[int, list[dict[str, Any]]] = {}

# Language preference store: user_id (int) → "en" | "my"
_language_prefs: dict[int, str] = {}


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
    """Clear the conversation history and language preference for a user."""
    _store.pop(user_id, None)
    _language_prefs.pop(user_id, None)


def get_history_length(user_id: int) -> int:
    """Return the number of stored messages for a user."""
    return len(_store.get(user_id, []))


def set_language(user_id: int, lang: str) -> None:
    """Set the language preference for a user. Must be 'en' or 'my'."""
    if lang not in ("en", "my"):
        raise ValueError("lang must be 'en' or 'my'")
    _language_prefs[user_id] = lang


def get_language(user_id: int) -> str | None:
    """Return 'en', 'my', or None if not yet set."""
    return _language_prefs.get(user_id)


def clear_language(user_id: int) -> None:
    """Remove the language preference for a user."""
    _language_prefs.pop(user_id, None)


_pending_payment: dict[int, dict[str, Any]] = {}


def set_pending_payment(user_id: int, booking_reference: str, amount: float) -> None:
    """Store pending payment info (booking_reference, amount) for a user."""
    _pending_payment[user_id] = {
        "booking_reference": booking_reference,
        "amount": amount,
    }


def get_pending_payment(user_id: int) -> dict[str, Any] | None:
    """Return pending payment info for a user, or None if not set."""
    return _pending_payment.get(user_id)


def clear_pending_payment(user_id: int) -> None:
    """Remove pending payment info for a user."""
    _pending_payment.pop(user_id, None)
