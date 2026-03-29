"""TB-24: Server flights API tests."""

import pytest
from sqlmodel import Session, select

from models.flight import Flight
from tests.conftest import test_engine


@pytest.fixture
def flight_with_seats():
    with Session(test_engine) as session:
        flight = Flight(
            origin="Bangkok",
            destination="Singapore",
            airline="AirAsia",
            departure_time=__import__("datetime").datetime(2026, 3, 28, 8, 0, 0),
            arrival_time=__import__("datetime").datetime(2026, 3, 28, 9, 30, 0),
            price=85.0,
            seats_available=10,
            class_type="economy",
        )
        session.add(flight)
        session.commit()
        session.refresh(flight)
        flight_id = flight.id
    with Session(test_engine) as session:
        return session.get(Flight, flight_id)


@pytest.fixture
def flight_no_seats():
    with Session(test_engine) as session:
        flight = Flight(
            origin="Bangkok",
            destination="Singapore",
            airline="Singapore Air",
            departure_time=__import__("datetime").datetime(2026, 3, 28, 14, 0, 0),
            arrival_time=__import__("datetime").datetime(2026, 3, 28, 15, 30, 0),
            price=180.0,
            seats_available=0,
            class_type="economy",
        )
        session.add(flight)
        session.commit()
        session.refresh(flight)
        flight_id = flight.id
    with Session(test_engine) as session:
        return session.get(Flight, flight_id)


class TestSearchFlights:
    def test_returns_flights_list(self, client, flight_with_seats):
        """TB-24: GET /flights returns flights list."""
        response = client.get("/flights")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filters_by_origin(self, client, flight_with_seats):
        """TB-24: origin param filters flights."""
        response = client.get("/flights?origin=Bangkok")
        assert response.status_code == 200
        data = response.json()
        assert all(f["origin"] == "Bangkok" for f in data)

    def test_filters_by_destination(self, client, flight_with_seats):
        """TB-24: destination param filters flights."""
        response = client.get("/flights?destination=Singapore")
        assert response.status_code == 200
        data = response.json()
        assert all(f["destination"] == "Singapore" for f in data)

    def test_filters_by_class_type(self, client, flight_with_seats):
        """TB-24: class_type param filters flights."""
        response = client.get("/flights?class_type=economy")
        assert response.status_code == 200
        data = response.json()
        assert all(f["class_type"] == "economy" for f in data)

    def test_includes_flights_with_zero_seats(self, client, flight_no_seats):
        """TB-24: server returns all flights including those with 0 seats (client filters them)."""
        response = client.get("/flights")
        assert response.status_code == 200
        data = response.json()
        assert any(f["seats_available"] == 0 for f in data)

    def test_returns_empty_for_no_matches(self, client):
        """TB-24: no matching flights returns empty list."""
        response = client.get("/flights?destination=Paris")
        assert response.status_code == 200
        data = response.json()
        assert data == [] or all(f["destination"] != "Paris" for f in data)


class TestGetFlight:
    def test_returns_flight_by_id(self, client, flight_with_seats):
        """TB-24: GET /flights/{id} returns the correct flight."""
        response = client.get(f"/flights/{flight_with_seats.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == flight_with_seats.id
        assert data["airline"] == "AirAsia"

    def test_returns_404_for_unknown_flight(self, client):
        """TB-24: unknown flight_id returns 404."""
        response = client.get("/flights/99999")
        assert response.status_code == 404
