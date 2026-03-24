"""Tests for salebot/mcp_tools.py — FR-1: search_flights."""

import pytest
import respx
import httpx

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools import (
    TOOLS,
    TIMEOUT,
    execute_search_flights,
    execute_tool,
)


# ---------------------------------------------------------------------------
# Tool definition tests
# ---------------------------------------------------------------------------


class TestSearchFlightsToolDefinition:
    def _get_tool(self):
        return next(t for t in TOOLS if t["name"] == "search_flights")

    def test_no_import_errors(self):
        """FR-1: mcp_tools imports without errors."""
        import mcp_tools as _m  # noqa: F401
        assert _m is not None

    def test_search_flights_tool_valid_anthropic_format(self):
        """FR-1: search_flights_tool has name, description, and input_schema."""
        tool = self._get_tool()
        assert "name" in tool
        assert "description" in tool
        assert "input_schema" in tool
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema

    def test_search_flights_destination_is_required(self):
        """FR-1: destination is the only required field."""
        tool = self._get_tool()
        assert tool["input_schema"]["required"] == ["destination"]

    def test_search_flights_origin_optional(self):
        """FR-1: origin is optional (not in required list)."""
        tool = self._get_tool()
        assert "origin" in tool["input_schema"]["properties"]
        assert "origin" not in tool["input_schema"]["required"]

    def test_search_flights_class_type_optional(self):
        """FR-1: class_type is optional (not in required list)."""
        tool = self._get_tool()
        assert "class_type" in tool["input_schema"]["properties"]
        assert "class_type" not in tool["input_schema"]["required"]

    def test_tools_list_exists(self):
        """FR-1: TOOLS list exists and is a list."""
        assert isinstance(TOOLS, list)
        assert len(TOOLS) > 0

    def test_tools_list_contains_search_flights(self):
        """FR-1: TOOLS list contains search_flights tool."""
        names = [t["name"] for t in TOOLS]
        assert "search_flights" in names


# ---------------------------------------------------------------------------
# execute_search_flights tests
# ---------------------------------------------------------------------------


class TestExecuteSearchFlights:
    @pytest.mark.asyncio
    @respx.mock
    async def test_uses_10s_timeout(self, mock_flight_response):
        """FR-1: execute_search_flights uses httpx.AsyncClient with 10s timeout."""
        assert TIMEOUT == 10.0
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=mock_flight_response)
        )
        result = await execute_search_flights({"destination": "Singapore"})
        assert "Thai Airways" in result

    @pytest.mark.asyncio
    @respx.mock
    async def test_query_params_exclude_none_values(self):
        """FR-1: query params only include non-None values."""
        route = respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=[])
        )
        await execute_search_flights({"destination": "Singapore"})
        request = route.calls[0].request
        assert "origin" not in str(request.url)
        assert "class_type" not in str(request.url)
        assert "destination=Singapore" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_flights_filters_out_zero_seats(self, mock_flight_response):
        """FR-1: seats_available == 0 must be filtered out per spec."""
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=mock_flight_response)
        )
        result = await execute_search_flights({"destination": "Singapore"})
        import json
        flights = json.loads(result)
        for f in flights:
            assert f["seats_available"] > 0

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_flights_no_results_message(self):
        """FR-1: returns 'No flights found...' when no results after filtering."""
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await execute_search_flights({"destination": "Tokyo"})
        assert result == "No flights found matching the search criteria."

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_flights_all_zero_seats_gives_no_results_message(self, mock_flight_response):
        """FR-1: all results with seats_available==0 produce 'no results' message."""
        zero_seats = [dict(f, seats_available=0) for f in mock_flight_response]
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=zero_seats)
        )
        result = await execute_search_flights({"destination": "Singapore"})
        assert result == "No flights found matching the search criteria."

    @pytest.mark.asyncio
    async def test_search_flights_server_unreachable_message(self):
        """FR-1: returns graceful message when FastAPI is unreachable (no exception raised)."""
        result = await execute_search_flights({"destination": "Singapore"})
        assert result == "Flight search is currently unavailable. Please try again."

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_flights_with_all_params(self, mock_flight_response):
        """FR-1: origin and class_type are passed as query params when provided."""
        route = respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=[mock_flight_response[0]])
        )
        result = await execute_search_flights({
            "origin": "Bangkok",
            "destination": "Singapore",
            "class_type": "economy",
        })
        request = route.calls[0].request
        assert "origin=Bangkok" in str(request.url)
        assert "destination=Singapore" in str(request.url)
        assert "class_type=economy" in str(request.url)
        import json
        assert len(json.loads(result)) == 1


# ---------------------------------------------------------------------------
# execute_tool dispatcher tests
# ---------------------------------------------------------------------------


class TestExecuteTool:
    @pytest.mark.asyncio
    @respx.mock
    async def test_execute_tool_routes_search_flights(self, mock_flight_response):
        """FR-1: execute_tool dispatcher routes 'search_flights' correctly."""
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=[mock_flight_response[0]])
        )
        result = await execute_tool("search_flights", {"destination": "Singapore"})
        import json
        flights = json.loads(result)
        assert len(flights) == 1

    @pytest.mark.asyncio
    async def test_execute_tool_unknown_tool(self):
        """FR-1: execute_tool returns error message for unknown tool names."""
        result = await execute_tool("nonexistent_tool", {})
        assert "Unknown tool" in result
        assert "nonexistent_tool" in result
