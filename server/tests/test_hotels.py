"""TB-24: Server hotels API tests."""

import pytest
from sqlmodel import Session, select

from models.hotel import Hotel
from tests.conftest import test_engine


@pytest.fixture
def hotel_with_rooms():
    with Session(test_engine) as session:
        hotel = Hotel(
            name="The Singapore Suites",
            location="Singapore",
            city="Singapore",
            stars=4,
            price_per_night=120.0,
            rooms_available=5,
            amenities="pool,wifi,gym",
        )
        session.add(hotel)
        session.commit()
        session.refresh(hotel)
        hotel_id = hotel.id
    with Session(test_engine) as session:
        return session.get(Hotel, hotel_id)


@pytest.fixture
def hotel_no_rooms():
    with Session(test_engine) as session:
        hotel = Hotel(
            name="Full Hotel",
            location="Singapore",
            city="Singapore",
            stars=3,
            price_per_night=80.0,
            rooms_available=0,
            amenities="wifi",
        )
        session.add(hotel)
        session.commit()
        session.refresh(hotel)
        hotel_id = hotel.id
    with Session(test_engine) as session:
        return session.get(Hotel, hotel_id)


class TestSearchHotels:
    def test_returns_hotels_list(self, client, hotel_with_rooms):
        """TB-24: GET /hotels returns hotels list."""
        response = client.get("/hotels")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_filters_by_city(self, client, hotel_with_rooms):
        """TB-24: city param filters hotels."""
        response = client.get("/hotels?city=Singapore")
        assert response.status_code == 200
        data = response.json()
        assert all(h["city"] == "Singapore" for h in data)

    def test_filters_by_stars(self, client, hotel_with_rooms):
        """TB-24: stars param filters hotels."""
        response = client.get("/hotels?stars=4")
        assert response.status_code == 200
        data = response.json()
        assert all(h["stars"] == 4 for h in data)

    def test_filters_by_max_price(self, client, hotel_with_rooms):
        """TB-24: max_price param filters hotels."""
        response = client.get("/hotels?max_price=150")
        assert response.status_code == 200
        data = response.json()
        assert all(h["price_per_night"] <= 150 for h in data)

    def test_includes_hotels_with_zero_rooms(self, client, hotel_no_rooms):
        """TB-24: server returns all hotels including those with 0 rooms (client filters them)."""
        response = client.get("/hotels")
        assert response.status_code == 200
        data = response.json()
        assert any(h["rooms_available"] == 0 for h in data)


class TestGetHotel:
    def test_returns_hotel_by_id(self, client, hotel_with_rooms):
        """TB-24: GET /hotels/{id} returns the correct hotel."""
        response = client.get(f"/hotels/{hotel_with_rooms.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == hotel_with_rooms.id
        assert data["name"] == "The Singapore Suites"

    def test_returns_404_for_unknown_hotel(self, client):
        """TB-24: unknown hotel_id returns 404."""
        response = client.get("/hotels/99999")
        assert response.status_code == 404
