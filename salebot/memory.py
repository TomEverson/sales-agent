"""In-memory bot memory with JSON file persistence.

Data is loaded from JSON on startup and written back after every mutation.
Files:
  - data/conversations.json  — user conversation histories
  - data/preferences.json    — language prefs + pending payments
"""

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MAX_MESSAGES = 20

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_BASE_DIR = Path(__file__).parent
_CONV_FILE = _BASE_DIR / "data" / "conversations.json"
_PREFS_FILE = _BASE_DIR / "data" / "preferences.json"


def _ensure_data_dir() -> None:
    (_BASE_DIR / "data").mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# In-memory state
# ---------------------------------------------------------------------------

# user_id (int) → list of message dicts
_store: dict[int, list[dict[str, Any]]] = {}

# user_id (int) → "en" | "my"
_language_prefs: dict[int, str] = {}

# user_id (int) → {"booking_reference": str, "amount": float}
_pending_payment: dict[int, dict[str, Any]] = {}


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------


def _load_json(path: Path) -> dict:
    if path.exists():
        try:
            with open(path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning("Failed to load %s: %s", path, e)
    return {}


def _save_json(path: Path, data: dict) -> None:
    try:
        _ensure_data_dir()
        with open(path, "w") as f:
            json.dump(data, f, indent=2, default=str)
    except IOError as e:
        logger.error("Failed to save %s: %s", path, e)


def _load() -> None:
    """Load all persisted data from JSON files into memory."""
    global _store, _language_prefs, _pending_payment

    conv_data: dict = _load_json(_CONV_FILE)
    # JSON keys are strings; convert to int
    _store = {int(k): v for k, v in conv_data.items()}

    prefs_data: dict = _load_json(_PREFS_FILE)
    _language_prefs = {int(k): v for k, v in prefs_data.get("lang", {}).items()}
    _pending_payment = {
        int(k): v for k, v in prefs_data.get("pending_payment", {}).items()
    }


def _persist_conversations() -> None:
    """Persist conversation histories to disk."""
    _save_json(_CONV_FILE, {str(k): v for k, v in _store.items()})


def _persist_preferences() -> None:
    """Persist language prefs and pending payments to disk."""
    _save_json(
        _PREFS_FILE,
        {
            "lang": {str(k): v for k, v in _language_prefs.items()},
            "pending_payment": {str(k): v for k, v in _pending_payment.items()},
        },
    )


# ---------------------------------------------------------------------------
# Load persisted data on module import
# ---------------------------------------------------------------------------

_load()


# ---------------------------------------------------------------------------
# Conversation history
# ---------------------------------------------------------------------------


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
    _persist_conversations()


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
    _persist_conversations()


def clear_history(user_id: int) -> None:
    """Clear the conversation history and language preference for a user."""
    _store.pop(user_id, None)
    _language_prefs.pop(user_id, None)
    _pending_payment.pop(user_id, None)
    _persist_conversations()
    _persist_preferences()


def get_history_length(user_id: int) -> int:
    """Return the number of stored messages for a user."""
    return len(_store.get(user_id, []))


# ---------------------------------------------------------------------------
# Language preferences
# ---------------------------------------------------------------------------


def set_language(user_id: int, lang: str) -> None:
    """Set the language preference for a user. Must be 'en' or 'my'."""
    if lang not in ("en", "my"):
        raise ValueError("lang must be 'en' or 'my'")
    _language_prefs[user_id] = lang
    _persist_preferences()


def get_language(user_id: int) -> str | None:
    """Return 'en', 'my', or None if not yet set."""
    return _language_prefs.get(user_id)


def clear_language(user_id: int) -> None:
    """Remove the language preference for a user."""
    _language_prefs.pop(user_id, None)
    _persist_preferences()


# ---------------------------------------------------------------------------
# Pending payments
# ---------------------------------------------------------------------------


def set_pending_payment(user_id: int, booking_reference: str, amount: float) -> None:
    """Store pending payment info (booking_reference, amount) for a user."""
    _pending_payment[user_id] = {
        "booking_reference": booking_reference,
        "amount": amount,
    }
    _persist_preferences()


def get_pending_payment(user_id: int) -> dict[str, Any] | None:
    """Return pending payment info for a user, or None if not set."""
    return _pending_payment.get(user_id)


def clear_pending_payment(user_id: int) -> None:
    """Remove pending payment info for a user."""
    _pending_payment.pop(user_id, None)
    _persist_preferences()
