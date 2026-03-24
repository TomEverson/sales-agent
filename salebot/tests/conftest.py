import pytest


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
