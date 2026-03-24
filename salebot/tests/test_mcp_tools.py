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
    execute_search_hotels,
    execute_search_activities,
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


# ---------------------------------------------------------------------------
# TestExecuteSearchHotels — FR-2
# ---------------------------------------------------------------------------


class TestExecuteSearchHotels:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_hotels_for_valid_city(self, mock_hotel_response):
        """FR-2: valid city returns list of hotels from FastAPI."""
        respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=mock_hotel_response)
        )
        result = await execute_search_hotels({"city": "Singapore"})
        import json
        hotels = json.loads(result)
        assert len(hotels) == 1
        assert hotels[0]["name"] == "The Singapore Suites"

    @pytest.mark.asyncio
    @respx.mock
    async def test_filters_out_zero_rooms(self, mock_hotel_response):
        """FR-2: hotels with rooms_available == 0 must be excluded per spec."""
        respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=mock_hotel_response)
        )
        result = await execute_search_hotels({"city": "Singapore"})
        import json
        hotels = json.loads(result)
        for h in hotels:
            assert h["rooms_available"] > 0

    @pytest.mark.asyncio
    async def test_city_is_required(self):
        """FR-2: missing city returns clear error message per spec."""
        result = await execute_search_hotels({})
        assert result == "City is required to search for hotels."

    @pytest.mark.asyncio
    @respx.mock
    async def test_optional_stars_sent_as_param(self, mock_hotel_response):
        """FR-2: stars param is included in query only when provided."""
        route = respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=mock_hotel_response)
        )
        await execute_search_hotels({"city": "Singapore", "stars": 4})
        request = route.calls[0].request
        assert "stars=4" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_optional_max_price_sent_as_param(self, mock_hotel_response):
        """FR-2: max_price param is included in query only when provided."""
        route = respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=mock_hotel_response)
        )
        await execute_search_hotels({"city": "Singapore", "max_price": 150.0})
        request = route.calls[0].request
        assert "max_price=150" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_none_params_not_sent(self):
        """FR-2: None values must not be sent as query params per spec."""
        route = respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=[])
        )
        await execute_search_hotels({"city": "Singapore"})
        request = route.calls[0].request
        assert "stars" not in str(request.url)
        assert "max_price" not in str(request.url)
        assert "city=Singapore" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_results_returns_message(self):
        """FR-2: empty list from API returns no hotels found message per spec."""
        respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await execute_search_hotels({"city": "Tokyo"})
        assert result == "No hotels found in Tokyo matching the search criteria."

    @pytest.mark.asyncio
    async def test_server_unreachable_returns_message(self):
        """FR-2: connection error returns unavailable message per spec."""
        result = await execute_search_hotels({"city": "Singapore"})
        assert result == "Hotel search is currently unavailable. Please try again."

    @pytest.mark.asyncio
    @respx.mock
    async def test_error_message_includes_city_name(self):
        """FR-2: no results message must include the searched city name."""
        respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await execute_search_hotels({"city": "Nairobi"})
        assert "Nairobi" in result


# ---------------------------------------------------------------------------
# TestExecuteSearchActivities — FR-3
# ---------------------------------------------------------------------------


class TestExecuteSearchActivities:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_activities_for_valid_city(self, mock_activity_response):
        """FR-3: valid city returns list of activities from FastAPI."""
        respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=mock_activity_response)
        )
        result = await execute_search_activities({"city": "Singapore"})
        import json
        activities = json.loads(result)
        assert len(activities) == 3

    @pytest.mark.asyncio
    async def test_city_is_required(self):
        """FR-3: missing city returns clear error message per spec."""
        result = await execute_search_activities({})
        assert result == "City is required to search for activities."

    @pytest.mark.asyncio
    @respx.mock
    async def test_optional_category_sent_as_param(self, mock_activity_response):
        """FR-3: category param is included in query only when provided."""
        route = respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=mock_activity_response)
        )
        await execute_search_activities({"city": "Singapore", "category": "food"})
        request = route.calls[0].request
        assert "category=food" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_none_params_not_sent(self):
        """FR-3: None values must not be sent as query params per spec."""
        route = respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=[])
        )
        await execute_search_activities({"city": "Singapore"})
        request = route.calls[0].request
        assert "category" not in str(request.url)
        assert "city=Singapore" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_results_returns_message(self):
        """FR-3: empty list from API returns no activities found message per spec."""
        respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await execute_search_activities({"city": "Tokyo"})
        assert result == "No activities found in Tokyo matching the search criteria."

    @pytest.mark.asyncio
    @respx.mock
    async def test_error_message_includes_city_name(self):
        """FR-3: no results message must include the searched city name."""
        respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=[])
        )
        result = await execute_search_activities({"city": "Nairobi"})
        assert "Nairobi" in result

    @pytest.mark.asyncio
    async def test_server_unreachable_returns_message(self):
        """FR-3: connection error returns unavailable message per spec."""
        result = await execute_search_activities({"city": "Singapore"})
        assert result == "Activity search is currently unavailable. Please try again."

    @pytest.mark.asyncio
    @respx.mock
    async def test_all_results_returned_regardless_of_availability(self, mock_activity_response):
        """FR-3: availability field must not be used to filter results per spec."""
        respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=mock_activity_response)
        )
        result = await execute_search_activities({"city": "Singapore"})
        import json
        activities = json.loads(result)
        # All 3 returned including the "weekends" one
        assert len(activities) == 3

    @pytest.mark.asyncio
    @respx.mock
    async def test_category_filter_adventure(self, mock_activity_response):
        """FR-3: category adventure is passed correctly as query param."""
        route = respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=[mock_activity_response[2]])
        )
        await execute_search_activities({"city": "Singapore", "category": "adventure"})
        request = route.calls[0].request
        assert "category=adventure" in str(request.url)

    @pytest.mark.asyncio
    @respx.mock
    async def test_category_filter_food(self, mock_activity_response):
        """FR-3: category food is passed correctly as query param."""
        route = respx.get("http://localhost:8000/activities").mock(
            return_value=httpx.Response(200, json=[mock_activity_response[1]])
        )
        await execute_search_activities({"city": "Singapore", "category": "food"})
        request = route.calls[0].request
        assert "category=food" in str(request.url)
