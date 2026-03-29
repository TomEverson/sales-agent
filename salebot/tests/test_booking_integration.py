"""TB-24: Bot E2E booking integration tests."""

import pytest
import respx
import httpx

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tools import execute_tool


@pytest.fixture
def mock_flight_search_response():
    return [
        {
            "id": 1,
            "origin": "Bangkok",
            "destination": "Singapore",
            "airline": "AirAsia",
            "departure_time": "2026-03-28T08:00:00",
            "arrival_time": "2026-03-28T09:30:00",
            "price": 85.0,
            "seats_available": 10,
            "class_type": "economy",
        }
    ]


@pytest.fixture
def mock_booking_response():
    return {
        "id": 1,
        "flight_id": 1,
        "passenger_name": "John Smith",
        "contact_email": "john@example.com",
        "booking_reference": "TB-20260328-A3F7",
        "status": "confirmed",
        "seats_booked": 1,
        "created_at": "2026-03-28T10:00:00",
    }


@pytest.fixture
def mock_hotel_search_response():
    return [
        {
            "id": 1,
            "name": "The Singapore Suites",
            "city": "Singapore",
            "stars": 4,
            "price_per_night": 120.0,
            "rooms_available": 5,
            "amenities": "pool,wifi,gym",
        }
    ]


@pytest.fixture
def mock_hotel_booking_response():
    return {
        "id": 1,
        "hotel_id": 1,
        "guest_name": "John Smith",
        "contact_email": "john@example.com",
        "check_in_date": "2026-03-28",
        "check_out_date": "2026-03-30",
        "nights": 2,
        "guests": 1,
        "booking_reference": "TB-20260328-B2K9",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00",
    }


class TestFullBookingFlow:
    @pytest.mark.asyncio
    @respx.mock
    async def test_search_then_book_flight_flow(
        self, mock_flight_search_response, mock_booking_response
    ):
        """TB-24: full flow from search to booking confirmation."""
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=mock_flight_search_response)
        )
        respx.post("http://localhost:8000/bookings/flights").mock(
            return_value=httpx.Response(201, json=mock_booking_response)
        )

        search_result = await execute_tool(
            "search_flights", {"destination": "Singapore"}
        )
        assert "Singapore" in search_result

        book_result = await execute_tool(
            "book_flight",
            {
                "flight_id": 1,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert "Booking confirmed" in book_result
        assert "TB-20260328-A3F7" in book_result

    @pytest.mark.asyncio
    @respx.mock
    async def test_search_then_book_hotel_flow(
        self, mock_hotel_search_response, mock_hotel_booking_response
    ):
        """TB-24: full hotel search → book → confirm."""
        respx.get("http://localhost:8000/hotels").mock(
            return_value=httpx.Response(200, json=mock_hotel_search_response)
        )
        respx.post("http://localhost:8000/bookings/hotels").mock(
            return_value=httpx.Response(201, json=mock_hotel_booking_response)
        )

        search_result = await execute_tool("search_hotels", {"city": "Singapore"})
        assert "Singapore" in search_result

        book_result = await execute_tool(
            "book_hotel",
            {
                "hotel_id": 1,
                "guest_name": "John Smith",
                "contact_email": "john@example.com",
                "check_in_date": "2026-03-28",
                "check_out_date": "2026-03-30",
                "nights": 2,
            },
        )
        assert "Hotel booking confirmed" in book_result

    @pytest.mark.asyncio
    @respx.mock
    async def test_handles_booking_failure_gracefully(
        self, mock_flight_search_response
    ):
        """TB-24: handles 422 seat unavailable gracefully."""
        respx.get("http://localhost:8000/flights").mock(
            return_value=httpx.Response(200, json=mock_flight_search_response)
        )
        respx.post("http://localhost:8000/bookings/flights").mock(
            return_value=httpx.Response(422, json={"detail": "Not enough seats"})
        )

        book_result = await execute_tool(
            "book_flight",
            {
                "flight_id": 1,
                "passenger_name": "John Smith",
                "contact_email": "john@example.com",
            },
        )
        assert "not enough" in book_result.lower() or "no longer" in book_result.lower()
