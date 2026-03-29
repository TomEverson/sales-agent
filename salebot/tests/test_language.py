"""TB-25: Burmese language support tests."""

import pytest

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestLanguagePreference:
    def test_set_and_get_language(self):
        """TB-25: set_language stores preference, get_language returns it."""
        from memory import set_language, get_language, clear_language

        user_id = 99999
        clear_language(user_id)

        set_language(user_id, "en")
        assert get_language(user_id) == "en"

        set_language(user_id, "my")
        assert get_language(user_id) == "my"

        clear_language(user_id)

    def test_set_invalid_language_raises(self):
        """TB-25: set_language rejects anything other than en/my."""
        from memory import set_language, clear_language

        user_id = 99998
        clear_language(user_id)

        with pytest.raises(ValueError, match="lang must be 'en' or 'my'"):
            set_language(user_id, "fr")

        clear_language(user_id)

    def test_get_language_returns_none_when_not_set(self):
        """TB-25: get_language returns None for unknown user."""
        from memory import get_language, clear_language

        user_id = 99997
        clear_language(user_id)

        assert get_language(user_id) is None

        clear_language(user_id)

    def test_clear_history_also_clears_language(self):
        """TB-25: clear_history resets language preference."""
        from memory import (
            set_language,
            get_language,
            clear_history,
            clear_language,
        )

        user_id = 99996
        set_language(user_id, "my")
        assert get_language(user_id) == "my"

        clear_history(user_id)
        assert get_language(user_id) is None

        clear_language(user_id)


class TestPromptSelection:
    def test_load_english_prompt(self):
        """TB-25: load_system_prompt('en') loads English prompt."""
        from agent import load_system_prompt

        prompt = load_system_prompt("en")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "Travelbase Assistant" in prompt

    def test_load_burmese_prompt(self):
        """TB-25: load_system_prompt('my') loads Burmese prompt."""
        from agent import load_system_prompt

        prompt = load_system_prompt("my")
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_caches_prompts(self):
        """TB-25: prompts are cached after first load."""
        from agent import load_system_prompt

        prompt_en_1 = load_system_prompt("en")
        prompt_en_2 = load_system_prompt("en")
        assert prompt_en_1 is prompt_en_2

        prompt_my_1 = load_system_prompt("my")
        prompt_my_2 = load_system_prompt("my")
        assert prompt_my_1 is prompt_my_2

    def test_burmese_prompt_contains_burmese_text(self):
        """TB-25: Burmese prompt file contains actual Burmese characters."""
        from agent import load_system_prompt

        prompt = load_system_prompt("my")
        has_burmese = any("\u1000" <= c <= "\u109f" for c in prompt)
        assert has_burmese, "Burmese prompt should contain Burmese Unicode characters"


class TestAutoDetect:
    def test_burmese_text_detected(self):
        """TB-25: text with Burmese Unicode chars triggers my detection."""
        from bot import _detect_language

        result = _detect_language("မင်္ဂလာပါ")
        assert result == "my"

    def test_english_text_detected(self):
        """TB-25: ASCII-only text triggers en detection."""
        from bot import _detect_language

        result = _detect_language("Hello, I want to visit Singapore")
        assert result == "en"

    def test_mixed_text_defaults_to_burmese(self):
        """TB-25: text containing any Burmese chars detected as my."""
        from bot import _detect_language

        result = _detect_language("Hello မင်္ဂလာပါ")
        assert result == "my"
