"""Tests for salebot/prompts/system_prompt.md — FR-8: System Prompt."""

import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "system_prompt.md"


# ---------------------------------------------------------------------------
# TestSystemPromptExists
# ---------------------------------------------------------------------------


class TestSystemPromptExists:
    def test_file_exists(self):
        """FR-8: system_prompt.md must exist at correct path per spec."""
        assert PROMPT_PATH.exists()

    def test_file_is_not_empty(self, system_prompt_content):
        """FR-8: system_prompt.md must not be empty per spec."""
        assert len(system_prompt_content.strip()) > 0

    def test_file_is_not_placeholder(self, system_prompt_content, placeholder_content):
        """FR-8: file must not contain only the FR-5 placeholder content per spec."""
        assert system_prompt_content.strip() != placeholder_content.strip()


# ---------------------------------------------------------------------------
# TestSystemPromptSections
# ---------------------------------------------------------------------------


class TestSystemPromptSections:
    def test_contains_identity_section(self, system_prompt_content):
        """FR-8: prompt contains identity and role definition per spec."""
        content = system_prompt_content.lower()
        assert "identity" in content or "role" in content

    def test_contains_travelbase_name(self, system_prompt_content):
        """FR-8: prompt references Travelbase as the platform name per spec."""
        assert "Travelbase" in system_prompt_content

    def test_contains_extraction_rules(self, system_prompt_content):
        """FR-8: prompt contains all 4 extraction rules per spec."""
        content = system_prompt_content.lower()
        assert "destination" in content
        assert "budget" in content
        assert "traveler" in content
        assert "date" in content

    def test_requires_destination(self, system_prompt_content):
        """FR-8: prompt instructs agent to ask for destination if missing per spec."""
        assert "destination" in system_prompt_content.lower()
        assert "Where would you like to travel" in system_prompt_content

    def test_requires_budget(self, system_prompt_content):
        """FR-8: prompt marks budget as required per spec."""
        assert "required" in system_prompt_content.lower() or \
               "never build a package without a budget" in system_prompt_content.lower()

    def test_defaults_travelers_to_one(self, system_prompt_content):
        """FR-8: prompt defaults number of travelers to 1 per spec."""
        assert "1 traveler" in system_prompt_content or "assume 1" in system_prompt_content

    def test_contains_search_strategy(self, system_prompt_content):
        """FR-8: prompt contains search order instructions per spec."""
        assert "search_flights" in system_prompt_content
        assert "search_hotels" in system_prompt_content
        assert "search_activities" in system_prompt_content

    def test_search_order_flights_first(self, system_prompt_content):
        """FR-8: search strategy lists flights as first search per spec."""
        flights_pos = system_prompt_content.find("search_flights")
        hotels_pos = system_prompt_content.find("search_hotels")
        assert flights_pos < hotels_pos

    def test_search_order_hotels_second(self, system_prompt_content):
        """FR-8: search strategy lists hotels as second search per spec."""
        hotels_pos = system_prompt_content.find("search_hotels")
        activities_pos = system_prompt_content.find("search_activities")
        assert hotels_pos < activities_pos

    def test_search_order_activities_third(self, system_prompt_content):
        """FR-8: search strategy lists activities as third search per spec."""
        activities_pos = system_prompt_content.find("search_activities")
        transport_pos = system_prompt_content.find("search_transport")
        assert activities_pos < transport_pos

    def test_contains_package_assembly_rules(self, system_prompt_content):
        """FR-8: prompt contains package assembly rules per spec."""
        content = system_prompt_content.lower()
        assert "assembly" in content or "package" in content

    def test_minimum_one_activity_rule(self, system_prompt_content):
        """FR-8: prompt states minimum 1 activity required per spec."""
        assert "1 activity" in system_prompt_content or \
               "at least 1 activity" in system_prompt_content or \
               "minimum" in system_prompt_content.lower()

    def test_contains_seats_available_rule(self, system_prompt_content):
        """FR-8: prompt instructs agent to filter seats_available == 0 per spec."""
        assert "seats_available == 0" in system_prompt_content

    def test_contains_rooms_available_rule(self, system_prompt_content):
        """FR-8: prompt instructs agent to filter rooms_available == 0 per spec."""
        assert "rooms_available == 0" in system_prompt_content

    def test_contains_refinement_rules(self, system_prompt_content):
        """FR-8: prompt contains tweak and refinement handling per spec."""
        content = system_prompt_content.lower()
        assert "tweak" in content or "refine" in content or "refinement" in content

    def test_contains_tweak_invitation_rule(self, system_prompt_content):
        """FR-8: prompt instructs agent to always end with tweak invitation per spec."""
        content = system_prompt_content.lower()
        assert "tweak invitation" in content or \
               ("always" in content and "tweak" in content)

    def test_contains_hard_rules_section(self, system_prompt_content):
        """FR-8: prompt contains hard NEVER/ALWAYS rules per spec."""
        assert "NEVER" in system_prompt_content
        assert "ALWAYS" in system_prompt_content

    def test_never_invent_prices_rule(self, system_prompt_content):
        """FR-8: prompt contains rule to never invent prices per spec."""
        content = system_prompt_content.lower()
        assert "invent" in content and "price" in content

    def test_contains_tone_guide(self, system_prompt_content):
        """FR-8: prompt contains tone and style guidance per spec."""
        content = system_prompt_content.lower()
        assert "tone" in content or "style" in content

    def test_no_certainly_phrase(self, system_prompt_content):
        """FR-8: prompt explicitly bans Certainly! per spec."""
        assert "Certainly!" in system_prompt_content

    def test_default_origin_is_bangkok(self, system_prompt_content):
        """FR-8: prompt sets Bangkok as default origin city per spec."""
        assert "Bangkok" in system_prompt_content


# ---------------------------------------------------------------------------
# TestSystemPromptLoadedByAgent
# ---------------------------------------------------------------------------


class TestSystemPromptLoadedByAgent:
    def setup_method(self):
        import agent
        agent._system_prompt = None

    def teardown_method(self):
        import agent
        agent._system_prompt = None

    def test_agent_loads_system_prompt(self):
        """FR-8: load_system_prompt() in agent.py returns full prompt not placeholder."""
        import agent
        prompt = agent.load_system_prompt()
        assert "Travelbase" in prompt
        assert "Bangkok" in prompt
        assert "NEVER" in prompt

    def test_prompt_length_is_substantial(self):
        """FR-8: loaded prompt must be at least 1000 characters per spec."""
        import agent
        prompt = agent.load_system_prompt()
        assert len(prompt) >= 1000
