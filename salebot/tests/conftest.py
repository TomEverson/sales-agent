import pytest
from unittest.mock import MagicMock

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(autouse=True)
def clear_memory_store():
    """FR-6: reset the memory store before each test to ensure isolation."""
    from memory import _store

    _store.clear()
    yield
    _store.clear()


@pytest.fixture
def user_id_a():
    """FR-6: sample user_id for primary test user."""
    return 111111


@pytest.fixture
def user_id_b():
    """FR-6: sample user_id for secondary test user (isolation tests)."""
    return 222222


@pytest.fixture
def sample_messages():
    """FR-6: list of sample messages for populating history in tests."""
    return [{"role": "user", "content": f"Message {i}"} for i in range(25)]


@pytest.fixture
def mock_end_turn_response():
    """FR-5: simulates Claude API response with stop_reason end_turn."""
    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [MagicMock(type="text", text="Here is your tour package!")]
    return response


@pytest.fixture
def mock_tool_use_response():
    """FR-5: simulates Claude API response with stop_reason tool_use."""
    response = MagicMock()
    response.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "tool_123"
    tool_block.name = "search_flights"
    tool_block.input = {"destination": "Singapore"}
    response.content = [tool_block]
    return response


@pytest.fixture
def sample_history():
    """FR-5: sample conversation history in Anthropic message format."""
    return [
        {"role": "user", "content": "I want to visit Singapore"},
        {"role": "assistant", "content": "Great choice! What is your budget?"},
    ]


@pytest.fixture
def system_prompt_content():
    """FR-8: loads the full system prompt from file for content tests."""
    from pathlib import Path

    prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.md"
    if prompt_path.exists():
        return prompt_path.read_text()
    return ""


@pytest.fixture
def placeholder_content():
    """FR-8: the FR-5 placeholder text to check against."""
    return (
        "You are Travelbase Assistant, a friendly travel sales agent.\n"
        "Help users find flights, hotels, activities, and transport for their trips.\n"
        "Use the available tools to search real inventory.\n"
        "Never invent prices or availability."
    )


@pytest.fixture
def mock_hotel_response():
    """FR-2: shared sample hotel data for tests."""
    return [
        {
            "id": 1,
            "name": "The Singapore Suites",
            "city": "Singapore",
            "stars": 4,
            "price_per_night": 120.0,
            "amenities": "pool,wifi,gym",
            "rooms_available": 5,
        },
        {
            "id": 2,
            "name": "Budget Inn Singapore",
            "city": "Singapore",
            "stars": 2,
            "price_per_night": 40.0,
            "amenities": "wifi",
            "rooms_available": 0,  # ← should be filtered out
        },
    ]


@pytest.fixture
def mock_activity_response():
    """FR-3: shared sample activity data for tests."""
    return [
        {
            "id": 1,
            "name": "Gardens by the Bay Tour",
            "city": "Singapore",
            "category": "nature",
            "duration_hours": 3.0,
            "price": 25.0,
            "availability": "daily",
        },
        {
            "id": 2,
            "name": "Singapore Food Walk",
            "city": "Singapore",
            "category": "food",
            "duration_hours": 2.0,
            "price": 35.0,
            "availability": "weekends",
        },
        {
            "id": 3,
            "name": "Night Safari",
            "city": "Singapore",
            "category": "adventure",
            "duration_hours": 4.0,
            "price": 55.0,
            "availability": "daily",
        },
    ]


@pytest.fixture
def mock_update():
    """FR-9: mock Telegram Update object for handler tests."""
    from unittest.mock import AsyncMock

    update = MagicMock()
    update.effective_user.id = 12345
    update.effective_chat.id = 12345
    update.message.text = "I want to visit Singapore, budget $1000"
    update.message.reply_text = AsyncMock()
    update.effective_message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """FR-9: mock Telegram CallbackContext for handler tests."""
    from unittest.mock import AsyncMock

    context = MagicMock()
    context.bot.send_chat_action = AsyncMock()
    context.bot.send_message = AsyncMock()
    context.error = Exception("test error")
    return context


@pytest.fixture
def mock_env(monkeypatch):
    """FR-9: set required environment variables for bot tests."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token_123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_key_456")


@pytest.fixture
def mock_fastapi(respx_mock):
    """FR-10: mocks all 4 FastAPI endpoints with realistic SEA travel data."""
    import httpx

    respx_mock.get("http://localhost:8000/flights").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "origin": "Bangkok",
                    "destination": "Singapore",
                    "airline": "AirAsia",
                    "departure_time": "2026-03-28T08:00:00",
                    "arrival_time": "2026-03-28T09:30:00",
                    "price": 85.0,
                    "seats_available": 50,
                    "class_type": "economy",
                }
            ],
        )
    )
    respx_mock.get("http://localhost:8000/hotels").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "The Singapore Suites",
                    "city": "Singapore",
                    "stars": 4,
                    "price_per_night": 120.0,
                    "amenities": "pool,wifi,gym",
                    "rooms_available": 5,
                }
            ],
        )
    )
    respx_mock.get("http://localhost:8000/activities").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "Gardens by the Bay Tour",
                    "city": "Singapore",
                    "category": "nature",
                    "duration_hours": 3.0,
                    "price": 25.0,
                    "availability": "daily",
                },
                {
                    "id": 2,
                    "name": "Singapore Food Walk",
                    "city": "Singapore",
                    "category": "food",
                    "duration_hours": 2.0,
                    "price": 35.0,
                    "availability": "daily",
                },
            ],
        )
    )
    respx_mock.get("http://localhost:8000/transport").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "type": "car",
                    "origin": "Singapore Airport",
                    "destination": "Singapore City",
                    "departure_time": "2026-03-28T10:00:00",
                    "arrival_time": "2026-03-28T10:45:00",
                    "price": 30.0,
                    "capacity": 4,
                }
            ],
        )
    )
    return respx_mock


@pytest.fixture
def mock_fastapi_down(respx_mock):
    """FR-10: mocks all FastAPI endpoints as unreachable."""
    import httpx

    respx_mock.get("http://localhost:8000/flights").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    respx_mock.get("http://localhost:8000/hotels").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    respx_mock.get("http://localhost:8000/activities").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    respx_mock.get("http://localhost:8000/transport").mock(
        side_effect=httpx.ConnectError("Connection refused")
    )
    return respx_mock


@pytest.fixture
def mock_claude(mocker):
    """FR-10: mocks Anthropic Claude API — tool_use (3 tools) then end_turn."""
    from unittest.mock import AsyncMock

    def _tool_block(id_, name, input_):
        b = MagicMock()
        b.type = "tool_use"
        b.id = id_
        b.name = name
        b.input = input_
        return b

    tool_response = MagicMock()
    tool_response.stop_reason = "tool_use"
    tool_response.content = [
        _tool_block("t1", "search_flights", {"destination": "Singapore"}),
        _tool_block("t2", "search_hotels", {"city": "Singapore"}),
        _tool_block("t3", "search_activities", {"city": "Singapore"}),
    ]

    final_response = MagicMock()
    final_response.stop_reason = "end_turn"
    final_response.content = [
        MagicMock(
            type="text",
            text=(
                "Here is your Singapore package!\n\n"
                "✈️ Flight: Bangkok → Singapore | AirAsia | $85.00\n"
                "🏨 Hotel: The Singapore Suites ⭐⭐⭐⭐ | $120.00/night\n"
                "🎯 Activities: Gardens by the Bay Tour | $25.00\n"
                "💰 Total: $350.00 (Budget remaining: $650.00)\n\n"
                "Would you like to adjust anything?"
            ),
        )
    ]

    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(side_effect=[tool_response, final_response])
    mocker.patch("agent._get_client", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_transport_response():
    """FR-4: shared sample transport data for tests."""
    return [
        {
            "id": 1,
            "type": "car",
            "origin": "Singapore Airport",
            "destination": "Singapore City",
            "departure_time": "2026-03-28T08:00:00",
            "arrival_time": "2026-03-28T08:45:00",
            "price": 30.0,
            "capacity": 4,
        },
        {
            "id": 2,
            "type": "bus",
            "origin": "Singapore Airport",
            "destination": "Singapore City",
            "departure_time": "2026-03-28T09:00:00",
            "arrival_time": "2026-03-28T10:00:00",
            "price": 5.0,
            "capacity": 40,
        },
        {
            "id": 3,
            "type": "ferry",
            "origin": "Singapore",
            "destination": "Batam",
            "departure_time": "2026-03-28T10:00:00",
            "arrival_time": "2026-03-28T11:00:00",
            "price": 25.0,
            "capacity": 60,
        },
    ]


@pytest.fixture
def sample_flight():
    """FR-7: sample PackageFlight for formatting tests."""
    from package_builder import PackageFlight

    return PackageFlight(
        origin="Bangkok",
        destination="Singapore",
        airline="AirAsia",
        class_type="economy",
        departure_time="Sat 08:00",
        arrival_time="Sat 09:30",
        price=85.0,
    )


@pytest.fixture
def sample_hotel():
    """FR-7: sample PackageHotel for formatting tests."""
    from package_builder import PackageHotel

    return PackageHotel(
        name="The Singapore Suites",
        stars=4,
        price_per_night=120.0,
        nights=2,
    )


@pytest.fixture
def sample_activities():
    """FR-7: sample list of PackageActivity for formatting tests."""
    from package_builder import PackageActivity

    return [
        PackageActivity(name="Gardens by the Bay Tour", price=25.0, duration_hours=3.0),
        PackageActivity(name="Singapore Food Walk", price=35.0, duration_hours=2.0),
    ]


@pytest.fixture
def sample_transport():
    """FR-7: sample PackageTransport for formatting tests."""
    from package_builder import PackageTransport

    return PackageTransport(
        origin="Singapore Airport",
        destination="Singapore City",
        type="car",
        price=30.0,
    )


@pytest.fixture
def sample_package_with_transport(
    sample_flight, sample_hotel, sample_activities, sample_transport
):
    """FR-7: complete TourPackage with transport for formatting tests."""
    from package_builder import TourPackage

    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=sample_transport,
    )


@pytest.fixture
def sample_package_no_transport(sample_flight, sample_hotel, sample_activities):
    """FR-7: complete TourPackage without transport for formatting tests."""
    from package_builder import TourPackage

    return TourPackage(
        flight=sample_flight,
        hotel=sample_hotel,
        activities=sample_activities,
        budget=1000.0,
        transport=None,
    )


@pytest.fixture
def mock_flight_response():
    """Shared sample flight data for FR-1 tests."""
    return [
        {
            "id": 1,
            "airline": "Thai Airways",
            "origin": "Bangkok",
            "destination": "Singapore",
            "departure_time": "2026-04-01T08:00:00",
            "arrival_time": "2026-04-01T11:30:00",
            "price": 250.0,
            "seats_available": 5,
            "class_type": "economy",
        },
        {
            "id": 2,
            "airline": "Singapore Air",
            "origin": "Bangkok",
            "destination": "Singapore",
            "departure_time": "2026-04-01T14:00:00",
            "arrival_time": "2026-04-01T17:30:00",
            "price": 180.0,
            "seats_available": 0,
            "class_type": "economy",
        },
    ]


@pytest.fixture
def mock_booking_response():
    """TB-23: sample FlightBooking response from server."""
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
def mock_hotel_booking_response():
    """TB-23: sample HotelBooking response from server."""
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


@pytest.fixture
def mock_activity_booking_response():
    """TB-23: sample ActivityBooking response from server."""
    return {
        "id": 1,
        "activity_id": 1,
        "participant_name": "John Smith",
        "contact_email": "john@example.com",
        "activity_date": "2026-03-29",
        "participants": 1,
        "booking_reference": "TB-20260328-C5T1",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00",
    }


@pytest.fixture
def mock_transport_booking_response():
    """TB-23: sample TransportBooking response from server."""
    return {
        "id": 1,
        "transport_id": 1,
        "passenger_name": "John Smith",
        "contact_email": "john@example.com",
        "passengers": 1,
        "booking_reference": "TB-20260328-D7R3",
        "status": "confirmed",
        "created_at": "2026-03-28T10:00:00",
    }
